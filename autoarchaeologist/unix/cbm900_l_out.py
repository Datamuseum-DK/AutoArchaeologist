'''
   CBM900 l.out files
   ------------------

   Can probably be generalized for other segmented archtectures
   given suitable examples to work from.
'''

import struct

import autoarchaeologist.generic.hexdump as hexdump

SEGS = (
    "L_SHRI",
    "L_PRVI",
    "L_BSSI",
    "L_SHRD",
    "L_PRVD",
    "L_BSSD",
    "L_DEBUG",
    "L_SYM",
    "L_REL",
    "L_ABS",
    "L_REF",
)


class L_Out():

    ''' CBM900 L.out binary format '''

    def __init__(self, this):
        self.this = this
        if len(this) < 46:
            return
        self.words = struct.unpack("<HHHL9L", this[:46])
        if self.words[0] != 0o407:
            return
        this.type = "CBM900 l.out"
        this.add_note("CBM900 l.out")
        this.add_interpretation(self, self.html_as_interpretation)

    def html_as_interpretation(self, fo, _this):
        ''' split and hexdump '''
        fo.write("<H3>CBM900 l.out</H3>\n")
        fo.write("<pre>\n")
        fo.write("struct ldheder {\n")
        fo.write("    .l_magic = 0%o,\n" % self.words[0])
        fo.write("    .l_flag = 0x%x,\n" % self.words[1])
        fo.write("    .l_machine = 0x%x,\n" % self.words[2])
        fo.write("    .l_entry = 0x%x,\n" % self.words[3])
        fo.write("    .l_ssize = {\n")
        for i in range(9):
            fo.write("        [%s] = 0x%x,\n" % (SEGS[i], self.words[4+i]))
        fo.write("    },\n")
        fo.write("};\n")
        fo.write("\n")
        hexdump.hexdump_to_file(self.this[:46], fo)
        fo.write("</pre>\n")

        offset = 48
        for i, segnam in enumerate(SEGS):

            if segnam in ("L_BSSI", "L_BSSD", "L_ABS", "L_REF",):
                continue
            seglen = self.words[4 + i]
            if not seglen:
                continue

            if offset + seglen > len(self.this):
                break
            fo.write("<H4>CBM900 %s</H4>\n" % segnam)
            fo.write("<pre>\n")
            hexdump.hexdump_to_file(self.this[offset:offset+seglen], fo)
            if segnam == "L_SYM":
                for j in range(0, seglen, 22):
                    symoff = offset + j
                    words = struct.unpack("<16sHL", self.this[symoff:symoff+22])
                    n = words[0].rstrip(b'\x00').decode("ASCII")
                    fo.write("%16s %04x %08x\n" % (n, words[1], words[2]))
            offset += seglen
            fo.write("</pre>\n")
