'''
   ANSI tape labels
   ----------------
'''

def vol1(this, label):
    ''' Add a note with the volume name '''
    this.add_note("Volume=" + label[4:10].strip())

def hdr1(this, label):
    ''' Add a note with the file name '''
    this.add_note("File=" + label[4:21].strip())


ANSI_HEADERS = {
    "VOL1": vol1,
    "HDR1": hdr1,
    "HDR2": True,
    "HDR3": True,
    "EOF1": True,
    "EOF2": True,
    "EOF3": True,
    "UVL1": True,
    "UVL2": True,
}

class Ansi_Tape_labels():
    ''' ANSI Tape Labels '''
    def __init__(self, this):
        if not this.records:
            return
        for i in this.records:
            if i != 80:
                return
        print("?ANSI", this)
        for tour in range(2):
            if tour:
                this.add_type("ANSI Tape Label")
            offset = 0
            for length in this.records:
                label = this[offset:offset+length].decode("ASCII")
                offset += length
                t = ANSI_HEADERS.get(label[:4])
                if not t:
                    print("ANSITAPELABEL", this, "Unknown label", label[:4])
                    return
                if tour and t is not True:
                    t(this, label)
        self.this = this
        this.add_interpretation(self, self.html_list)

    def html_list(self, fo, _this):
        ''' Print with handy ruler '''
        fo.write("<H3>ANSI tape labels</H3>\n")
        fo.write("<pre>\n")
        fo.write("".join(["%01d" % (x // 10) for x in range(1,81)]) + "\n")
        fo.write("".join(["%01d" % (x % 10) for x in range(1,81)]) + "\n")
        fo.write("-" * 80 + "\n")
        offset = 0
        for length in self.this.records:
            label = self.this[offset:offset+length].decode("ASCII")
            fo.write(label + "\n")
            offset += length
        fo.write("-" * 80 + "\n")
        fo.write("</pre>\n")
