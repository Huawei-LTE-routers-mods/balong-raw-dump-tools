#!/usr/bin/env python3

'''
Convert Huawei Balong router RAW NAND dump with oob and ecc (read with programmer) to Huawei block format
by ValdikSS <iam@valdikss.org.ru>, 2020

1040 data
14 junk
994 data
2 junk
14 data
48 junk
'''

import sys
print("RAW NAND dump to Huawei block converter by ValdikSS <iam@valdikss.org.ru>, 2020")
print("https://github.com/Huawei-LTE-routers-mods")
if len(sys.argv) != 3:
    print("Usage: {} <input raw dump.bin> <output proper dump.bin>".format(sys.argv[0]))
    sys.exit(1)

f = open(sys.argv[1], "rb")
w = open(sys.argv[2], "wb")

while True:
    r = f.read(1040)
    f.read(14)
    r += f.read(994)
    f.read(2)
    r += f.read(14)
    f.read(48)
    if not r:
        break
    w.write(r)

f.close()
w.close()
print("OK")
