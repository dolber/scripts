#!/usr/bin/env python3

from netaddr import *
import ipaddress
import re


def is_valid_ip(ip):
    m = re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip)
    return bool(m)

def check_ip(ip, add_value):
    ip = ipaddress.IPv4Address(ip).exploded
    a, b, c, d = ip.split(".")
    if (d == "255" or d == "0"):
        # print("last didgit is 255 or 0 on " + ip )
        ip = ip
    else:
        if (add_value == "+1"):
            ip = str(ipaddress.IPv4Address(ip) + 1)
        else:
            ip = str(ipaddress.IPv4Address(ip) - 1)
    return ip


def convert_to_cidr(iprange):

    if ("/" in iprange):
        # print("network is " + iprange)
        return iprange
    elif ("-" in iprange):

        ip_first, ip_last = iprange.split("-")
        ip_first = ip_first.strip()
        ip_last = ip_last.strip()

        ip_first1 = check_ip(ip_first, "-1")
        ip_last1 = check_ip(ip_last, "+1")

        # ip_first1 = str(ipaddress.IPv4Address(ip_first)-1)
        # ip_last1 = str(ipaddress.IPv4Address(ip_last)+1)

        if (len(IPRange(ip_first, ip_last).cidrs()) < len(IPRange(ip_first1, ip_last1).cidrs())):
            for cidr in IPRange(ip_first, ip_last).cidrs():
                # print(cidr)
                return cidr
        else:
            # print("printing from " + ip_first1 + " to " + ip_last1)
            for cidr in IPRange(ip_first1, ip_last1).cidrs():
                # print(cidr)
                return cidr

    elif (is_valid_ip(iprange)):
        print(iprange + "/32")
        return iprange + "/32"

    else:
        print("UNABLE TO PARSE " + iprange)
        exit(1)


file = open('iplist.txt', 'r')

for iprange in file:
    iprange = iprange.strip()
    # print("WORKING ON " + iprange)
    cidr  = convert_to_cidr(iprange)
    print(cidr)
