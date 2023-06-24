

'''
   CR80 floppies have inverted bits
'''

class CR80_Interleave():

    def __init__(self, this):
        if not this.has_type("inv"):
            return

        img = bytearray(len(this))

        ileave = [
                  0,  2,  4,  6,  8, 10, 12, 14, 16, 18, 20, 22, 24,
                  1,  3,  5,  7,  9, 11, 13, 15, 17, 19, 21, 23, 25,
        ]
        for cyl in range(77):
            for sect in range(26):
                pcyl = cyl
                psect = ileave[(cyl * 0 + sect + 26) % 26]
                padr = pcyl * 26 * 128 + psect * 128
                octets = this[padr:padr+0x80]
                lba = cyl * 26 * 128 + sect * 128
                for n, i in enumerate(octets):
                    img[lba+n] = i
        that = this.create(bits=img)
        that.add_type("ileave2")
