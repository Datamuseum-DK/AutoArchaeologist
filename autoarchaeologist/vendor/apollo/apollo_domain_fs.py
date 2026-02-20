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

def ranges(numbers):
    ''' Reduce list of numbers to ranges '''

    diff = None
    for i,j in enumerate(sorted(numbers)):
        if i - j != diff:
            if diff is not None:
                yield first,last
            first = j
            diff = i -j
        last = j
    if diff is not None:
        yield first,last

def make_ranges(data):
    ''' Eliminate small ranges '''
    for low, high in ranges(data):
        if low == high:
            yield low, low
        elif low + 1 == high:
            yield low, low
            yield high, high
        else:
            yield low, high


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
        self.name = None
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
            self.add_field("name", ov.Text(10))
        elif self.kind == 0x4:
            self.add_field("uid", Uid)
            if self.nlen.val:
                self.add_field("name", ov.Text(self.nlen.val))
            if self.f03.val:
                self.add_field("name2", ov.Text(self.f03.val))
        if self.hi & 3:
            self.add_field("pad", 4 - (self.hi & 3))
        self.done()
        self.ns = None

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
        self.dirents = []
        for i in self.idx:
            if 0 == i.val:
                break
            if i.val <= 0x1000:
                y = DirEnt(tree, self.lo + i.val).insert()
                self.dirents.append(y)
        self.done()

    def populate(self, pns):
        for de in self.dirents:
            if de.f00.val == 4:
                continue
            if de.ns:
                print("Dirent with multiple NS", de)
                continue
            if not de.name:
                print("Dirent with no name", de)
                continue
            vtx = self.tree.uid2vtocx.get(de.uid.val)
            if not vtx:
                print("Blind dirent (vtox)", de)
                continue
            vte = self.tree.vtocx2vtoce.get(vtx)
            print("X", pns.ns_path(), hex(de.lo), de.name, vte)
            if not vte:
                print("Blind dirent (vte)", de)
                continue
            de.ns = ns.NameSpace(
                name=de.name.txt.rstrip(),
                parent=pns,
                this=vte.that,
            )
            if vte.dir:
                vte.dir.populate(de.ns)


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
        self.val = sum(self)

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
            map_=ov.Array(8, VtocMapE, vertical=True, elide=(0,)),
            pad_=28,

            vertical=True,
        )


