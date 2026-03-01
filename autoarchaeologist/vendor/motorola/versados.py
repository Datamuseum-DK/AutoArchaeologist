#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Versados floppies
   =================

   Very rudimentary.
   Based on info about 'REPAIR' pdf pg 236ff in

   https://bitsavers.org/pdf/motorola/versados/M68KVSF_D7_VERSAdosSysFacilities_Oct85.pdf
'''

from ...base import namespace as ns
from ...base import octetview as ov

class NameSpace(ns.NameSpace):
    ''' ... '''

class VolumeIdBlock(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vidvol_=ov.Text(4),
            vidusn_=ov.Be16,
            vidsat_=ov.Be32,
            vidsal_=ov.Be16,
            vidsds_=ov.Be32,
            vidpdl_=ov.Be32,
            vidoss_=ov.Be32,
            vidosl_=ov.Be16,
            vidose_=ov.Be32,
            vidosa_=ov.Be32,
            viddte_=ov.Be32,
            vidvd_=ov.Text(20),
            vidvno_=ov.Text(4),
            vidchk_=ov.Be16,
            viddtp_=64,
            viddta_=ov.Be32,
            viddas_=ov.Be32,
            viddal_=ov.Be16,
            vidslt_=ov.Be32,
            vidsll_=ov.Be16,
            vidcas_=ov.Be32,
            vidcal_=1,
            vidipc_=1,
            vidalt_=1,
            vidrs1_=97,
            vidmac_=ov.Text(8),

            vertical=True,
        )

class SectorAllocationTable(ov.Dump):
    ''' ... '''


class SecondaryDirectoryEntry(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sdbusn_=ov.Be16,
            sdbclg_=ov.Text(8),
            sdbpdp_=ov.Be32,
            sdbac1_=ov.Octet,
            sdbrs1_=ov.Octet,
        )
        if self.sdbpdp.val == 0:
            self.pdb = None
        else:
            self.pdb = PrimaryDirectoryBlock(
                self.tree,
                self.sdbpdp.val << 8,
            ).insert()

class SecondaryDirectoryBlock(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            sdbfpt_=ov.Be32,
            sdbrs1_=12,
            sdbstr_=ov.Array(15, SecondaryDirectoryEntry, vertical=True),
            vertical=True,
        )

class PrimaryDirectoryEntry(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            dirfil_=ov.Text(8),
            dirext_=ov.Text(2),
            dirrsi_=2,
            dirfs_=ov.Be32,
            dirfe_=ov.Be32,
            direof_=ov.Be32,
            direor_=ov.Be32,
            dirwcd_=ov.Octet,
            dirrcd_=ov.Octet,
            diratt_=ov.Octet,
            dirlbz_=ov.Octet,
            dirlrl_=ov.Be16,
            dirrsz_=ov.Octet,
            dirkey_=ov.Octet,
            dirfab_=ov.Octet,
            dirdat_=ov.Octet,
            dirdtec_=ov.Be16,
            dirdtea_=ov.Be16,
            dirrs3_=8,
        )
        self.fabhs = []
        if self.dirfs.val != 0 and self.diratt.val == 3:
            ptr = self.dirfs.val << 8
            while ptr > 0:
                self.fabhs.append(
                    FileAccessBlockHeader(
                        self.tree,
                        ptr,
                    ).insert()
                )
                ptr2 = self.fabhs[-1].fabflk.val << 8
                print(tree.this, "L", len(self.fabhs), hex(self.fabhs[-1].lo), hex(ptr), hex(ptr2))
                if ptr == ptr2:
                    break
                ptr = ptr2
            dbs = []
            for fabh in self.fabhs:
                for seg in fabh.fabseg:
                    if seg.fabpsn.val == 0:
                        break
                    dbs.append(
                        DataBlock(
                            self.tree,
                            seg.fabpsn.val << 8,
                            seg.fabsgs.val,
                            seg.fabrec.val,
                        ).insert()
                    )
            lines = []
            for db in dbs:
                for rec in db.recs:
                    lines.append(rec.text())
            that = self.tree.this.create(octets="\n".join(lines).encode("utf8"))
            NameSpace(
                (self.dirfil.txt + "." + self.dirext.txt).replace(' ', ''),
                parent = self.tree.ns,
                this = that,
            )

class Record(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            len_=ov.Be16,
            more = True
        )
        #self.add_field("rec", ov.Text(self.len.val))
        self.add_field("rec", self.len.val)
        if self.len.val & 1:
            self.add_field("pad", 1)
        self.done()

    def text(self):
        t = []
        tc = self.tree.this.type_case
        for ch in self.rec:
            if ch < 0x80:
                t.append(tc.slugs[ch].long)
            else:
                t.append(" " * (ch - 128))
        return "".join(t)

    def render(self):
        yield "»" + self.text() + "«"


class DataBlock(ov.Struct):
    def __init__(self, tree, lo, hi, nrec):
        # nrec = min(nrec, 2)
        super().__init__(
            tree,
            lo,
            recs_=ov.Array(nrec, Record, vertical=True),
            vertical=True,
        )

class PrimaryDirectoryBlock(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            dirfpt_=ov.Be32,
            dirusn_=ov.Be16,
            dirclg_=ov.Text(8),
            dirrs1_=2,
            dirstr_=ov.Array(20, PrimaryDirectoryEntry, vertical=True),
            dirrs2_=8,
            vertical=True,
        )

class Key(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            keylen_=ov.Octet,
            more=True,
        )
        if self.keylen.val > 0:
            self.add_field("key", self.keylen.val)
        self.done()

class FileSegmentDescriptor(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            fabpsn_=ov.Be32,
            fabrec_=ov.Be16,
            fabsgs_=ov.Octet,
            fabkey_=Key,
        )

class FileAccessBlockHeader(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            fabflk_=ov.Be32,
            fabblk_=ov.Be32,
            fabuse_=ov.Octet,
            fabpky_=Key,
            more=True,
            vertical=True,
        )
        # XXX: 30 probably only if key is zero length  ?
        self.add_field(
            "fabseg",
            ov.Array(30, FileSegmentDescriptor, vertical=True)
        )
        self.done()

class VersaDos(ov.OctetView):

    SECTOR_OFFSET = 0

    def __init__(self, this):
        if len(this) not in (512512,):
            return

        if this[0xf8:0x100].tobytes() != b'EXORMACS':
            return

        super().__init__(this)

        self.ns = NameSpace(
            name = "",
            root = this,
        )
        this.add_interpretation(self, self.ns.ns_html_plain)

        vid = VolumeIdBlock(self, 0).insert()
        sat = SectorAllocationTable(
            self,
            lo = vid.vidsat.val << 8,
            hi = (vid.vidsat.val + vid.vidsal.val) << 8,
        ).insert()

        sdbs = []
        sdbs.append(
            SecondaryDirectoryBlock(
                self,
                vid.vidsds.val << 8,
            ).insert()
        )

        self.add_interpretation(more=True)
