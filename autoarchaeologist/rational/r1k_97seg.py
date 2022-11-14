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

#######################################################################

class DianaChain(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        c = seg.cut(address, -1)
        super().__init__(seg, c)
        self.compact = DIANA_COMPACT
        self.get_fields(
            ("chain_type", 1),
            ("next_p", 26),
        )
        if self.chain_type == 1:
            self.get_fields(
                ("chain_2_p", 26),
            )
            self.finish()
            y = bittools.make_one(self, 'chain_2_p', bittools.R1kSegBase, someclass)
        else:
            self.finish()
            y = bittools.make_one(self, 'end', bittools.R1kSegBase, someclass)
            if y:
                seg.dot.edge(self, y, "color=green")

class DianaChain2(bittools.R1kSegBase):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = True
        self.get_fields(
            ("chain2_type", 9),
            ("chain2_1_p", 26),
            ("next_p", 26),
        )
        self.finish()
        if not self.chain2_type:
            bittools.make_one(self, 'chain2_1_p', bittools.R1kSegBase, someclass)

def make_chains(seg, address, func):
    ''' Follow a chain non-recusively '''
    reval = None
    last = None
    while address:
        y = func(seg, address)
        address = y.next_p
        if last:
            seg.dot.edge(last, y)
        last = y
        if reval is None:
            reval = y
    return reval

def make_chain(seg, address):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, DianaChain)

def make_chain2(seg, address):
    ''' Follow a chain non-recusively '''
    return make_chains(seg, address, DianaChain2)

#######################################################################

class SomeBlock(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address, length):
        super().__init__(seg, seg.cut(address, 0x9d), ident="(%d)" % length)
        self.compact = True
        self.get_fields(
            ("p1_p", 32),
            ("p2_p", 32),
            ("p3_p", 32),
            ("p4", 3),
            ("p5_p", 32),
            ("p6_p", 26),
        )
        bittools.make_one(self, 'p1_p', SomeBlock, length=length)
        seg.mkcut(self.p2_p)
        #seg.mkcut(self.p3_p)
        bittools.make_one(self, 'p5_p', bittools.R1kSegBase, someclass)

class SomeList(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 256*32))
        length = 0
        self.items = []
        for a in range(0, 256*32, 32):
            val = int(self.chunk.bits[a:a+32], 2)
            if not val:
                continue
            if length is None:
                length = val
                continue
            if val == a + self.begin + 32:
                length = None
                continue
            y = SomeBlock(seg, val, length)
            seg.dot.edge(self, y)
            self.items.append((length, val))

    def render_fields(self, fo):
        ''' one line per element '''
        for length, address in self.items:
            fo.write("    0x%x bytes free at 0x%06x\n" % (length, address))
        return len(self.chunk)

class Diana_10c91(bittools.R1kSegBase):
    "t p p c 6 P 17 ."
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = False
        self.get_fields(
            ("Diana_10c91_type", 17),
            ("Diana_10c91_1_p", 26),
            ("Diana_10c91_2_p", 26),
            ("Diana_10c91_3_p", 26),
            ("Diana_10c91_4_p", 32),
            ("Diana_10c91_5_n", 17),
        )
        self.finish()
        bittools.make_one(self, 'Diana_10c91_4_p', bittools.R1kSegBase, Diana_10c91dst)
        bittools.make_one(self, 'Diana_10c91_1_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_10c91_2_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_10c91_3_p', DianaChain, func=make_chain)

class Diana_10c91dst(bittools.R1kSegBase):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = False
        self.get_fields(
            ("f1_n", 32),
            ("f2_p", 32),
        )
        self.finish()
        bittools.PointerArray(seg, self.f2_p, target=FooBar)

