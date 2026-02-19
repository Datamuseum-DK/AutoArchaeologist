#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license
#
# ref #1: AEGIS_Internals_and_Data_Structures_Jan86.pdf
# ref #2: 002398-04_Domain_Engineering_Handbook_Rev4_Jan87.pdf
# ref #3: https://github.com/domainos-archeology/apollofs

''' ... '''

from ...base import octetview as ov
from ...base import namespace as ns

UNREAD = b'_UNREAD_' * (4096//8)

class Uid(ov.Be64):

    def render(self):
        yield "Uid{0x%09x:%02x:%05x}" % (
            self.val >> 28,
            (self.val >> 20) & 0xff,
            self.val & 0xfffff,
        )

class VtocX(ov.Be32):
    ''' ... '''

class DirEnt(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Octet,
            nlen_=ov.Octet,
            f02_=ov.Octet,
            f03_=ov.Octet,
            more=True,
        )
        self.kind = self.f00.val & 0xf
        if self.kind == 0x1:
            self.add_field("f04", ov.Be32)
        elif self.kind == 0x2:
            self.add_field("uid", Uid)
            self.add_field("f0c", ov.Be32)
            if self.nlen.val:
                self.add_field("name", ov.Text(self.nlen.val))
        elif self.kind == 0x3:
            self.add_field("uid", Uid)
            self.add_field("f0c", ov.Be32)
            self.add_field("f10", ov.Be32)
            self.add_field("f14", ov.Text(10))
        elif self.kind == 0x4:
            self.add_field("uid", Uid)
            if self.nlen.val:
                self.add_field("name", ov.Text(self.nlen.val))
            if self.f03.val:
                self.add_field("name2", ov.Text(self.f03.val))
        if self.hi & 3:
            self.add_field("pad", 4 - (self.hi & 3))
        self.done()

class DirExtra(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            dir_06_=ov.Be16,
            dir_07_=ov.Be16,
            dir_08_=ov.Be16,
            dir_09_=ov.Be16,
            dir_13_=0x34,
            dir_14_=0x34,
        )

class Directory(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            dir_00_=2,
            dir_01_=Uid,
            dir_02_=ov.Be16,
            dir_03_=ov.Be16,
            dir_04_=ov.Be16,
            dir_05_=ov.Be16,
            vertical = True,
            more=True,
        )
        if self.dir_02.val == 0:
            self.add_field("dir_ex_", DirExtra)
        n = (self.dir_04.val - len(self)) // 2
        # n = 140
        self.add_field("idx", ov.Array(n, ov.Be16, elide=(0,), vertical=False))
        if self.dir_04.val != self.dir_05.val:
            ov.Opaque(tree, lo=self.lo + self.dir_04.val, hi=self.lo + self.dir_05.val).insert()
        lx = min(x.val for x in self.idx if x.val)
        cx = len(list(x.val for x in self.idx if x.val))
        hx = max(x.val for x in self.idx)
        # print("DX", hex(lo), hex(cx), hex(lx), hex(hx), hex(n))
        if 0 and lx < 0x1000 and len(self) < lx:
            self.add_field("padx_", lx - len(self))
        if False:
            if lx < 0x1000 and hx < 0x1000:
                self.add_field("dents", ov.Array(cx, DirEnt, vertical=True))
        else:
            for i in self.idx:
                if 0 == i.val:
                    break
                if i.val <= 0x1000:
                    DirEnt(tree, self.lo + i.val).insert()

        self.done()

class PvLabelT(ov.Struct):
    '''
       ref: #1/p57
       ref: #2/p54
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            version_=ov.Be16,
            apollo_=ov.Text(6),
            name_=ov.Text(32),
            id_=Uid,
            f30_=ov.Be16,
            dtype_=ov.Be16,
            blocks_per_pvol_=ov.Be32,
            blocks_per_track_=ov.Be16,
            blocks_per_cyl_=ov.Be16,
            lv_list_=ov.Array(10, ov.Be32, vertical=True),
            alt_lv_list_=ov.Array(10, ov.Be32, vertical=True),
            phys_badspot_daddr_=ov.Be32,
            phsy_diag_daddr_=ov.Be32,
            phys_sector_start_=ov.Be16,
            phys_sector_size_=ov.Be16,
            pre_comp_=ov.Be16,

            vertical=True,
        )

class VtocMapE(ov.Struct):
    '''
       ref: #2/p57
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            lt_blk_=ov.Be16,
            blk_add_=ov.Be32,
        )

class VtocHdrT(ov.Struct):
    '''
       ref: #2/p57
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            version_=ov.Be16,
            vtoc_size_=ov.Be16,
            vtoc_blocks_=ov.Be32,
            net_x_=VtocX,
            root_x_=VtocX,
            os_x_=VtocX,
            boot_x_=VtocX,
            map_=ov.Array(8, VtocMapE, vertical=True),
            pad_=28,

            vertical=True,
        )

class VtocCeHdrT(ov.Struct):
    '''
       ref: #2/p56
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f000_=ov.Be32,
            f001_=ov.Be32,
            f004_=ov.Array(8, VtocEntryHeader, vertical=True, elide=(0,)),
            fe88__=368,
            fff8_=ov.Be32,
            blkno_=ov.Be32,
            vertical=True,
        )

