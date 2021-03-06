#!/usr/bin/python2.7

import argparse
import sys

parser = argparse.ArgumentParser(description="Generate host iptables rules for Blue Team in Pros Vs Joes CTF.")
parser.add_argument("--enable-tcp-input-filtering", dest="enable_tcp_input_filtering", action='store_true', help="Enable TCP filtering on INPUT chain. (Default: False)")
parser.add_argument("--enable-tcp-output-filtering", dest="enable_tcp_output_filtering", action='store_true', help="Enable TCP filtering on OUTPUT chain. (Default: False)")
parser.add_argument("--enable-udp-filtering", dest="enable_udp_filtering", action='store_true', help="Enable UDP filtering. (Default: False)")
parser.add_argument("--tcp-input-ports", dest="tcp_input_ports", type=str, help="TCP ports for INPUT chain. Comma separated string.")
parser.add_argument("--tcp-output-ports", dest="tcp_output_ports", type=str, help="TCP ports for OUTPUT chain. Comma separated string.")
parser.add_argument("--udp-ports", dest="udp_ports", type=str, help="UDP ports for both directions. Comma separated string.")
args = parser.parse_args()

print ("#")
print ("# These rules were generated by " + sys.argv[0] + " with the following arguments:")
sys.stdout.write("# ")
for i in sys.argv:
    sys.stdout.write(i.replace(" ","") + " ")
sys.stdout.write("\n")
print ("#")

print("*filter")
print(":INPUT ACCEPT [0:0]")

if args.enable_tcp_input_filtering:
    if type(args.tcp_input_ports) is str:
        tcp_input_ports = args.tcp_input_ports.replace(" ", "").split(',')
    else:
        tcp_input_ports = []
    tcp_input_ports += ["22"]  # Don't lock ourselves out!
    tcp_input_ports += ["25", "80", "443"]  # Required by PvJ rules
    tcp_input_ports = list(set(tcp_input_ports))

if args.enable_tcp_output_filtering:
    if type(args.tcp_output_ports) is str:
        tcp_output_ports = args.tcp_output_ports.replace(" ", "").split(',')
    else:
        tcp_output_ports = []
    tcp_output_ports += tcp_input_ports + ["25", "80", "443"]  # Required by PvJ rules
    tcp_output_ports = list(set(tcp_output_ports))

if args.enable_udp_filtering:
    if type(args.udp_ports) is str:
        udp_ports = args.udp_ports.replace(" ", "").split(',')
    else:
        udp_ports = []
    udp_ports += ["53"] # We need DNS for sure
    udp_ports = list(set(udp_ports))

if args.enable_tcp_input_filtering:
    print("# TCP traffic filtering on INPUT chain")
    for port in tcp_input_ports:
        print("-A INPUT  -p tcp -m tcp --dport " + port + " -j ACCEPT")
    print("-A INPUT  -p tcp -m tcp --syn -j DROP")

if args.enable_udp_filtering:
    print("# UDP traffic filtering on INPUT chain")
    for port in udp_ports:
        print("-A INPUT  -p udp -m udp --sport " + port + " -j ACCEPT")
        print("-A INPUT  -p udp -m udp --dport " + port + " -j ACCEPT")
    print("-A INPUT  -p udp -m udp -j DROP")

print(":FORWARD ACCEPT [0:0]")

print(":OUTPUT ACCEPT [0:0]")

if args.enable_tcp_output_filtering:
    print("# TCP traffic filtering on OUTPUT chain")
    for port in tcp_output_ports:
        print("-A OUTPUT -p tcp -m tcp --dport " + port + " -j ACCEPT")
    print("-A OUTPUT -p tcp -m tcp --syn -j DROP")

if args.enable_udp_filtering:
    print("# UDP traffic filtering on OUTPUT chain")
    for port in udp_ports:
        print("-A OUTPUT -p udp -m udp --sport " + port + " -j ACCEPT")
        print("-A OUTPUT -p udp -m udp --dport " + port + " -j ACCEPT")
    print("-A OUTPUT -p udp -m udp -j DROP")

print("COMMIT")
