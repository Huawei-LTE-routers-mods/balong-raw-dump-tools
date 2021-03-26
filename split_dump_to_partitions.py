#!/usr/bin/env python3

'''
Split Huawei Balong router NAND block dump to separate partitions
by ValdikSS <iam@valdikss.org.ru>, 2021

This utility automatically finds pTable and splits the image
to partitions.

Balong V7R1, V7R2, V7R11, V7R22, V7R5 and 5000 series supported.
'''

import sys
print("Huawei Balong router NAND block dump splitter by ValdikSS <iam@valdikss.org.ru>, 2021")
print("https://github.com/Huawei-LTE-routers-mods")
if len(sys.argv) != 2:
    print("Usage: {} <flash dump.bin>".format(sys.argv[0]))
    sys.exit(1)

MODE_V7R11 = 1
MODE_5000  = 2

def parsePartitions(firstdata):
    partitions = []
    mode = MODE_V7R11
    number = 0

    # Balong V7R1, V7R2, V7R11, V7R22, V7R5
    ptablehead = firstdata.find(b"pTableHead")
    ptabletail = firstdata.find(b"pTableTail")
    if ptablehead == -1 or ptabletail == -1:
        # Balong 5000
        ptablehead = firstdata.find(b"PART")
        ptabletail = ptablehead + 2048
        mode = MODE_5000
    if ptablehead == -1:
        return

    if mode == MODE_V7R11:
        offset = 0x30
    else:
        offset = 12

    ptable = firstdata[ptablehead:ptabletail]
    while True:
        pname = ptable[offset:offset+16]
        if not pname or pname == b"\x00" * 16 or pname == b"T" + b"\x00" * 15:
            break
        pname = pname.decode().replace("\x00", "")
        poffset = int.from_bytes(ptable[offset+16:offset+20], 'little')
        param1 = int.from_bytes(ptable[offset+20:offset+24], 'little')
        param2 = int.from_bytes(ptable[offset+24:offset+28], 'little')
        partitions.append({"num": number,
                           "name": pname,
                           "offset": poffset,
                           "loadsize" if mode == MODE_V7R11 else "size": param1,
                           "size" if mode == MODE_V7R11 else "flags": param2
                           })
        if mode == MODE_V7R11:
            offset += 8*4 + 16
        else:
            offset += 3*4 + 16

        number += 1

    return {"mode": mode,
            "ptablehead": ptablehead,
            "ptabletail": ptabletail,
            "partitions": partitions}


f = open(sys.argv[1], "rb")
firstdata = f.read(0x2000)
parsed = parsePartitions(firstdata)
if not parsed:
    print("Found no partitions!")
    sys.exit(1)

print("Found pTableHead at {}, pTableTail at {}".format(parsed.get('ptablehead'), parsed.get('ptabletail')))

for part in parsed.get('partitions'):
    print("Partition {}, offset = {}, size = {}".format(
        part.get('name'), part.get('offset'), part.get('size')
        ))
    with open("{:02d}_{}_0x{:x}.bin".format(part.get('num'), part.get('name'), part.get('offset')), "wb") as w:
        f.seek(part.get('offset'), 0)
        w.write(f.read(part.get('size')))

f.close()