class Diana_10c94(bittools.R1kSegBase):
    ''' 0x10c94: "t p p c 6 P",		# Followed by [0x31...] '''
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = False
        self.get_fields(
            ("Diana_10c94_type", 17),
            ("Diana_10c94_1_p", 26),
            ("Diana_10c94_2_p", 26),
            ("Diana_10c94_3_p", 26),
            ("Diana_10c94_4_n", 6),
            ("Diana_10c94_5_p", 26),
            ("Diana_10c94_6_n", 17),
        )
        self.finish()
        bittools.make_one(self, 'Diana_10c94_1_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_10c94_2_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_10c94_3_p', DianaChain, func=make_chain)
        # XXX: Determine length of this sequence of 32 bit numbers
        bittools.make_one(
            self,
            'Diana_10c94_5_p',
            bittools.BitPointerArray, count=2
        )

class FooBar(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, 0x9d))
        self.compact = True
        self.get_fields(
            ("p1_p", 32),
            ("p2_p", 32),
            ("p3_p", 32),
            ("p4", 3),
            ("p5_p", 32),
            ("p6_p", 26),
        )
        y = bittools.make_one(self, 'p1_p', bittools.R1kSegBase, FooBar)
        if y:
            seg.dot.edge(self, y)
        if not self.p4:
            y = bittools.make_one(self, 'p5_p', bittools.R1kSegBase, someclass)
            if y:
                seg.dot.edge(self, y)
        #seg.mkcut(self.p2_p)
        ##seg.mkcut(self.p3_p)

class Snafu(bittools.PointerArray):
    ''' ... '''
    def __init__(self, seg, address):
        super().__init__(seg, address, width=32, target=FooBar)
        self.supress_zeros = True

class Diana_112a8(bittools.R1kSegBase):
    ''' ... '''
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = False
        self.get_fields(
            ("Diana_112a8_type", 17),
            ("Diana_112a8_1_p", 26),
            ("Diana_112a8_2_p", 26),
            ("Diana_112a8_3_p", 26),
            ("Diana_112a8_4_p", 26),
            ("Diana_112a8_5_p", 26),
            ("Diana_112a8_6_x", 6),
            ("Diana_112a8_6_p", 26),
            ("Diana_112a8_7", 17),
        )
        self.finish()
        bittools.make_one(self, 'Diana_112a8_1_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_112a8_2_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_112a8_3_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_112a8_4_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_112a8_5_p', bittools.R1kSegBase, someclass)
        bittools.make_one(self, 'Diana_112a8_6_p', bittools.R1kSegBase, Diana_112a8dst)

class Diana_112a8dst(bittools.R1kSegBase):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = False
        self.get_fields(
            ("f1_n", 32),
            ("f2_p", 32),
        )
        self.finish()
        y = bittools.PointerArray(seg, self.f2_p, width=32, target=Diana_112a8d2)
        y.supress_zeros = True
        seg.dot.edge(self, y)

class Diana_112a8d2(bittools.R1kSegBase):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = False
        self.get_fields(
            ("f1_n", 32),
            ("f2_n", 32),
            ("f3_p", 32),
        )
        self.finish()
        bittools.make_one(self, 'f3_p', bittools.R1kSegBase, Diana_112a8d3)

class Diana_112a8d3(bittools.R1kSegBase):
    def __init__(self, seg, address):
        super().__init__(seg, seg.cut(address, -1))
        self.compact = False
        self.get_fields(
            ("f1_n", 9),
            ("f2_p", 26),
            ("f3_n", 26),
        )
        self.finish()
        bittools.make_one(self, 'f2_p', bittools.R1kSegBase, someclass)

