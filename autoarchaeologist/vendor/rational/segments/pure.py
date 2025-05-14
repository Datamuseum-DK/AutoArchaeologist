#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

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
            try:
                self.add_field("text", bv.Text(self.ux01_020_n_.val))
                self.txt = self.text.txt
            except OverflowError:
                self.txt = "***OVERFLOW***"
            except ValueError:
                self.txt = "***VALUE***"
                 
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

class Location(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            offset_=-64,
            width_=-64,
        )

    def render(self):
        yield "Location {0x%x+0x%x=0x%x}" % (self.offset.val, self.width.val, self.offset.val + self.width.val)

class DiscreteComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dc_id__=UX01,
            dc_loc_=Location,
            dc_3_n_=bv.Constant(64, 0),
        )

class FloatComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dc_id__=UX01,
            dc_loc_=Location,
            dc_3_n_=bv.Constant(64, 0),
        )

class Compound(bv.Struct):

    def compound(self):
        n = 0
        self.children =[]
        while True:
            cls, isheap = some_object(self.tree, self.hi)
            if cls is None:
                self.bad_compound = True
                return
            if cls == 0:
                break
            self.add_field("m%03d" % n, cls)
            if cls in (
                HeapAccessComponent,
                DiscreteComponent,
                DiscriminatedRecordHeaderComponent,
                DiscriminatedRecordComponent,
                ClauseComponent,
                FloatComponent,
                RecordComponent,
                ArrayComponent,
                ArrayBoundsComponent,
                NullArrayBoundsComponent,
                IndirectFieldRefComponent,
            ):
                self.children.append(n)
                if hasattr(self.fields[-1][1], "bad_compound"):
                    self.bad_compound = True
                    return
            else:
                self.bad_compound = True
                return
            n += 1

        self.add_field("eom", -64)
        for n in reversed(self.children):
            self.add_field("t%03d" % n, -64)

    def render(self):
        yield from super().render()
        if hasattr(self, "bad_compound"):
            yield "BAD_COMPOUND " + self.__class__.__name__

class ArrayComponent(Compound):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            ac_id__=UX01,
            ac_loc_=Location,
            #ac_bounds_=ArrayBoundsComponent,
            more=True,
        )
        self.compound()
        #self.add_field("z00", -64)
        self.done()

class NullArrayBoundsComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            nabc_id__=UX01,
            nabc_loc_=Location,
            nabc_f00_=-64,
            nabc_f01_=-64,
            #nabc_f02_=-64,
        )

class ArrayBoundsComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            abc_id__=UX01,
            abc_loc_=Location,
            abc_3_n_=-64,
            abc_hi_=-64,
            abc_5_n_=-64,
        )

class HeapAccessComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            hac_id__=UX01,
            hac_loc_=Location,
            hac_3_n_=bv.Constant(64, 0),
        )

class ClauseComponent(Compound):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            clc_id__=UX01,
            clc_loc_=Location,
            clc_3_n_=-64,
            clc_4_n_=-64,
            more=True,
        )
        self.compound()
        self.done()

def some_object(bvtree, lo):
    y = UX01(bvtree, lo)
    if y.txt is None:
        return 0, False
    if y.txt == "DISCRETE_COMPONENT":
        return DiscreteComponent, False
    if y.txt == "FLOAT_COMPONENT":
        return FloatComponent, False
    if y.txt == "HEAP_ACCESS_COMPONENT":
        return HeapAccessComponent, True
    if y.txt == "RECORD_COMPONENT":
        return RecordComponent, True
    if y.txt == "DISCRIMINATED_RECORD_COMPONENT":
        return DiscriminatedRecordComponent, False
    if y.txt == "DISCRIMINATED_RECORD_HEADER_COMPONENT":
        return DiscriminatedRecordHeaderComponent, False
    if y.txt == "INDIRECT_FIELD_REF_COMPONENT":
        return IndirectFieldRefComponent, False
    if y.txt == "ARRAY_BOUNDS_COMPONENT":
        return ArrayBoundsComponent, False
    if y.txt == "ARRAY_COMPONENT":
        return ArrayComponent, False
    if y.txt == "NULL_ARRAY_BOUNDS_COMPONENT":
        return NullArrayBoundsComponent, False
    if y.txt == "CLAUSE_COMPONENT":
        return ClauseComponent, False
    print(bvtree.this, "SOMEOBJ", hex(lo), y.txt)
    return None, False

class RecordComponent(Compound):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            rc_id__=UX01,
            rc_loc_=Location,
            more=True,
        )
        self.compound()
        self.done()

class IndirectFieldRefComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            ifrc_id__=UX01,
            ifrc_loc_=Location,
        )

class DiscriminatedRecordComponent(Compound):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            drc_id__=UX01,
            drc_loc_=Location,
            drc_3_n_=-64,
            drc_4_n_=-64,
            vertical=True,
            more=True,
        )
        self.compound()
        self.done()

class DiscriminatedRecordHeaderComponent(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            drhc_id__=UX01,
            drhc_loc_=Location,
            drhc_3_n_=-64,
            vertical=False,
        )

class ObjPtr(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            mgr_id_=-64,
            obj_id_=-64,
        )

    def render(self):
        yield "<" + ",".join(
           [
               cm.obj_name(self.mgr_id.val),
               str(self.obj_id.val),
               "1",
           ]
        ) + ">"

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

class AdaObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            ada_000_=Property,
            ada_001_=Property,
            ada_002_=-64,
            ada_003_=-64,
            ada_004_=-64,
            ada_005_=Property,
            ada_006_=ObjId,
            ada_007_=-64,
        )

class FileObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            file_0_=Property,
            file_1_=Property,
            file_2_=UX01,
            file_3_=-64,
            file_4_=Property,
            file_5_=ObjId,
            file_6_=-64,
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

class DirectoryChild(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dc_name_=PureTxt,
            dc_0_=DirNo,
        )

class DirectoryVersion(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            dc_ver_=-64,
            dc_no_=DirNo,
        )

class AdaExtra(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            ae_0_=PureTxt,
            ae_1_=PureTxt,
            ae_2_=-40,
            ae_3_=-24,
            ae_4_=-1,
        )

class DirNo(bv.Number):
    fmt = "%d"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, width=64)

class DirectoryObject(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            dir_dir_no_=DirNo,
            dir_1_=PureTxt,
            dir_nver_=-64,
            more=True,
        )
        self.add_field(
            "versions",
            bv.Array(self.dir_nver.val, DirectoryVersion, vertical=True),
        )

        self.add_field("dir_nchild", -64)
        if self.dir_nchild.val > 0:
            self.add_field(
                "children",
                bv.Array(self.dir_nchild.val, DirectoryChild, vertical=True),
            )

        self.add_field("def_ver", DirNo)
        self.add_field("parent", DirNo)
        self.add_field("cls", -64)
        self.add_field("subcls", -64)
        self.add_field("vpid", -64)
        self.add_field("ctrlpt", DirNo)
        self.add_field("tail0", -64)
        self.add_field("tail1", -64)
        self.add_field("tail2", -64)
        self.add_field("tail3", -32)
        self.add_field("tail4", -32)
        if self.tail3.val in (0x50000000, 0xf0000000):
            self.add_field("tail5", -4)
        if self.cls.val == 1 and self.subcls.val in (2, 4, 6, 66):
            self.add_field("ada", AdaExtra)
        self.done()


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
        if self.kind.mgr_id.val == 1:
            self.add_field("obj", AdaObject)
        elif self.kind.mgr_id.val == 3:
            self.add_field("obj", FileObject)
        elif self.kind.mgr_id.val == 4:
            self.add_field("obj", UserObject)
        elif self.kind.mgr_id.val == 5:
            self.add_field("obj", GroupObject)
        elif self.kind.mgr_id.val == 6:
            self.add_field("obj", SessionObject)
        elif self.kind.mgr_id.val == 7:
            self.add_field("obj", TapeObject)
        elif self.kind.mgr_id.val == 8:
            self.add_field("obj", TerminalObject)
        elif self.kind.mgr_id.val == 9:
            self.add_field("obj", DirectoryObject)
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
            vertical=False,
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

        self.recent = 0
        try:
            self.spelunk()
        except Exception as err:
            print(tree.this, "BOOM", hex(self.recent), err)
            raise
        self.find_texts()

    def spelunk(self):
        enough = 10000000
        self.sofar = 0
        while self.find_one_thing():
            enough -= 1
            if enough == 0:
                return
        for lo, hi in self.tree.gaps():
            if (hi - lo) & 0x3f == 0:
                bv.Array((hi-lo)//64, -64, vertical=True)(self.tree, lo).insert()

    def find_texts(self):
        enough = 1000000
        for lo, hi in self.tree.gaps():
            for adr in range(lo, hi - 100):
                if self.try_text(adr):
                    y = PureTxt(self.tree, adr)
                    y.insert()
                    enough -= 1
                    if enough == 0:
                        return

        for lo, hi in self.tree.gaps():
            if (hi - lo) & 0x3f == 0:
                bv.Array((hi - lo) // 64, -64)(self.tree, lo).insert()

    def find_one_thing(self):
        for lo, hi in self.tree.gaps():
            if hi < self.sofar:
                continue
            for adr in range(max(lo, self.sofar), hi - 100):
                if self.try_text(adr):
                    self.recent = adr
                    y = PureTxt(self.tree, adr)
                    if self.expand(y):
                        self.sofar = adr + 1
                        return True
        return False

    def expand(self, txt):
        if txt.txt == "CONSISTENT":
            try:
                Object(self.tree, txt.lo - 64 * 3).insert()
            except Exception as err:
                print(self.tree.this, "OBJECT BOOM", hex(txt.lo - 64 * 3), err)
                txt.insert()
            return True
        if txt.txt == "DISCRETE_COMPONENT":
            DiscreteComponent(self.tree, txt.lo).insert()
            return True
        if txt.txt == "FLOAT_COMPONENT":
            FloatComponent(self.tree, txt.lo).insert()
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
            DiscriminatedRecordComponent(self.tree, txt.lo).insert()
            return True
        if txt.txt == "DISCRIMINATED_RECORD_HEADER_COMPONENT":
            DiscriminatedRecordHeaderComponent(self.tree, txt.lo).insert()
            return True
        else:
            return False

    def try_text(self, adr):
        x = int(self.tree.bits[adr:adr+64], 2)
        if x < 2 or x > 1000:
            return False
        for i in range(x):
            y = int(self.tree.bits[adr+64+i*8:adr+72+i*8], 2)
            if y < 32 or y > 126:
                return False
        return True
