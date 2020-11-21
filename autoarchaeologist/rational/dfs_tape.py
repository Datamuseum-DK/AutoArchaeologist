'''
   Rational 1000 DFS tapes
   -----------------------
'''

import struct

class R1K_DFS_Tape():

    def __init__(self, this):
        if this[:13].tobytes() != b'DFS_BOOTSTRAP':
            return
        if not this.has_type("TAPE file"):
            return

        # print("?R1KDFS", this, this.has_type("TAPE file"))

        n = 0
        offset = 0
        for r in this.iterrecords():
            if len(r) == 64:
                offset += len(r)
                n = 0
                lbl = r.tobytes()
                words = list(struct.unpack(">30sHHHHHH", lbl[:42]))
                if not 0x20 < words[0][0] <= 0x7f:
                    break
                words[0] = words[0].rstrip(b'\x00').decode("ASCII")
                txt = []
                txt.append(words[0].ljust(31))
                txt.append("0x%04x" % words[1])
                txt.append("0x%04x" % words[2])
                txt.append("0x%04x" % words[3])
                txt.append("0x%04x" % words[4])
                txt.append("0x%04x" % words[5])
                txt.append("0x%04x" % words[6])
                txt.append(lbl[42:].hex())
                # print(" ".join(txt))
                if words[2] != 0x400:
                    break
                y = this.create(start=offset, stop=offset+words[1]*words[2])
                y.add_note(words[0])
                i = words[0].split(".")
                y.add_type(i[-1])
            else:
                offset += len(r)
                n += 1
