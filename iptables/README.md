# Firewall rules on Linux (iptables)

## Generate iptables rules

Avi has written [iptgen_pvj.py](iptgen_pvj.py) (Python 2.7) to quickly generate iptables rules appropriate for the CTF. The rules generated are consistent with the firewall requirements [here](http://prosversusjoes.net/BSidesLV2017ProsVJoesCTFrules.html). To keep UDP filtering simple, any UDP port that's opened is opened in both directions.

### Usage

```
usage: iptgen_pvj.py [-h] [--enable-tcp-input-filtering]
                     [--enable-tcp-output-filtering] [--enable-udp-filtering]
                     [--tcp-input-ports TCP_INPUT_PORTS]
                     [--tcp-output-ports TCP_OUTPUT_PORTS]
                     [--udp-ports UDP_PORTS]

Generate host iptables rules for Blue Team in Pros Vs Joes CTF.

optional arguments:
  -h, --help            show this help message and exit
  --enable-tcp-input-filtering
                        Enable TCP filtering on INPUT chain. (Default: False)
  --enable-tcp-output-filtering
                        Enable TCP filtering on OUTPUT chain. (Default: False)
  --enable-udp-filtering
                        Enable UDP filtering. (Default: False)
  --tcp-input-ports TCP_INPUT_PORTS
                        TCP ports for INPUT chain. Comma separated string.
  --tcp-output-ports TCP_OUTPUT_PORTS
                        TCP ports for OUTPUT chain. Comma separated string.
  --udp-ports UDP_PORTS
                        UDP ports for both directions. Comma separated string.
```

### Example

```
python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "22, 80, 443" --udp-ports "53, 123" > rules/iptables.web
```



## Sample iptables rules

You can find sample rules for the various server clases in [rules](rules/). They use the ports in [fwrules](../fwrules). They filtering for TCP ingress and UDP in both directions, but not TCP egress. Before applying any rules, please review them for accuracy and suitability.

## Apply iptables rules

We want our iptables rules to be easily loadable, easily editable, and persistent across reboots.

### CentOS

On CentOS 7, the first thing to do is stop and disable firewalld, which conflicts with iptables. This wont be necessary on CentOS 6.

```
systemctl disable firewalld
systemctl stop firewalld
```

On CentOS, the iptables rules go in `/etc/sysconfig/iptables`.  You can insert the rules into the file (see the links in the table above), and then do:

```
service iptables restart
```

And to keep the rules persistent across reboots:

```
chkconfig iptables on
```

### Ubuntu

On Ubuntu, iptables rules go in in `/etc/iptables.rules`. You can insert the rules into the file (see the links in the table above), and then do:

```
iptables-restore < /etc/iptables.rules
```

The recommended [methods](https://help.ubuntu.com/community/IptablesHowTo#Configuration_on_startup) to make the rules persistent across reboots are a pain, but this quick hack should work:

```
echo "/sbin/iptables-restore < /etc/iptables.rules" >> /etc/rc.local
chmod u+x /etc/rc.local
```