class Indir(ov.Struct):
    '''
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            bnos_=ov.Array(4096//4, ov.Be32, vertical=True, elide=(0,)),
            vertical=True,
        )

    def render(self):
        l = list(x.val for x in self.bnos)
        while l and l[-1] == 0:
            l.pop(-1)
        yield "Indir {"
        for lo,hi in make_ranges(l):
            if lo == hi:
                yield "  0x%08x," % lo
            else:
                yield "  0x%08x…0x%08x" % (lo,hi)
        yield "}"

class Tail(ov.Opaque):
    ''' ... '''

class VtocEntryHeader(ov.Struct):
    '''
       Name adopted from ref: #3
    '''
    SIZEOF = 464

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
            f02c_=ov.Be64,
            f034_=ov.Be64,
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
        self.dir = None
        self.that = None

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
                if lba >= len(self.tree.this) // self.tree.block_size:
                    print(self.tree.this, hex(self.lo), "BOGO_BNO", hex(self.left), hex(lba))
                    return
                if self.left == 0:
                    return
                if self.left >= self.tree.block_size:
                    yield lba * self.tree.block_size, (lba+1) * self.tree.block_size
                    self.left -= self.tree.block_size
                else:
                    yield lba * self.tree.block_size, lba * self.tree.block_size + self.left
                    self.left = 0
                    return

        yield from work_through(self.dir_blk)
        if self.left == 0:
            return

        def get_indir(bno):
            lba = bno * self.tree.block_size
            if lba == 0:
                print(self.tree.this, hex(self.lo), "BOGO_INDIR", hex(self.left), self.indir_blk, bno)
                return None
            iblk = Indir(self.tree, lba).insert()
            return iblk

        ib = get_indir(self.indir_blk[0].val)
        if not ib:
            return
        yield from work_through(ib.bnos)
        if self.left == 0:
            return

        print(self.tree.this, hex(self.lo), "Need Indir2", hex(self.left), str(self.indir_blk))
        ib2 = get_indir(self.indir_blk[1].val)
        if not ib2:
            return
        for bno in ib2.bnos:
            ib = get_indir(bno.val)
            if not ib:
                return
            yield from work_through(ib.bnos)
            if self.left == 0:
                return
        print(self.tree.this, hex(self.lo), "Need Indir3", hex(self.left), str(self.indir_blk))

    def commit(self):
        self.committed = True
        #print(self.tree.this, "C", hex(self.lo), self.obj, self.system_type.val)
        if (self.length.val + 0xfff) // self.tree.block_size > self.n_blk.val:
            print(self.tree.this, hex(self.lo), "NOT ENOUGH BLOCKS?", hex(self.length.val), hex(self.n_blk.val), self.obj, self.obj_typ)
            return
        if self.system_type.val in (1, 2,):
            for fm, to in self.iter_frag():
                if to > len(self.tree.this):
                    print(self.tree.this, hex(self.lo), "BOGO_DIR", hex(fm), hex(to))
                    break
                assert fm != 0
                self.dir = Directory(self.tree, fm).insert()
        elif self.system_type.val in (0,):
            r = []
            for lo, hi in self.iter_frag():
                if lo == 0:
                    r.append(UNREAD[:hi])
                r.append(self.tree.this[lo:hi])
                y = ov.Opaque(self.tree, lo=lo, hi=hi).insert()
                y.rendered = "Data " + str(self.obj)
                if hi < lo + self.tree.block_size:
                    Tail(self.tree, lo=hi, width=self.tree.block_size).insert()
            if r:
                self.that = self.tree.this.create(records=r)
                ns.NameSpace(name=str(self.obj), parent=self.tree.uid_ns, this=self.that)
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

    def render(self):
        if self.committed:
            yield " ".join(
                (
                "YYY 0x%08x" % self.lo,
                str(self.tree.uid2vtocx.get(self.obj.val)),
                str(self.committed),
                "%d" % len(self),
                str(self.that),
                str(self.dir),
                )
            )
            yield from super().render()
        elif not sum(self):
            yield "VtocEntryHeader { Ø }"
        else:
            yield "VtocEntryHeader { " + str(self.obj) + " uncommitted }"

class VtocCeHdrT(ov.Struct):
    '''
       ref: #2/p56
    '''
    def __init__(self, tree, lo):
        n = (tree.block_size - 4 * 4) // VtocEntryHeader.SIZEOF
        super().__init__(
            tree,
            lo,
            f000_=ov.Be32,
            f001_=ov.Be32,
            f004_=ov.Array(n, VtocEntryHeader, vertical=True, elide=(0,)),
            vertical=True,
            more=True,
        )
        if len(self) < tree.block_size - 8:
            self.add_field("pad_", tree.block_size - (len(self) + 8))
        self.add_field("magic", ov.Be32)
        self.add_field("blkno", ov.Be32)
        self.done()
        if self.blkno.val * tree.block_size != self.lo:
            print(tree.this, "BAD BLOCKNO in VtocCeHdrT", hex(self.lo), hex(self.blockno))

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

       Twenty is the optimal choice for 1K block_size, if we assume
       an 8 byte overhead both here and in the ``VtocBucketBlock``
       struct.

    '''
    SIZEOF = 8 + 20 * 12

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vtb_f00_=ov.Be64,
            buckets_=ov.Array(20, VtocBucketEntry, vertical=True, elide=(0,)),
            vertical=True,
        )
        self.val = sum(self)
        for v in self.buckets:
            if v.uid.val:
                self.tree.uid2vtocx[v.uid.val] = v.vtocx.val

    def render(self):
        if sum(self):
            yield from super().render()
        else:
            yield "VtocBucket {Ø}"

