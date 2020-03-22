

# Firewall rules

This section is for planning the firewall rules we're going to set when we show up for the CTF.

## TCP and UDP ports by server class

We don't know what we're going to see when we show up at Pros Vs Joes. The information below is a best guess based on:

- The servers and services listed in the scoreboard for BSidesDC 2018 on the Pros Vs Joes [website](http://www.prosversusjoes.net).
- Avi's judgment about how to classify those servers and services.
- Port assignments Avi knows from personal experience or found on Google.

The necessary egress TCP ports are difficult to predict and are not considered here.

This table errs on the side of more ports vs less, but we should narrow them down further once we understand what's actually needed.

| Class   | OS      | Services                                                     | Ingress TCP destination ports                                | UDP ports                                                    | **Notes**                                                    |
| ------- | ------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| web     | Linux   | www, drupal, ecommerce, gitlab                               | 22, 80, 443                                                  | 53, 123                                                      |                                                              |
| samba   | Linux   | samba                                                        | 22, 135, 139, 445                                            | 53, 123, 135, 137, 138                                       |                                                              |
| mail    | Linux   | mail                                                         | 22, 25, 465, 587, 993, 995                                   | 53, 123                                                      |                                                              |
| freePBX | Linux   | freePBX                                                      | 21, 22, 80, 81, 82, 84, 443, 1443, 1994, 2001, 3443, 4443, 5000, 8001, 8002, 8003, 8088, 8089 | 53, 69, 82, 123, 1194, 3443, 5060, 5161, 4569, 4000:4999, 10000:20000 | See this [page](https://wiki.freepbx.org/display/PPS/Ports+used+on+your+PBX). We could probably narrow this down, but may not be worth the trouble. |
| ns      | Linux   | ns                                                           | 22, 53                                                       | 53, 123                                                      |                                                              |
| random  | Linux   | puzzle3, puzzle11, puzzle13, puzzle25, puzzlemail, specialApp | 22, 80, 31337, 54321                                         | 53, 123                                                      |                                                              |
| mongo   | Linux   | puzzle15                                                     | 22, 27017                                                    | 53, 123                                                      |                                                              |
| redis   | Linux   | redis                                                        | 22, 6379                                                     | 53, 123                                                      |                                                              |
| dc      | Windows | dc, dc2                                                      | 53, 88, 135, 139, 389, 445, 464,  636, 3268, 3269, 3389, 9389, 1024:65535 | 53, 88, 123, 137, 138, 389                                   | See this [page](https://support.microsoft.com/en-us/help/179442/how-to-configure-a-firewall-for-domains-and-trusts) and this [page](https://support.microsoft.com/en-us/help/832017/service-overview-and-network-port-requirements-for-windows). With all these ports open, especially 1024-65535, a firewall may be almost useless. This could use some more attention. |
| desktop | Windows | desktop-1, desktop-2                                         | 445, 3389                                                    | 53, 123, 137, 138                                            |                                                              |
| Web77v1 | Windows | Web77v1                                                      | 80, 3389                                                     | 53, 123                                                      |                                                              |

## Firewall rules on Linux (iptables)

See [iptables](../iptables).