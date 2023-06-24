

'''
   CR80 floppies have inverted bits
'''

class CR80_Invert():

    def __init__(self, this):
        if not this.top in this.parents:
            return
        if len(this) <= 77 * 26 * 128:
            return

        i = []
        for j in this:
            i.append(j ^ 0xff)
        that = this.create(bits=bytearray(i))
        that.add_type("inv")
