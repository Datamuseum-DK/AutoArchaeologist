#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   IBM System/3 (Preliminary)
   --------------------------
'''

from ....base import artifact
from ....base import octetview as ov
from ....base import namespace

class NameSpace(namespace.NameSpace):
    ''' ... '''

class SrcDirEnt(ov.Struct):
    '''
       See: SY21-0045-3 pdf pg 48 (no fieldnames given)

    '''
    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            sdnam_=ov.Text(7),	# sdtyp + sdnam
            sdfirst_=ov.Be16,
            sdlast_=ov.Be16,
            sdcount_=ov.Be16,
        )
        self.that = None

    def commit(self):
        if self.sdnam.txt.strip() == "":
            return
        bno = self.sdfirst.val
        recs = []
        while bno != 0xffff:
            w = self.tree.where(bno)
            recs.append(
                artifact.Record(
                    low=w,
                    high=w+0xfe,
                    frag=self.tree.this[w:w+0xfe],
                    key=(len(recs),),
                )
            )
            ov.Opaque(self.tree, w, width=0x100).insert()
            bno = self.tree.next_sect(w)
        if len(recs) > 0:
            that = self.tree.this.create(records=recs)
            that.add_type("s3xseg")
            ns = NameSpace(
                parent = self.tree.ns,
                name = self.sdnam.txt.rstrip(),
                this = that,
            )

class SrcDirSect(ov.Struct):
    ''' ... '''
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            f0_=ov.Array(19, SrcDirEnt, vertical=True),
            pad_=7,
            next_=ov.Be16,
            vertical=True,
        )

    def commit(self):
        for dirent in self.f0:
            dirent.commit()

def to_text(this, octets, prev="¿"):
    for c in octets:
        if c < 0x40:
            for i in range(c):
                yield prev
            continue
        sl = this.type_case.slugs[c]
        if sl.flags == 0:
            prev = sl.short
            yield prev
            continue
        prev = '\\x%02x' % c
        yield prev

class TextPages(ov.Octets):
    def __init__(self, tree, lo, hi):
        super().__init__(tree, lo=lo, hi=hi)
        self.nbrs = []
        t = []
        prev = "¿"
        for n in range(lo, hi, 0x100):
            t += list(to_text(tree.this, tree.this[n:n+0xfe], prev))
            prev = t[-1]
            self.nbrs.append(
                (self.this[n + 0xfe] << 8) + self.this[n + 0xff]
            )
        self.lines = []
        for n in range(0, len(t), 96):
            self.lines.append('        »' + ''.join(t[n:n+96]) + "«")

    def render(self):
        yield "TextPages {"
        yield "    Nbrs = " + ",".join("0x%04x" % x for x in self.nbrs)
        yield from self.lines
        yield "}"

class VolumeLabel(ov.Struct):
    '''
       See: SY21-0045-3 pdf pg 31

       Lives in cyl=0,sect=08
    '''
    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            vlid_=ov.Text(3),		# Label identifier "VOL"
            vlname_=ov.Text(6),		# Volume identifier, 1-6 characters
            vlvto_=ov.Be16,		# Volume Table of contents (C/S)
            vldpn_=ov.Be16,		# Source directory pointer (C/S)
            vlnas_=ov.Be16,		# Next avail. source lib sector (C/S)
            vleol_=ov.Be16,		# End of source lib (C/S)
            vldrs_=ov.Be16,		# Number of dir sectors in src lib
            vlpls_=ov.Be16,		# Number of perm src lib sectors
            vlact_=ov.Be16,		# Number of active src lib sectors
            vlavl_=ov.Be16,		# Number of avail src lib sectors
            vlres1_=12,			# Reserved
            vldrp_=ov.Be16,		# Obj lib dir ptr (C/S)
            vleod_=ov.Be16,		# End of obj lib (C/S)
            vlsol_=ov.Be16,		# Start of obj lib (C/S)
            vlael_=ov.Be16,		# Allocated end of obj lib (C/S)
            vleel_=ov.Be16,		# Extended end of obj lib (C/S)
            vlape_=ov.Be16,		# Avail dir ent in obj lib
            vlate_=ov.Be16,		# Avail temp dir ent
            vlftd_=ov.Be24,		# First temp dir en obj lib dir (C/S/D)
            vlnat_=ov.Be24,		# Next temp dir en obj lib dir (C/S/D)
            vlnal_=ov.Be16,		# Next avail obj lib sec perm (C/S)
            vlalt_=ov.Be16,		# Next avail obj lib sec temp (C/S)
            vlasp_=ov.Be16,		# Num avail obj lib sec perm
            vlast_=ov.Be16,		# Num avail obj lib sec temp
            vlals_=ov.Be16,		# Num act obj lib sect
            vlaop_=ov.Be16,		# Num act O-type perm sect
            vlarp_=ov.Be16,		# Num act R-type perm sect
            vlvsys_=ov.Octet,		# Valid System Indicator
            vlarr_=ov.Be16,		# Rollout/rollin area pointer (C/S)
            vlsrr_=ov.Octet,		# Rollout/rollin area size
            vlasw_=ov.Be16,		# Scheduler work area pointer (C/S)
            vlssw_=ov.Octet,		# Scheduler work area size
            vlbol_=ov.Be16,		# Start of libraries (C/S)
            vlend_=ov.Be16,		# End of libraries (C/S)
            vlownr_=ov.Text(10),	# Owner Identification
            vldvc_=14,			# Device constants
            vlalta_=12,			# Alternate track assignments
            vlf5_=51,			# Available tracks, format 5:
            vlcpk_=11,			# Copypack save area
            vlind_=ov.Octet,		# Library maintenance indicator
            vres2_=4,			# Reserved
            vlcr_=2,			# Checkpoint/restart
            vres3_=19,			# Reserved
            vlssfi_=10,			# Scientific system file indicator
            vlsdti_=24,			# Suspected defective track indicator
            vlssi_=16,			# Scientific system indicators
            vertical=True,
        )

class Foo003(ov.Struct):
    ''' ... '''
    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            f0_=3,
            f1_=ov.Text(0x13),
        )

class ObjDirEnt(ov.Struct):
    '''
       See: SY21-0045-3 pdf pg 51
    '''
    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            dirnam_=ov.Text(7),	# dirtyp + dirnam
            dircs_=ov.Be16,
            dirtxt_=1,
            dirlkn_=2,
            dirrld_=1,
            dirsca_=2,
            dirsiz_=1,
            diratr_=2,
            dirlev_=1,
            dirtot_=ov.Be16,
        )

    def commit(self):
        if self.dircs.val == 0:
            return
        if self.dirtot.val == 0:
            return
        ptr = self.tree.where2(self.dircs.val)
        y = ov.This(self.tree, ptr, self.dirtot.val<<8).insert()
        # print("CC", self, hex(y.lo))
        ns = NameSpace(
            parent = self.tree.ns2,
            name = self.dirnam.txt.rstrip(),
            this = y.that,
        )

class ObjDirSect(ov.Struct):
    ''' ... '''
    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            f0_=ov.Array(12, ObjDirEnt, vertical=True),
            f1_=4,
            vertical=True,
        )

    def commit(self):
        for i in self.f0:
            i.commit()

class S3X(ov.OctetView):
    ''' '''

    def __init__(self, this):

        if len(this) != 0x259242:
            return


        recs = []
        print("S3X", this)
        for frag in this.iter_rec():
            recs.append(
                artifact.Record(
                    low = frag.lo + 2,
                    high = frag.hi,
                    frag = frag.frag[2:],
                    key = ((frag.frag[0] << 8) + frag.frag[1],),
                )
            )
        this.create(records=recs)
        this.add_interpretation(self, this.html_interpretation_children)

class S3Y(ov.OctetView):
    ''' '''

    def __init__(self, this):

        if len(this) != 0x258c00:
            return

        super().__init__(this)

        y = ov.Text(17)(self, 0)
        if y.txt != "DUMP/RESTORE FILE":
            print("S3Y?", y)
            return
        y.insert()

        this.add_note("S3-Dump/Restore")

        this.type_case.set_slug(0x0, '░')

        self.ns = NameSpace(
            name = '',
            root = this,
            separator = "",
        )

        self.ns2 = NameSpace(
            name = '',
            root = this,
            separator = "",
        )

        if True:
            self.foo2 = VolumeLabel(self, 0xe00).insert()

        if True:
            ptr = self.where(self.foo2.vldpn.val)
            while True:
                y = SrcDirSect(self, ptr).insert()
                y.commit()

                nxt = self.next_sect(ptr)
                if nxt == 0xffff:
                    break
                whr = self.where(nxt)
                ptr = whr

        if True:
            a = self.where(self.foo2.vldrp.val)
            b = self.where(self.foo2.vleod.val)
            for ptr in range(a, b, 0x100):
                i = ObjDirSect(self, ptr).insert()
                i.commit()

        this.add_interpretation(self, self.ns.ns_html_plain)
        this.add_interpretation(self, self.ns2.ns_html_plain)
        self.add_interpretation(more=True)

    def next_sect(self, off):
        x = (self.this[off+0xfe]<<8) + self.this[off+0xff]
        return x

    def where(self, sect):
        return self.where2(sect)
        h = sect >> 7
        s = sect & 0x7f
        o = h * 0x1800 - 0x8400
        return o + (s << 6)

    def where2(self, adr):
        r = 128
        h = adr // r
        l = adr % r
        e = ((h * 96 + l) << 6) - 0x8400
        return e

class S3Z():
    ''' '''

    def __init__(self, this):

        if not this.has_type("s3xseg"):
            return

        prev = "¿"
        t = list(to_text(this, this))
        with this.add_utf8_interpretation("TextSegment") as file:
            for n in range(0, len(t), 96):
                file.write(''.join(t[n:n+96]) + "\n")
