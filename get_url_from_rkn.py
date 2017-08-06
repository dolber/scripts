#!/usr/bin/env python3

import re
from urllib.parse import urlparse
import whois
import sys
import dns.resolver
import tldextract

def check_domain_soa(domain):
    # print("Working with domain " + domain)
    try:
        dns_answer = dns.resolver.query(domain, 'SOA')
        for rdata in dns_answer:
            # print(rdata)
            if (rdata.serial):
                return True
                pass
    except dns.resolver.NoAnswer as e:
        # print("False NoAnswer" + str(e))
        return True
    except dns.resolver.NXDOMAIN as e:
        # print("False NXDOMAIN " + str(e))
        return False
    except dns.exception.DNSException as e:
        # print("False 1" + str(e))
        return False
    print("False last")
    return False


def run_only_number(number_run):
    global i
    i=i+1
    if (i == number_run):
        sys.exit()
    else:
        pass


hosts = set()
free_domains = set()
i = 0

extract = tldextract.TLDExtract(include_psl_private_domains=True)
extract.update() # necessary until #66 is fixed

with open('dump.csv', encoding="ISO-8859-1") as f:
    lines = str(f.readlines())
    urls = re.findall('https://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', lines)


for url in urls:
    # print("working on " + url)
    host = urlparse(url)
    host = host.netloc
    host = host.replace("www.", "").replace(":443", "").replace(";", "")
    host = tldextract.extract(host)
    host = host.domain + "." + host.suffix
    # print(url + " to " + host)
    hosts.add(host)

# print(hosts)
# print(str(len(hosts)))
print(str(len(hosts)) + " https domains found")


for domain in hosts:
    print("Start work with " + domain)
    if (check_domain_soa(domain) == False):
        free_domains.add(domain)

#    if (i == 4):
print(str(len(free_domains)) + " free https domains found")
with open('free_domains.txt', mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(list(free_domains)))

# run_only_number(5)
