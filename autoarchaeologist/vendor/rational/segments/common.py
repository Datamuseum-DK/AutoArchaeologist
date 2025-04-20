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

from . import pure

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

class StdHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hd_001_n_=-32,
            hd_002_n_=-32,
            hd_003_n_=-32,
            hd_004_n_=-32,
            hd_005_n_=-32,
            hd_006_n_=-31,
            hd_007_p_=bv.Pointer(),
            hd_008_n_=-32,
            hd_009_p_=bv.Pointer(),
            hd_010_n_=-32,
            hd_011_p_=bv.Pointer(),
            hd_012_n_=-32,
        )

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

class TimedProperty(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            tp_000_b__=bv.Constant(1, 0),
            tp_002_b_=TimeStampPrecise,
            tp_003_b_=-15,
            tp_004_b_=-24,
        )

class BTree(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            bt_00_z_=-143,
            bt_08_z_=-52,
            bt_09_z_=-10,
            bt_10_p_=bv.Pointer(BTree),
            bt_11_p_=bv.Pointer(BTree),
            bt_12_p_=bv.Pointer(BTree),
            bt_13_p_=bv.Pointer(BTree),
        )

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
        self.add_field("array", bv.Array(dimension, bv.Pointer(cls, elide=elide), vertical=True))
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

class StringPointer(bv.Pointer(StringArray)):
    ''' ... '''

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
        yield retval[0] + "(»" + dst.txt + "«)"


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
        print(self.__class__.__name__, this, self)
        self.spelunk()
        if True:
            for lo, hi in self.gaps():
                print(this, "GAP", hex(lo), hex(hi), hex(hi - lo))
        # dot_graph.add_interpretation(this, self)
        self.add_interpretation(more=True)

    def add_interpretation(self, title="BitView", more=False, **kwargs):
        ''' Render via UTF-8 file '''
        with self.this.add_utf8_interpretation(title, more=more) as file:
            for line in self.render(default_width=128, **kwargs):
                file.write(line + '\n')

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

class ManagerSegment(Segment):

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

class AclEntry(bv.Struct):

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

class ObjRef(bv.Struct):
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

# See 5d3bfb73b, 00_class, 75_tag, seg_0ea8df
OBJECTS = {
    1: ("ADA", {
            2: "WORLD",
            3: "DIRECTORY",
            4: "SUBSYSTEM",
            5: "SPEC_VIEW",
            6: "LOAD_VIEW",
            8: "GENERIC_PROCEDURE",
            9: "GENERIC_FUNCTION",
            10: "GENERIC_PACKAGE",
            12: "PACKAGE_INSTANTIATION",
            13: "PACKAGE_SPEC",
            16: "PROCEDURE_INSTANTIATION",
            17: "PROCEDURE_SPEC",
            20: "FUNCTION_INSTANTIATION",
            21: "FUNCTION_SPEC",
            28: "PROCEDURE_BODY",
            29: "FUNCTION_BODY",
            31: "TASK_BODY",
            32: "PACKAGE_BODY",
            33: "UNRECOGNIZABLE",
            39: "COMPILATION_UNIT",
            56: "MAIN_PROCEDURE_SPEC",
            57: "MAIN_PROCEDURE_BODY",
            59: "MAIN_FUNCTION_BODY",
            62: "LOADED_PROCEDURE_SPEC",
            63: "LOADED_FUNCTION_SPEC",
            66: "COMBINED_VIEW",
            77: "SYSTEM_SUBSYSTEM",
        }
    ),
    2: ("DDB", {}),
    3: ("FILE", {
            0: "NIL",
            42: "TEXT",
            43: "BINARY",
            47: "SWITCH",
            46: "ACTIVITY",
            48: "SEARCH_LIST",
            49: "OBJECT_SET",
            51: "POSTSCRIPT",
            52: "SWITCH_DEFINITION",
            61: "COMPATIBILITY_DATABASE",
            70: "CMVC_DATABASE",
            71: "DOCUMENT_DATABASE",
            72: "CONFIGURATION",
            73: "VENTURE",
            74: "WORK_ORDER",
            80: "CMVC_ACCESS",
            83: "MARKUP",
            555: "BINARY_GATEWAY",
            597: "REMOTE_TEXT_GATEWAY",
        }
    ),
    4: ("USER", {}),
    5: ("GROUP", {}),
    6: ("SESSION", {}),
    7: ("TAPE", {}),
    8: ("TERMINAL", {}),
    9: ("DIRECTORY", {}),
    10: ("CONFIGURATION", {}),
    11: ("CODE_SEGMENT", {}),
    12: ("LINK", {}),
    13: ("NULL_DEVICE", {}),
    14: ("PIPE", {}),
    15: ("ARCHIVED_CODE", {}),
    16: ("PROGRAM_LIBRARY", {}),
    17: ("NATIVE_SEGMENT_MAP", {}),
}

class SegId(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            segno_n_=-22,
            vpid_n_=-10,
        )

