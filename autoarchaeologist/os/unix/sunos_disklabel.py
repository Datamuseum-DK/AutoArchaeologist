#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

import struct

class SunOsDiskLabel():

    def __init__(self, this):
        if this.top not in this.parents:
            return

        self.this = this

        self.sl_magic, self.sl_cksum = struct.unpack(">2H", this[0x1fc:0x200])
        if self.sl_magic != 55998:
            return

        w = struct.unpack(">10H", this[0x1a4:0x1b8])
        print(this, w)
        self.sl_rpm = w[0]
        self.sl_pcyl = w[1]
        self.sl_sparecyl = w[2]
        self.sl_interleave = w[4]
        self.sl_ncyl = w[5]
        self.sl_acyl = w[6]
        self.sl_ntracks = w[8]
        self.sl_nsectors = w[9]

        csize = self.sl_ntracks * self.sl_nsectors
        for i in range(8):
            if i == 2:
                continue
            w = struct.unpack(">LL", this[0x1bc + 8 * i:0x1bc + 8 * (i+1)])
            if not max(w):
                continue
            if not w[1]:
                continue
            start = (w[0] * csize) << 9
            stop = start + (w[1] << 9)
            print(this, w, "0x%x" % start, "0x%x" % stop)
            y = this.create(start=start, stop=stop)
            y.add_type("SunOS Partition")
            this.taken = self
