'''
   Rational 1000 DFS tapes
   -----------------------
'''

import html
import struct

class R1K_DFS_Tape():

    def __init__(self, this):
        if this[:13].tobytes() != b'DFS_BOOTSTRAP':
            return
        if not this.has_type("TAPE file"):
            return

        print("?R1KDFS", this, this.has_type("TAPE file"))

        this.add_interpretation(self, self.render_dfs_tape)

        offset = 0
        self.files = []
        for r in this.iterrecords():
            if len(r) == 64:
                offset += len(r)
                lbl = r.tobytes()
                words = list(struct.unpack(">30sHHHHHH", lbl[:42]))
                assert 0x20 < words[0][0] < 0x7e
                words[0] = words[0].rstrip(b'\x00').decode("ASCII")
                txt = []
                # txt.append(words[0].ljust(31))
                txt.append("0x%04x" % words[1])
                txt.append("0x%04x" % words[2])
                txt.append("0x%04x" % words[3])
                txt.append("0x%04x" % words[4])
                txt.append("0x%04x" % words[5])
                txt.append("0x%04x" % words[6])
                # assert not max(lbl[42:]), lbl[42:].hex()
                txt.append(lbl[42:].hex())
                y = this.create(
                    start=offset,
                    stop=offset+((words[1]-1)<<10)+words[2]
                )
                y.set_name(words[0])
                i = words[0].split(".")
                y.add_type(i[-1])
                self.files.append((offset, " ".join(txt), y))
            else:
                offset += len(r)

    def render_dfs_tape(self, fo, _this):
        fo.write("<H3>DFS Tape</H3>\n")
        fo.write("<pre>\n")
        for offset, txt, that in self.files:
            fo.write("0x%08x " % offset + txt + " " + that.summary() + "\n")
        fo.write("</pre>\n")
