'''
   R1000 'A6' segments
   ===================

'''

import os
import html
import autoarchaeologist.rational.r1k_bittools as bittools

COMPACT = False

class A6String(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=pink')
        seg.dot.write("X_0x%x -> T_0x%x" % (self.begin, self.begin))
        self.compact = True
        self.get_fields(
            ("p1_n", 32),
            ("p2_n", 32),
        )
        _i, self.text = bittools.to_text(
            seg,
            self.chunk,
            self.offset,
            self.p2_n
        )
        self.offset += self.p2_n * 8
        self.finish()
        seg.dot.write('T_0x%x [shape=plaintext, label="%s"]' % (self.begin, html.escape(self.text).replace('.', '.\\l')))

    def render(self, _chunk, fo):
        ''' Dont dump the text as bits because of missing field '''
        fo.write(self.title)
        self.render_fields(fo)

class A6Chain(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, target=None, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=orange')
        self.compact = True
        self.get_fields(
            ("next_p", 32),
            ("p2_p", 32),
        )
        self.finish()
        if target:
            bittools.make_one(self, 'p2_p', target)
            seg.mkcut(self.p2_p)

class A6Chain2(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, target=None, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=orange')
        self.compact = True
        self.get_fields(
            ("next_p", 32),
            ("p2_p", 32),
            ("p3_p", 32),
        )
        self.finish()
        if target:
            bittools.make_one(self, 'p2_p', target)

def make_chains(seg, address, func, **kwargs):
    ''' Follow a chain non-recusively '''
    reval = None
    while address:
        y = func(seg, address, **kwargs)
        address = y.next_p
        if reval is None:
            reval = y
    return reval

def make_chain(seg, address, **kwargs):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, A6Chain, **kwargs)

def make_chain2(seg, address, **kwargs):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, A6Chain2, **kwargs)

class A6Record00(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec00_0_p", 32),
            ("rec00_1_p", 32),
            ("rec00_2_p", 32),
            ("rec00_3_p", 32),
            ("rec00_4_n", 1),
        )
        self.finish()
        if self.rec00_4_n:
            seg.dot.node(self, 'style=filled', 'fillcolor=red')
        seg.dot.node(self, 'shape=circle')


        bittools.make_one(self, 'rec00_0_p', A6String, ident="rec00")

        bittools.make_one(self, 'rec00_1_p', A6Record01)
        bittools.make_one(self, 'rec00_2_p', A6Record00)
        bittools.make_one(self, 'rec00_3_p', A6Record00)

        bittools.make_one(self, 'rec00_3_p', A6Record00)

class A6Record01(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=cyan')
        self.compact = COMPACT
        self.get_fields(
            ("rec01_00_p", 32),
            ("rec01_01_p", 32),
            ("rec01_02_p", 32),
            ("rec01_03_p", 32),
            ("rec01_04_n", 32),
            ("rec01_05_n", 32),
            ("rec01_06_n", 29),
            ("rec01_07_p", 32),
            ("rec01_08_n", 3),
            ("rec01_09_n", 32),
            ("rec01_10_n", 30),
            ("rec01_11_p", 32),
            ("rec01_12_n", 128),
            ("rec01_13_n", 128),
            ("rec01_14_n", 96),
            ("rec01_15_p", 32),
            ("rec01_16_n", 36),
            ("rec01_17_p", 32),
            ("rec01_18_n", 28),
            ("rec01_19_n", 32),
            ("rec01_20_n", 71),
            ("rec01_21_p", 32),
            ("rec01_22_p", 32),
            ("rec01_23_n", 1),
            ("rec01_24_p", 32),
            ("rec01_25_n", 64),
        )
        self.finish()
        bittools.make_one(self, 'rec01_00_p', A6Record01, ident="xxx0")
        bittools.make_one(self, 'rec01_01_p', A6Record01, ident="xxx0")
        bittools.make_one(self, 'rec01_02_p', A6Record01, ident="xxx0")
        bittools.make_one(self, 'rec01_07_p', A6Record16, func=make_chain16)
        bittools.make_one(self, 'rec01_15_p', A6Record03)
        bittools.make_one(self, 'rec01_17_p', A6Array23)
        y = bittools.make_one(self, 'rec01_21_p', A6Record24, ident="r01_21")
        if y:
            self.rec01_21_part2_p = y.end
            z = bittools.make_one(self, 'rec01_21_part2_p', A6Record21, ident="r01_21")
        bittools.make_one(self, 'rec01_22_p', A6Record25)
        bittools.make_one(self, 'rec01_24_p', A6Record14)
        make_chain2(seg, self.rec01_03_p, target=A6Record01, ident="rec01")

class A6Record03(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec03_00_p", 32),
            ("rec03_01_n", 32),
            ("rec03_02_n", 30), # Not a pointer
            ("rec03_03_n", 1),
            ("rec03_04_n", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec03_00_p', A6Record13, func=make_chain13)

class A6Record04(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=salmon')
        self.compact = COMPACT
        self.get_fields(
            ("rec04_00_p", 32),
            ("rec04_01_p", 32),
            ("rec04_02_p", 32),
            ("rec04_03_p", 32),
            ("rec04_04_n", 1),
        )
        self.finish()
        bittools.make_one(self, 'rec04_00_p', A6String, ident="rec04")
        bittools.make_one(self, 'rec04_01_p', A6Record01)
        bittools.make_one(self, 'rec04_02_p', A6Record04)
        bittools.make_one(self, 'rec04_03_p', A6Record04)

class A6Record05(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=lightgreen')
        self.compact = COMPACT
        self.get_fields(
            ("rec05_00_p", 32),
            ("rec05_01_p", 32),
            ("rec05_02_p", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec05_00_p', A6Record05)
        bittools.make_one(self, 'rec05_01_p', A6String, ident="rec05")

class A6Record06(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec06_00_p", 32),
            ("rec06_01_z", 32),
            ("rec06_02_z", 64),
            ("rec06_03_z", 128),
        )
        self.finish()
        bittools.make_one(self, 'rec06_00_p', A6Record06)

class A6Record07(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec07_00_p", 32),
            ("rec07_01_z", 128),
            ("rec07_02_z", 128),
            ("rec07_03_z", 95),
        )
        self.finish()
        bittools.make_one(self, 'rec07_00_p', A6Record07)


class A6Record08(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'shape=pentagon')
        self.compact = COMPACT
        self.get_fields(
            ("rec08_00_n", 8),
        )
        if self.rec08_00_n == 0:
            self.get_fields(
                ("rec08_a_01_n", 24),
                ("rec08_a_02_p", 32),
                ("rec08_a_03_z", 32),
                ("rec08_a_04_p", 32),
                ("rec08_a_05_z", 32),
                ("rec08_a_06_p", 32),
                ("rec08_a_07_z", 32),
                ("rec08_a_08_p", 32),
                ("rec08_a_09_z", 32),
            )
        elif self.rec08_00_n == 1:
            self.get_fields(
                ("rec08_b_01_n", 32),
                ("rec08_b_02_p", 32),
                ("rec08_b_03_z", 32),
                ("rec08_b_04_p", 32),
                ("rec08_b_05_z", 32),
                ("rec08_b_06_p", 32),
                ("rec08_b_07_z", 32),
                ("rec08_b_08_p", 32),
                ("rec08_b_09_z", 32),
                ("rec08_b_10_p", 32),
            )
        else:
            raise Exception("A6 Record08 selector=0x%x" % self.rec08_0_n)
        self.finish()
        if self.rec08_00_n == 0:
            make_chain2(seg, self.rec08_a_02_p, ident="rec08_a_002", target=A6Record09A)
            make_chain2(seg, self.rec08_a_04_p, ident="rec08_a_004", target=A6Record10)
            make_chain2(seg, self.rec08_a_06_p, ident="rec08_a_006", target=A6Record11A)
            make_chain2(seg, self.rec08_a_08_p, ident="rec08_a_008", target=A6Record12)
        elif self.rec08_00_n == 1:
            make_chain2(seg, self.rec08_b_02_p, ident="rec08_b_002", target=A6Record09B)
            make_chain2(seg, self.rec08_b_04_p, ident="rec08_b_004", target=A6Record10)
            make_chain2(seg, self.rec08_b_06_p, ident="rec08_b_006", target=A6Record11B)
            make_chain2(seg, self.rec08_b_08_p, ident="rec08_b_008", target=A6Record12)
            bittools.make_one(self, 'rec08_b_10_p', A6Record18)

class A6Record09A(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec09a_0_z", 0x80),
            ("rec09a_1_z", 0x80),
            ("rec09a_2_n", 0x53),
        )
        self.finish()


class A6Record09B(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec09b_0_z", 0x80),
            ("rec09b_1_z", 0x80),
        )
        self.finish()

class A6Record10(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec10_0_n", 48),
            ("rec10_1_z", 94),
        )
        self.finish()

class A6Record11A(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec11a_0_n", 0x80),
        )
        self.finish()

class A6Record11B(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec11b_0_n", 0x40),
        )
        self.finish()

class A6Record12(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec12_0_n", 0x60),
        )
        self.finish()

class A6Record13(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("next_p", 32),
            ("rec13_1_n", 95),
        )
        self.finish()

def make_chain13(seg, address, **kwargs):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, A6Record13, **kwargs)

class A6Record14(bittools.R1kSegBase):
    ''' ...  '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=yellow')
        self.compact = COMPACT
        self.get_fields(
            ("rec14_00_p", 32),
            ("rec14_01_p", 32),
            ("rec14_02_p", 32),
            ("rec14_03_n", 32),
            ("rec14_04_n", 8),
        )
        if self.rec14_04_n == 0:
            self.get_fields(
                ("rec14_a_05_z", 24),
                ("rec14_a_06_p", 32),
                ("rec14_a_07_n", 16),
                ("rec14_a_08_z", 16),
                ("rec14_a_09_n", 32), # XXX: sometimes _p
            )
        else:
            self.get_fields(
                ("rec14_b_05_n", 8),
                ("rec14_b_06_p", 32),
                ("rec14_b_07_z", 80),
            )
        self.finish()
        bittools.make_one(self, 'rec14_00_p', A6Record33, func=make_chain33)
        bittools.make_one(self, 'rec14_01_p', A6Record20)
        bittools.make_one(self, 'rec14_02_p', A6Record30, func=make_chain30)

        if self.rec14_04_n == 0:
            bittools.make_one(self, 'rec14_a_06_p', A6Record31)
            if 0x400 < self.rec14_a_09_n < 8 * len(seg.this):
                print("rec14_a_09_n Hack 0x%x" % self.rec14_a_09_n)
                y = bittools.make_one(self, 'rec14_a_09_n', A6Array26) # XXX: Only sometimes
                if y:
                    seg.dot.edge(self, y)
        elif self.rec14_04_n == 1:
            bittools.make_one(self, 'rec14_b_06_p', A6Record15)

        if 0x400 < self.rec14_03_n < 8 * len(seg.this) and self.rec14_03_n not in (
            0x10900,
            0x10a00,
            0x10b00,
        ):
            print("rec14_03_n Hack 0x%x" % self.rec14_03_n)
            y = bittools.make_one(self, 'rec14_03_n', A6Record32) # XXX: Only sometimes
            if y:
                seg.dot.edge(self, y)

class A6Record15(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=seagreen')
        self.compact = COMPACT
        self.get_fields(
            ("rec15_01_n", 128),
            ("rec15_02_n", 128),
            ("rec15_03_n", 0x1d),
        )
        self.finish()

class A6Record16(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        seg.dot.node(self, 'style=filled', 'fillcolor=seagreen')
        self.compact = COMPACT
        self.get_fields(
            ("next_p", 32),
            ("rec16_01_p", 32),
            ("rec16_02_p", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec16_01_p', A6Record01)
        bittools.make_one(self, 'rec16_02_p', A6Record01)

def make_chain16(seg, address, **kwargs):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, A6Record16, **kwargs)

class A6Record18(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec18_00_p", 32),
            ("rec18_01_p", 32),
            ("rec18_02_z", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec18_00_p', A6Record18)
        bittools.make_one(self, 'rec18_01_p', A6Array19)

class A6Array19(bittools.Array):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, address, width=64, **kwargs)

class A6Record20(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec20_00_p", 32),
            ("rec20_01_n", 32+95),
            ("rec20_02_p", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec20_00_p', A6Record01)
        bittools.make_one(self, 'rec20_02_p', A6Record20)

class A6Record21(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec21_00_p", 32),
            ("rec21_01_n", 95 - 32),
            ("rec21_02_p", 32),
            ("rec21_03_p", 32),
            ("rec21_04_p", 32),
            ("rec21_05_p", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec21_02_p', A6Record01)

class A6Array23(bittools.Array):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, address, width=1, **kwargs)

class A6Record24(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec24_00_p", 32),
            ("rec24_01_p", 32),
            ("rec24_02_p", 32),
            ("rec24_03_n", 32),
            ("rec24_04_n", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec24_00_p', A6Record24, ident="r24_00")
        bittools.make_one(self, 'rec24_01_p', A6Record01)
        bittools.make_one(self, 'rec24_02_p', A6Record01)

class A6Record25(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec25_00_p", 32),
            ("rec25_01_n", 32),
            ("rec25_02_n", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec25_00_p', A6Record25)
        bittools.make_one(self, 'end', A6Record24, ident="r25_e")

class A6Array26(bittools.Array):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, address, width=64, **kwargs)

class A6Record27(bittools.BitPointerArray):
    ''' ... '''
    def __init__(self, seg, address, count=120, **kwargs):
        super().__init__(seg, address, count=count, target=A6Record00, **kwargs)

class A6Record30(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = True
        self.get_fields(
            ("next_p", 32),
            ("rec30_1_n", 32),
            ("rec30_2_n", 64),
        )
        self.finish()
        #bittools.make_one(self, 'rec30_0_p', A6Record30)

def make_chain30(seg, address, **kwargs):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, A6Record30, **kwargs)

class A6Record31(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec31_00_n", 32),
            ("rec31_01_n", 32),
            ("rec31_02_p", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec31_02_p', A6Record31)

class A6Record32(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("rec32_00_n", 32),
            ("rec32_01_p", 32),
        )
        self.finish()
        bittools.make_one(self, 'rec32_01_p', A6Record32)

class A6Record33(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = COMPACT
        self.get_fields(
            ("next_p", 32),
            ("rec33_01_n", 14),
            ("rec33_02_n", 32),
            ("rec33_03_n", 32),
            ("rec33_04_n", 32),
        )
        self.finish()

def make_chain33(seg, address, **kwargs):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, A6Record33, **kwargs)

class A6Head(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        self.compact = False
        self.get_fields(
            ("a6head_00_c", 32),
            ("a6head_01_c", 30),
            ("a6head_02_n", 32),
            ("a6head_03_c", 32),
            ("a6head_04_z", 32),
            ("a6head_05_z", 32),
            ("a6head_06_z", 32),
            ("a6head_07_c", 32),
            ("a6head_08_z", 32),
            ("a6head_09_c", 32),
            ("a6head_10_z", 32),
            ("a6head_11_c", 32),
            ("a6head_12_c", 32),
            ("a6head_13_n", 30), # ⟦231cadacd⟧ past end of allocation
            ("a6head_14_c", 32),
            ("a6head_15_n", 32),
            ("a6head_16_n", 33), # ⟦2e8bae5d8⟧ past end of allocation
            ("a6head_17_n", 16),
            ("a6head_18_n", 16),
            ("a6head_19_p", 32), # @2bd: 7c1, 7e9 -> String
            ("a6head_20_p", 32), # @2dd: 59f...
            ("a6head_21_p", 32), # @2fd
            ("a6head_22_n", 32), # @31d
            ("a6head_23_p", 33), # @33d: 59f ...
            ("a6head_24_p", 32), # @35e
            ("a6head_25_p", 32), # @37e
            ("a6head_26_n", 32), # @39e
            ("a6head_27_p", 33), # @3be
            ("a6head_28_z", 32), # @3df
            ("a6head_29_p", 32), # @3ff
            ("a6head_30_z", 32), # @41f
            ("a6head_31_p", 32), # @43f
            ("a6head_32_z", 32), # @45f
            ("a6head_33_p", 32), # @47f
            ("a6head_34_p", 32), # @49f
            ("a6head_35_p", 32), # @4bf
            ("a6head_36_p", 32), # @4df
            ("a6head_37_z", 32), # @4ff
            ("a6head_38_p", 32), # @51f
            ("a6head_39_p", 32), # @53f
            ("a6head_40_z", 32), # @55f
            ("a6head_41_z", 32), # @57f
        )
        self.finish()

        bittools.make_one(self, 'a6head_19_p', A6String, ident="head_19")
        bittools.make_one(self, 'a6head_20_p', A6Record00)
        bittools.make_one(self, 'a6head_21_p', A6Record27, count=0xcb)
        bittools.make_one(self, 'a6head_23_p', A6Record00)
        bittools.make_one(self, 'a6head_24_p', A6Record04)
        bittools.make_one(self, 'a6head_27_p', A6Record04)
        bittools.make_one(self, 'a6head_29_p', A6Record05)
        make_chain2(seg, self.a6head_31_p, target=A6Record01, ident="hd31")
        make_chain2(seg, self.a6head_33_p, ident="hd33")
        bittools.make_one(self, 'a6head_34_p', A6Record07)
        bittools.make_one(self, 'a6head_35_p', A6Record06)
        bittools.make_one(self, 'a6head_36_p', A6Record13, func=make_chain13)
        make_chain2(seg, self.a6head_38_p, target=A6Array23, ident="hd38")
        bittools.make_one(self, 'a6head_39_p', A6Record08)


class R1kSegA6():
    ''' ... '''
    def __init__(self, seg):
        self.seg = seg

        if True:
            for a in (
                0xd969,
            ):
            #for a in range(0x26390, 0x2646f):
                for i in seg.hunt(bin((1<<32)|a)[3:]):
                    print("HUNT 0x%x" % a, "<- 0x%x" % i[2])

        try:
            A6Head(seg, 0x80)
        except:
            #pass
            raise

        if True:
            for _offset, chunk in seg.tree:
                if not chunk.owner:
                    self.hunt_strings(seg, chunk)

        if "AA_RUN_DOT" in os.environ:
            while 1 and seg.hunt_orphans(verbose=True):
                continue

    def hunt_strings(self, seg, chunk):
        a = 0
        locs = []
        for n, i in enumerate(chunk.bits):
            a += a + ord(i) - 0x30
            a &= 0xffffffffffffffff
            if not a & 0xfff:
                continue
            if not a & 0xfff00000000:
                continue
            if  a & 0xfffff000fffff000:
                continue
            try:
                j, t = bittools.to_text(seg, chunk, n + 1, 128, no_fail=True)
            except:
                print(seg.this, "A6-text fail at 0x%x" % n)
                continue
            if j < 2 or j != a & 0xfff:
                continue
            if not t[0].isalpha() and t[0] != '!':
                continue
            locs.append(n + chunk.begin - 63)
        for i in locs:
            try:
                y = A6String(seg, i, ident="hunted")
            except:
                print(seg.this, "A6-string-hunt fail at 0x%x" % i)
