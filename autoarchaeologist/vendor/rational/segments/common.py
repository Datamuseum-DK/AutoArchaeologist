#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Segments - common stuff
   =========================================
'''

import time

from ....base import bitview as bv
from ....base import dot_graph
from .. import r1k_defs 
from . import pure

OBJECTS = r1k_defs.OBJECT_MANAGERS

class Unallocated(bv.Opaque):
    ''' ... '''

class SegHeap(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            first_free_=-32,
            max_=-32,
            zero_=-32,
            allocated_=-32,
        )

        lo = self.hi + self.first_free.val - 1
        hi = self.allocated.val
        if lo < bvtree.hi and hi < bvtree.hi and lo < hi:
            self.unalloc = Unallocated(
                bvtree,
                lo = lo,
                hi = hi + 1,
            )
            self.unalloc.insert()

class SegHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            sh_flg_=-1,
            sh_seg_=-22,
            sh_vpid_=-10,
        )

class MgrHead(bv.Struct):
    '''
       Based on ⟦31d12fb28⟧ group.pure description

       NB:
       We assume that a 0x40 wide HeapAccessComponent means
       that there are two pointers, but this is unconfirmed
       because so far we have never seen mgr_003 point to anything
    '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            mgr_001_n_=-31,
            mgr_002_n_=bv.Array(2, -32),
            mgr_003_p_=bv.Array(2, bv.Pointer),
       )

class FarPointer(bv.Struct):
    ''' ... '''

    def __init__(self, bvtree, lo, target=None):
        super().__init__(
            bvtree,
            lo,
            more=True,
        )
        y = bv.Number(bvtree, lo + 32, width=32)
        if y.val == 0:
            self.add_field("dst", bv.Pointer.to(target))
            self.add_field("off_", -32)
        else:
            self.add_field("seg", -22),
            self.add_field("world", -10),
            self.add_field("off", -32),
        self.done()

    @classmethod
    def to(cls, target):
        return (cls, {"target": target})

class TimeStamp(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            day_=-16,
            sec_=-16,
        )
        self.ts = (self.day.val - (69 * 365 + 18)) * 86400 + self.sec.val * 2
        gm = time.gmtime(self.ts)
        self.tstamp = time.strftime("%Y%m%d_%H%M%S", gm)

    def render(self):
        yield self.tstamp

class TimeStampPrecise(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            day_=-16,
            sec_=-17,
        )
        self.ts = (self.day.val - (69 * 365 + 18)) * 86400 + self.sec.val
        gm = time.gmtime(self.ts)
        self.tstamp = time.strftime("%Y%m%d_%H%M%S", gm)

    def render(self):
        yield self.tstamp

class Day(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            day_=-17,
        )
        self.ts = (self.day.val - (69 * 365 + 18)) * 86400
        gm = time.gmtime(self.ts)
        self.tstamp = time.strftime("%Y-%m-%d", gm)

    def render(self):
        yield self.tstamp

class Time(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            time_=-32,
        )
        tmp = self.time.val >> 15
        h = tmp // 3600
        m = (tmp // 60) % 60
        s = tmp % 60
        frac = tmp & 0x7fff
        self.tstamp = "%02d:%02d:%02d.0x%04x" % (h, m, s, self.time.val & 0x7fff)

    def render(self):
        yield self.tstamp

class DayTime(bv.Struct):
    '''
       Based on ⟦31d12fb28⟧ group.pure description
    '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            day_=Day,
            time_=Time,
        )

class TimedProperty(bv.Struct):
    '''
       Based on ⟦31d12fb28⟧ group.pure description
    '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            tp_000_b_=DayTime,
            tp_001_b_=-24,
        )

    def render(self):
        yield "Timed_Property {" + ", ".join(
            (
                 self.tp_000_b.day.tstamp,
                 self.tp_000_b.time.tstamp,
                 hex(self.tp_001_b.val),
            )
        ) + "}"

