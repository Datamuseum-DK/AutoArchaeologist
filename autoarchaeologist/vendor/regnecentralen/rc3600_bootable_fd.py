#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC3600 Flexible disc MT Emulator
   ================================

'''

BOOTLOADER = bytes.fromhex('''
c2 ff 10 21 91 d4 00 95  00 52 00 2a 0c b5 fc 01
12 09 09 49 00 b6 00 d3  0e 09 00 4a 04 11 fc 01
00 02 00 08 00 00 01 00  03 00 40 00 ff 00 fb 00
f8 00 2a 90 fa 19 18 01  f9 29 f7 49 00 50 01 58
f3 11 f2 31 16 09 31 71  f5 39 04 f7 3f 66 31 75
ee 39 00 f7 ed 39 0d f5  05 01 eb 39 0d f5 f1 01
3f 66 00 30 01 38 10 ad  31 63 f3 8e fe 01 00 03
f1 60 71 72 b1 67 ff 01  00 03 c4 09 74 ff 77 59
07 09 c0 f2 05 09 c0 f6  00 c6 71 05 04 00 70 59
31 7b 73 19 6d 05 6d 51  6d 49 6d 41 74 31 6d 51
f1 60 6e 39 50 f2 00 f6  50 d2 00 f6 00 c3 6a 29
22 09 05 fa 67 39 65 59  63 21 1d 09 5d 29 5c 41
0d 8d 04 01 5c 31 00 96  12 09 5b 31 10 09 58 11
31 75 5a 39 00 f7 5a 39  0d dd 05 01 58 39 0d dd
e0 01 3f 66 46 31 46 29  46 21 d3 01 71 72 b1 67
ff 01 00 03 0b 59 00 fd  48 31 50 82 40 fa 0a bd
00 bd 40 82 04 d3 fb 01  01 05 00 00 bf 65 36 31
ee 09 38 31 35 51 50 d5  30 51 ba 09 c5 f2 fe 01
b7 09 c0 f6 00 c2 00 ca  ab 09 34 51 a9 09 4b aa
16 01 2e 49 1d 31 ab 39  00 f5 2c 39 00 bd 13 f4
0c 01 27 31 1b ce 24 11  12 ce 4b aa 99 09 22 55
21 11 1e 11 fb 01 04 82  3f 66 e0 01 04 82 fd 01
19 31 bf 65 4b d2 00 02  3f 66 ff 01 00 00 00 00
00 00 00 00 00 00 00 00  00 00 00 02 00 03 00 00
00 00 1a 00 81 00 ff 00  f0 ff fb 00 f8 00 00 00
10 00 00 00 bc 01 00 00  00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
''')

INTERLEAVE = [
    1,  8, 15, 22,
    3, 10, 17, 24,
    5, 12, 19, 26,
    7, 14, 21,
    2,  9, 16, 23,
    4, 11, 18, 25,
    6, 13, 20
]

assert len(INTERLEAVE) == 26
assert len(set(INTERLEAVE)) == 26

class BootableFd():
    ''' ... '''
    def __init__(self, this):
        if not this.top in this.parents:
            return
        if len(this) != 77 * 26 * 128:
            return

        if this[:len(BOOTLOADER)] != BOOTLOADER:
            return
        this.add_note("Bootable Floppy")

        self.this = this

        sects = []
        rest = 0
        done = False
        for sect in self.reader():
            sects.append(sect)
            ptr = 0
            while True:
                if rest > 0:
                    take = min(rest, 128 - ptr)
                    #print(this, "TAKE", ptr, take)
                    ptr += take
                    rest -= take
                if done and rest == 0:
                    break
                if ptr == len(sect):
                    break
                width = (sect[ptr + 1] << 8) | sect[ptr]
                if width >= 0xfff0:
                    rest = (0x10003 - width) * 2
                elif width == 0xffef:
                    rest = 8
                elif width == 0x0001:
                    done = True
                    rest = 6
                else:
                    print(this, "Unknown WIDTH", hex(width), ptr, rest, sect[ptr:ptr+8].hex())
                    return
            if done and rest == 0:
                break

        sects[-1] = sects[-1][:ptr]
        y = this.create(start=0, stop=len(BOOTLOADER))
        y.add_type("Floppy Bootloader")
        y = this.create(records = sects)


    def reader(self):
        for trk in range(1, 77):
            for sect in INTERLEAVE:
                ptr = trk * 26 * 128 + (sect - 1) * 128
                yield self.this[ptr:ptr+128]
