


from ..base import octetview as ov
from ..base import namespace

class NameSpace(namespace.NameSpace):
    ''' ... '''

    def ns_render(self):
        hdr = self.ns_priv
        return [
            hdr.type.txt,
            hdr.name.txt,
            hdr.recs.val,
            hdr.reclen.val,
            str(hdr.pad),
        ] + super().ns_render()

class Header(ov.Struct):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            type_=ov.Text(1),
            name_=ov.Text(8),
            recs_=ov.Be24,
            reclen_=ov.Octet,
            pad_=27,
            **kwargs,
        )
        self.insert()

class MemberP(ov.OctetView):
    def __init__(self, this):
        print(this, "S34Library::MemberP")

        super().__init__(this)
        self.parts = []
        adr = 0
        while adr < len(this):
            ctl = ov.Octet(self, adr).insert()
            code = ctl.val
            if code == 0:
                break
            if code & 0x80:
                y = ov.Text(code & 0x7f)(self, ctl.hi).insert()
                self.parts.append(y.txt)
                adr = y.hi
            else:
                self.parts.append(" " * code)
                adr += 1

        tfn = self.this.add_utf8_interpretation("Text Member")
        linelen = this.member_head.reclen.val
        with open(tfn.filename, "w", encoding="utf-8") as file:
            pos = 0
            for part in self.parts:
                file.write(part)
                pos += len(part)
                while pos >= linelen:
                    pos -= linelen
                    file.write("\n")
        self.add_interpretation(more=True)

class S34Library(ov.OctetView):

    def __init__(self, this):
        if this[:9] not in (
            bytes.fromhex("d6 c1 d3 c9 c7 d5 40 40 40"),
            bytes.fromhex("d6 5b c8 c1 d5 c7 40 40 40"),
            bytes.fromhex("d6 c4 d2 c5 e3 7c 40 40 40"),
            bytes.fromhex("d6 e4 e3 f0 f0 c1 c1 40 40"),
            bytes.fromhex("d6 c3 c1 e3 f0 40 40 40 40"),
        ):
            return
        print(this, "S34Library")

        super().__init__(this)

        self.namespace = namespace.NameSpace(name='', root=this, separator=".")

        y = Header(self, 0)
        while True:
            if y.recs.val == 0 or y.type.txt == " " or y.recs.val > 1000:
                break
            adr = y.hi + (y.recs.val << 7)
            print(hex(adr), y)
            if adr >= len(self.this):
                break
            that = self.this.create(
                 start = y.hi,
                 stop = adr,
            )
            that.add_note(y.name.txt)
            that.add_note("MEMBER_" + y.type.txt)
            that.member_head = y
            NameSpace(y.name.txt, self.namespace, this=that, priv=y)
            if y.type.txt == "P":
                MemberP(that)
            elif y.type.txt == "S":
                MemberP(that)

            y = Header(self, adr)

        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation()
