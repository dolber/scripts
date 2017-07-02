#!/usr/bin/env python3

import pyasn

# Initialize module and load IP to ASN database
# the sample database can be downloaded or built - see below
# asndb = pyasn.pyasn('ipasn_20170505.0800.dat')
asndb = pyasn.pyasn('ipasn_20170627.1200.dat')


# print(asndb.lookup('8.8.8.8'))
# should return: (15169, '8.8.8.0/24'), the origin AS, and the BGP prefix it matches

# print(asndb.get_as_prefixes(15169))
# print(len(asndb.get_as_prefixes(15169)))
# returns ['130.161.0.0/16', '131.180.0.0/16', '145.94.0.0/16'], TU-Delft prefixes

# corbina AS8402
# print(asndb.get_as_prefixes(8402))
# AS13238 - AS-YANDEX
# AS15169 - GOOGLE
# AS47764 - mail.ru 

# for net in asndb.get_as_prefixes(8402):
#     print(net)

print("geo $seo_user {");
print("default 0;")
print("");

print("# AS-YANDEX networks")
for net in asndb.get_as_prefixes(13238):
    print(net + " 1;")

print("")
print("# GOOGLE networks")
for net in asndb.get_as_prefixes(15169):
    print(net + " 1;")

print("")
print("}")
print("")
