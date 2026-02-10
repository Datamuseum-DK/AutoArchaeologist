#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   HP LIF filesystems
   ~~~~~~~~~~~~~~~~~~

   Sources:
      https://www.hp9845.net/9845/projects/hpdir/
      https://bitsavers.org/test_equipment/hp/64000/software/64941-90906_Jan-1984.pdf
'''

from ...base import octetview as ov
from ...base import namespace

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = [
        ("r", "Type"),
        ("r", "Start"),
        ("r", "Length"),
        ("r", "Time"),
        ("r", "Vol"),
        ("r", "GP"),
        ("l", "Name"),
        ("l", "Artifact"),
    ]


def is_valid_lif_name(t):
    ''' Is t a valid LIF VOLUME or FILE name ? '''

    for n, i in enumerate(t.rstrip()):
        if 'A' <= i <= 'Z':
            continue
        if 'a' <= i <= 'z':
            continue
        if '0' <= i <= '9':
            continue
        if i in "_":
            continue
        if n and i == " ":
            continue
        return False
    return True

class DateTime(ov.Struct):
    ''' LIF timestamp '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            y_=ov.Octet,
            m_=ov.Octet,
            d_=ov.Octet,
            H_=ov.Octet,
            M_=ov.Octet,
            S_=ov.Octet,
        )
        self.year = (self.y.val >> 4) * 10 + (self.y.val & 0xf)

        # Y2K mitigation according to https://www.hp9845.net/9845/projects/hpdir/
        if self.year >= 70:
            self.year += 1900
        else:
            self.year += 2000

        self.month = (self.m.val >> 4) * 10 + (self.m.val & 0xf)
        self.day = (self.d.val >> 4) * 10 + (self.d.val & 0xf)
        self.hour = (self.H.val >> 4) * 10 + (self.H.val & 0xf)
        self.minute = (self.M.val >> 4) * 10 + (self.M.val & 0xf)
        self.second = (self.S.val >> 4) * 10 + (self.S.val & 0xf)

    def render(self):
        ''' ... ''' 

        yield "%04d-%02d-%02d-%02d:%02d:%02d" % (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
        )

class VolumeLabel(ov.Struct):

    ''' Volume Label in first sector of filesystem '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            magic_=ov.Be16,
            name_=ov.Text(6),
            dirstart_=ov.Be32,
            lifid_=ov.Be16,
            unused1_=ov.Be16,
            dirlen_=ov.Be32,
            lifver_=ov.Be16,
            unused2_=ov.Be16,
            more=True,
            vertical = True,
        )

        if self.lifver.val > 0:
            self.add_field("tracks", ov.Be32)
            self.add_field("heads", ov.Be32)
            self.add_field("sectors", ov.Be32)
            self.add_field("voltime", DateTime)

        self.done()

    def sane(self):
        ''' Does this look OK ? '''

        if self.magic.val != 0x8000:
            return False
        if self.unused1.val != 0x0000:
            return False
        if self.unused2.val != 0x0000:
            return False
        if not is_valid_lif_name(self.name.txt):
            return False

        # We do not check zero padding because extensions
        # unknown to us may use that space.

        return True

class Directory(ov.Struct):
    ''' Directory entry '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(10),
            type_=ov.Be16,
            start_=ov.Be32,
            length_=ov.Be32,
            time_=DateTime,
            vol_=ov.Be16,
            gp_=ov.Be32,
        )
        self.val = (self.sane() and self.type.val) or self.type.val == 0xffff

    def sane(self):
        ''' Does this look OK ? '''

        if self.start.val + self.length.val == 0:
            return False
        if (self.start.val + self.length.val) << 8 > len(self.tree.this):
            return False
        if not is_valid_lif_name(self.name.txt):
            return False
        return True


class LifFileSystem(ov.OctetView):

    ''' LIF Filesystem '''

    def __init__(self, this):
        if this.top not in this.parents and not this.has_note("LIF"):
            return
        if this[0] != 0x80:
            return
        if this[1] != 0x00:
            return
        super().__init__(this)

        sb = VolumeLabel(self, 0).insert()
        if not sb.sane():
            #sb.vertical=False
            #print(this, sb)
            return

        this.add_note("LIF")

        directory = ov.Array(
            sb.dirlen.val * 8,
            Directory,
            vertical=True,
            elide=(False,),
        )(self, sb.dirstart.val << 8).insert()

        pns = NameSpace(name="", root=this, separator="")

        for de in directory:
            if de.val:
                if de.type.val in (0x0000,):
                    # Purged file, ignore
                    continue
                if not de.sane():
                    break
                if de.type.val in (0xffff,):
                    break
                lo = de.start.val << 8
                if de.gp.val:
                    hi = lo + de.gp.val
                else:
                    hi = lo + (de.length.val << 8)
                if lo < hi <= len(this):
                    that = ov.This(self, lo=lo, hi=hi).insert().that
                else:
                    that = None
                NameSpace(
                    name=de.name.txt.rstrip(),
                    parent=pns,
                    this=that,
                    flds=[
                        "0x%04x" % de.type.val,
                        de.start.val,
                        de.length.val,
                        "".join(de.time.render()),
                        "0x%04x" % de.vol.val,
                        "0x%08x" % de.gp.val,
                    ]
                )

        this.add_interpretation(self, pns.ns_html_plain)
        self.add_interpretation(title="LIF HexDump", more=True)

class LifHardDisk(ov.OctetView):
    def __init__(self, this):
        if this.top not in this.parents:
            return
        l = []
        for ptr in range(0, len(this), 0x100):
            if this[ptr+0x00] != 0x80:
                continue
            if this[ptr+0x01] != 0x00:
                continue
            if this[ptr+0x0e] != 0x00:
                continue
            if this[ptr+0x0f] != 0x00:
                continue
            if not 0x40 < this[ptr+2] <= 0x5d:
                continue
            l.append(ptr)
        if len(l) == 1 and l[0] == 0:
            return
        super().__init__(this)
        prev = 0
        for ptr in l:
            if ptr > prev:
                this.create(start=prev, stop=ptr)
            sb = VolumeLabel(self, ptr)
            ln = sb.sectors.val << 8
            prev = ptr + ln
            that = this.create(start=ptr, stop=prev)
            that.add_note("LIF")
        if prev < len(this):
            this.create(start=prev, stop=len(this))
        if this.children:
            this.add_interpretation(self, this.html_interpretation_children)

ALL = [
	LifHardDisk,
	LifFileSystem,
]
