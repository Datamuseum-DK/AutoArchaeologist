'''
   R1000 '7b' segments
   ===================

   Based on number of blocks in different snapshots, this is probably the "File"
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
            #f2c_=32,
            #f2d_=32,
            #f3_=0x42,
            **kwargs
        )

class Head2(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=True,
            f0a_=32,
            f1b_=32,
            f2a_=65,
        )


class Thing1(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            thing1_=32,
            f1_=32,
            f2_=32,
            f3_=32,
            f4_=32,
            f5_=1,
            **kwargs
        )

        assert self.thing1 == 3

        if self.f3:
            Thing1(up, self.f3).insert()
        if self.f2:
            Thing2(up, self.f2).insert()
        if self.f4:
            Thing1(up, self.f4).insert()

class Thing2(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            thing2_=32,
            f0_=35,
            **kwargs
        )
        Thing3(up, self.thing2).insert()

class Thing3(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            z0_=1068,
            #z0_=113,
            #z1_=Thing4,
            #z2_=339,
            #z19_=Thing4,
            #z23_=24,
            #z24_=18,
            #z25_=28,
            #z26__=93,
            **kwargs
        )
        #assert not self.z26_

class Thing4(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            t4a_=32,
            t4b_=31,
            t4c_=32,
            t4d_=32,
        )

class R1kSeg7b(bv.BitView):
    ''' ... '''
    def __init__(self, this):
        if not hasattr(this, "r1ksegment"):
            return
        if this.r1ksegment.tag != 0x7b:
            return
        super().__init__(this)
        y = SegHeap(self, 0).insert()
        self.hi = y.used
        self.head = Head(self, 0x80).insert()

        n = 0
        for a in range(0x242, 0x8ebe, 333):
            OurStruct(self, a, what_=-333).insert()
            n+=1
        print("N", n)

        Head2(self, 0x1c0).insert()
        OurStruct(self, 0x98de, x0_=32).insert()
        Thing1(self, 0x1207d).insert()

        for a in range(0x3f0):
            y = OurStruct(self, 0x98fe + a * 32, ptr_=32).insert()
            Thing1(self, y.ptr).insert()

        self.render()