class VtocBucketBlock(ov.Struct):
    '''
       Name adopted from ref: #3

       The magic number (0xfedca984) and blockno at the tail is
       probably there for recovery purposes.
    '''
    def __init__(self, tree, lo):
        n_buckets = min(16, (tree.block_size-8) // VtocBucket.SIZEOF)
        super().__init__(
            tree,
            lo,
            buckets_=ov.Array(n_buckets, VtocBucket, vertical=True, elide=(0,)),
            vertical=True,
            more=True,
        )
        if len(self) < tree.block_size - 8:
            self.add_field("pad_", tree.block_size - (len(self) + 8))
        self.add_field("magic", ov.Be32)
        self.add_field("blkno", ov.Be32)
        self.done()
        if self.blkno.val * tree.block_size != self.lo:
            print(tree.this, "BAD BLOCKNO in VtocBucketBlock", hex(self.lo), hex(self.blockno))

class Bat(ov.Dump):
    ''' ... '''

class BatHdrT(ov.Struct):
    '''
       Block Availability Table Header
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       ref: #1/p60
       ref: #2/p37

    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            n_blk_=ov.Be32,
            n_free_=ov.Be32,
            addr_=ov.Be32,
            base_add_=ov.Be32,
            vcd_=ov.Be16,
            bat_step_=ov.Be32,
            vertical=True,
            more=True,
        )
        self.done(-0x20)

class LvLabelT(ov.Struct):
    '''
       Logical Volume Label
       ~~~~~~~~~~~~~~~~~~~~~
       ref: #1/p58
       ref: #2/p52

       Not obvious how this scales with larger blocks, maybe the
       bad_spot_list absorbs the extra space?

    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            version_=ov.Be16,
            f02_=ov.Be16,
            name_=ov.Text(32),
            id_=Uid,
            bat_hdr_=BatHdrT,
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

class FreeBlock(ov.Opaque):
    ''' ... '''

class ApolloDomainLogicalVolume(ov.OctetView):

    '''
       Apollo Domain Logical Volume
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    '''

    def __init__(self, this):
        n = this.has_type("ApolloDomainLogicalVolume")
        if n is None:
            return
        super().__init__(this)
        print(this, "ApolloDomainLogicalVolume", n)
        self.block_size = max(x.get('block_size', 0) for x in n)

        self.uid_ns = ns.NameSpace(name='', root=this, separator='')
        self.ns = ns.NameSpace(name='', root=this, separator='/')
        lvl1 = LvLabelT(self, 0x0).insert()
        lvl2 = LvLabelT(self, len(this) - self.block_size).insert()

        self.bat_hdr = lvl1.bat_hdr

        self.bat_add = self.bat_hdr.base_add.val
        self.bat_base = self.bat_hdr.addr.val * self.block_size
        i = self.bat_hdr.n_blk.val / (8 * self.block_size)
        if i > int(i):
            i += 1
        i = int(i)

        if False:
            for o in range(0, i * self.block_size, 0x20):
                Bat(self, lo=self.bat_base + o, width=0x20).insert()
        else:
            Bat(self, lo=self.bat_base, width=i * self.block_size).insert()

        self.uid2vtocx = {}

        ov.Array(
            lvl1.vtoc_hdr.map[0].lt_blk.val,
            VtocBucketBlock,
            vertical=True,
        )(self, lvl1.vtoc_hdr.map[0].blk_add.val * self.block_size).insert()

        self.vtocx2vtoce = {}
        vtocce = {}
        for uid, vtocx in self.uid2vtocx.items():
            if not vtocx:
                continue
            lba = (vtocx >> 4) * self.block_size
            i = vtocce.get(lba)
            if i is None:
                i = VtocCeHdrT(self, lba).insert()
                vtocce[lba] = i
            j = i.f004[vtocx & 0xf]
            j.commit()
            self.vtocx2vtoce[vtocx] = j

        for nm, vtx in (
            ("NET", lvl1.vtoc_hdr.net_x.val),
            ("ROOT", lvl1.vtoc_hdr.root_x.val),
            ("OS", lvl1.vtoc_hdr.os_x.val),
            ("BOOT", lvl1.vtoc_hdr.boot_x.val),
        ):
            vte = self.vtocx2vtoce.get(vtx)
            if vte is None:
                print(nm.ljust(8), vte)
                continue
            print(nm.ljust(8), hex(vte.lo), vte.obj)
            if vte.dir:
                print("  ", vte.dir)
                for de in vte.dir.dirents:
                    print("    ", de)
                if nm == "NET":
                    vte.dir.populate(self.ns)

        self.check_bat()

        this.add_interpretation(self, self.ns.ns_html_plain)
        this.add_interpretation(self, self.uid_ns.ns_html_plain)
        self.add_interpretation(title="ApolloDomainLogicalVolume", more=True)

    def check_bat(self):
        ''' Check the BAT for consistency '''

        nfree = 0
        nused = 0
        nwrong = 0
        for bno in range(self.bat_add, self.bat_add + self.bat_hdr.n_blk.val):
            l = list(self.find(bno * self.block_size, (bno+1) * self.block_size))
            f = self.bfree(bno)
            if f:
                nfree += 1
            else:
                nused += 1
            if f and len(l) == 0:
                FreeBlock(self, lo=bno * self.block_size, width=self.block_size).insert()
            elif not f and len(l) > 0:
                pass
            else:
                print(self.this, "? 0x%08x" % (self.block_size * bno), f, l)
                nwrong += 1
        print(self.this, "Blocks marked free:", nfree, "marked used:", nused, "wrong:", nwrong)


    def bfree(self, bno):
        ''' Is block free ? '''

        bno -= self.bat_add
        if bno < 0:
            return None

        p = self.bat_base + 4 * (bno // 32)
        w = ov.Be32(self, p).val
        m = 0x1 << (bno & 0x1f)
        return w & m != 0

#######################################################################

class PvLabelT(ov.Struct):
    '''
       Physical Volume Label
       ~~~~~~~~~~~~~~~~~~~~~
       ref: #1/p56
       ref: #2/p54

       Our images evidently use a 4kB block size, but we have no
       idea where this fact is stored, and no artifacts using a
       different block size.

       The information must be in the ``PvLabelT``, because the
       ``lv_list`` and ``alt_lv_list`` tables are in units of the
       block size.

       It is evident from our artifacts that for SR10 the `PvLabelT`
       has been extended relative to the documented SR9 format, but
       no documentation covers that.

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
            track_per_cyl_=ov.Be16,
            lv_list_=ov.Array(10, ov.Be32, vertical=True),
            alt_lv_list_=ov.Array(10, ov.Be32, vertical=True),
            phys_badspot_daddr_=ov.Be32,
            phys_diag_daddr_=ov.Be32,
            phys_sector_start_=ov.Be16,
            phys_sector_size_=ov.Be16,
            pre_comp_=ov.Be16,

            vertical=True,
        )


class ApolloDomainPhysicalVolume(ov.OctetView):

    '''
       Apollo Domain disk image
       ~~~~~~~~~~~~~~~~~~~~~~~~
    '''

    def __init__(self, this):
        if this.top not in this.parents:
            return
        if bytes(this[0x2:0x8]) != b'APOLLO':
            return

        super().__init__(this)

        this.add_type("ApolloDomainPhysicalVolume")

        pvl = PvLabelT(self, 0).insert()

        # Heuristic to guess blocksize:  Diag area is near the very end.
        self.block_size = 1024 * int((len(this) / pvl.phys_diag_daddr.val) // 1024)
        print(this, "Guessing blocksize is %d" % self.block_size)

        for lv,alt in zip(pvl.lv_list, pvl.alt_lv_list):
            if lv.val and alt.val > lv.val:
                y = ov.This(
                    self,
                    lo=lv.val * self.block_size,
                    hi=(alt.val+1) * self.block_size,
                ).insert()
                y.that.add_type("ApolloDomainLogicalVolume", block_size=self.block_size)

        this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(title="ApolloDomainPhysicalVolume", more=False)

#######################################################################

class ApolloCoff():
    def __init__(self, this):
        if this[0] == 0x01 and this[1] == 0x97:
            this.add_type("COFF", system="Apollo", cpu="68k")
        elif this[0] == 0x01 and this[1] == 0x94:
            this.add_type("COFF", system="Apollo", cpu="88k")

#######################################################################

ALL = [
    ApolloDomainPhysicalVolume,
    ApolloDomainLogicalVolume,
    ApolloCoff,
]
