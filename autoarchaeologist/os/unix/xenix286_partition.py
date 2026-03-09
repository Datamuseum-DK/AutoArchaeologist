#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Xenix-286 partition
   ====================

   There is no partition table, it's compiled into the kernel.

   Heuristically hunt for filesystems.
'''

from ...base import octetview as ov

from . import xenix286_fs

ROOT_DIR_SIG = bytes().fromhex('02 00 2e 00 00 00 00 00 00 00 00 00 00 00 00 00')

assert len(ROOT_DIR_SIG) == 16

class RC39_Partition(ov.OctetView):
    ''' The sizes are hardcoded in the device driver source code '''

    def __init__(self, this):
        if this.top not in this.parents:
            return

        super().__init__(this)

        rootdirs = []
        for i in range(0, len(this), 0x400):
            if this[i:i+16].tobytes() == ROOT_DIR_SIG:
                print(this, hex(i), "ROOTDIR")
                rootdirs.append(i)

        lo = 0
        parts = []
        for i in rootdirs:
            print(this, "Rootdir 0x%x" % i)
            for k in range(i - 0x400, lo - 0x400, -0x400):
                if max(this[k:k+12]):
                    continue
                sb = xenix286_fs.FilSys(self, k)
                sb.vertical = False
                print(this, hex(k), "SB", sb.credible, sb)
                if not sb.credible:
                    continue
                if (sb.fs_maxblock.val << 10) + k < i:
                    print("   Not big enough 0x%x" % k)
                    continue
                print("   Could be 0x%x" % k)
                w = (sb.fs_maxblock.val + 1) << 10
                if k + w > len(this):
                    print("   but that would be too long 0x%x (>0x%x)" % (k + w, len(this)))
                    continue
                y = this.create(start=k, stop=k+w)
                y.add_type("XENIX Partition")
                lo = k+w
                break

        if 0 and parts:
            parts.append(len(this))
            print(this, "XENIX PARTS", parts)
            for i in range(0, len(parts)-1):
                start=parts[i]
                stop=parts[i+1]
                print(this, "%x" % start, "%x" % stop)
                y = this.create(start=start, stop=stop)
                y.add_type("XENIX Partition")
            this.add_interpretation(self, this.html_interpretation_children)
