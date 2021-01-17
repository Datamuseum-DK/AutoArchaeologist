'''
   R1000 '97' segments
   ===================

   Diana-trees, at least that's the current working theory.

'''

import autoarchaeologist.rational.r1k_bittools as bittools

def what_is(self, attr):
    ''' Report if self.attr points to know chunks '''
    a = getattr(self, attr)
    if not a:
        return
    p = self.seg.starts.get(a)
    if not p:
        return
    self.seg.dot.edge(self.chunk, p)
    if p.owner:
        print("IS 0x%06x" % a, self, attr, p.owner)

#######################################################################
# Diana Tree

DIANA_COMPACT=True

class Dummy(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        p = seg.mkcut(address)
        t = int(p[:17], 2)
        c = seg.cut(address, 1)
        super().__init__(seg, c, title="Dummy_0x%x" % t)
        self.compact = True
        seg.dot.node(self, "shape=ellipse,fillcolor=red,style=filled")

class DianaNPtr(bittools.R1kSegBase):
    def __init__(self, seg, address, nptrs, basename=None):
        if basename is None:
             basename = self.__class__.__name__
        c = seg.cut(address, -1)
        super().__init__(seg, c)
        self.compact = DIANA_COMPACT
        self.get_fields(
            (basename + "_type", 17),
        )
        for i in range(nptrs):
            self.get_fields(
                (basename + "_%d_p" % (i+1), 26),
            )
        self.nptrs = nptrs
        self.basename = basename

    def explore(self):
        self.truncate()
        for i in range(self.nptrs):
            bittools.make_one(
                self,
                self.basename + '_%d_p' % (i+1),
                bittools.R1kSegBase, someclass
            )

class Diana_100ab(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_10100(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_10135(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_1017b(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_10183(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_10210(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_1025c(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_1025d(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_1037a(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_10402(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_10437(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_1043c(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_1043e(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_10440(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_10447(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_1044d(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_1044f(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_10450(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_1047c(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_1049f(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_104a1(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_10630(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_10638(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_10639(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_1063b(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_1063d(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_10641(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_10648(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_1064e(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_1065b(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_10760(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_1088a(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_10890(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_10893(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_10899(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_10945(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_10980(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 0)
        self.explore()

class Diana_10984(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.get_fields(
            ("Diana_10984_3_p", 26),
        )
        self.explore()
        bittools.make_one(self, "Diana_10984_3_p", DianaChain)

class Diana_10985(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_10989(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.get_fields(
            ("Diana_10989_3_p", 26),
        )
        self.explore()
        bittools.make_one(self, "Diana_10989_3_p", DianaChain)

class Diana_10956(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.get_fields(
            ("Diana_10956_3_p", 26),
        )
        self.explore()
        bittools.make_one(self, "Diana_10956_3_p", DianaChain)

class Diana_10995(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_10997(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.get_fields(
            ("Diana_10977_3_p", 26),
        )
        self.explore()
        bittools.make_one(self, "Diana_10977_3_p", DianaChain)

class Diana_10c8c(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.get_fields(
            ("Diana_10c8c_3_p", 26),
        )
        self.explore()
        bittools.make_one(self, "Diana_10c8c_3_p", DianaChain)

class Diana_10c8f(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_10c91(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.get_fields(
            ("Diana_10c91_3_p", 26),
        )
        self.explore()
        bittools.make_one(self, "Diana_10c91_3_p", DianaChain)

class Diana_10c94(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.get_fields(
            ("Diana_10c94_3_p", 26),
        )
        self.explore()
        bittools.make_one(self, "Diana_10c94_3_p", DianaChain)

class Diana_10f05(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 4)
        self.explore()

class Diana_112a8(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_11666(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_11821(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_11829(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_1182c(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_11a7d(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_11a7e(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_11a7f(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_11d8d(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 3)
        self.explore()

class Diana_12010(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_12122(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_12436(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_1282a(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_1282d(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_12a4a(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_12f09(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_13312(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 5)
        self.explore()

class Diana_13677(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_1382f(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 2)
        self.explore()

class Diana_13a16(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_13b17(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_13eab(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

class Diana_13f5a(DianaNPtr):
    def __init__(self, seg, address):
        super().__init__(seg, address, 1)
        self.explore()

diana_types = {
    0x100ab: Diana_100ab,
    0x10100: Diana_10100,
    0x10135: Diana_10135,
    0x1017b: Diana_1017b,
    0x10183: Diana_10183,
    0x10210: Diana_10210,
    0x1025c: Diana_1025c,
    0x1025d: Diana_1025d,
    0x1037a: Diana_1037a,
    0x10402: Diana_10402,
    0x10437: Diana_10437,
    0x1043c: Diana_1043c,
    0x1043e: Diana_1043e,
    0x10440: Diana_10440,
    0x10447: Diana_10447,
    0x1044d: Diana_1044d,
    0x1044f: Diana_1044f,
    0x10450: Diana_10450,
    0x1047c: Diana_1047c,
    0x1049f: Diana_1049f,
    0x104a1: Diana_104a1,
    0x10630: Diana_10630,
    0x10638: Diana_10638,
    0x10639: Diana_10639,
    0x1063b: Diana_1063b,
    0x1063d: Diana_1063d,
    0x10641: Diana_10641,
    0x10648: Diana_10648,
    0x1064e: Diana_1064e,
    0x1065b: Diana_1065b,
    0x10760: Diana_10760,
    0x1088a: Diana_1088a,
    0x10890: Diana_10890,
    0x10893: Diana_10893,
    0x10899: Diana_10899,
    0x10945: Diana_10945,
    0x10956: Diana_10956,
    0x10980: Diana_10980,
    0x10984: Diana_10984,
    0x10985: Diana_10985,
    0x10989: Diana_10989,
    0x10995: Diana_10995,
    0x10997: Diana_10997,
    0x10c8c: Diana_10c8c,
    0x10c8f: Diana_10c8f,
    0x10c91: Diana_10c91,
    0x10c94: Diana_10c94,
    0x10f05: Diana_10f05,
    0x112a8: Diana_112a8,
    0x11666: Diana_11666,
    0x11821: Diana_11821,
    0x11829: Diana_11829,
    0x1182c: Diana_1182c,
    0x11a7d: Diana_11a7d,
    0x11a7e: Diana_11a7e,
    0x11a7f: Diana_11a7f,
    0x11d8d: Diana_11d8d,
    0x12010: Diana_12010,
    0x12122: Diana_12122,
    0x12436: Diana_12436,
    0x1282a: Diana_1282a,
    0x1282d: Diana_1282d,
    0x12a4a: Diana_12a4a,
    0x12f09: Diana_12f09,
    0x13312: Diana_13312,
    0x13677: Diana_13677,
    0x1382f: Diana_1382f,
    0x13a16: Diana_13a16,
    0x13b17: Diana_13b17,
    0x13eab: Diana_13eab,
    0x13f5a: Diana_13f5a,
}

def someclass(seg, address):
    p = seg.mkcut(address)
    typ = int(p[:17], 2)
    t = diana_types.get(typ)
    if not t:
        print(seg.this, "Dummy for 0x%x" % typ, " at 0x%x" % address)
        t = Dummy
    return t(seg, address)

class DianaChain(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        c = seg.cut(address, -1)
        super().__init__(seg, c)
        self.compact = DIANA_COMPACT
        self.get_fields(
            ("diana04_type", 1),
            ("diana04_next_p", 26),
        )
        if self.diana04_type == 1:
            self.get_fields(
                ("diana04_2_p", 26),
            )
            self.truncate()
            bittools.make_one(self, 'diana04_2_p', bittools.R1kSegBase, someclass)
        else:
            self.truncate()
            bittools.make_one(self, 'end', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'diana04_next_p', DianaChain)

#######################################################################
# D1xx is header variant 1

class D100(bittools.R1kSegBase):
    ''' This might be a hashtable '''
    def __init__(self, seg, address):
        c = seg.cut(address, 64)
        super().__init__(seg, c)
        #self.compact = True
        self.get_fields(
            ("d100_0", 32),
            ("d100_a101", 32),
        )
        bittools.make_one(self, 'd100_a101', D101)

class D101(bittools.BitPointerArray):
    ''' ... '''
    def __init__(self, seg, address):
        super().__init__(seg, address, count=0x67, target=D102)

class D102(bittools.R1kSegBase):
    '''
       What D100 hashes.
       Possibly references to other segments.
       (d102_1 = seg#, d102_2 = vol# ?)
    '''
    def __init__(self, seg, address):
        c = seg.cut(address, 71)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d102_0", 9),
            ("d102_1", 26),
            ("d102_2", 5),
            ("d102_d102", 32),
        )
        bittools.make_one(self, 'd102_d102', D102)

#######################################################################
# D3xx is header variant 1

class D300(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        c = seg.cut(address, 192)
        super().__init__(seg, c)
        #self.compact = True
        self.get_fields(
            ("d300_0", 32),
            ("d300_1", 32),
            ("d300_2", 32),
            ("d300_d305", 32),
            ("d300_4", 32),
            ("d300_d301", 32),
        )
        bittools.make_one(
            self,
            'd300_1',
            bittools.BitPointerArray, count=(self.d300_d305 - self.d300_1)>>5
        )
        bittools.make_one(self, 'd300_d305', D305)
        bittools.make_one(self, 'd300_d301', D301)

class D301(bittools.BitPointerArray):
    ''' ... '''
    def __init__(self, seg, address):
        super().__init__(seg, address, count=0x67, target=D302)

class D302(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        c = seg.cut(address, 160)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d302_0", 32),
            ("d302_d302", 32),
            ("d302_d303", 32),
            ("d302_3", 32),
            ("d302_4", 32),
        )
        bittools.make_one(self, 'd302_d302', D302)
        bittools.make_one(self, 'd302_d303', D303)
        bittools.make_one(self, 'end', bittools.ArrayString)

class D303(bittools.R1kSegBase):
    ''' ...  '''
    def __init__(self, seg, address):
        c = seg.cut(address, 160)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d303_0", 37),
            ("d303_1", 32),
            ("d303_2", 15),
            ("d303_3", 76),
        )
        bittools.make_one(self, 'd303_1', D304)

class D304(bittools.R1kSegBase):
    ''' ...  '''
    def __init__(self, seg, address):
        c = seg.cut(address, 52)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d304_0", 52),
        )

class D305(bittools.BitPointerArray):
    ''' ... '''
    def __init__(self, seg, address):
        super().__init__(seg, address, count=0x67, target=D306)

class D306(bittools.R1kSegBase):
    '''
       Extended version of D102 ?
    '''
    def __init__(self, seg, address):
        c = seg.cut(address, 131)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d306_d303", 32),
            ("d306_1", 32),
            ("d306_2", 3),
            ("d306_d307", 32),
            ("d306_d308", 32),
        )
        bittools.make_one(self, 'd306_d303', D303)
        bittools.make_one(self, 'd306_d307', D307)
        bittools.make_one(self, 'd306_d308', D308)

class D307(bittools.R1kSegBase):
    ''' ...  '''
    def __init__(self, seg, address):
        c = seg.cut(address, 127)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d307_0", 7),
            ("d307_1", 25),
            ("d307_2", 32),
            ("d307_3", 32),
            ("d307_d307", 31),
        )
        bittools.make_one(self, 'd307_d307', D307)

class D308(bittools.R1kSegBase):
    ''' ...  '''
    def __init__(self, seg, address):
        c = seg.cut(address, 131)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d308_d303", 32),
            ("d308_1", 3),
            ("d308_2", 32),
            ("d308_d307", 32),
            ("d308_d308", 32),
        )
        bittools.make_one(self, 'd308_d303', D303)
        bittools.make_one(self, 'd308_d307', D307)
        bittools.make_one(self, 'd308_d308', D308)

#######################################################################

class Thing13(bittools.R1kSegBase):
    ''' Something #13 '''
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0x83)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        self.get_fields(
            ("t13_0", 32),
            ("t13_1", 32),
            ("t13_3",  3),
            ("t13_4", 32),
            ("t13_5", 32),
        )
        bittools.make_one(self, "t13_0", Thing9)
        bittools.make_one(self, "t13_4", Thing12)
        bittools.make_one(self, "t13_5", Thing7)

class Thing12(bittools.R1kSegBase):
    ''' Something #12 '''
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0x7f)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        self.get_fields(
            ("t12_n", -1),
        )

class Thing10(bittools.R1kSegBase):
    ''' Something #10 '''
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0x34)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        self.get_fields(
            ("t10_n", -1),
        )

class Thing9(bittools.R1kSegBase):
    ''' Something #9 '''
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0xa0)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        self.get_fields(
            ("t9_0", 37),
            ("t9_1", 32),
            ("t9_2", 15),
            ("t9_3", 77),
        )
        bittools.make_one(self, "t9_1", Thing10)

class Thing8(bittools.R1kSegBase):
    ''' Something #8 '''
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        i = int(p[0xc0:0xe0], 2)
        c = seg.cut(address, 0xe0 + i * 8)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("t8_0", 32),
            ("t8_1", 32),
            ("t8_2", 32),
            ("t8_3", 32),
            ("t8_4", 32),
            ("t8_5", 32),
            ("t8_6", 32),
        )
        _i, self.text = bittools.to_text(seg, self.chunk, offset, self.t8_6)
        bittools.make_one(self, "t8_1", Thing8)
        bittools.make_one(self, "t8_2", Thing9)

class Thing7(bittools.R1kSegBase):
    ''' Something #7 '''
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0x83)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        self.get_fields(
            ("t7_0", 32),
            ("t7_1", 32),
            ("t7_2", 3),
            ("t7_3", 32),
            ("t7_4", 32),
        )
        bittools.make_one(self, "t7_0", Thing9)
        bittools.make_one(self, "t7_3", Thing12)
        bittools.make_one(self, "t7_4", Thing7)

class Thing6(bittools.R1kSegBase):
    ''' Something #6 '''
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        c = seg.cut(address, 0x20 * 103)
        super().__init__(seg, c, **kwargs)
        # self.compact = True
        for n, i in enumerate(range(0, len(self.chunk), 0x20)):
            self.fields.append(
                (i, 32, "t6_%d" % n, int(self.chunk[i:i+0x20], 2))
            )
            setattr(self, self.fields[-1][2], self.fields[-1][3])

        for offset, width, name, val in self.fields:
            if val and 0:
                print("T6", self, offset, width, name, "0x%x" % val)
                p = seg.mkcut(val)
                if p[0] == '0':
                    bittools.make_one(self, name, Thing7)
                else:
                    bittools.make_one(self, name, Thing8)


class Thing5(bittools.R1kSegBase):
    ''' Something #5 '''
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("THING5_97")
        p = seg.mkcut(address)
        n = int(p[32:64], 2)
        if n <= address:
            print("T5?", seg.this, "N 0x%x" % n, "Address 0x%x" % address)
            return
        assert n >= address
        c = seg.cut(address, min(n - address, 0x80))
        super().__init__(seg, c, **kwargs)
        # self.compact = True
        for n, i in enumerate(range(0, len(self.chunk), 0x20)):
            self.fields.append(
                (i, 32, "t5_%d" % n, int(self.chunk[i:i+0x20], 2))
            )
            setattr(self, self.fields[-1][2], self.fields[-1][3])

        for _offset, _width, name, val in self.fields[2:]:
            if val:
                bittools.make_one(self, name, Thing6)

class Thing4(bittools.R1kSegBase):
    ''' Something #4 '''
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        y = int(p[32:64], 2)
        c = seg.cut(address, 0x40 + y * 38)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("x", 32),
            ("y", 32),
        )
        self.a = []
        for i in range(offset, len(c), 38):
            j = int(c[i:i+38], 2)
            self.a.append((j >> 15, j & 0x7fff))
            if not j & 0x7fff:
                break

    def render(self, _chunk, fo):
        ''' ... '''
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")
        for n, i in enumerate(self.a):
            if i:
                fo.write("  [0x%x] = 0x%x, 0x%x\n" % (n, i[0], i[1]))


class Thing3(bittools.R1kSegBase):
    ''' Something #3 '''
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        y = int(p[32:64], 2)
        # y = 0
        c = seg.cut(address, 0x40 + y * 8)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        offset = self.get_fields(
            ("x", 32),
            ("y", 32),
        )
        self.pad = (14 - (self.begin + offset) % 8) % 8
        offset += self.pad
        self.a = []
        while offset < len(self.chunk) - 24:
            i = int(self.chunk.bits[offset:offset+16], 2)
            j = int(self.chunk.bits[offset+16:offset+24], 2)
            if i == 0 or j == 0 or i > 0x100 or offset + 24 + j * 8 > len(self.chunk):
                break
            try:
                text = bittools.to_text(seg, self.chunk, offset + 24, j)
            except bittools.NotText:
                break
            offset += 24 + 8 * j
            self.a.append((offset, i, j, text))
        self.tail = offset

    def render(self, _chunk, fo):
        ''' ... '''
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")
        for n, i in enumerate(self.a):
            fo.write("    [0x%x] = " % n + str(i) + "\n")

class Thing2(bittools.R1kSegBase):
    '''
        Simple, Singled list elements, one `next` pointer
        and one `payload` pointer
    '''
    def __init__(self, seg, address, payload_handler, **kwargs):
        super().__init__(seg, seg.cut(address, 0x40), **kwargs)
        self.compact = True
        self.get_fields(
            ("payload", 32),
            ("next", 32),
        )
        if self.payload:
            #payload_handler(seg, self.payload)
            bittools.make_one(self, "payload", payload_handler)

class Thing1(bittools.R1kSegBase):
    '''
        The `THING1` structure is pointed to from 0xdf,
        and contains the heads & tails of two linked lists.

        Chain1 contains 38 bit wide Arrays of unidentified content.

        Chain2 contains symbol-table-like chunks.
    '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, 0x10c), **kwargs)
        self.get_fields(
            ("t1_unknown0", 0x20),
            ("t1_unknown1", 0x4c),
            ("t1_c1_head", 0x20),
            ("t1_c2_last", 0x20),
            ("t1_array1", 0x20),
            ("t1_c2_tail", 0x20),
            ("t1_c1_tail", 0x20),
        )

        i = self.t1_c1_tail
        prev = self
        while i:
            follow = Thing2(seg, i, payload_handler=Thing4, ident="Chain1")
            seg.dot.edge(prev.chunk, follow.chunk)
            i = follow.next
            prev = follow

        i = self.t1_c2_tail
        prev = self
        while i:
            follow = Thing2(seg, i, payload_handler=Thing3, ident="Chain2")
            seg.dot.edge(prev.chunk, follow.chunk)
            i = follow.next
            prev = follow

        if self.t1_c2_last:
            bittools.make_one(self, "t1_c2_last", Thing3)

        if self.t1_array1:
            bittools.make_one(self, "t1_array1", Thing4)

class Head(bittools.R1kSegBase):
    '''
        The start of the segment

    '''
    def __init__(self, seg, address, extra=0, **kwargs):
        super().__init__(seg, seg.cut(address, 0x1e0 + extra), **kwargs)
        #self.compact = True
        self.get_fields(
            ("head_z_000", 32,),           # 0x80000001
            ("head_unknown_020", 32,),     # Unique except for two cases
            ("head_c_040", 31,),           # 0x1
            ("head_chains", 32,),          # 0x231a, one case 0x0
            ("head_z_07f", 1,),            # 0x0
            ("head_z_80", 31,),            # 0x0
            ("head_stuff1", 32,),          # bit-address
            ("head_c_bf", 33,),            # 0x12, one case 0x0
            ("head_unknown_e0", 32,),      # looks like addres, most invalid
            ("head_c_100", 32,),           # 0x4
            ("head_z_120", 32,),           # 0
            ("head_z_140", 32,),           # 0
            ("head_z_160", 32,),           # 0
            ("head_z_180", 32,),           # 0
            ("head_z_1a0", 32,),           # 0
            ("head_z_1c0", 32,),           # 0
        )

        bittools.make_one(self, "head_chains", Thing1)
        # make_one(self, "head_trees", Thing5)

class HeadVar1(Head):
    ''' First variant of Head '''
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("VAR1")
        super().__init__(seg, address, 138, **kwargs)
        #self.compact = True
        self.get_fields(
            ("hv1_v", 7,),
            ("hv1_d", 3,),
            ("hv1_z0", 32,),
            ("hv1_d100", 32,),
            ("hv1_tl", -1,),
        )
        bittools.make_one(self, 'hv1_d100', D100)

class HeadVar2(Head):
    ''' Second variant of Head '''
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("VAR2")
        super().__init__(seg, address, 138, **kwargs)
        #self.compact = True
        self.get_fields(
            ("hv2_v", 7,),
            ("hv2_d", 3,),
            ("hv2_u0", 32,),
            ("hv2_u1", 32,),
            ("hv2_u2", 32,),
            ("hv2_u3", 32,),
        )
        bittools.make_one(self, 'hv2_u1', bittools.R1kCut)
        bittools.make_one(self, 'hv2_u3', bittools.R1kCut)

class HeadVar3(Head):
    ''' Third variant of Head '''
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("VAR3")
        super().__init__(seg, address, 74, **kwargs)
        #self.compact = True
        self.get_fields(
            ("hv3_v", 7,),
            ("hv3_d", 3,),
            ("hv3_u0", 32,),
            ("hv3_d300", 32,),
        )
        bittools.make_one(self, 'hv3_d300', D300)


class R1kSeg97():
    ''' A Diana Tree Segmented Heap '''
    def __init__(self, seg):
        p = seg.mkcut(0x80)
        if len(p) <= 0x400:
            return
        self.seg = seg


        variant = int(p[0x1e0:0x1e7], 2)

        # variant = int(seg.mkcut(self.head.end).bits[:7], 2)
        if variant == 1:
            self.head = HeadVar1(seg, 0x80)
        elif variant == 2:
            self.head = HeadVar2(seg, 0x80)
        elif variant == 3:
            self.head = HeadVar3(seg, 0x80)
        else:
            self.head = Head(seg, 0x80)
            print("97SEG", seg.this, "Unknown head variant", variant)
        seg.dot.edge(seg.mkcut(0), self.head)
        if False:
            bittools.make_one(self.head, 'head_stuff1', Diana00)
        else:
            bittools.make_one(self.head, 'head_stuff1', bittools.R1kSegBase, someclass)
        #seg.hunt_orphans(26, verbose=False)


        self.table = bittools.BitPointerArray(seg, 0x31a, 256)
        seg.dot.edge(self.head, self.table)
