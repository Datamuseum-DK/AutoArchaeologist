'''
   CBM900 Harddisk partitioning
   ----------------------------
'''

SLICE = 0x50c000
NSLICE = 4

class CBM900_Partition():
    ''' The sizes are hardcoded in the device driver source code '''

    def __init__(self, this):
        if len(this) < NSLICE * SLICE:
            return

        this.taken = self
        for i in range(NSLICE):
            this.create(start=i * SLICE, stop=(i+1) * SLICE)

        this.add_interpretation(self, this.html_interpretation_children)
