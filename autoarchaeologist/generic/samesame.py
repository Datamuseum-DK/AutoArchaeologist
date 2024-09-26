#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license text

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
        this.add_type("SameSame")
