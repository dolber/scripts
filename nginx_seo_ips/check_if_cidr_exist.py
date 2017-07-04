#!/usr/bin/env python3

from netaddr import *
import re

def is_valid_network(ip):
    m = re.match(r'(?<!\d\.)(?<!\d)(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}(?!\d|(?:\.\d))', ip)
    return bool(m)

def get_cidr_from_file(filename):
    # cidr = [];
    ipset = IPSet()
    file = open(filename, 'r')

    for line in file:
        if (is_valid_network(line)):
            line = re.sub(' 1;', '', line)
            line = re.sub('#.*', '', line)
            line = re.sub(r'^\s*$', '', line)
            line = line.strip()
            if line.strip():
                ipset.add(line)
                # cidr.append(ipaddress.ip_network(line))
    return ipset


gov_user_networks = get_cidr_from_file('gov_user.conf')
rkn_networks = get_cidr_from_file('rkn_3_07_2017')
rkn_networks_fulllist = get_cidr_from_file('rkn_3_07_2017.fulllist')

all_block = gov_user_networks | rkn_networks | rkn_networks_fulllist

not_in_gov_user = all_block ^ gov_user_networks

print("#######################")
print("# Total IP's in gov_user_networks " + str(len(gov_user_networks)))
print("# Total IP's in rkn_networks " + str(len(rkn_networks)))
print("# Total IP's in rkn_networks_fulllist " + str(len(rkn_networks_fulllist)))
print("# Total IP's in all_block " + str(len(all_block)))
print("# Total IP's in not_in_gov_user " + str(len(not_in_gov_user)))

for cidr in not_in_gov_user.iter_cidrs():
    print(str(cidr) + " 1;")

