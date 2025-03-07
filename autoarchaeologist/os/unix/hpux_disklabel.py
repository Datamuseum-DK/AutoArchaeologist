#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

import struct

class HPUXDiskLabel():

    def __init__(self, this):
        if this.top not in this.parents:
            return

        self.this = this

        if this[:8].tobytes() != bytes.fromhex("80 00 49 53 4c 31 30 20"):
            return

        for a in range(0x800, 0xa00, 32):
            b = this[a:a+32].tobytes()
            if not b[0]:
                continue
            w = struct.unpack(">10sH5L", b[:32])
            print(b.hex())
            print("   ", w)
            name = this.type_case.decode(w[0].rstrip(b' '))
            print("   ", name)
            start = w[2] << 8
            length = w[3] << 8
            print("  ", start, length)
            y = this.create(start=start, stop=start + length)
            y.add_type("HPUX Partition")
            y.add_note(name)
            this.taken = True
