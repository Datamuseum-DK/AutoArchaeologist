#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Norsk Data Filesystem - "NORD"
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   NB: Preliminary

   Based on ND-60122-02-EN.pdf: NORD file System - System Documentation

   NB: The code assumes/expects a block-size of 2K

   NB: The sameple image this is based on, sometimes have the top bit
       set in ASCII bytes in files.
  
'''

from ...base import octetview as ov
from ...base import namespace as ns

class NameSpace(ns.NameSpace):
    ''' ... '''

class Pointer(ov.Be32):
    def __init__(self, tree, lo):
        super().__init__(tree, lo)
        self.s = (self.val >> 31) & 1
        self.i = (self.val >> 30) & 1
        self.val &= 0x3fffffff
        self.dst = self.val << 11

    def render(self):
        yield "<Ptr %d %d 0x%x>" % (self.s, self.i, self.val)

class DirEnt(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(16),
            objptr_=Pointer,
            userptr_=Pointer,
            bitptr_=Pointer,
            free_=ov.Be32,
            vertical=True,
        )

class FileIndexBlock(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            index_=ov.Array(8, Pointer, vertical=True),
            vertical=True,
        )

class UserFileIndexBlock(FileIndexBlock):
    ''' ... '''

class ObjectFileIndexBlock(FileIndexBlock):
    ''' ... '''
class ObjectFileSubIndexBlock(FileIndexBlock):
    ''' ... '''

class User(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w0_=ov.Be16,
            name_=ov.Text(16),
            created_date_=ov.Be32,
            created_time_=ov.Be32,
            pages_reserved_=ov.Be32,
            pages_used_=ov.Be32,
            user_index_=ov.Be16,
            mail_flag_=ov.Be16,
            user_default_file_access_=ov.Be16,
            unused_=4 * 2,
            friend_table_=ov.Array(8, ov.Be16),
        )

class Object(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w0_=ov.Be16,
            name_=ov.Text(16),
            type_=ov.Text(4),
            next_=ov.Be16,
            prev_=ov.Be16,
            access_=ov.Be16,
            ftype_=ov.Be16,
            devno_=ov.Be16,
            w20_=ov.Be16,
            w21_=ov.Be16,
            w22_=ov.Be16,
            w23_=ov.Be16,
            w24_=ov.Be32,
            w26_=ov.Be32,
            w30_=ov.Be32,
            max_pages_=ov.Be32,
            max_bytes_=ov.Be32,
            pointer_=Pointer,
        )

class NordFs(ov.OctetView):

    def __init__(self, this):
        if this.top not in this.parents:
            return
        super().__init__(this)

        ns = NameSpace(name='', root=this)

        dir0 = DirEnt(self, 0x7e0).insert()
        ufib = UserFileIndexBlock(self, dir0.userptr.dst).insert()
        for i in ufib.index:
            if i.dst == 0:
                break
            ov.Array(2048//64, User)(self, i.dst, vertical=True).insert()

        assert dir0.objptr.s
        ofsib = ObjectFileSubIndexBlock(self, dir0.objptr.dst).insert()
        objents = []
        for i in ofsib.index:
            if not i.dst:
                continue
            ofib = ObjectFileIndexBlock(self, i.dst).insert()
            for j in ofib.index:
                if not j.dst:
                    continue
                y = ov.Array(2048//64, Object)(self, j.dst, vertical=True).insert()
                for k in y:
                    if k.w0.val:
                        objents.append(k)

        for oe in objents:
            print(oe)
            frags = []
            if not oe.pointer.dst:
                continue
            for adr in self.iter_pages(oe.pointer):
                delta = min(1<<11, oe.max_bytes.val - (len(frags)<<11))
                if delta <= 0:
                    break
                frags.append(this[adr:adr+delta])
                print("  ", hex(adr))
            if frags:
                that = this.create(records=frags)
            else:
                that = None
            NameSpace(
                parent=ns,
                name=oe.name.txt.rstrip() + "." + oe.type.txt.rstrip(),
                this = that,
            )

        this.add_interpretation(self, ns.ns_html_plain)
        self.add_interpretation(title="HexDump", elide=0x100)

    def iter_pages(self, pointer):
        assert pointer.dst
        if pointer.i or pointer.s:
            y = FileIndexBlock(self, pointer.dst).insert()
            for i in y.index:
                if i.dst:
                    yield from self.iter_pages(i)
        elif pointer.dst:
            yield pointer.dst
