
import autoarchaeologist

class R1K_Tape_blocks():

    def __init__(self, this):
        if not this.records:
            return

        try:
            head = this[:5].tobytes().decode('ASCII')
            i = int(head, 10)
        except UnicodeDecodeError:
            return
        except ValueError:
            return

        print("?R1KTB", this, this[0], this[:5])
        offset = 0
        b = bytearray()
        while offset < len(this):
            head = this[offset:offset + 5].tobytes().decode('ASCII')
            length = int(head[1:], 10)
            b += this[offset + 5: offset + length]
            offset += length
        self.this = this
        self.that = autoarchaeologist.Artifact(this, b)
        self.that.add_type("R1K_tapefile")
        this.add_interpretation(self, self.html_redirect)
        this.taken = self

    def html_redirect(self, fo, _this):
        fo.write('<H3>Rational 1000 Tape blocking</H3>\n')
        fo.write('<pre>\n')
        fo.write('This artifact strips the Rational 1000 tape blocking\n')
        fo.write('The result is here: ' + self.that.summary() + "\n")
        fo.write('</pre>\n')
