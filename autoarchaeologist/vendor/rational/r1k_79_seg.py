'''
   R1000 '79' segments
   ===================

   Based on number of blocks in different snapshots, this is probably the "Ada"
   daemon's metadata.

'''

from ...generic import bitview as bv

class OurStruct(bv.Struct):
    def __init__(self, up, lo, **kwargs):

        # Set these early for diags, .done() may happen much later
        self.lo = lo
        self.name = self.__class__.__name__
        super().__init__(up, lo, name=self.name, **kwargs)

class SegHeap(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=True,
            used_=32,
            f1_=32,
            f2_=32,
            alloc_=32,
            **kwargs
        )

class Head(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=True,
            f0a_=32,
            f0b_=32,
            f0c_=32,
            f0d_=32,
            f1a_=32,
            f1b_=32,
            f1c_=32,
            f1d_=32,
            f2a_=32,
            f2b_=32,
            f2c_=32,
            f2d_=32,
            f3a_=7,
            f3b_=32,
            f3c_=32,
            f4a_=32,
            f4b_=32,
            f4c_=32,
            f4d_=32,
            f4e_=32,
            f4f_=32,
            f4g_=32,
            f4h_=32,
            **kwargs
        )

class Thing1(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            thing1_=32,
            **kwargs
        )
        if self.thing1:
            Thing2(up, self.thing1).insert()

class Thing2(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            f6_=7,
            f7_=31,
            f8_=31,
            f9_=31,
            **kwargs
        )

class Thing3(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            thing3_=32,
            f00_=32,
            f01_=32,
            f02_=32,
            f03_=32,
            **kwargs
        )

        Thing4(up, self.f01).insert()
        if self.f02:
            Thing3(up, self.f02).insert()
        if self.f03:
            Thing3(up, self.f03).insert()

class Thing4(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            t4a_=32,
            t4b_=35,
        )
        Thing5(up, self.t4a).insert()

class Thing5(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            t5a_=-1024,
        )

class Thing6(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            t6a_=205,
            t6w_=32,
            t6x_=32,
            t6y_=32,
            t6z_=32,
        )
        up.t6[self.lo] = self
        if self.t6w:
            up.todo.append((Thing6, self.t6w))
        if self.t6x:
            up.todo.append((Thing6, self.t6x))
        if self.t6y:
            up.todo.append((Thing6, self.t6y))
        if self.t6z:
            up.todo.append((Thing6, self.t6z))

class R1kSeg79(bv.BitView):
    ''' ... '''
    def __init__(self, this):
        if not hasattr(this, "r1ksegment"):
            return
        if this.r1ksegment.tag != 0x79:
            return
        super().__init__(this)
        y = SegHeap(self, 0).insert()
        self.hi = y.used

        self.head = Head(self, 0x80).insert()

        for a in range(self.head.f4f, self.head.f4h - 32, 32):
            y = OurStruct(self, a, what_=32).insert()
        for a in range(self.head.f4h, self.head.f2b, 132):
            Thing1(self, a).insert()

        self.todo = []
        self.t6 = {}
        Thing6(self, self.head.f2b).insert()
        while self.todo:
            i, j = self.todo.pop(0)
            if j not in self.t6:
                i(self, j).insert()

        for a in range(self.head.f2d, 0x15bb5a2, 32):
            y = OurStruct(self, a, what2_=32).insert()
            if y.what2:
                Thing3(self, y.what2).insert()

        self.render()
