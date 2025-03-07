#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Xenix-286 partition
   --------------------

   There is no partition table, it's compiled into the kernel.

   Heuristically hunt for filesystems.
'''

ROOT_DIR_SIG = bytes().fromhex('''
	02 00 2e 00 00 00 00 00  00 00 00 00 00 00 00 00
''')

assert len(ROOT_DIR_SIG) == 16

class RC39_Partition():
    ''' The sizes are hardcoded in the device driver source code '''

    def __init__(self, this):
        if this.top not in this.parents:
            return

        rootdirs = []
        for i in range(0, len(this), 0x400):
            if this[i:i+16].tobytes() == ROOT_DIR_SIG:
                rootdirs.append(i)

        lo = 0
        parts = []
        for i in rootdirs:
            print(this, "Rootdir 0x%x" % i)
            for j in range(i, lo, -0x400):
                if this[j+1] not in (0x80, 0x81):
                    continue
                k = j - 0x800
                if max(this[k:k+12]):
                    continue
                if not max(this[k + 12:k+16]):
                    continue
                print("   Could be 0x%x" % k)
                print(this[k:k+64].hex())
                lo = k + 0x800
                parts.append(k)
                break

        print(this, parts)

        if parts:
            parts.append(len(this))
            for i in range(0, len(parts)-1):
                start=parts[i]
                stop=parts[i+1]
                print(this, "%x" % start, "%x" % stop)
                y = this.create(start=start, stop=stop)
                y.add_type("XENIX Partition")