class BTree(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            bt_k0_n_=-9,
            bt_00_z_=-4,
            bt_07_z_=-32,
            bt_08_z_=-32,
            more=True,
        )

        # This variant structure is based on the "data dictionary" in
        # the ".pure" GROUP segment.  All inspected ".pure" segments
        # had the same layout.
        if self.bt_k0_n.val == 0x1:
            self.add_field("bt_a0_z", -64)
            self.add_field("bt_a1_z", -64)
        elif self.bt_k0_n.val == 0x2:
            self.add_field("bt_b0_z", -8)
            self.add_field("bt_b1_z", -8)
            self.add_field("bt_b9_z", bv.Constant(112, 0))
        elif self.bt_k0_n.val == 0x3:
            self.add_field("bt_c0_z", -1)
            self.add_field("bt_c1_z", -8)
            self.add_field("bt_c9_z", bv.Constant(119, 0))
        else:
            self.add_field("bt_d9_z", bv.Constant(128, 0))

        self.add_field("bt_10_p", bv.Pointer.to(BTree))
        self.add_field("bt_11_p", bv.Pointer.to(BTree))
        self.add_field("bt_12_p", bv.Pointer.to(BTree))
        self.add_field("bt_13_p", bv.Pointer.to(BTree))
        self.done()

class PointerArray(bv.Struct):

    def __init__(self, bvtree, lo, cls=None, dimension=None, elide=None):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            more = True,
        )
        self.elide = elide
        if dimension is None:
            self.add_field("pa_min", -32)
            self.add_field("pa_max", -32)
            assert self.pa_min.val == 0
            dimension = self.pa_max.val
        self.add_field(
            "array",
            bv.Array(
                dimension,
                bv.Pointer.args(target=cls, elide=elide),
                vertical=True
            )
        )
        self.done()

    def __iter__(self):
        yield from self.array

    def __getitem__(self, idx):
        return self.array[idx]

class StringArray(bv.Struct):
    ''' String on Array format'''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            sa_min_=-32,
            sa_max_=-32,
            more = True,
        )
        if self.sa_min.val != 1:
            print("SA_MIN", self.sa_min.val)
        assert self.sa_min.val == 1
        self.add_field("text", bv.Text(self.sa_max.val))
        self.txt = self.text.txt
        self.done()

    def iter_glyphs(self):
        yield from self.text.iter_glyphs()

    def render(self):
        yield 'StringArray {»' + self.txt + '«}'

    def dot_node(self, dot):
        return "»" + self.txt + '«', ["shape=plaintext"]

class StringPointer(bv.Pointer):
    ''' ... '''

    TARGET = StringArray

    def text(self):
        if self.val:
            dst = self.dst()
            return '»' + dst.txt + '«'
        return ""

    def dot_node(self, dot):
        return "→ %s" % self.text(), ["shape=plaintext"]

    def render(self):
        if not self.val:
            yield from super().render()
            return
        dst = self.dst()
        retval = list(super().render())
        if dst:
            yield retval[0] + "(»" + dst.txt + "«)"
        else:
            yield retval[0] + "(»…«)"


