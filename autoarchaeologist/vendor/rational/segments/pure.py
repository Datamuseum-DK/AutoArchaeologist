#!/usr/bin/env python3

'''
'''
    
from ....base import bitview as bv

from . import common as cm

class UX00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux00_010_n_=-32,
            ux00_020_n_=-32,
            ux00_030_n_=-32,
            ux00_040_n_=-32,
            ux00_050_n_=-32,
            ux00_060_n_=-32,
            ux00_070_n_=-32,
            ux00_080_n_=-32,
            ux00_090_n_=-32,
            vertical=True,
        )

class UX01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux01_020_n__=-64,
            more = True,
        )
        if self.ux01_020_n_.val:
            self.add_field("text", bv.Text(self.ux01_020_n_.val))
            self.txt = self.text.txt
        else:
            self.txt = None
        self.done()

class UX02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux01_007_n_=bv.Constant(64, 4),
            ux01_008_n_=-64,
            ux01_009_n_=-64,
            ux01_010_n_=UX01,
            ux01_019_n_=-64,
            ux01_020_n_=UX01,
            ux01_029_n_=-64,
            ux01_030_n_=UX01,
            ux01_039_n_=-64,
            ux01_040_n_=UX01,
            ux01_049_n_=-64,
            ux01_050_n_=UX01,
            ux01_060_n_=bv.Constant(64, 1),
            ux01_061_n_=bv.Constant(64, 1),
            ux01_062_n_=-64,
            ux01_063_n_=bv.Constant(64, 5),
            ux01_064_n_=-64,
            ux01_065_n_=bv.Constant(64, 1),
            ux01_066_n_=bv.Constant(64, 9),
            ux01_067_n_=-64,
            ux01_068_n_=bv.Constant(64, 1),
            ux01_069_n_=-64,
            ux01_070_n_=bv.Constant(64, 5),
            ux01_071_n_=bv.Constant(64, 2),
            ux01_072_n_=bv.Constant(64, 1),
            ux01_073_n_=bv.Constant(64, 5),
            ux01_074_n_=bv.Constant(64, 1),
            #ux01_075_n_=-64,
            #ux01_076_n_=-64,
            #ux01_077_n_=-64,
            #ux01_078_n_=-64,
            #ux01_079_n_=-64,
            #ux01_080_n_=-64,
            #ux01_081_n_=-64,
            #ux01_082_n_=-64,
            #vertical=True,
        )

class DiscreteComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dc_id__=UX01,
            dc_1_n_=-64,
            dc_width_=-64,
            dc_3_n_=-64,
        )

class ArrayComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ac_id__=UX01,
            ac_1_n_=-64,
            ac_totalbits_=-64,
            ac_bounds_=ArrayBoundsComponent,
            vertical=True,
        )

class NullArrayBoundsComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            nabc_id__=UX01,
            nabc_0_=-64,
            nabc_1_=-64,
        )

class ArrayBoundsComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            abc_id__=UX01,
            abc_1_n_=-64,
            abc_2_n_=-64,
            abc_3_n_=-64,
            abc_hi_=-64,
            abc_5_n_=-64,
            vertical=True,
            more=True,
        )
        heap = False
        y = UX01(bvtree, self.hi)
        if y.txt == "DISCRETE_COMPONENT":
            self.add_field("element", DiscreteComponent)
        elif y.txt == "HEAP_ACCESS_COMPONENT":
            self.add_field("element", HeapAccessComponent)
            heap = True 
        else:
            print(bvtree.this, "ARRAY", y)
            self.add_field("element", PureTxt)
        if heap:
            self.add_field("end", -64)
            self.add_field("t_heap", -64)

        #self.add_field("x", -64)
        #self.add_field("y", -64)
        #self.add_field("z", -64)
 
        self.done()

class HeapAccessComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hac_id__=UX01,
            hac_1_n_=-64,
            hac_2_n_=-64,
            hac_3_n_=-64,
        )

class ClauseComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            clc_id__=UX01,
            clc_1_n_=-64,
            clc_2_n_=-64,
            clc_3_n_=-64,
            clc_4_n_=-64,
            clc_5_=DiscreteComponent,
            clc_6_=DiscreteComponent,
            clc_7_=-64,
            clc_8_=-64,
            clc_9_=-64,
            vertical=True,
        )

