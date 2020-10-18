'''
   Regnecentralen Papertape checksum
   -------------------------------

   At the end of original (and some copies of) Regnecentralen
   papertapes, an identifier is punched in ASCII with even
   parity:

       "U*U*U*U*" checksum

   We guess the last two characters is a checksum, but that
   is only a guess.  The specific checksum calculation has
   not been investigated/found.

   This scheme seems inherited from Data General, but without
   punching the product number.
'''


class RC_PaperTapeCheckSum():
    ''' Recognize artifacts with a single byte value '''

    def __init__(self, this):
        if this.has_note("RC-PaperTapeCheckSum"):
            return

        idx = this.rfind(b'\xaa\x55\xaa\x55\xaa\x55\xaa\x55')
        if idx < 0 or len(this[idx:]) < 12:
            return
        if len(this[idx:]) > 12 and this[idx+12]:
            return

        if idx or len(this) > 12:
            this = this.slice(idx, 12)
        if not this.has_note("RC-PaperTapeCheckSum"):
            this.add_type("RC-PaperTapeCheckSum")
