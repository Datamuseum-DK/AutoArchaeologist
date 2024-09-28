#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   CBM900 Harddisk partitioning
   ----------------------------
'''

class CBM900Partition():
    '''
       The partition size is hardcoded in the disk device driver.
       (See: ⟦d8c2abf42⟧ and ⟦ddd97c367⟧)
       We only have/handle 20MB disk images.
    '''

    NSLICE = 4
    SLICE = 0x50c000

    def __init__(self, this):
        if this.top not in this.parents:
            return

        if len(this) < self.NSLICE * self.SLICE:
            return

        this.taken = self
        for i in range(self.NSLICE):
            that = this.create(start=i * self.SLICE, stop=(i+1) * self.SLICE)
            that.add_type("CBM900_Partition")

        this.add_interpretation(self, this.html_interpretation_children)