diana_types = {
    0x10079: "t",
    0x100ab: "t",
    0x100be: "t",
    0x10100: "t 43 26",		# followed by [0x2b|0x45] (disk-address?)
    0x10135: "t",
    0x1015e: "t",
    0x1015f: "t",
    0x1016b: "t p p p",
    0x1016d: "t p p p",
    0x1017b: "t p p p",
    0x10180: "t p p p",
    0x10183: "t p p p",
    0x10188: "t p p p",		# ⟦7163615b7⟧
    0x10210: "t",
    0x1024b: "t p p p",
    0x10252: "t p p p",
    0x10255: "t p p p",
    0x1025c: "t p p p",
    0x1025d: "t p p p",
    0x1036c: "t p p p p",
    0x1037a: "t p p p",
    0x10381: "t p p p p",
    0x10382: "t p p p p",
    0x103a9: "t p p p p .",
    0x103aa: "t p p p p",
    0x10402: "t p p p p 17",
    0x10437: "t p p p p 17",
    0x1043a: "t p p p p 17",
    0x1043c: "t p p p p 17",
    0x1043e: "t p p p p 17",
    0x1043f: "t p p p p 17",
    0x10440: "t p p p p 17",
    0x10442: "t p p p p 17",
    0x10444: "t p p p p 17",
    0x10446: "t p p p p 17",
    0x10447: "t p p p p 17",
    0x10449: "t p p p p 17",
    0x1044d: "t p p p p 17",		# ⟦fd533ba7a⟧
    0x1044f: "t p p p p 17",
    0x10450: "t 8 26 1",		# `26` is sometimes obj-ptr
    0x10451: "t p p p p 17",
    0x10457: "t p p p p 17",
    0x10458: "t p p p p 17",
    0x1045e: "t p p p p 17",
    0x10460: "t p p p p 17",
    0x10479: "t p p p p 17",
    0x1047c: "t p p p p 17",
    0x1049e: "t p p p p 17",
    0x1049f: "t p p p p 17",
    0x104a1: "t p p p p 17",
    0x105a0: "t p p p p 17",
    0x10630: "t 8 p 32",
    0x10638: "t p p p p p 17",
    0x10639: "t p p p p p 17",
    0x1063b: "t p p p p p 17",
    0x1063d: "t p p p p p 17",
    0x10641: "t p p p p p 17",
    0x10643: "t p p p p p 17",
    0x10648: "t p p p p p 17",
    0x1064c: "t p p p p p 17",
    0x1064e: "t p p p p p 17",
    0x10653: "t p p p p p 17",
    0x10654: "t p p p p p 17",
    0x1065b: "t p p p p p 17",
    0x10701: "t p p",		# ⟦4c2cac0c5⟧
    0x10760: "t 50",
    0x10863: "t p p c",
    0x1086e: "t p p c",
    0x1088a: "t p p c",		# ⟦fd533ba7a⟧
    0x1088b: "t p p c",
    0x10890: "t p p c",
    0x10892: "t p p c",
    0x10893: "t p p c",		# Followed by [0x34]
    0x10899: "t p p c",
    0x10945: "t p p c",
    0x10956: "t p p c",
    0x10980: "t 8 p" ,
    0x10984: "t p p c 17",
    #0x10985: "t p p c 17",
    0x10985: "t p p 8",
    0x10989: "t p p c 17",
    0x10995: "t p p c 17",
    0x10996: "t p p c 17",
    0x10997: "t p p c 17",
    0x10a0d: "t p p p",
    0x10a90: "t",
    0x10b03: "t p p p",
    0x10bb0: "t",
    0x10cc0: "t",
    0x10c8c: "t p p c",
    0x10c8f: "t p p P",
    # 0x10c91: "t p p c 6 P 17 .",
    0x10c91: Diana_10c91,
    0x10c94: Diana_10c94,
    0x10e0e: "t p p p p",
    0x10f05: "t p p p p",
    0x10f0a: "t p p p p",
    0x10f0f: "t p p p p",
    0x11004: "t p p p p p",
    0x112a8: Diana_112a8,
    0x1131d: "t p p 117",
    0x11423: "t p p",		# ⟦a51d6cbb0⟧ Followed by [0x18/0x55/0x7e]
    0x1151e: "t p p",
    0x11666: "t p p p p 105",	# Followed by [0x4f|0x69]
    0x11731: "t p p",		# ⟦b8f057163⟧
    0x11732: "t p p",		# ⟦9f223cbfc⟧
    0x11821: "t p p",		# ⟦fd533ba7a⟧
    #0x11829: "t p p 170",
    0x11829: "t p p 59 p",
    0x1182c: "t p p 59 p 9 26 9 26 15",		# ⟦929481dbc⟧
    0x1182e: "t p p",
    0x11833: "t p p 24",	# ⟦d765ea804⟧
    0x11962: "t p p",
    0x11a7d: "t p p p p p",
    0x11a7e: "t p p p p p 1",	# Followed by [0x1]
    0x11a7f: "t p p p p p",
    0x11a9b: "t p p p p p 1 .",
    0x11c20: "t p p 56",
    0x11b1f: "t p p 24 p",
    0x11d8d: "t p p p P",		# ⟦fd533ba7a⟧ Followed by [0x9]
    0x11e64: "t p p p p",	# ⟦24afbc399⟧
    0x11f65: "t p p p p",	# ⟦24afbc399⟧
    0x1ff9c: "t p p",
    0x1ff9d: "t p p",
    0x12010: "t p",
    0x12122: "t p p",
    0x12224: "t p p",		# ⟦9510ebe8f⟧
    0x12225: "t p p",		# ⟦6e365d751⟧
    0x12311: "t p p p",
    0x12436: "t p p",
    0x1256f: "t p p p",		# ⟦d765ea804⟧
    0x12626: "t p p",		# ⟦929481dbc⟧
    0x12770: "t p p",		# ⟦9cfd7dc2c⟧
    0x12771: "t p p",
    0x1282a: "t p p",
    0x1282b: "t p p",
    0x1282d: "t p p",
    0x12927: "t p p",
    0x12959: "t p p",
    0x12a4a: "t p p p p",
    0x12b06: "t p p",
    0x12c07: "t p p",
    0x12d30: "t p p 7 x 9 p p 15",
    0x12d28: "t p p",
    0x12e08: "t p 84",
    0x12f09: "t p",
    0x13101: "t p 1",
    0x13161: "t p p p p",
    0x13272: "t p p",		# ⟦5fe7c3ee3⟧
    0x13312: "t p p p p 43",
    0x13413: "t p p p p",
    0x1350b: "t p p",		# ⟦f7592710e⟧
    0x13677: "t p p 1",
    0x13773: "t p p p",
    0x1382f: "t p p 16 34 34 16",
    0x13915: "t p",
    0x13a0c: "t p p",
    0x13a16: "t p",		# always followed by [0x32...]
    0x13b14: "t p p",
    0x13b17: "t p 32 1 x 35",
    0x13eab: "t p",
    0x13f5a: "t p",
    0x13f5f: "t p",
    0x1ffa4: "t p p 12",
    0x1ff74: "t p p 12",
    0x1ff75: "t p p 12",
    0x1ff76: "t p p 12",
}