class Segment(bv.BitView):

    TAG = None
    VPID = None
    POINTER_WIDTH = 32

    def __init__(self, this):
        if self.TAG is not None and not this.has_note("tag_%02x" % self.TAG):
            return
        if self.VPID is not None and not this.has_note("vpid_%04d" % self.VPID):
            return
        print(this, "SEG", self.VPID, "%x" % self.TAG)
        super().__init__(bits = this.bits())
        self.this = this
        self.type_case = this.type_case
        print(this, self.__class__.__name__, self)
        self.spelunk()
        if False:
            for lo, hi in self.gaps():
                print(this, "GAP", hex(lo), hex(hi), hex(hi - lo))
        # dot_graph.add_interpretation(this, self)
        self.add_interpretation(more=True)

    def find_all(self, match, start=0, stop=None, width=32):
        b = self.bits
        if stop is None:
            stop = len(b)
        match=bin((1<<width)|match)[3:]
        while start < stop:
            start = b.find(match, start, stop)
            if start == -1:
                return
            yield start
            start += 1

    def pointers_internal(self, lo, hi):
        print("PINT", hex(lo), hex(hi))
        for adr in range(lo, hi - 32):
            p = int(self.bits[adr:adr+32], 2)
            if p < lo or p > hi:
                continue
            for hit in self.find(p):
                if hit.lo != p:
                    continue
                print(
                    hex(lo),
                    "+", hex(adr - lo),
                    "->",
                    hex(hit.lo),
                    hit.__class__.__name__,
                )
    def pointers_inside(self, lo, hi):
        print("POUT", hex(lo), hex(hi))
        for adr in range(lo, hi - 32):
            p = int(self.bits[adr:adr+32], 2)
            if p < 0x1000:
                continue
            for hit in self.find(p):
                if hit.lo != p:
                    continue
                print(
                    hex(lo),
                    "+", hex(adr - lo),
                    "->",
                    hex(hit.lo),
                    hit.__class__.__name__,
                )

    def pointers_into(self, lo, hi):
        print("PINTO", hex(lo), hex(hi))
        for adr in range(lo, hi):
            for hit in self.find_all(adr):
                w = list(self.find(hit))
                if not w:
                    print(
                        hex(lo),
                        "+",
                        hex(adr-lo),
                        "<-",
                        hex(hit),
                        "= .+",
                        hex(hit-lo),
                    )
                else:
                    for x in w:
                        print(
                            hex(lo),
                            "+",
                            hex(adr-lo),
                            "<-",
                            hex(hit),
                            x.__class__.__name__,
                            hex(hit - x.lo)
                        )

    def spelunk(self):
        ''' discover things '''
        assert None

class ManagerSegment(Segment):
    ''' Stuff common to manager segments '''

    def spelunk(self):

        self.this.add_note(self.TOPIC + "-State")
        self.seg_heap = SegHeap(self, 0).insert()
        self.seg_head = SegHead(self, self.seg_heap.hi).insert()
        if self.seg_head.sh_flg.val:
            try:
                self.spelunk_manager()
            except Exception as err:
                print(self.this, self.__class__.__name__, "BOOM", err)
                #raise
        else:
            pure.Pure(self)
            self.this.add_note("Pure")

    def spelunk_manager(self):
        ''' discover things '''
        assert None

class IndirectFieldRefComponent(bv.Struct):
    ''' ... '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            offset_=-32,
            width_=-32,
        )

class AclEntry(bv.Struct):
    ''' ... '''

    # Not quite a bitmap...
    modes = {
        0x1: "R",
        0x3: "RW",
        0x5: "RC",
        0x6: "CD",
        0xd: "RCO",
        0xf: "RCOD",
    }

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            subj_=-10,
            mode_=-4,
        )

class Acl(bv.Struct):
    ''' ... '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a_=bv.Array(7, AclEntry),
        )

class ObjName(bv.Struct):
    ''' ... '''
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            oclass_=-32,
            onumber_=-32,
        )

    def render(self):
        c = OBJECTS.get(self.oclass.val)
        if not c:
            yield "<0x%x,%d>" % (self.oclass.val, self.onumber.val)
        else:
            yield "<%s,%d>" % (c[0], self.onumber.val)

class ObjRef(bv.Struct):
    '''
       Based on ⟦31d12fb28⟧ group.pure description

       According to the group.pure description, this is
       a variant structure. probably on the "flg" field
       which could then act as a "valid" flag.
    '''

    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u04_flg_=-1,
            u04_mgr_=-31,
            u04_obj_=-31,
            u04_mach_=bv.Constant(32, 1),
            **kwargs,
        )

    def render(self):
        yield "%d:<" % self.u04_flg.val + ",".join(
           [
               obj_name(self.u04_mgr.val),
               str(self.u04_obj.val),
               str(self.u04_mach.val),
           ]
        ) + ">"

def obj_name(cls, subclass=None):
    i = OBJECTS.get(cls)
    if i is None:
        cln = "%d" % cls
        scl = {}
    else:
        cln, scl = i
    if subclass is None:
        return cln
    scn = scl.get(subclass)
    if scn is None:
        scn = "%d" % subclass
    return cln + "." + scn

class SegId(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            segno_n_=-22,
            vpid_n_=-10,
        )
