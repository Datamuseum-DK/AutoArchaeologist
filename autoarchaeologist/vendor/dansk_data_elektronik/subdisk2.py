#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

import struct

SIGNATURE = bytes.fromhex('73 75 62 64 69 73 6b 32 20 70 72 65 73 65 6e 74')

class SubDisk2():

    def __init__(self, this):
        if not this.top in this.parents:
            return
        if this[900:900 + len(SIGNATURE)].tobytes() != SIGNATURE:
            return

        words = struct.unpack(">32H", this[0x300:0x340])
        print("?SD2", this)
        print("\t", words)
        print("\t", words[0] << 16, len(this))
        if words[0] << 16 > len(this):
            return
        offset = 8192
        for i in range(2, len(words), 2):
            if not words[i]:
                break
            print("I", i, offset, words[i] << 16)
            this.create(start=offset, stop=offset+(words[i]<<16))
            offset += words[i] << 16
