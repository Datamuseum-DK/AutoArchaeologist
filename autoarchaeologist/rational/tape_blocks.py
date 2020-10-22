
import autoarchaeologist

class R1K_Tape_blocks():

    def __init__(self, this):
        if not this.records:
            return

        try:
            head = this[:5].decode('ASCII')
            i = int(head, 10)
        except UnicodeDecodeError:
            return
        except ValueError:
            return

        print("?R1KTB", this, this[0], this[:5])
        offset = 0
        b = bytearray()
        while offset < len(this):
            head = this[offset:offset + 5].decode('ASCII')
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

def hunt_up(some, want_type):
    for i in some.parents:
        if i.has_type(want_type):
             yield i
             return
        yield from hunt_up(i, want_type)

def hunt_down(some, want_type):
    for i in some.children:
        if i.has_type(want_type):
             yield i
        yield from hunt_down(i, want_type)

def find_partner(this):
    ''' Find our peer tape file '''
    tape = list(hunt_up(this, "TAP tape"))
    print("TAPE", tape)
    assert len(tape) == 1
    peers = list(hunt_down(tape[0], "R1K_tapefile"))
    peers.remove(this)
    assert len(peers) == 1
    print("PEER", peers)
    return peers[0]

class R1K_Tape_hack():

    def __init__(self, this):
        if not this.has_type("R1K_tapefile"):
            return
        print("?R1KTH", this)
        try:
            b = this.split(b'\n', 1)[0].decode("ASCII").split()
        except UnicodeDecodeError:
            return
        if len(b) != 3 or b[0] != "***" or b[2] != "***":
            return

        # XXX: try except that b[1] is a number

        peer = find_partner(this)

        # Find partnerfile

        for stanza in this.decode("ASCII").split("\n!"):
            lines = stanza.split("\n")
            if len(lines) < 2:
                continue
            if not lines[1]:
                continue
            if lines[1][0] not in "EFVQ":
                continue
            i = lines[1][1:].split("|")
            if len(i) != 8:
                continue
            print('-' * 72)
            print(lines[0])
            print(lines[1])
            print("\t", len(i), i)
            if i[0]:
                offset = int(i[0], 10)
            else:
                offset = 0
            if not i[1]:
                continue
            length = -int(i[1], 10)
            a = peer.slice(offset, length)
            try:
                a.set_name(lines[0])
            except autoarchaeologist.core_classes.DuplicateName:
                a.add_note(lines[0])
            print("0x%06x" % offset, "0x%06x" % length, a.summary())
        peer.puzzle()
           
