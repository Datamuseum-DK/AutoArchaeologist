
from ...generic import hexdump


class R1K_Ucode_File():

    def __init__(self, this):
        good = False
        for i in this.iter_types():
            if i[-6:] == "_UCODE":
                good = True
        if not good:
            return
        this.add_type("UCODE")
        this.add_interpretation(self, self.render_hexdump)


    def render_hexdump(self, fo, this):
        fo.write("<H4>HexDump</H4>\n")
        fo.write("<pre>\n")
        hexdump.hexdump_to_file(
            this.tobytes(),
            fo,
            width=32
        )
        fo.write("</pre>\n")