class Tail(ov.Opaque):
    ''' ... '''

class VtocEntryHeader(ov.Struct):
    '''
       Name adopted from ref: #3
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            version_=ov.Octet,
            system_type_=ov.Octet,
            flags_=ov.Be16,
            obj_=Uid,
            obj_typ_=Uid,
            length_=ov.Be32,
            n_blk_=ov.Be32,
            last_mod_=ov.Be32,
            extdtm_=ov.Be16,
            refcnt_=ov.Be16,
            last_use_=ov.Be32,
            f028_=ov.Be32,
            f02c_=Uid,
            f034_=Uid,
            dir_=Uid,
            obj_lock_key_=ov.Be32,
            user_=Uid,
            group_=Uid,
            org_=Uid,
            f064_=40,
            acl_=Uid,
            f094__=52,
            indir_blk_=ov.Array(3, ov.Be32, elide=(0,), vertical=True),
            dir_blk_=ov.Array(64, ov.Be32, elide=(0,), vertical=True),

            vertical=True,
            more=True
        )
        self.done(-464)
        self.val = sum(self)
        self.committed = False
        return
        if not self.val:
            return
        vtocx = self.tree.vtocx.get(self.obj.val)
        if not vtocx:
            # print(self.tree.this, hex(self.lo), "NO VTOCX", vtocx, self.obj, self.obj_typ)
            return
        try:
            self.commit()
        except Exception as err:
            print(self.tree.this, "COMMIT FAILED", hex(self.lo), err)

    def render(self):
        yield "YYY 0x%08x " % self.lo + str(self.tree.vtocx.get(self.obj.val)) + " " + str(self.committed)
        yield from super().render()

    def iter_frag(self):
        self.left = self.length.val

        def work_through(x):
            for bno in x:
                if self.left == 0:
                    return
                lba = bno.val
                if lba == 0:
                    print(self.tree.this, hex(self.lo), "ZERO_BNO", hex(self.left))
                lba &= 0x7fffffff
                if lba >= len(self.tree.this) >> 12:
                    print(self.tree.this, hex(self.lo), "BOGO_BNO", hex(self.left), hex(lba))
                    return
                if self.left == 0:
                    return
                if self.left >= 1<<12:
                    yield lba<<12, (lba+1) << 12
                    self.left -= 1<<12
                else:
                    yield lba<<12, (lba<<12) + self.left
                    self.left = 0
                    return

        yield from work_through(self.dir_blk)
        if self.left == 0:
            return

        def get_indir(bno):
            lba = bno << 12
            if lba == 0:
                print(self.tree.this, hex(self.lo), "BOGO_INDIR", hex(self.left), self.indir_blk, bno)
                return None
            iblk = ov.Array((1<<12)//4, ov.Be32, elide=(0,), vertical=True)(self.tree, lba).insert()
            return iblk

        ib = get_indir(self.indir_blk[0].val)
        if not ib:
            return
        yield from work_through(ib)
        if self.left == 0:
            return

        print(self.tree.this, hex(self.lo), "Need Indir2", hex(self.left), str(self.indir_blk))
        ib2 = get_indir(self.indir_blk[1].val)
        if not ib2:
            return
        for bno in ib2:
            ib = get_indir(bno.val)
            if not ib:
                return
            yield from work_through(ib)
            if self.left == 0:
                return
        print(self.tree.this, hex(self.lo), "Need Indir3", hex(self.left), str(self.indir_blk))

    def commit(self):
        self.committed = True
        #print(self.tree.this, "C", hex(self.lo), self.obj, self.system_type.val)
        if (self.length.val + 0xfff) >> 12 > self.n_blk.val:
            print(self.tree.this, hex(self.lo), "NOT ENOUGH BLOCKS?", hex(self.length.val), hex(self.n_blk.val), self.obj, self.obj_typ)
            return
        if self.system_type.val in (1, 2,):
            for fm, to in self.iter_frag():
                if to > len(self.tree.this):
                    print(self.tree.this, hex(self.lo), "BOGO_DIR", hex(fm), hex(to))
                    break
                assert fm != 0
                Directory(self.tree, fm).insert()
        elif self.system_type.val in (0,):
            r = []
            for lo, hi in self.iter_frag():
                if lo == 0:
                    r.append(UNREAD[:hi])
                r.append(self.tree.this[lo:hi])
                y = ov.Opaque(self.tree, lo=lo, hi=hi).insert()
                y.rendered = "Data " + str(self.obj)
                if hi < lo + (1<<12):
                    Tail(self.tree, lo=hi, hi=lo + (1<<12)).insert()
            if r:
                y = self.tree.this.create(records=r)
                ns.NameSpace(name=str(self.obj), parent=self.tree.ns, this=y)
        elif self.system_type.val == 3:
            # ACL
            pass
        elif self.system_type.val == 4:
            # DISK
            pass
        elif self.system_type.val == 5:
            # DEVICE
            pass
        else:
            print(self.tree.this, hex(self.lo), "WHAT?", hex(self.system_type.val), self.obj, self.obj_typ)

class xVtocEntry(ov.Struct):
    '''
       ref: #1/p67
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=VtocCeHdrT,
            file_map_=ov.Array(0x23, ov.Be32, vertical=False),
            vertical=False,
        )


