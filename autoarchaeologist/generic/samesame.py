'''
   Artifacts with only one byte value
'''

class SameSame():
    ''' Recognize artifacts with only a single byte value '''
    def __init__(self, this):
        i = this[0]
        for j in this:
            if i != j:
                return

        self.this = this
        note = "Boring" if this[0] else "Blank"
        if not this.has_note(note):
            this.add_type(note)
            this.add_interpretation(self, self.html_as_interpretation)

    def html_as_interpretation(self, fo, _this):
        ''' Pseudo assembler syntax '''
        fo.write("<H3>SameSame</H3>\n")
        fo.write("<pre>\n")
        fo.write("0x%02x[0x%x]" % (self.this[0], len(self.this)))
        fo.write("</pre>\n")
