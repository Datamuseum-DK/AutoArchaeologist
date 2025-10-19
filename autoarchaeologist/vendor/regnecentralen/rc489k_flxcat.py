#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC4000/RC8000/RC9000 "flxcat"
   -----------------------------

'''

import html

from ...base import octetview as ov
from ...base import namespace
from .rc489k_utils import DWord, ShortClock

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("l", "state"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        ''' ... '''
        return [
            self.ns_priv.state
        ] + super().ns_render()

#################################################
#
# A file can be a subdirectory if it has key=10

class FlxHdr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w000_=DWord,
            magic_=ov.Text(6),
            w011_=ov.Text(12),
            #w012_=ov.Be24,
            #w013_=ov.Be24,
            nent_=ov.Be24,
            nrec_=ov.Be24,
            tstamp_=ShortClock,
            w024_=ov.Be24,
            w026_=ov.Be24,
            w028_=ov.Be24,
            flxset_=ov.Text(6),
            flxno_=ov.Be24,
            firstvol_=ov.Text(6),
            nextvol_=ov.Text(6),
            # vertical=True,
        )
        self.nextvid = self.nextvol.txt.strip().lower
        self.next = None

class FlxDirSec(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w00_=DWord,
            w01_=FlxDirEnt,
            w02_=FlxDirEnt,
            vertical=True,
        )

class FlxDirEnt(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(18),
            w02_=ov.Be24,
            w03_=ov.Be24,
            range_=Range,
            w6_=ov.Be24,
            w07_=ov.Text(12),
            w10_=ShortClock,
            w11_=ov.Be24,
            w12_=ov.Be24,
            w13_=ov.Be24,
            w14_=ov.Be24,
        )

    def top_list(self):
        if self.substantial():
            yield str(self)

    def substantial(self):
        x = self.range
        if x.start is None:
            return False
        if x.start.val == 0 and x.end.val == 0:
            return False
        if x.start.val > 0 and x.end.val > 0 and x.start.val > x.end.val:
            return False
        return True

class Range(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            more=True,
        )
        if 0x00 < tree.this[lo] < 0xff:
            self.add_field("ref", ov.Text(6))
            self.start = None
            self.end = None
        else:
            self.add_field("start", ov.Bs24)
            self.add_field("end", ov.Bs24)
            self.ref = None
        self.done()

    def render(self):
        if self.ref:
            yield "@" + self.ref.txt
        else:
            yield "[%#06x…%#06x]" % (self.start.val, self.end.val)

class FlxContrib():
    def __init__(self, vol, cat, contrib):
        self.vol = vol
        self.cat = cat
        self.contrib = contrib
        self.range = contrib.range
        self.firstvol = cat.hdr.firstvol.txt.strip()
        self.nextvol = cat.hdr.nextvol.txt.strip()
        self.thisvol = vol.lower().strip()

    def __lt__(self, other):
        if self.range.start.val > 0:
            return True
        if self.thisvol == self.nextvol:
            return False
        return self.thisvol < other.thisvol

    def topint(self, file):
        file.write(
            html.escape(
                "    " + " ".join(
                    (
                    self.thisvol + ":",
                    str(self.range),
                    "[" + self.firstvol + "…" + self.nextvol + "]"
                    )
                ) + "\n"
            )
        )


class FlxFile():
    def __init__(self, sect, fname):
        self.sect = sect
        self.fname = fname
        self.state = "incomplete"
        self.contrib = []
        self.that = None
        self.ns = NameSpace(
            name = sect.sectid + "." + self.fname,
            parent = sect.grp.ns,
            priv = self
        )

    def add_contrib(self, volid, cat, contrib):
        rg = contrib.range
        if rg.start is None:
            return
        if rg.start.val == 0 and rg.end.val == 0:
            return
        if rg.end.val > 0 and rg.start.val > rg.end.val:
            self.state = "cancelled"
            return
        self.contrib.append(FlxContrib(volid, cat, contrib))
        if rg.start.val > 0 and rg.end.val > rg.start.val:
            self.instantiate(self.contrib[-1:])
            return
        if self.state != "incomplete":
            return

        self.contrib.sort()
        l = []
        cur = self.contrib[0]
        if cur.range.start.val < 0:
            return
        l.append(cur)
        for c in self.contrib[1:]:
            if cur.nextvol == c.thisvol:
                cur = c
                l.append(cur)
                if cur.nextvol == cur.thisvol:
                    cur = None
                    break
        if not cur:
            self.instantiate(l)

    def instantiate(self, parts):
        l = []
        for part in parts:
            b = part.range.start.val
            if b < 0:
                b = -b
            e = part.range.end.val
            if e < 0:
                e = -e
            for i in range(b, e + 1):
                l.append(part.cat.get_block(i))
        self.state = "complete"
        self.that = parts[0].cat.this.create(records = l)
        self.that.add_note("flxfile")
        self.that.add_name(self.fname)
        self.ns.ns_set_this(self.that)

    def topint(self, file):
        file.write(html.escape("  »" + self.fname + "«\n"))
        if not self.contrib:
            return
        for contrib in sorted(self.contrib):
            contrib.topint(file)

class FlxSect():
    def __init__(self, grp, sectid):
        self.grp = grp
        self.sectid = sectid
        self.cats = set()
        self.files = {}

    def add_cat(self, cat, volid):
        self.cats.add((volid, cat))
        for ent in cat.entries:
            ff = self.files.get(ent.name.txt)
            if ff is None:
                ff = FlxFile(self, ent.name.txt)
                self.files[ent.name.txt] = ff
            ff.add_contrib(volid, cat, ent)

    def topint(self, file):
        s = set(f.state for f in self.files.values())
        if "incomplete" not in s:
            return
        file.write("»" + html.escape(self.sectid) + "« incomplete files:\n")
        for _name, ff in sorted(self.files.items()):
            if ff.state == "incomplete":
                ff.topint(file)

class FlxGrp():
    def __init__(self, this, tstamp, flxset):
        self.vols = set()
        self.cats = set()
        self.sects = {}
        self.tstamp = tstamp
        self.flxset = flxset
        this.top.add_interpretation(self, self.topint)
        self.ns = namespace.NameSpace(
            name="",
            root=this,
            separator="",
        )

    def add_vol(self, that, vol):
        self.vols.add((that, vol))

    def add_cat(self, cat, volid):
        self.cats.add((cat, volid))
        sectid = cat.hdr.flxset.txt.strip() + ":" + str(cat.hdr.flxno.val)
        sect = self.sects.get(sectid)
        if not sect:
            sect = FlxSect(self, sectid)
            self.sects[sectid] = sect
        sect.add_cat(cat, volid)

    def topint(self, file, _this):
        file.write("<HR/><H2>FlxGrp »")
        file.write(html.escape(self.flxset))
        file.write("« " +  "".join(self.tstamp.render()) + "</H2>\n")
        file.write("<PRE>\n")
        for that, _vol in sorted(self.vols):
            that.html_derivation(file, False)
        file.write("</PRE>\n")
        file.write("<P>\n")
        for that, _vol in sorted(self.vols):
            file.write(file.str_link_to_that(that) + "  ")
            file.write(html.escape(that.summary(notes=True, names=True)) + "<br/>\n")
        file.write("<P>\n")
        if not self.ns.ns_isempty():
            self.ns.ns_html_plain_noheader(file, None)
        file.write("<PRE>\n")
        for _j,i in sorted(self.sects.items()):
            i.topint(file)
        file.write("</PRE>\n")

class FlxCat(ov.OctetView):
    def __init__(self, this):
        if this[6:12] != b'flxcat':
            return

        self.ga21f = this.has_note("GA21-9182-File")
        if not self.ga21f:
            return

        this.add_interpretation(self, this.html_interpretation_children)

        this.add_type("flxcat")
        super().__init__(this)

        recs = []
        for r in this.iter_rec():
            n = len(r) // 126
            for i in range(n):
                recs.append(r.lo + i * 126)

        self.entries = []
        self.blocks = {}
        for o in recs:
            y = DWord(self, o)
            self.blocks[y.w1.val] = y.hi
            if y.w0.val == 1:
                self.hdr = FlxHdr(self, o).insert()
            elif y.w0.val == 2:
                y = FlxDirSec(self, o).insert()
                self.entries.append(y.w01)
                self.entries.append(y.w02)
            else:
                y.insert()

        self.entries = self.entries[:self.hdr.nent.val]

        volset_dict = this.top.get_by_class_dict(self)

        def find_grp(vol):
            grp = volset_dict.get(vol.tree.this)
            if grp:
                return grp
            for grp in volset_dict.values():
                if grp.flxset != self.hdr.flxset.txt:
                    continue
                if (grp.tstamp.val ^ self.hdr.tstamp.val) & ~0x1f:
                    continue
                volset_dict[vol.tree.this] = grp
                return grp
            grp = FlxGrp(this, self.hdr.tstamp, self.hdr.flxset.txt)
            volset_dict[vol.tree.this] = grp
            return grp

        for identity in self.ga21f:
            # print("FLX-id", identity)
            vol = identity["vol"]
            grp = find_grp(vol)
            grp.add_vol(this, vol)
            grp.add_cat(self, vol.volume_identifier.txt.strip())

        self.add_interpretation(more=False)

    def get_block(self, n):
        p = self.blocks[n]
        return self.this[p:p+120]

    def volptrs(self):
        return self.hdr.firstvol.txt.strip(), self.hdr.nextvol.txt.strip()

    def __str__(self):
        return "".join(
            (
            "FlxCat(",
            self.hdr.flxset.txt,
            ":",
            str(self.hdr.flxno.val),
            " ",
            "".join(self.hdr.tstamp.render()),
            " {",
            self.hdr.firstvol.txt.strip(),
            "…",
            self.hdr.nextvol.txt.strip(),
            "}",
            ")"
            )
        )

    def __lt__(self, other):
        if self.hdr.flxset.txt != other.hdr.flxset.txt:
            return self.hdr.flxset.txt < other.hdr.flxset.txt
        if self.hdr.flxno.val != other.hdr.flxno.val:
            return self.hdr.flxno.val < other.hdr.flxno.val
        return self.hdr.tstamp.val < other.hdr.tstamp.val
