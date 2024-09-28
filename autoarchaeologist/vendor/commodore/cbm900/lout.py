#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   CBM900 l.out files
   ------------------
'''

from ....base import octetview as ov

class LdHeader(ov.Struct):
    ''' see ⟦29d670bb4⟧ '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            l_magic_=ov.Le16,
            l_flag_=ov.Le16,
            l_machine_=ov.Le16,
            l_entry_=ov.Le32,
            l_ssize_=ov.Array(9, ov.Le32, vertical=True),
            vertical=True,
            more=True,
        )
        self.done(0x30)

class LSHRI(ov.Dump):
    ''' Shared Instruction space '''

class LPRVI(ov.Dump):
    ''' Private Instruction space '''

class LSHRD(ov.Dump):
    ''' Shared Data space '''

class LPRVD(ov.Dump):
    ''' Private Data space '''

class LDEBUG(ov.Dump):
    ''' Debug tables '''

class LdSym(ov.Struct):
    ''' Symbols '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            ls_id_=ov.Text(16),
            ls_type_=ov.Le16,
            ls_vaddr_=ov.Le32,
        )

class LSYM(ov.Struct):
    ''' Relocation '''

    def __init__(self, tree, lo, width):
        super().__init__(
            tree,
            lo,
            symbols_=ov.Array(width // 22, LdSym, vertical=True),
            vertical=True,
        )

class LREL(ov.Dump):
    ''' ... '''

class CBM900LOut(ov.OctetView):

    ''' CBM900 L.out binary format '''

    def __init__(self, this):
        if len(this) < 46:
            return
        super().__init__(this)
        header = LdHeader(self, 0)
        if header.l_magic.val != 0o407 or header.l_flag.val != 0x10:
            return
        header.insert()

        self.section = {}
        ptr = header.hi
        for cls, i in zip(
            (LSHRI, LPRVI, None, LSHRD, LPRVD, None, LDEBUG, LSYM, LREL),
            header.l_ssize,
        ):
            flags = i.val & (0xff<<24)
            width = i.val - flags
            if cls is None:
                continue
            if width == 0:
                self.section[cls.__name__] = None
                continue
            if ptr + width <= len(this):
                y = cls(self, lo = ptr, width=width).insert()
                ptr = y.hi
                self.section[cls.__name__] = y
            else:
                print(this, "OVERFLOW", cls.__name__, i)
                break

        this.add_type("CBM900 l.out")
        self.add_interpretation()
