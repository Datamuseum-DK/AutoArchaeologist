#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license text

'''
   IBM S/34 'O' members descripting screen forms

   I dont think this format is documented anywhere.

   The most complex part of each form description contains the
   precise data sequence sent to the display, which is documented
   in the alphabetically sorted "Encylopedia" section of this document:

      GA21-9247-6 5250 Information Display System Functions Reference Manual

   which bitsavers have here:

      http://bitsavers.org/pdf/ibm/5250_5251/

   Start from "Orders" on page 2-136 (pdf pg 188)
   
'''

from ....base import octetview as ov

class FormPointer(ov.Struct):
    ''' Points to where the form lives in the member '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            name_=ov.Text(8),
            f1_=ov.Octet,
            f2_=ov.Octet,
            start_=ov.Octet,
            f4_=ov.Octet,
            len_=ov.Octet,
            f6_=ov.Octet,
            f7_=ov.Octet,
            f8_=ov.Octet,
            **kwargs,
        )
        self.insert()

class FormHead(ov.Struct):
    ''' Form description '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            f0_=ov.Octet,
            f1_=ov.Octet,
            f2_=ov.Text(8),
            f3_=ov.Be16,
            f4_=ov.Be32,
            **kwargs,
        )

class FieldDef(ov.Struct):
    ''' Field description '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            off_=ov.Be16,
            f00_=ov.Be16,
            f01_=ov.Be16,
            **kwargs,
            more=True,
        )
        if self.f00.val == 0xffff:
            pass
        elif self.f01.val == 0xffff:
            self.add_field("f02", ov.Be16)
        elif self.f01.val & 0x8000:
            self.add_field("f02", ov.Be16)
            self.add_field("f80", 8)
        self.done()

class StartOfHeader(ov.Struct):
    ''' GA21-9247-6 pdf page 191 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            soh_=1,
            len_=ov.Octet,
            **kwargs,
            more=True,
        )
        if 0 < self.len.val < 10:
            self.add_field("extra", self.len.val)
            self.done()
        else:
            self.done()
            print(self.tree.this, "FORM: Bad SOH len", self)

class ClearUnit(ov.Struct):
    ''' GA21-9247-6 pdf page 61 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            esc_=1,
            cu_=1,
            **kwargs,
        )

class ClearFormatTable(ov.Struct):
    ''' GA21-9247-6 pdf page 61 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            esc_=1,
            cft_=1,
            **kwargs,
        )

class WriteToDisplay(ov.Struct):
    ''' GA21-9247-6 pdf page 65 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            esc_=1,
            wtd_=1,
            flags_=ov.Be16, # pdf page 91
            **kwargs,
        )

class InsertCursor(ov.Struct):
    ''' GA21-9247-6 pdf page 189 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            ic_=1,
            line_=ov.Octet,
            col_=ov.Octet,
            **kwargs,
        )

class SetBufferAddress(ov.Struct):
    ''' GA21-9247-6 pdf page 189 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            ic_=1,
            line_=ov.Octet,
            col_=ov.Octet,
            **kwargs,
        )

class StartField(ov.Struct):
    ''' GA21-9247-6 pdf page 190 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            sf_=1,
            ffw_=ov.Be16,	# pdf pg 120
            **kwargs,
            more=True,
        )
        if self.tree.this[self.hi] & 0x80:
            self.add_field("fcw", ov.Be16)  # pdf pg 117
        self.add_field("attr", ov.Octet)
        self.add_field("len", ov.Be16)
        self.done()

