
'''
   RC7000/RC3600 AUTOLOADER file
   -----------------------------

   Typically paper tapes.

   See RCSL 44-RT-551 RC3600 Binary Loader (30000212)
'''

from ..base import octetview as ov

class Preamble(ov.Struct):
    ''' The loader preamble-loader '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            wc_=ov.Be16,
            more=True,
        )
        if 0xffe0 < self.wc.val < 0xfff8:
            print("PP", hex(self.wc.val), hex(self.hi), hex(len(tree.this)))
            self.add_field(
                "preamble",
                ov.Array(0xffff - self.wc.val, ov.Be16,)
            )
            self.good = True
        else:
            self.good = False
        self.done()


class BinaryLoader(ov.Struct):
    ''' The binary loader '''
    def __init__(self, tree, lo, cls):
        super().__init__(
            tree,
            lo,
            wc_=cls,
            more=True,
        )
        if self.wc.val > 0xff80:
            self.add_field(
                "loader",
                ov.Array(0x10000 - self.wc.val, cls)
            )
        self.done()

class AbsBinRecord(ov.Struct):
    ''' we should really steal it from data_general/absbin... '''
    def __init__(self, tree, lo, cls):
        super().__init__(
            tree,
            lo,
            wc_=cls,
            adr_=cls,
            csum_=cls,
            more=True,
        )
        if self.wc.val >= 0xfff0:
            self.add_field(
                "data",
                ov.Array(0x10000 - self.wc.val, cls),
            )
        elif self.wc.val >= 0xffef:
            self.add_field(
                "data",
                ov.Array(1, cls),
            )
        self.done()

class SyncByte(ov.Opaque):
    ''' just for the name '''

class Leader(ov.Opaque):
    ''' just for the name '''

class AutoLoad(ov.OctetView):

    ''' Autoloading paper tapes.
        See: RCSL 44-RT-551 RC3600 Binary Loader (30000212)
    '''

    def __init__(self, this):

        #if not this.top in this.parents:
        #    return

        super().__init__(this)

        adr = 0
        while adr < len(this) and this[adr] == 0:
            adr += 1

        if len(this) - adr < 0x40:
            return
        sync = SyncByte(self, adr, width=1).insert()

        preamble = Preamble(self, sync.hi).insert()
        if not preamble.good:
            #print(this, "Bad preamble", preamble)
            return

        this.add_type("AutoLoader")

        that = this.create(start = sync.lo, stop = preamble.hi)
        that.add_type("BinaryLoaderPreamble")

        wc = ov.Be16(self, preamble.hi)
        if wc.val > 0xff80:
            loader = BinaryLoader(self, preamble.hi, ov.Be16).insert()
        else:
            loader = BinaryLoader(self, preamble.hi, ov.Le16).insert()
        if loader.wc.val < 0xff80:
            return

        that = this.create(start = loader.lo, stop = loader.hi)
        that.add_type("BinaryLoader")

        adr = loader.hi

        cls = ov.Le16
        abrecs = []
        while adr < len(this):
            a0 = adr
            while a0 < len(this) and this[a0] == 0:
                a0 += 1
            if a0 > adr:
                ld = Leader(self, adr, a0 - adr)
                adr = a0
            else:
                ld = None
            y = AbsBinRecord(self, adr, cls)
            wc =  y.wc.val
            if wc == 1 or wc >= 0xffef:
                if ld:
                    ld.insert()
                y.insert()
                abrecs.append(y)
                adr = y.hi
            else:
                return
            if wc == 1:
                break

        that = this.create(start = abrecs[0].lo, stop = abrecs[-1].hi)

        #self.add_interpretation()
