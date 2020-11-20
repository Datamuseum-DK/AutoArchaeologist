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
    "UHL\x01": True,    # Pretty sure this is a mistake
                        # on 30000544::58cd75c1
    "UVL1": True,
    "UVL2": True,
}

class Ansi_Tape_labels():
    ''' ANSI Tape Labels '''
    def __init__(self, this):
        # print("?ANSI", this)
        for tour in range(2):
            if tour:
                this.add_type("ANSI Tape Label")
            for label in this.iterrecords():
                if len(label) != 80:
                    return
                label=label.tobytes().decode("ASCII")
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
        for label in self.this.iterrecords():
            label=label.tobytes().decode("ASCII")
            fo.write(label + "\n")
        fo.write("-" * 80 + "\n")
        fo.write("</pre>\n")
