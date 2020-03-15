#!/usr/bin/env python3

'''
Split Huawei Balong router NAND block dump to separate partitions
by ValdikSS <iam@valdikss.org.ru>, 2020

This utility automatically finds pTable and splits the image
to partitions.
'''

import sys
print("Huawei Balong router NAND block dump splitter by ValdikSS <iam@valdikss.org.ru>, 2020")
print("https://github.com/Huawei-LTE-routers-mods")
if len(sys.argv) != 2:
    print("Usage: {} <flash dump.bin>".format(sys.argv[0]))
    sys.exit(1)

f = open(sys.argv[1], "rb")
firstdata = f.read(0x2000)
ptablehead = firstdata.find(b"pTableHead")
ptabletail = firstdata.find(b"pTableTail")
if not ptablehead or not ptabletail:
    print("Can't find pTableHead or pTableTail!")
    sys.exit(1)
print("Found pTableHead at {}, pTableTail at {}".format(ptablehead, ptabletail))
ptable = firstdata[ptablehead:ptabletail]

number = 0
offset = 0x30
while True:
    pname = ptable[offset:offset+16]
    if not pname or pname == b"\x00" * 16 or pname == b"T" + b"\x00" * 15:
        break
    pname = pname.decode().replace("\x00", "")
    poffset = int.from_bytes(ptable[offset+16:offset+20], 'little')
    ploadsize = int.from_bytes(ptable[offset+20:offset+24], 'little')
    pcapacity = int.from_bytes(ptable[offset+24:offset+28], 'little')
    print("Partition {}, offset = {}, loadsize = {}, capacity = {}".format(
        pname, poffset, ploadsize, pcapacity
        ))
    with open("{:02d}_{}_0x{:x}.bin".format(number, pname, poffset), "wb") as w:
        f.seek(poffset, 0)
        w.write(f.read(pcapacity))
    offset += 8*4 + 16
    number += 1

f.close()
