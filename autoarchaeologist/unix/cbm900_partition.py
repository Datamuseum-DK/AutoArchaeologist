'''
   CBM900 Harddisk partitioning
   ----------------------------
'''

import autoarchaeologist

class CBM900_Partition():
    ''' The sizes are hardcoded in the device driver source code '''

    def __init__(self, this):
        if this[0x50c3e4:0x50c3f0] != b'nonamenopack':
            return

        this.taken = self
        autoarchaeologist.Artifact(this, this[:0x50c000])
        autoarchaeologist.Artifact(this, this[0x50c000:0xa18000])
        autoarchaeologist.Artifact(this, this[0xa18000:0xf24000])
        autoarchaeologist.Artifact(this, this[0xf24000:])