class DianaSkeleton(bittools.R1kSegBase):
    ''' Skeleton class configured from the short-hand strings '''
    def __init__(
        self,
        seg,
        address,
        name,
        length,
        flds,
        objs,
        chains,
        cuts,
    ):
        c = seg.cut(address, length)
        super().__init__(seg, c, title=name)
        self.compact = DIANA_COMPACT
        self.get_fields(*flds)
        for i in objs:
            y = bittools.make_one(
                self,
                i,
                bittools.R1kSegBase,
                func=someclass,
            )
            if y:
                seg.dot.edge(self, y)
        for field, cls, func in chains:
            y = bittools.make_one(
                self,
                field,
                cls,
                func=func,
            )
            if y:
                seg.dot.edge(self, y)
        for i in cuts:
            seg.mkcut(getattr(self, i))

class PrepareTypes():
    ''' Turn the short-hand strings into classes '''
    def __init__(self):
        for a, b in list(diana_types.items()):
            if not isinstance(b, str):
                continue

            self.fields = []
            self.objs = []
            self.chains = []
            self.offset = 0
            self.cuts = []
            self.nbr = 0

            for spec in b.split():
                if spec == "c":
                    self.add_field(a, "%d_p" % self.nbr, 26, False)
                    self.chains.append((self.fields[-1][0], DianaChain, make_chain))
                elif spec == "c2":
                    self.add_field(a, "%d_p" % self.nbr, 26, False)
                    self.chains.append((self.fields[-1][0], DianaChain2, make_chain2))
                elif spec == "e":
                    self.objs.append('end')
                elif spec == "P":
                    self.add_field(a, "%d_p" % self.nbr, 26, False)
                    self.cuts.append(self.fields[-1][0])
                elif spec == "p":
                    self.add_field(a, "%d_p" % self.nbr, 26, True)
                elif spec == "t":
                    self.add_field(a, "type", 17, False)
                elif spec == "x":
                    self.add_field(a, "txt", 8, False)
                elif spec.isnumeric():
                    self.add_field(a, "%d_n" % self.nbr, int(spec), False)
                elif spec == ".":
                    pass	# Marker meaning "done"
                else:
                    raise ValueError("spec: <%s>" % spec)

            diana_types[a] = (
                "diana_%x" % a,
                self.offset,
                self.fields,
                self.objs,
                self.chains,
                self.cuts,
            )

    def add_field(self, address, name, width, obj):
        ''' for convenience '''
        name = 'd_%x_' % address + name
        self.fields.append((name, width))
        if obj:
            self.objs.append(name)
        self.nbr += 1
        self.offset += width

