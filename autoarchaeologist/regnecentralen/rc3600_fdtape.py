'''
   RC3600 Flexible disc MT Emulator
   --------------------------------

   See: RCSL 43-GL-7420

   Some disks use sector interleave = 7

'''

import struct

import autoarchaeologist

SIGNATURE_RAW = bytes.fromhex('''
    54 49 4d 45 20 4f 55 54 20 44 49 53 43 00
    42 0e 0c 02
    48 41 52 44 20 45 52 52 4f 52 20 4f 4e 20 44 49 53 43 2c 53 54 41
    54 45 3a 20 00
''')

SIGNATURE_INTERLEAVE = bytes.fromhex('''
    54 49 4d 45 20 4f 55 54 20 44 49 53 43 00
    42 0b 0c 02
    48 41 52 44 20 45 52 52 4f 52 20 4f 4e 20 44 49 53 43 2c 53 54 41
    54 45 3a 20 00
''')

class RC3600_FD_Tape():
    ''' RCSL 43-GL-7420 '''
    def __init__(self, this):
        if not this.top in this.parents:
            return
        if this.has_type("RC3600_FD_Tape"):
            return
        if len(this) != 77 * 26 * 128:
            return

        if this.tobytes().find(SIGNATURE_RAW) > 0:
            self.interleave = False
            self.this = this
        elif this.tobytes().find(SIGNATURE_INTERLEAVE) > 0:
            self.interleave = True
            self.this = this
        else:
            return

        self.index = []
        words = struct.unpack(">64H", this[0xb80:0xc00])
        for tour in range(2):
            if tour:
                this.add_interpretation(self, self.html_as_virtual_tape)
                this.add_type("RC3600_FD_Tape")
                this.taken = self
            last_offset = 26 << 7
            for word_idx, i in enumerate(words):
                offset = i << 7
                if not offset or offset > len(this):
                    return

                if words[word_idx + 1] & 0x8000:
                    break

                if offset < last_offset:
                    return
                last_offset = offset

                if not tour:
                    continue
                label = autoarchaeologist.Artifact(this, self[i])
                label.add_type("Namelabel")
                name = None
                b = label.tobytes().rstrip(b'\x00')
                if b:
                    try:
                        name = b.decode('ASCII')
                    except UnicodeDecodeError:
                        name = None
                    if name:
                        label.add_note(name)
                body = bytes()
                for j in range(i + 1, words[word_idx + 1]):
                    body = body + self[j]
                body = autoarchaeologist.Artifact(this, body)
                body.add_type("VirtualTapeFile")
                if name:
                    body.add_note(name)
                self.index.append((name, i, label, body))

    def __getitem__(self, n):
        if not self.interleave:
            return self.this[n << 7:(n + 1) << 7]
        cyl = n // 26
        sect = n % 26
        isect = (sect * 7) % 26
        phys = cyl * 26 + isect
        b = self.this[phys << 7:(phys + 1) << 7]
        return b

    def html_as_virtual_tape(self, fo, _this):
        ''' Render as table '''
        fo.write("<H3>Virtual Tape</H3>\n")
        fo.write('<table style="font-size: 80%;">\n')
        for name, secno, head, body in self.index:
            fo.write("<tr>\n")


            fo.write("<td>\n")
            fo.write("0x%04x" % secno)
            fo.write("</td>\n")

            fo.write('<td style="padding-left: 10px;">\n')
            if name:
                fo.write(name)
            fo.write("</td>\n")

            fo.write('<td style="padding-left: 10px;">\n')
            fo.write(self.this.top.html_link_to(head))
            fo.write("</td>\n")

            fo.write('<td style="padding-left: 10px;">\n')
            fo.write(body.summary())
            fo.write("</td>\n")
            fo.write("</tr>\n")
        fo.write("</table>\n")
