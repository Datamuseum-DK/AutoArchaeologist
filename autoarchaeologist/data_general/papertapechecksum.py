'''
   Data General Papertape checksum
   -------------------------------

   At the end of original (and some copies of) Data General
   papertapes, an identifier is punched in ASCII with even
   parity:

       "U*U*U*U*" product-number checksum

   We guess the last two characters is a checksum, but that
   is only a guess.  The specific checksum calculation has
   not been investigated/found.
'''

class DGC_PaperTapeCheckSum():

    def __init__(self, this):
        if this.has_note("DGC-PaperTapeCheckSum"):
            return

        start = this.tobytes().rfind(b'\xaa\x55\xaa\x55\xaa\x55\xaa\x55')
        if start < 0:
            return
        last = this[start:].tobytes().find(b'\x00')
        if last < 0:
            stop = start + len(this[start:])
        else:
            stop = start + last + 1
        if stop - start > 30:
            return

        txt = ""
        for i in this[start:stop]:
            i = i & 0x7f
            if 0x20 < i < 0x7f:
                txt += "%c" % (i & 0x7f)
            elif txt[-1] != "_":
                txt += "_"
        txt = txt.strip()

        if start or stop < len(this):
            this = this.slice(start, stop - start)
        if not this.has_note("DGC-PaperTapeCheckSum"):
            this.add_type("DGC-PaperTapeCheckSum")
            this.add_note(txt)
