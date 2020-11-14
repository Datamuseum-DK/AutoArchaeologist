'''
   CBM900 Harddisk partitioning
   ----------------------------
'''

import autoarchaeologist

SLICE = 0x50c000
NSLICE = 4

class CBM900_Partition():
    ''' The sizes are hardcoded in the device driver source code '''

    def __init__(self, this):
        if len(this) < NSLICE * SLICE:
            return

        this.taken = self
        for i in range(NSLICE):
            autoarchaeologist.Artifact(this, this[i * SLICE:(i+1) * SLICE])
