# SELinux

## SELinux support

**SELinux is supported on CentOS, but not on Ubuntu.**

On Ubuntu, there's a similar MAC system AppArmor. It's easier to configure and use than SELinux, but functionality is not as mature. For instance, the AppArmor module for Apache wont do anything without further customizations.

## Should we use SELinux?

### SELinux advantages

SELinux could substantially limit the damage caused by a compromised service.

As an example, our web apps under Apache are likely to be compromised. In the event that this happens, the attackers may try to:

- Launch forward or reverse shells.
- Start beacons, showing scorebot we've been compromised.
- Read flags from the filesystem.
- Escalate privileges.

However, with SELinux running, Apache will run under the limited httpd_t context, and a compromised Apache should run in the same context. This should make the above actions more difficult.

- A forward shell would be more difficult to launch because only TCP ports 80, 81, 443, 488, 8008, 8009, 8443, and 9000 are permitted by the http_port_t context.
- A reverse shell and a beacon would be more difficult to launch with the httpd_can_network_connect boolean set to 0 (default), which should prevent most outbound connections.
- Files outside of typical Apache directories (e.g. /var/www) will be difficult to read.
- The network and file restrictions will likely make privilege escalation more difficult.

### SELinux disadvantages

SELinux can be inconvenient to use, especially without a good understanding of it. For that reason, disabling SELinux is often one of the first things a sysadmin does after a Linux install.

- **A reboot will likely be required. If the server is in a bad state, it's possible we'll have difficulty getting it back up.**
- If we enable SELinux in enforcing mode on an already functioning system, we're likely to break things. This may cause outages and loss of points. (We could try to mitigate this by first enabling it in permissive mode and then troubleshooting.)
- Specifically, root's authorized_keys may stop working. To fix: `restorecon -R -v /root/.ssh`
- We may need to spend a substantial amount of time flipping SELinux booleans, changing file contexts, making other changes, and troubleshooting. This will take up time we could be using for other purposes.
- It's possible we wont be able to get SELinux to work right.
- We might end up with Ubuntu which doesn't support SELinux.

## SELinux quick start

### CentOS 6

1. In `/etc/sysconfig/selinux`, change `SELINUX=disabled` to  `SELINUX=permissive` and then reboot. (Or skip this step if it's already `permissive`.)

2. Install setroubleshoot and setroubleshoot-server, and then restart the necessary services:

   ```
   yum install setroubleshoot setroubleshoot-server
   service auditd restart
   service messagebus restart
   ```
   
3. Restart the services monitored by scorebot and wait a few minutes for scorebot to do its testing.

4. Look in /var/log/messages for SELinux alerts and mitigation instructions. Example:

   ```
   Oct 21 18:59:06 localhost setroubleshoot: SELinux is preventing /usr/sbin/httpd from read access on the file index.html. For complete SELinux messages. run sealert -l 4935d9aa-6f8e-4b2e-85d3-127f681ed4ef
   ```

5. Use `getsebool`, `setsebool`, `semanage`, `restorecon`, and `chcon` as necessary to mitigate all alerts. See the section below for details on specific services.

6. After you've successfully mitigated all alerts: In `/etc/sysconfig/selinux`, change `SELINUX=permissive` to  `SELINUX=enforcing`. Then run `setenforce 1` to enable enforcing without a reboot.

7. Carefully monitor the leaderboard and ensure all services are green. If anything breaks, change SELinux back to permissive.


## SELinux for different services

### SSH server

In Avi's lab, root's authorized_keys wouldn't work with SELinux's default configuration on CentOS 6.0. To fix:

```
restorecon -R -v /root/.ssh
```

### Apache

See: https://fedoraproject.org/wiki/SELinux/apache

For web apps on Apache, SELinux is unlikely to work out of the box. If we enable it in enforcing mode, we'll probably break things. It's likely we'll need to do one or more of the following:

- Change the context of files using either `chcon` (quick hacky way) or `semanage fcontext` followed by `restorecon`.
- Flip SELinux booleans for Apache. See [here](https://fedoraproject.org/wiki/SELinux/apache) for the booleans and their descriptions.

#### Joomla

If we get a Joomla web app running on Apache, these instructions (adapted from [here](https://forum.joomla.org/viewtopic.php?t=933652#p3481769)) may be sufficient to get SELinux working with Joomla:

```
cd <path_to_joomla_files>
chcon -Rv -t httpd_sys_content_t    joomla
chcon -Rv -t httpd_cache_t          joomla/administrator/cache
chcon -Rv -t httpd_cache_t          joomla/cache
chcon -Rv -t httpd_sys_log_t        joomla/logs
chcon -Rv -t httpd_sys_rw_content_t joomla/tmp
setsebool -P httpd_can_network_connect_db=1
setsebool -P httpd_can_sendmail=1
setsebool -P httpd_unified=1
```

#### Drupal

If we get a Drupal web app running on Apache, these instructions (adapted from [here](https://www.drupal.org/docs/7/install/os-specific-download-notes#linux)) may be sufficient to get SELinux working with Drupal:

```
chcon -R -t httpd_sys_content_t <path_to_drupal_files>
setsebool -P httpd_can_network_connect_db=1
setsebool -P httpd_can_sendmail=1
setsebool -P httpd_unified=1
```

### Samba

See: https://fedoraproject.org/wiki/SELinux/samba

The setup is likely similar to Apache: change some file contexts and flip a few booleans.

### BIND

BIND, chroot or not, should likely work out of the box with SELinux.

### Gitlab

Gitlab appears to have an embedded Nginx web server. On CentOS, there doesn't appear to be modules for Gitlab or Nginx. So to keep it simple, we should probably just leave SELinux in permissive.

## Learn more

"[SELinux for mere morals](https://www.youtube.com/watch?v=MxjenQ31b70)" is a very good practical intro to SELinux.