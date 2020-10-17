
class PaperTapeCheckSum():

    def __init__(self, this):
        if this.has_note("DG-PaperTapeCheckSum"):
            return

        idx = this.rfind(b'\xaa\x55\xaa\x55\xaa\x55\xaa\x55')
        if idx < 0 or len(this[idx:]) < 25:
            return
        if len(this[idx:]) > 25 and this[idx+25]:
            return

        x = this[idx:idx+25]
        if 0 in x:
            return

        txt = ""
        for i in x[8:-4]:
            txt += "%c" % (i & 0x7f)
        txt = txt.strip()

        if idx or len(this) > 25:
            this = this.slice(idx, 25)
        if not this.has_note("DG-PaperTapeCheckSum"):
            this.add_type("DG-PaperTapeCheckSum")
            this.add_note(txt)