PrepareTypes()

def someclass(seg, address):
    ''' Select class dynamically '''
    p = seg.mkcut(address)
    typ = int(p[:17], 2)
    t = diana_types.get(typ)
    if isinstance(t, tuple):
        reval = DianaSkeleton(seg, address, *t)
    elif not t:
        print(seg.this, "Dummy for 0x%x" % typ, " at 0x%x" % address)
        reval = Dummy(seg, address)
    else:
        reval = t(seg, address)
    return reval

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
            ("d102_2", 4),
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
            ("d302_d302_p", 32),
            ("d302_d303_p", 32),
            ("d302_3", 32),
            ("d302_4", 32),
        )
        bittools.make_one(self, 'd302_d302_p', D302)
        bittools.make_one(self, 'd302_d303_p', D303)
        bittools.make_one(self, 'end', bittools.ArrayString)

class D303(bittools.R1kSegBase):
    ''' ...  '''
    def __init__(self, seg, address):
        c = seg.cut(address, 160)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d303_0", 37),
            ("d303_1_p", 32),
            ("d303_2", 15),
            ("d303_3", 76),
        )
        bittools.make_one(self, 'd303_1_p', D304)

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
            ("d306_d303_p", 32),
            ("d306_1", 32),
            ("d306_2", 3),
            ("d306_d307_p", 32),
            ("d306_d308_p", 32),
        )
        i = bittools.make_one(self, 'd306_d303_p', D303)
        if i:
            seg.dot.edge(self.chunk, i.chunk)
        i = bittools.make_one(self, 'd306_d307_p', D307)
        if i:
            seg.dot.edge(self.chunk, i.chunk)
        i = bittools.make_one(self, 'd306_d308_p', D308)
        if i:
            seg.dot.edge(self.chunk, i.chunk)

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
            ("d307_d307_p", 31),
        )
        i = bittools.make_one(self, 'd307_d307_p', D307)
        if i:
            seg.dot.edge(self.chunk, i.chunk)

class D308(bittools.R1kSegBase):
    ''' ...  '''
    def __init__(self, seg, address):
        c = seg.cut(address, 131)
        super().__init__(seg, c)
        self.compact = True
        self.get_fields(
            ("d308_d303_p", 32),
            ("d308_1", 3),
            ("d308_2", 32),
            ("d308_d307_p", 32),
            ("d308_d308_p", 32),
        )
        bittools.make_one(self, 'd308_d303_p', D303)
        bittools.make_one(self, 'd308_d307_p', D307)
        bittools.make_one(self, 'd308_d308_p', D308)

#######################################################################

class Thing13(bittools.R1kSegBase):
    ''' Something #13 '''
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0x83)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        self.get_fields(
            ("t13_0_p", 32),
            ("t13_1", 32),
            ("t13_3",  3),
            ("t13_4_p", 32),
            ("t13_5_p", 32),
        )
        bittools.make_one(self, "t13_0_p", Thing9)
        bittools.make_one(self, "t13_4_p", Thing12)
        bittools.make_one(self, "t13_5_p", Thing7)

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

