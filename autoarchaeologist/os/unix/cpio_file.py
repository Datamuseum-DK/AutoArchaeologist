#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   CPIO(1) format
'''

from ...base import namespace
from ...base import octetview as ov
from . import unix_namespace as uns

class CpioOldBeEnt(ov.Struct):
    ''' ... '''

    MAGIC = 0o70707
    NAME = "CPIO.V7.BE"

    bad = False

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            h_magic_=ov.Be16,
            h_dev_=ov.Be16,
            h_ino_=ov.Be16,
            h_mode_=ov.Be16,
            h_uid_=ov.Be16,
            h_gid_=ov.Be16,
            h_nlink_=ov.Be16,
            h_majmin_=ov.Be16,
            h_mtime_=ov.Be32,
            h_namesize_=ov.Be16,
            h_filesize_=ov.Be32,
            more=True,
        )
        if self.h_magic.val != self.MAGIC:
            self.bad = True
        else:
            self.add_field("h_filename", ov.Text(self.h_namesize.val))
            if self.h_namesize.val & 1:
                self.add_field("namepad", 1)
        self.done()

class CpioFile(ov.OctetView):

    ''' A UNIX cpio(1) file '''

    FORMATS = {
        CpioOldBeEnt.MAGIC: CpioOldBeEnt,
    }

    def __init__(self, this):
        if len(this) <= 512:
            return

        magic = (this[0] << 8) | this[1]

        entcls = self.FORMATS.get(magic)
        if entcls is None:
            return

        super().__init__(this)

        ptr = 0
        entries = []
        final = False
        while ptr < len(this):
            y = entcls(self, ptr).insert()
            #print(hex(ptr), y)
            if y.bad:
                return
            ptr = y.hi
            if y.h_filesize.val > 0:
                z = ov.Opaque(self, ptr, width=y.h_filesize.val).insert()
                ptr = z.hi
                if y.h_filesize.val & 1:
                    w = ov.Opaque(self, ptr, width=1).insert()
                    ptr = w.hi
            else:
                z = None
            entries.append((y, z))
            if y.h_filename.txt == "TRAILER!!! ":
                final = True
                break

        if not final:
            return
        this.add_type(entcls.NAME)

        print(this, "TAIL", hex(len(this) - ptr))
        ov.Opaque(self, lo=ptr, hi=len(this)).insert()

        namespace = uns.NameSpace(name = "", separator = "", root = this)

        for ent, obj in entries:
            if obj is not None:
                obj = this.create(start=obj.lo, stop=obj.hi)
            uns.NameSpace(
                name = ent.h_filename.txt,
                parent = namespace,
                this = obj,
                flds = [
                    ent.h_mode.val,
                    ent.h_nlink.val,
                    ent.h_uid.val,
                    ent.h_gid.val,
                    ent.h_filesize.val,
                    ent.h_mtime.val,
                ]
            )

        this.add_interpretation(self, namespace.ns_html_plain)

        self.add_interpretation(more=True)