def some_object(bvtree, lo):
    y = UX01(bvtree, lo)
    if y.txt is None:
        return 0, False
    if y.txt == "DISCRETE_COMPONENT":
        return DiscreteComponent, False
    if y.txt == "HEAP_ACCESS_COMPONENT":
        return HeapAccessComponent, True
    if y.txt == "RECORD_COMPONENT":
        return RecordComponent, False
    if y.txt == "DISCRIMINATED_RECORD_COMPONENT":
        return DiscriminatedRecordComponent, False
    if y.txt == "INDIRECT_FIELD_REF_COMPONENT":
        return IndirectFieldRefComponent, False
    if y.txt == "ARRAY_COMPONENT":
        return ArrayComponent, False
    if y.txt == "NULL_ARRAY_BOUNDS_COMPONENT":
        return NullArrayBoundsComponent, False
    if y.txt == "CLAUSE_COMPONENT":
        return ClauseComponent, False
    print(bvtree.this, "SOMEOBJ", y.txt)
    return None, False

class RecordComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            rc_id__=UX01,
            rc_1_n_=-64,
            rc_2_n_=-64,
            more=True,
        )
        n = 0
        heaps = []
        done = False
        while True:
            cls, isheap = some_object(bvtree, self.hi)
            if cls is None:
                break
            if cls == 0:
                done = True
                break
            self.add_field("m%03d" % n, cls)
            if isheap:
                heaps.append(n)
            n += 1

        if done:
            for i in heaps:
                self.add_field("t%03d" % i, -64)
            for i in heaps:
                self.add_field("q%03d" % i, -64)
            # self.add_field("z" % i, -64)
            

        self.done()

class IndirectFieldRefComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ifrc_id__=UX01,
            ifrc_0_=-64,
            ifrc_1_=-64,
        )

class DiscriminatedRecordComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            drc_id__=UX01,
            drc_1_n_=-64,
            drc_2_n_=-64,
            drc_3_n_=-64,
            drc_4_n_=-64,
            drc_5_n_=DiscriminatedRecordHeaderComponent,
            vertical=True,
        )

class DiscriminatedRecordHeaderComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            drhc_id__=UX01,
            drhc_1_n_=-64,
            drhc_2_n_=-64,
            drhc_3_n_=-64,
            drhc_4_n_=DiscreteComponent,
            drhc_5_n_=DiscreteComponent,
            #drhc_6_n_=DiscreteComponent,
            vertical=True,
        )

class ObjId(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            mgr_id_=-64,
            obj_id_=-64,
            mach_id_=-64,
        )

    def render(self):
        yield "<" + ",".join(
           [
               cm.obj_name(self.mgr_id.val),
               str(self.obj_id.val),
               str(self.mach_id.val),
           ]
        ) + ">"

class Property(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            prop_0_=PureTxt,
            prop_1_=-64,
        )

class UserObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            user_0_=Property,
            user_1_=Property,
            user_2_=PureTxt,
            user_3_=-64,
            user_4_=ObjId,
            user_5_=-64,
            user_6_=-64,
            user_7_=ObjId,
            user_8_=ObjId,
            ngrp_=-64,
            more=True
        )
        self.add_field("groups", bv.Array(self.ngrp.val, ObjId))
        self.add_field("nses", -64)
        self.add_field("sessions", bv.Array(self.nses.val, ObjId))
        self.done()

class GroupObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            group_0_=Property,
            group_1_=Property,
            group_2_=PureTxt,
            group_3_=-64,
            group_4_=ObjId,
            group_5_=-64,
            group_6_=-64,
        )


class SessionObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sess_0_=Property,
            sess_1_=Property,
            sess_2_=Property,
            sess_3_=ObjId,
            sess_4_=-64,
            sess_5_=-64,
            more=True
        )
        if self.sess_5.val:
            self.add_field("sess_6", ObjId)
        self.add_field("sess_7", PureTxt)
        self.add_field("sess_8", PureTxt)
        self.add_field("sess_9", PureTxt)
        self.done()

class TapeObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            tape_0_=PureTxt,
            tape_1_=ObjId,
            tape_2_=-64,
            tape_3_=-64,
            tape_4_=Property,
            tape_5_=Property,
            tape_6_=Property,
        )

class TerminalObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            term_0_=PureTxt,
            term_1_=PureTxt,
            term_2_=ObjId,
            term_3_=-64,
            term_4_=Property,
            term_5_=Property,
            term_6_=Property,
        )

class NullObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            null_0_=PureTxt,
            null_1_=ObjId,
            null_2_=-64,
            null_3_=Property,
            null_4_=Property,
            null_5_=Property,
        )

class ArchivedCodeObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            ac_0_=Property,
            ac_1_=Property,
            ac_2_=-1,
            ac_3_=PureTxt,
            ac_4_=-47,
            ac_5_=Property,
            ac_6_=ObjId,
            ac_7_=-64,
        )

class Object(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            kind_=ObjId,
            state_=UX01,
            obj_3_=-64,
            more=True,
        )
        if self.kind.mgr_id.val == 4:
            self.add_field("obj", UserObject)
        elif self.kind.mgr_id.val == 5:
            self.add_field("obj", GroupObject)
        elif self.kind.mgr_id.val == 6:
            self.add_field("obj", SessionObject)
        elif self.kind.mgr_id.val == 7:
            self.add_field("obj", TapeObject)
        elif self.kind.mgr_id.val == 8:
            self.add_field("obj", TerminalObject)
        elif self.kind.mgr_id.val == 13:
            self.add_field("obj", NullObject)
        elif self.kind.mgr_id.val == 15:
            self.add_field("obj", ArchivedCodeObject)
        self.done()

    def xrender(self):
        yield "Object {<%s,%d,%d> CONSISTENT 0x%x}" % (
            cm.obj_name(self.obj_0.val),
            self.obj_1.val,
            self.obj_2.val,
            self.obj_4.val,
        )

class PureTxt(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ux01_020_n__=-64,
            more = True,
        )
        self.add_field("text", bv.Text(self.ux01_020_n_.val))
        self.txt = self.text.txt
        self.done()

class PureHead(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ph_0_=-32,
            ph_1_=-64,
            ph_2_=-64,
            ph_3_=-64,
            ph_4_=-64,
            ph_nobj_=-64,
            ph_kind_=-64,
        )

class Pure():

    def __init__(self, tree):
        self.tree = tree

        self.pure_head = PureHead(tree, 0xa1).insert()

        self.spelunk()

        for i in self.tree.find_all(0x88581):
            print("FF", hex(i))

        for i in self.tree.find_all(0x885c1):
            print("FF", hex(i))

    def spelunk(self):
        self.sofar = 0
        while self.find_one_thing():
            continue

        for lo, hi in self.tree.gaps():
            for adr in range(lo, hi - 100):
                if self.try_text(adr):
                    y = PureTxt(self.tree, adr)
                    y.insert()

        for lo, hi in self.tree.gaps():
            if (hi - lo) & 0x3f == 0:
                bv.Array((hi - lo) // 64, -64)(self.tree, lo).insert()

    def find_one_thing(self):
        for lo, hi in self.tree.gaps():
            if hi < self.sofar:
                continue
            for adr in range(lo, hi - 100):
                if self.try_text(adr):
                    y = PureTxt(self.tree, adr)
                    if self.expand(y):
                        self.sofar = adr
                        return True
        return False

    def expand(self, txt):
        if txt.txt == "CONSISTENT":
            Object(self.tree, txt.lo - 64 * 3).insert()
            return True
        if txt.txt == "DISCRETE_COMPONENT":
            DiscreteComponent(self.tree, txt.lo).insert()
            return True
        if txt.txt == "ARRAY_COMPONENT":
            ArrayComponent(self.tree, txt.lo).insert()
            return True
        if txt.txt == "ARRAY_BOUNDS_COMPONENT":
            return False
        if txt.txt == "HEAP_ACCESS_COMPONENT":
            HeapAccessComponent(self.tree, txt.lo).insert()
            return True
        if txt.txt == "CLAUSE_COMPONENT":
            ClauseComponent(self.tree, txt.lo).insert()
            return True
        if txt.txt == "RECORD_COMPONENT":
            RecordComponent(self.tree, txt.lo).insert()
            return True
        if txt.txt == "DISCRIMINATED_RECORD_COMPONENT":
            # DiscriminatedRecordComponent(self.tree, txt.lo).insert()
            return False
        if txt.txt == "DISCRIMINATED_RECORD_HEADER_COMPONENT":
            #DiscriminatedRecordHeaderComponent(self.tree, txt.lo).insert()
            return False
        else:
            txt.insert()

    def try_text(self, adr):
        x = int(self.tree.bits[adr:adr+64], 2)
        if x < 2 or x > 1000:
            return False
        for i in range(x):
            y = int(self.tree.bits[adr+64+i*8:adr+72+i*8], 2)
            if y < 32 or y > 126:
                return False
        return True