class StringIndex(bittools.R1kSegBase):
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

    def render(self, _chunk, fo):
        ''' ... '''
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")
        for n, off in enumerate(range(64, len(self.chunk), 38)):
            txt = self.seg.txttab.get(n+1)
            if not txt:
                continue
            j = int(self.chunk[off:off+38], 2)
            a = j >> 15
            # A * 8 + t1_c1_head_p seem to point to string
            b = j & 0x7fff
            # B is zero or a serial number
            fo.write("  [$0x%04x] " % (n + 1))
            fo.write(" 0x%05x %03x" % (a * 8, b))
            fo.write(" »%s«" % txt.txt)
            fo.write("\n")

class TxtTab():
    def __init__(self, offset, idx0, idx1, idx2, txt):
        self.offset = offset
        self.idx0 = idx0
        self.idx1 = idx1
        self.idx2 = idx2
        self.txt = txt

    def render(self):
        t = "    @0x%05x " % self.offset
        t += "[0x%02x] = " % self.idx0
        t += " $0x%04x" % self.idx1
        #t += " 0x%x" % self.idx2
        t += " »" + self.txt + "«"
        return t


class StringStore(bittools.R1kSegBase):
    ''' Something #3 '''
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        y = int(p[32:64], 2)
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
        n = 0
        while offset < len(self.chunk) - 24:
            strno = int(self.chunk.bits[offset:offset+16], 2)
            if strno == 0:
                break
            strlen = int(self.chunk.bits[offset+16:offset+24], 2)
            if offset + 24 + strlen * 8 >= len(self.chunk):
                #print("Text overflow $0x%04x" % strno, "0x%x" % strlen, p, "at 0x%x" % offset)
                break
            # print("Text $0x%04x" % strno, "0x%x" % strlen, p, "at 0x%x" % offset, c, "0x%x" % (len(self.chunk) - 24))
            try:
                text = bittools.to_text(seg, self.chunk, offset + 24, strlen)
                txt = TxtTab(self.chunk.begin + offset, n, strno, strlen, text[1])
            except bittools.NotText as err:
                tt = []
                for i in range(offset+24, offset+24 + strlen*8, 8):
                    tt.append(int(self.chunk[i:i+8],2))
                txt = TxtTab(self.chunk.begin + offset, n, strno, strlen, "".join("\\x%02x" % x for x in tt))
            self.a.append(txt)
            seg.txttab[strno] = txt
            offset += 24 + 8 * strlen
            n += 1
        self.tail = offset

    def render(self, _chunk, fo):
        ''' ... '''
        fo.write(self.title)
        self.render_fields_compact(fo)
        fo.write("\n")
        for n, i in enumerate(self.a):
            fo.write(i.render() + "\n")

class Thing2(bittools.R1kSegBase):
    '''
        Simple, Singled list elements, one `next` pointer
        and one `payload` pointer
    '''
    def __init__(self, seg, address, payload_handler, **kwargs):
        super().__init__(seg, seg.cut(address, 0x40), **kwargs)
        self.compact = True
        self.get_fields(
            ("payload_p", 32),
            ("next_p", 32),
        )
        if self.payload_p:
            #payload_handler(seg, self.payload_p)
            bittools.make_one(self, "payload_p", payload_handler)

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
            ("t1_00_n", 0x6c),
            ("t1_c1_head_p", 0x20),
            ("t1_c2_last_p", 0x20),
            ("t1_array1_p", 0x20),
            ("t1_c2_tail_p", 0x20),
            ("t1_c1_tail_p", 0x20),
        )

        i = self.t1_c2_tail_p
        prev = self
        while i:
            follow = Thing2(seg, i, payload_handler=StringStore, ident="Chain2")
            seg.dot.edge(prev.chunk, follow.chunk)
            i = follow.next_p
            prev = follow

        if self.t1_c2_last_p:
            t3 = bittools.make_one(self, "t1_c2_last_p", StringStore)

        i = self.t1_c1_tail_p
        prev = self
        while i:
            follow = Thing2(seg, i, payload_handler=StringIndex, ident="Chain1")
            seg.dot.edge(prev.chunk, follow.chunk)
            i = follow.next_p
            prev = follow

        if 1 and self.t1_array1_p:
            bittools.make_one(self, "t1_array1_p", StringIndex)
            #bittools.Array(seg, self.t1_array1_p, 38)