class Attribute(ov.Struct):
    ''' GA21-9247-6 pdf page 195 '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            type_=ov.Octet,
            **kwargs,
        )

class Form(ov.Struct):
    ''' One form in the member '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            head_=FormHead,
            **kwargs,
            more=True,
        )

        self.pane = []
        for _i in range(26):
            self.pane.append([' '] * 80)
        self.pos_x = 0
        self.pos_y = 0


        this = self.tree.this
        while True:
            if self.head.f4.val:
                return
            nf = 0
            if this[self.hi] & 0x40:
                self.add_field("formxx", 4)

            while True:
                if this[self.hi] == 0xff and this[self.hi+1] == 0xff:
                    self.add_field(None, 2)
                    continue
                y = self.add_field("fld_%d" % nf, FieldDef)
                if y.f00.val == 0:
                    break
                nf += 1
            end = y.off.val + y.lo
            if end > len(this):
                print(this, "BAD FORM END", hex(end))
                end = len(this) - 10
            while self.hi < end:
                if this[self.hi] == 0x04 and this[self.hi+1] == 0x40:
                    self.add_field(None, ClearUnit)
                    continue
                if this[self.hi] == 0x04 and this[self.hi+1] == 0x11:
                    self.add_field(None, WriteToDisplay)
                    continue
                if this[self.hi] == 0x04 and this[self.hi+1] == 0x50:
                    self.add_field(None, ClearFormatTable)
                    continue
                if this[self.hi] == 0x01:
                    y = self.add_field(None, StartOfHeader)
                    continue
                if this[self.hi] in (0x03, 0x13):
                    self.add_field(None, InsertCursor)
                    continue
                if this[self.hi] == 0x11:
                    y = self.add_field(None, SetBufferAddress)
                    self.pos_y = y.line.val
                    self.pos_x = y.col.val
                    continue
                if this[self.hi] == 0x1d:
                    y = self.add_field(None, StartField)
                    save = (self.pos_x, self.pos_y)
                    self.add_glyph('├')
                    for _i in range(y.len.val):
                        self.add_glyph('┴')
                    self.add_glyph('┤')
                    self.pos_x, self.pos_y = save
                    continue
                if this[self.hi] & 0xe0 == 0x20:
                    self.add_field(None, Attribute)
                    self.add_glyph('╳')
                    continue
                ptr = self.hi
                while ptr < end:
                    if this[ptr] in (0x01, 0x04, 0x03, 0x11, 0x13, 0x1d,):
                        break
                    if this[ptr] & 0xe0 == 0x20:
                        break
                    ptr += 1
                    if self.pos_x + (ptr - self.hi) > 79:
                        break
                if ptr > self.hi:
                    y = self.add_field(None, ov.Text(ptr - self.hi))
                    for c in y.txt:
                        self.add_glyph(c)
                    continue
                print(this, "Unknown FORM data", bytes(this[self.hi:self.hi+16]).hex())
                break

            break
        self.done()
        self.insert()

    def add_glyph(self, glyph):
        ''' Add a glyph and advance cursor '''
        while self.pos_x > 79:
            self.pos_x -= 80
            self.pos_y += 1
        if self.pos_y == 25 and self.pos_x == 0:
            pass
        elif self.pos_y > 25:
            print(
                self.tree.this,
                "FORM add_glyph outside screen",
                hex(self.hi),
                self.pos_y,
                self.pos_x,
                glyph
            )
            return
        self.pane[self.pos_y][self.pos_x] = glyph
        self.pos_x += 1
        if self.pos_x > 79:
            self.pos_x -= 80
            self.pos_y += 1

    def render_pane(self):
        ''' Render image of pane '''
        yield '┌' + '─' * 80 + '┐'
        for line in self.pane:
            yield '│' + ''.join(line) + '│'
        yield '└' + '─' * 80 + '┘'

    def render(self):
        yield from super().render()
        yield from self.render_pane()

class S34Form(ov.OctetView):
    ''' IBM S/34 'O' members describing screen forms '''

    def __init__(self, this):

        if len(this) < 16:
            return
        if this[8] or this[9]:
            return
        if this[10] == 0:
            return
        if not this.has_note("MEMBER_O"):
            return

        super().__init__(this)
        this.type_case.set_slug(0x0, '░')

        self.hdrs = {}
        adr = 0
        while adr < len(this) and this[adr] != 0xff:
            y = FormPointer(self, adr)
            # print("FP", y)
            if y.f1.val:
                return
            if y.f2.val:
                return
            if y.f8.val:
                return
            if ' ' in y.name.txt.rstrip():
                return
            adr = y.hi
            self.hdrs[y.name.txt] = y

        self.this.add_note("FORM")

        self.forms = []
        for hdr in self.hdrs.values():
            y = Form(self, hdr.start.val << 8, vertical=True)
            self.forms.append(y)

        with self.this.add_utf8_interpretation("Forms") as file:
            for hdr, form in zip(self.hdrs.values(), self.forms):
                file.write(str(hdr) + "\n")
                for i in form.render_pane():
                    file.write(i + "\n")
        self.add_interpretation(more=True)
