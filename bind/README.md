# Securing BIND

This page includes some of notes on securing BIND for the Capcha This Blue Team in the Joes Vs Pros CTF at BSidesDC 2019. It's important to note that securing the underlying OS is beyond the scope of these notes, and the notes here will not protect BIND if root on the OS is compromised via other means.

## Previous years' experience

### The importance of BIND

The scorebot relies on DNS, which runs on BIND. If our DNS goes down, we lose a ton of points until we get it back up.

### configure_chroot_jail.sh

Last year, a member of Techtonic's team put together a [configure_chroot_jail.sh](bind/configure_chroot_jail.sh) script to secure BIND from attackers. Techtonic notes that towards the end of the game they lost access to this box. DNS still functioned, but they could not access the box. They never confirmed if Red was the culprit, or if they did it to themselves with the script.

Avi has additional concerns about the script, and would advise not using it this year.

### TKEY vulnerability

A few previous Blue team players note that this TKEY query DoS [vulnerability](https://kb.isc.org/docs/aa-01272) has been a target. See [here](../previous_winners_notes.txt) and [here](https://lockboxx.blogspot.com/2016/08/blue-teaming-at-pros-vs-joes-ctf.html?view=classic). This should be easily patched with a package upgrade.

## Upgrade the packages

### Upgrade the BIND packages

The first thing we should do is do an apt or yum upgrade of the BIND packages. This should be a safe enough upgrade.

#### Ubuntu 16

```
apt install bind9
```

#### CentOS 6

```
yum install bind
```

### Upgrade the packages for libraries used by BIND

We could be subject to attacks on vulnerabilities in libraries used by BIND. We can use these commands to upgrade those.

#### Ubuntu 16

To identify the packages to upgrade:

```
for i in $(ldd /usr/sbin/named | cut -d'>' -f2 | cut -d'(' -f1); do dpkg -S $i | cut -d':' -f1; done | sort | uniq | tr '\n' ' '; echo
```

To upgrade them:

```
apt install libbind9-140 libc6 libcap2 libcomerr2 libdns162 libgcc1 libgeoip1 libgssapi-krb5-2 libicu55 libisc160 libisccc140 libisccfg140 libk5crypto3 libkeyutils1 libkrb5-3 libkrb5support0 liblwres141 liblzma5 libssl1.0.0 libstdc++6 libxml2 zlib1g
```

#### CentOS 6

To identify the packages to upgrade:

```
for i in $(ldd /usr/sbin/named | cut -d'>' -f2 | cut -d'(' -f1); do rpm -qf $i | sed 's/-[0-9].*//'; done | sort | uniq | tr '\n' ' '; echo
```

To upgrade them:

```
yum install bind-libs glibc keyutils-libs krb5-libs libattr libcap libcom_err libselinux libxml2 openssl zlib
```

## AppArmor vs chroot

BIND can be run in a chroot, and this is often recommened for improved security. However, the Ubuntu documentation [recommends](https://help.ubuntu.com/community/BIND9ServerHowto) using AppArmor instead of chroot. On Ubuntu 7.10 and later, AppArmor is enabled by default. But we don't know for sure what OS we're getting, and even if we get Ubuntu, we might find that AppArmor is broken, disabled, or misconfigured.

### Enable AppArmor for BIND

*Note: The AppArmor instructions here are applicable to Ubuntu. They may also be somewhat relevant to Debian or SuSE. But they are not at all relevant to CentOS, which does not support AppArmor.*

On Ubuntu 7.10 and later, AppArmor should be configured and enabled by default. But we might find it broken, disabled, or misconfigured.

This [page](https://help.ubuntu.com/community/AppArmor#Enable_AppArmor_framework) under **Enable AppArmor framework** has instructions on enabling AppArmor in Ubuntu, which may help if we need to fix it.

Additionally, On Ubuntu 16, the AppArmor profile for BIND should look like this out of the box:

```
root@ubuntu16:~# cat /etc/apparmor.d/usr.sbin.named
# vim:syntax=apparmor
# Last Modified: Fri Jun  1 16:43:22 2007
#include <tunables/global>

/usr/sbin/named {
  #include <abstractions/base>
  #include <abstractions/nameservice>

  capability net_bind_service,
  capability setgid,
  capability setuid,
  capability sys_chroot,
  capability sys_resource,

  # /etc/bind should be read-only for bind
  # /var/lib/bind is for dynamically updated zone (and journal) files.
  # /var/cache/bind is for slave/stub data, since we're not the origin of it.
  # See /usr/share/doc/bind9/README.Debian.gz
  /etc/bind/** r,
  /var/lib/bind/** rw,
  /var/lib/bind/ rw,
  /var/cache/bind/** lrw,
  /var/cache/bind/ rw,

  # gssapi
  /etc/krb5.keytab kr,
  /etc/bind/krb5.keytab kr,

  # ssl
  /etc/ssl/openssl.cnf r,

  # GeoIP data files for GeoIP ACLs
  /usr/share/GeoIP/** r,

  # dnscvsutil package
  /var/lib/dnscvsutil/compiled/** rw,

  @{PROC}/net/if_inet6 r,
  @{PROC}/*/net/if_inet6 r,
  @{PROC}/sys/net/ipv4/ip_local_port_range r,
  /usr/sbin/named mr,
  /{,var/}run/named/named.pid w,
  /{,var/}run/named/session.key w,
  # support for resolvconf
  /{,var/}run/named/named.options r,

  # some people like to put logs in /var/log/named/ instead of having
  # syslog do the heavy lifting.
  /var/log/named/** rw,
  /var/log/named/ rw,

  # gssapi
  /var/lib/sss/pubconf/krb5.include.d/** r,
  /var/lib/sss/pubconf/krb5.include.d/ r,
  /var/lib/sss/mc/initgroups r,
  /etc/gss/mech.d/ r,

  # ldap
  /etc/ldap/ldap.conf r,
  /{,var/}run/slapd-*.socket rw,

  # dynamic updates
  /var/tmp/DNS_* rw,

  # Site-specific additions and overrides. See local/README for details.
  #include <local/usr.sbin.named>
}
root@ubuntu16:~#
```

The `aa-unconfined` command (which requires the `apparmor-utils` package) can be used to verify that AppArmor is enabled on /usr/sbin/named (BIND):

```
root@ubuntu16:~# aa-unconfined
7889 /sbin/dhclient confined by '/sbin/dhclient (enforce)'
8757 /usr/sbin/sshd not confined
10325 /usr/sbin/named confined by '/usr/sbin/named (enforce)'
root@ubuntu16:~#
```

### Enable chroot for BIND

#### Ubuntu 16

The Ubuntu documentation recommends AppArmor instead of chroot. But if we decide we want chroot anyway, these Debian [instructions](https://wiki.debian.org/Bind9#Bind_Chroot) seem to be the best available. On Ubuntu 16, however, **a few additional changes are necessary**:

1. BIND should not be stopped until the end of the chroot setup, since BIND outages will cost us lots of points. At the end of the chroot setup we should do a BIND restart, and be prepared to fix something or roll back if needed.

2. Follow the instructions for systemd / jesse, unless we're on an older release of Ubuntu.

3. Some additional OpenSSL engine fixes are required before BIND will restart properly:

   ```
   mkdir -p /var/bind9/chroot/usr/lib/x86_64-linux-gnu/openssl-1.0.0/engines/
   cp -p /usr/lib/x86_64-linux-gnu/openssl-1.0.0/engines/* /var/bind9/chroot/usr/lib/x86_64-linux-gnu/openssl-1.0.0/engines/
   echo "/var/bind9/chroot/usr/lib/x86_64-linux-gnu/openssl-1.0.0/engines/* r," >> /etc/apparmor.d/local/usr.sbin.named
   service apparmor reload
   ```

#### CentOS 6

For CentOS 6, the chroot setup is very easy.

```
yum install bind-chroot
service named restart
```

Then verify that it's running from the chroot like this:

```
[root@centos6 ~]# ps auxw | grep named
named      2217  0.0  0.5 159344 11056 ?        Ssl  12:04   0:00 /usr/sbin/named -u named -t /var/named/chroot
root       2246  0.0  0.0 103148   852 pts/0    S+   12:07   0:00 grep named
[root@centos6 ~]#
```

#### CentOS 7

For CentOS 7, the chroot setup is also very easy.

```
yum install bind-chroot
systemctl disable named
systemctl enable named-chroot
systemctl stop named
systemctl start named-chroot
```

For more information, see this Red Hat knowledge base [article](https://access.redhat.com/articles/770133). To get access, register for free at the [Red Hat Developer](https://developers.redhat.com/#) website.

## Filesystem permissions

### Preventing unprivileged writes to BIND's files

We need to ensure that unprivileged users cannot write to any of BIND's files.

The following commands should report BIND files that may be writable by unprivileged users.

#### Ubuntu 16:

```
find /var/bind9/chroot /etc/bind /var/cache/bind \( -type f -or -type d \) -and \( \( ! -user root -and ! -user bind \) -or -perm -o+w \)
```

#### CentOS 6:

```
find /etc/rndc.key /etc/named.conf /etc/named /var/named/data /var/named/dynamic /var/named/slaves /var/named/named* /var/named/chroot/var/named \( -type f -or -type d \) -and \( \( ! -user root -and ! -user named \) -or -perm -o+w \)
```

Additionally, if ACLs are enabled on the filesystem, then it will be necessary to look at the ACLs too using `getfacl`. To check if ACLs are enabled, look for the `acl` mount option.

```
mount | grep acl
```

## BIND configuration parameters to secure

The following are some configuration parameters we should ensure are secure.

### Disable remote administration

To disable remote administration, the `controls {}` block should be defined as follows or not included at all.

```
controls {
  inet 127.0.0.1 allow { localhost; } keys { "rndc-key"; };
};
```

### Limit statements related to zone transfers and updates

If we don't have any slaves, then any `allow` parameters that relate to zone transfers and updates should be set to `none`. Otherwise, they should be defined as limited as possible.

These parameters may appear in either `options { ... }` or in `zone ... { ... }`.

```
allow-notify { none; };
allow-transfer { none; };
allow-update { none; };
allow-update-forwarding { none; };
```

Additionally, if we have no slaves, then we should be on the lookout for any of the following [other parameters](http://www.zytrax.com/books/dns/ch7/xfer.html) related to zone transfers and updates, because they probably shouldn't be there.

- also-notify
- alt-transfer-source[-v6]
- ixfr-from-differences
- max-journal-size
- max-refresh-time, min-refresh-time
- max-retry-time, min-retry-time
- max-transfer-idle-in
- max-transfer-idle-out
- max-transfer-time-in
- max-transfer-time-out
- max-transfer-idle-in
- multi-master
- max-transfer-idle-in
- notify
- notify-source
- notify-source-v6
- provide-ixfr
- request-ixfr
- serial-query-rate
- transfer-format
- transfer-source
- transfer-source-v6
- transfers-in
- transfers-out
- transfer-per-ns
- update-policy
- use-alt-transfer-source

### Enable minimal responses

This may reduce our vulnerability to DoS attacks and shouldn't break anything:

```
options {
	minimal-responses yes;
};
```

In addition, in the unlikely event that we have BIND >= 9.11, then we may want to enable `minimal-any` too:

```
options {
	minimal-any yes;
};
```

## RNDC key security

If the BIND server has already been compromised, the Red Team may already have our RNDC key, which could be used to launch future attacks. After we secure BIND, we should regenerate the RNDC key and restart BIND. We might need to do this multiple times if we are repeatedly compromised.

### Ubuntu 16

```
rndc-confgen -a -r /dev/urandom
service bind9 restart
rndc status
```

Example:

```
root@ubuntu16:~# rndc-confgen -a -r /dev/urandom
wrote key file "/etc/bind/rndc.key"
root@ubuntu16:~# service bind9 restart
root@ubuntu16:~# rndc status
version: BIND 9.10.3-P4-Ubuntu <id:ebd72b3>
boot time: Tue, 15 Oct 2019 21:18:24 GMT
last configured: Tue, 15 Oct 2019 21:18:24 GMT
CPUs found: 1
worker threads: 1
UDP listeners per interface: 1
number of zones: 101
debug level: 0
xfers running: 0
xfers deferred: 0
soa queries in progress: 0
query logging is OFF
recursive clients: 0/0/1000
tcp clients: 3/100
server is up and running
root@ubuntu16:~#
```

### CentOS 6

```
rndc-confgen -a -r /dev/urandom
service named restart
rndc status
```

Example:

```
[root@centos6 ~]# rndc-confgen -a -r /dev/urandom
wrote key file "/etc/rndc.key"
[root@centos6 ~]# service named restart
Stopping named: .                                          [  OK  ]
Starting named:                                            [  OK  ]
[root@centos6 ~]# rndc status
version: 9.8.2rc1-RedHat-9.8.2-0.68.rc1.el6_10.3
CPUs found: 1
worker threads: 1
number of zones: 19
debug level: 0
xfers running: 0
xfers deferred: 0
soa queries in progress: 0
query logging is OFF
recursive clients: 0/0/1000
tcp clients: 2/100
server is up and running
[root@centos6 ~]#
```

### CentOS 7

```
rndc-confgen -a -r /dev/urandom
service named-chroot restart
rndc status
```

## Other security features

### DNSSEC

This might help prevent MITM attacks on DNS, but Avi doesn't understand it well enough to set it up yet. Probably not worth the trouble. TBD.

### TSIG for secure zone transfers

Probably no BIND slaves, so probably not needed?

## Further reading

### General BIND security

This presentation on securing BIND is very helpful:

- https://www.youtube.com/watch?v=_9nvn3jdpmU
- https://www.slideshare.net/MenandMice/a-secure-bind-9-best-practices