class VtocBucketEntry(ov.Struct):
    '''
       Name adopted from ref: #3
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            uid_=Uid,
            vtocx_=VtocX,
        )
        self.val = sum(self)


class VtocBucket(ov.Struct):
    '''
       Name adopted from ref: #3
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Be64,
            buckets_=ov.Array(0x14, VtocBucketEntry, vertical=True, elide=(0,)),
            vertical=True,
        )
        for v in self.buckets:
            if v.uid.val:
                self.tree.vtocx[v.uid.val] = v.vtocx.val

class VtocBucketBlock(ov.Struct):
    '''
       Name adopted from ref: #3
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            buckets_=ov.Array(16, VtocBucket, vertical=True),
            ff80_=120,
            fff8_=ov.Be32,
            blockno_=ov.Be32,
            vertical=True,
        )
        if self.blockno.val<<12 != self.lo:
            print(tree.this, "BAD BLOCKNO in VtocBucketBlock", hex(self.lo))

class LvLabelT(ov.Struct):
    '''
       ref: #2/p52
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            version_=ov.Be16,
            f02_=ov.Be16,
            name_=ov.Text(32),
            id_=Uid,
            bat_hdr_=0x20,
            #vtoc_hdr_=0x64,
            vtoc_hdr_=VtocHdrT,
            label_write_time_=ov.Be32,
            last_mounted_node_=ov.Be32,
            node_boot_time_=ov.Be32,
            mounted_time_=ov.Be32,
            dismounted_time_=ov.Be32,
            salvage_node_=ov.Be32,
            salvage_time_=ov.Be32,
            salvage_mode_=ov.Be16,
            sys_shut_state_=ov.Be16,
            dump_start_time_=ov.Be32,
            dump_end_time_=ov.Be32,
            dump_cur_uid_=Uid,
            utc_delta_=ov.Be16,
            timezone_name_=ov.Text(4),
            last_valid_time_=ov.Be32,
            fea_=ov.Be16,
            bad_spot_barrier_=ov.Be32,
            bad_spot_list_=ov.Array(256-60, ov.Be32, vertical=True, elide=(0,)),

            vertical=True,
        )

class ApolloDomainLogicalVolume(ov.OctetView):

    def __init__(self, this):
        if not this.has_type("ApolloDomainLogicalVolume"):
            return
        super().__init__(this)

        self.ns = ns.NameSpace(name='', root=this, separator='')
        lvl1 = LvLabelT(self, 0x0).insert()
        lvl2 = LvLabelT(self, len(this) - (1<<12)).insert()

        self.vtocx = {}

        if False:
            for n in range(lvl1.vtoc_hdr.map[0].lt_blk.val):
                p = (lvl1.vtoc_hdr.map[0].blk_add.val+n)<<12
                y = VtocBucketBlock(self, p).insert()
        else:
            ov.Array(
                lvl1.vtoc_hdr.map[0].lt_blk.val,
                VtocBucketBlock,
                vertical=True,
            )(self, lvl1.vtoc_hdr.map[0].blk_add.val<<12).insert()

        vtocce = {}
        for uid, vtocx in self.vtocx.items():
            if not vtocx:
                continue
            lba = (vtocx & ~0xf) << 8
            i = vtocce.get(lba)
            if i is None:
                i = VtocCeHdrT(self, lba).insert()
                vtocce[lba] = i
            j = i.f004[vtocx & 0xf]
            j.commit()

        this.add_interpretation(self, self.ns.ns_html_plain)
        #this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(title="ApolloDomainLogicalVolume", more=True)

class ApolloDomainPhysicalVolume(ov.OctetView):

    def __init__(self, this):
        if this.top not in this.parents:
            return
        if bytes(this[0x2:0x8]) != b'APOLLO':
            return
        this.add_type("ApolloDomainFileSystem")

        super().__init__(this)

        pvl = PvLabelT(self, 0).insert()
        for lv,alt in zip(pvl.lv_list, pvl.alt_lv_list):
            if not lv.val or alt.val <= lv.val:
                continue
            y = ov.This(self, lo=lv.val<<12, hi=(alt.val+1)<<12).insert()
            y.that.add_type("ApolloDomainLogicalVolume")
            print(lv, alt)

        this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(title="ApolloDomainPhysicalVolume", more=False)

class ApolloCoff():
    def __init__(self, this):
        if this[0] == 0x01 and this[1] == 0x97:
            this.add_type("Apollo_68k_COFF")
        elif this[0] == 0x01 and this[1] == 0x94:
            this.add_type("Apollo_88k_COFF")

ALL = [
    ApolloDomainPhysicalVolume,
    ApolloDomainLogicalVolume,
    ApolloCoff,
]
