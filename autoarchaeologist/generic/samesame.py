
class SameSame():
    ''' Recognize artifacts with only a single byte value '''
    def __init__(self, this):
        lo_val = min(this)
        hi_val = max(this)
        if lo_val != hi_val:
            return

        self.this = this
        note = "Boring" if lo_val else "Blank"
        if not this.has_note(note):
            this.add_type(note)
            this.add_interpretation(self, self.html_as_interpretation)

    def html_as_interpretation(self, fo, _this):
        fo.write("<H3>SameSame</H3>\n")
        fo.write("<pre>\n")
        fo.write("0x%02x[0x%x]" % (self.this[0], len(self.this)))
        fo.write("</pre>\n")
