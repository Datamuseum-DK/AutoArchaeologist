#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   IBM S/34 libraries containing members

   I am not aware of any documentation for this.

   The only data I have to operate on are 8" floppies.
'''

from ....base import octetview as ov
from ....base import namespace

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("l", "type"),
        ("r", "recs"),
        ("r", "reclen"),
        ("l", "f00"),
        ("l", "f96"),
        ("l", "f97"),
        ("l", "f98"),
        ("l", "f99"),
        ("l", "pad"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        hdr = self.ns_priv
        if hdr is None:
            return [ [] * (len(self.TABLE) - 2) ] + super().ns_render()
        return [
            hdr.type.txt,
            hdr.recs.val,
            hdr.reclen.val,
            str(hdr.f00),
            str(hdr.f96),
            str(hdr.f97),
            str(hdr.f98),
            str(hdr.f99),
            str(hdr.pad),
        ] + super().ns_render()

class Header(ov.Struct):
    ''' Header of the member '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            type_=ov.Text(1),
            name_=ov.Text(8),
            recs_=ov.Be24,
            reclen_=ov.Octet,
            f00_=ov.Be16,
            f96_=ov.Be24,
            f97_=ov.Be32,
            f98_=ov.Be16,
            f99_=ov.Be16,
            pad_=14,
            **kwargs,
        )
        self.insert()

class MemberText(ov.OctetView):
    ''' Content of the member '''
    def __init__(self, this):
        #print(this, "S34Library::MemberP")

        super().__init__(this)
        this.taken = self
        self.parts = []
        adr = 0
        while adr < len(this):
            ctl = ov.Octet(self, adr).insert()
            code = ctl.val
            if code in (0x00, 0x80):
                break
            if code & 0x80:
                y = ov.Text(code & 0x7f)(self, ctl.hi).insert()
                self.parts.append(y.txt)
                adr = y.hi
            else:
                self.parts.append(" " * code)
                adr += 1

        with self.this.add_utf8_interpretation("Text Member") as file:
            linelen = this.member_head.reclen.val
            pos = 0
            for part in self.parts:
                file.write(part)
                pos += len(part)
                while pos >= linelen:
                    pos -= linelen
                    file.write("\n")
        self.add_interpretation(more=True)

class S34Library(ov.OctetView):
    ''' Libraries of members '''
    def __init__(self, this):
        hdr = getattr(this, "ga21_9128", None)
        if not hdr:
            return

        # NB: This is a very weak criteria
        if hdr.record_length.txt != "0008":
            return
        #print(this, "S34Library")

        super().__init__(this)

        self.namespace = NameSpace(name='', root=this, separator=".")

        y = Header(self, 0)
        while True:
            if y.recs.val == 0 or y.type.txt == " " or y.recs.val > 1000:
                break
            adr = y.hi + (y.recs.val << 7)
            #print(hex(adr), y)
            if adr >= len(self.this):
                break
            that = ov.This(self, lo=y.hi, hi=adr).insert().that
            if b'_UNREAD__UNREAD_' in that.tobytes():
                that.add_note("BADSECT")
            that.add_note("MEMBER_" + y.type.txt)
            that.member_head = y
            NameSpace(y.name.txt, self.namespace, this=that, priv=y)
            if y.type.txt == "P":
                MemberText(that)
            elif y.type.txt == "S":
                MemberText(that)

            y = Header(self, adr)

        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)
