#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Ohio Scientific Inc - OS65U BASIC
   =================================

   This is a Microsoft BASIC.  It is unclear how compatible the
   BASIC was across the various OSI product lines.

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor.ohio_scientific import os65u_basic
       …
       self.add_examiner(*os65u_basic.ALL)

   Notes
   -----

   The token list has been extracted from the boot-code in the first
   six tracks.


   Test input
   ----------

   * Bits:30009355

   Documentation
   -------------

   https://osi.marks-lab.com/index.php

'''

from ...base import octetview as ov
from ...base import type_case

# This can be extracted from the image - see below.
BASIC_TOKENS = {
    0x80: 'END',
    0x81: 'FOR',
    0x82: 'NEXT',
    0x83: 'DATA',
    0x84: 'INPUT',
    0x85: 'DIM',
    0x86: 'READ',
    0x87: 'LET',
    0x88: 'GOTO',
    0x89: 'RUN',
    0x8a: 'IF',
    0x8b: 'RESTORE',
    0x8c: 'GOSUB',
    0x8d: 'RETURN',
    0x8e: 'REM',
    0x8f: 'STOP',
    0x90: 'ON',
    0x91: 'NULL',
    0x92: 'WAIT',
    0x93: 'LOAD',
    0x94: 'SAVE',
    0x95: 'DEF',
    0x96: 'POKE',
    0x97: 'PRINT',
    0x98: 'CONT',
    0x99: 'LIST',
    0x9a: 'CLEAR',
    0x9b: 'INDEX<',
    0x9c: 'OPEN',
    0x9d: 'CLOSE',
    0x9e: 'FIND',
    0x9f: 'DEV',
    0xa0: 'FLAG',
    0xa1: 'NEW',
    0xa2: 'TAB(',
    0xa3: 'TO',
    0xa4: 'FN',
    0xa5: 'SPC(',
    0xa6: 'THEN',
    0xa7: 'NOT',
    0xa8: 'STEP',
    0xa9: '+',
    0xaa: '-',
    0xab: '*',
    0xac: '/',
    0xad: '^',
    0xae: 'AND',
    0xaf: 'OR',
    0xb0: '>',
    0xb1: '=',
    0xb2: '<',
    0xb3: 'SGN',
    0xb4: 'INT',
    0xb5: 'ABS',
    0xb6: 'USR',
    0xb7: 'FRE',
    0xb8: 'POS',
    0xb9: 'SQR',
    0xba: 'RND',
    0xbb: 'LOG',
    0xbc: 'EXP',
    0xbd: 'COS',
    0xbe: 'SIN',
    0xbf: 'TAN',
    0xc0: 'ATN',
    0xc1: 'PEEK',
    0xc2: 'LEN',
    0xc3: 'STR$',
    0xc4: 'VAL',
    0xc5: 'ASC',
    0xc6: 'CHR$',
    0xc7: 'INDEX',
    0xc8: 'LEFT$',
    0xc9: 'RIGHT$',
    0xca: 'MID$',
}

class OsuBasicHead(ov.Struct):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            skip_=ov.Le16,
            length_=ov.Le16,
            f03_=ov.Octet,
        )

class OsuBasicPtr(ov.Struct):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            ptr_=ov.Le16,
        )
        if self.ptr.val:
            self.dst = self.ptr.val + 4 - 0x6000
        else:
            self.dst = 0

    def render(self):
        yield self.__class__.__name__ + "{ 0x%04x → 0x%04x }" % (self.ptr.val, self.dst)

class OsuBasicLine(ov.Struct):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            ptr_=OsuBasicPtr,
            lineno_=ov.Le16,
            more=True,
        )
        if self.ptr.dst:
            self.add_field("tokens", self.ptr.dst - self.hi)
        else:
            self.tokens = b''
        self.done()

    def basic(self):
        ''' Render as BASIC statement '''
        if self.ptr.dst:
            yield "%05d " % self.lineno.val + self.tree.type_case.decode_long(self.tokens)

class BasicTypeCase(type_case.TypeCase):
    ''' A typecase augmented with BASIC tokens '''

    def __init__(self, model):
        super().__init__(model.name + "-BASIC")
        for n, s in enumerate(model.slugs):
            if s.flags != model.INVALID:
                self.set_slug(n, s.short, s.long, s.flags)
        for n, t in BASIC_TOKENS.items():
            self.set_slug(n, ' ', t)

class Osu65uBasic(ov.OctetView):
    ''' A OSU65U file containing a BASIC program '''

    def __init__(self, this):
        note = this.get_note("OS65UFile")
        if not note:
            return
        dirent = note[0]["dirent"]
        if dirent.filetype != 1:
            return

        super().__init__(this)
        this.add_note("OSU65U-BASIC")
        self.type_case = BasicTypeCase(this.type_case)

        hdr = OsuBasicHead(self, 0).insert()

        if hdr.skip.val:
            this.add_note("Embedded-Machine-Code", args="0x%x" % hdr.skip.val)

        p = hdr.hi + hdr.skip.val
        y = None
        while p + 5 <= hdr.hi + hdr.length.val:
            y = OsuBasicLine(self, p).insert()
            p = y.hi

        y = ov.Le16(self, y.hi).insert()
        pad = ov.Opaque(self, lo=y.hi, hi=len(this)).insert()
        pad.rendered = "[Padding]"

        with this.add_utf8_interpretation("BASIC") as file:
            if hdr.skip.val:
                file.write("NB: Preceeded by 0x%x bytes - probably machine code\n\n" % hdr.skip.val)
            for i in self:
                if isinstance(i, OsuBasicLine):
                    for j in i.basic():
                        file.write(j + "\n")

        self.add_interpretation(more=True, elide=0)

ALL = (
    Osu65uBasic,
)