class From31a(bittools.R1kSegBase):
    def __init__(self, seg, address, **kwargs):
        c = seg.cut(address, 0x11c)
        super().__init__(seg, c, **kwargs)
        self.compact = True
        self.get_fields(
            ("x0_n", 284),
        )
        # bittools.make_one(self, "t9_1", Thing10)

class Head(bittools.R1kSegBase):
    '''
        The start of the segment

    '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(seg, seg.cut(address, -1), **kwargs)
        #self.compact = True
        self.get_fields(
            ("head_z_000", 32,),           # 0x80000001
            ("head_segment", 31,),         # Segment#
            ("head_c_03f", 32,),           # 0x1
            ("head_chains_p", 32,),        # 0x231a, one case 0x0
            ("head_07f_z", 1,),            # 0x0
            ("head_080_z", 31,),           # 0x0
            ("head_stuff1_p", 32,),        # bit-address
            ("head_c_bf", 33,),            # 0x12, one case 0x0
            ("head_object", 30,),          # for instance library number
            ("head_c_fe", 32,),            # 0x4
            ("head_11e_z", 32,),           # 0
            ("head_13e_z", 32,),           # 0
            ("head_15e_z", 32,),           # 0
            ("head_17e_z", 32,),           # 0
            ("head_19e_z", 32,),           # 0
            ("head_1be_z", 32,),           # 0
            ("head_1de_z", 7,),            # 0
            ("head_variant", 2,),          # 01/10/11
        )

class HeadVar1(Head):
    ''' First variant of Head '''
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("VAR1")
        super().__init__(seg, address, **kwargs)
        self.get_fields(
            ("hv1_1e7_n", 3,),
            ("hv1_1ea_z", 32,),
            ("hv1_20a_p", 32,),
            ("hv1_22a_d", 52,),		   # World-ID ?
            ("hv1_25e_z", 48,),
            ("hv1_28e_n", 48,),
        )
        self.finish()
        y = bittools.make_one(self, 'hv1_20a_p', D100)
        if y:
            seg.dot.edge(self, y)

class HeadVar2(Head):
    ''' Second variant of Head '''
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("VAR2")
        super().__init__(seg, address, **kwargs)
        #self.compact = True
        self.get_fields(
            ("hv2_1e7_n", 3,),
            ("hv2_1ea_z", 32,),
            ("hv2_20a_p", 32,),
            ("hv2_22a", 32,),
            ("hv2_24a_p", 32,),
            ("hv2_26a_z", 32,),
            ("hv2_28a_n", 160,),
        )
        self.finish()
        bittools.make_one(self, 'hv2_20a_p', bittools.R1kCut)
        bittools.make_one(self, 'hv2_24a_p', bittools.R1kCut)

class HeadVar3(Head):
    ''' Third variant of Head '''
    def __init__(self, seg, address, **kwargs):
        seg.this.add_note("VAR3")
        super().__init__(seg, address, **kwargs)
        #self.compact = True
        self.get_fields(
            ("hv3_1e7_n", 3,),
            ("hv3_1ea_z", 32,),
            ("hv3_20a_p", 32,),
            ("hv3_22a_z", 64,),
            ("hv3_26a_n", 64,),
        )
        self.finish()
        bittools.make_one(self, 'hv3_20a_p', D300)


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
            print("97SEG", seg.this, "Unknown head variant", variant)
            return
        # print("MAP", seg.this, "OBJ", self.head.head_object, "VAR", variant)

        seg.dot.edge(seg.mkcut(0), self.head)
        #self.table = bittools.BitPointerArray(seg, 0x31a, 160)
        #self.table = bittools.BitPointerArray(seg, 0x31a, 160)
        #seg.dot.edge(seg.mkcut(0), self.table)

        y = bittools.make_one(self.head, "head_chains_p", Thing1)
        if y:
            seg.dot.edge(self.head, y)
        if self.head.head_stuff1_p:
            y = someclass(seg, self.head.head_stuff1_p)
            seg.dot.edge(self.head, y)

        # seg.hunt_orphans(26, verbose=False)


