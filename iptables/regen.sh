#!/bin/bash

python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "22, 80, 443" --udp-ports "53, 123" > rules/iptables.web
python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "22, 135, 139, 445" --udp-ports "53, 123, 135, 137, 138" > rules/iptables.samba
python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "22, 25, 465, 587, 993, 995" --udp-ports "53, 123" > rules/iptables.mail
python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "21, 22, 80, 81, 82, 84, 443, 1443, 1994, 2001, 3443, 4443, 5000, 8001, 8002, 8003, 8088, 8089" --udp-ports "53, 69, 82, 123, 1194, 3443, 5060, 5161, 4569, 4000:4999, 10000:20000" > rules/iptables.freePBX
python iptgen_pvj.py --enable-tcp-input-filtering --enable-tcp-output-filtering --enable-udp-filtering --tcp-input-ports "22, 53" --udp-ports "53, 123" > rules/iptables.ns
python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "22, 80, 31337, 54321" --udp-ports "53, 123" > rules/iptables.random
python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "22, 27017" --udp-ports "53, 123" > rules/iptables.mongo
python iptgen_pvj.py --enable-tcp-input-filtering --enable-udp-filtering --tcp-input-ports "22, 6379" --udp-ports "53, 123" > rules/iptables.redis
