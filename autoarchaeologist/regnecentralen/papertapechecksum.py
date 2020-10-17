
class RC_PTR_CheckSum():
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
