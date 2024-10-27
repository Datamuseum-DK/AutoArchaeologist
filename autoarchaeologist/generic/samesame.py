#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Artifacts where all bytes are identical
'''

class SameSame():
    ''' Tag artifacts with only a single byte value '''
    def __init__(self, this):
        i = this[0]
        for j in this:
            if i != j:
                return

        self.this = this
        kind = "0x%02x[0x%x]" % (this[0], len(this))
        this.add_type(kind)
        with self.this.add_utf8_interpretation(kind) as file:
            file.write(kind + '\n')
