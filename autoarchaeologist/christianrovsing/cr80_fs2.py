

'''
   CR80 Filesystem type 2

   See https://ta.ddhf.dk/wiki/Bits:30004479
'''

import struct

import autoarchaeologist.generic.octetview as ov

from .cr80_util import *

class Text_(ov.Octets):
    def __init__(self, up, lo, *args, **kwargs):
        super().__init__(up, lo, width=self.width, *args, **kwargs)
        t = []
        for a in range(self.width):
            if a & 1:
                 t.append(self.this[lo + a])
                 t.append(b)
            else:
                 b = self.this[lo + a]
        try:
            i = t.index(0)
            if i > 0:
                t = t[:i]
        except ValueError:
            pass
        self.txt = "".join("%c" % x for x in t)

    def render(self):
        yield '»' + self.txt + '«' + " " * (self.width - len(self.txt))

class DataSect(ov.Octets):
    def __init__(self, up, lo, bfd, n):
        super().__init__(up, lo, width=512)
        self.bfd = bfd
        self.n = n

    def render(self):
        yield "DataSector " + str(self.bfd) + " #0x%x" % self.n
        return
        for a in range(0, 512, 16):
            y = ov.Octets(self.up, self.lo + a, 16)
            yield from ("  " + x for x in y.render())

class Text16_(Text):
    width = 16
        
class HomeBlock(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=True,
            label_=Text16,
            magic_=ov.Be16,
            f00_=ov.Be16,
            f01_=ov.Be16,
            f02_=ov.Be16,
            f03_=ov.Be16,
            f04_=ov.Be16,
            f05_=ov.Be16,
            f06_=ov.Be16,
            f07_=ov.Be16,
            f08_=ov.Be16,
            more=True,
        )
        self.done(pad=0x200)

    def render(self):
        yield "Superblock"
        yield from super().render()

class IndexBlock(ov.Struct):
    def __init__(self, up, lo, bfd):
        super().__init__(
            up,
            lo,
            vertical=True,
            pad00_=ov.Be16,
            pad01_=ov.Be16,
            more=True,
        )
        self.bfd = bfd
        self.list = []
        for i in range(bfd.nsect.val):
            y = self.addfield(None, ov.Be16)
            self.list.append(y)
            y = self.addfield(None, ov.Be16)
            
        self.done(pad=0x200)

    def iter_sectors(self):
        for i in self.list:
            yield i.val

    def render(self):
        a = list(super().render())
        yield a[0]
        yield "  bfd = " + str(self.bfd)
        yield from a[1:]

class BasicFileDesc(ov.Struct):
    def __init__(self, up, nbr, lo):
        self.nbr = nbr
        super().__init__(
            up,
            lo,
            vertical=True,
            bfd00_=ov.Be16,
            bfd01_=ov.Be16,
            bfd02_=ov.Be16,
            type_=ov.Be16,
            length_=ov.Be16,
            bfd05_=ov.Be16,
            nsect_=ov.Be16,
            bfd07_=ov.Be16,
            kind_=ov.Be16,
            sector_=ov.Be16,
            bfd0a_=ov.Be16,
            bfd0b_=ov.Be16,
            flags_=ov.Be16,
            bfd0d_=ov.Be16,
            min3_=ov.Be16,
            bfd0f_=ov.Be16,
            more=True,
        )
        self.done(pad=0x200)
        self.sfd = None
        self.that = None
        self.block_list = []
        self.bad_bl = False
        if not self.valid():
            return

        if self.kind.val == 0:
            for i in range(self.nsect.val):
                self.block_list.append(self.sector.val + i)
        elif self.kind.val == 1:
            self.index_block = IndexBlock(up, self.sector.val << 9, self)
            self.index_block.insert()
            self.block_list = list(self.index_block.iter_sectors())
        elif self.kind.val == 5:
            self.index_block = IndexBlock(up, self.sector.val << 9, self)
            self.index_block.insert()
            for bn in self.index_block.iter_sectors():
                 for mult in range(5):
                     self.block_list.append(bn + mult)

        if 0 in self.block_list:
            print("BFD zero in BL", self, self.block_list)
            self.block_list = []
            self.bad_bl = True
        if self.block_list and max(self.block_list) << 9 > len(self.up.this):
            print("BFD huge sec# BL", self, hex(max(self.block_list)))
            self.block_list = []
            self.bad_bl = True
        # print("bfd", hex(self.lo), hex(self.hi), self)

    def valid(self):
        if self.type.val not in (0, 10, 12, 14):
             return False
        if self.bad_bl:
             return False
        return True

    def __str__(self):
        return " ".join(
            (
                 "{BFD" if self.valid() else "{bfd",
                 "#0x%x" % self.nbr,
                 "type=" + hex(self.type.val),
                 "kind=" + hex(self.kind.val),
                 "length=" + hex(self.length.val),
                 "sector=" + hex(self.sector.val),
                 "nsect=" + hex(self.nsect.val),
                 "flags=" + hex(self.flags.val),
                 "min3=" + hex(self.min3.val),
                 "" if self.sfd is None else self.sfd.fname.txt,
                 "" if self.that is None else self.that.top.html_link_to(self.that),
                 "}",
            )
        )

    def render(self):
        a = list(super().render())
        yield a[0]
        yield "  nbr = #0x%x" % self.nbr
        yield from a[1:]

    def iter_sectors(self):
        yield from self.block_list

class SymbolicFileDesc(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=False,
            valid_=ov.Be16,
            fname_=Text16,
            file_=ov.Be16,
            bfd3_=12,
        )

class SfdSect(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=True,
            more=True,
        )
        for off in range(0, 512, 32):
            valid = ov.Be16(up, lo + off)
            if valid.val == 1:
                y = self.addfield(None, SymbolicFileDesc)
                up.add_sfd(y)
            else:
                y = self.addfield(None, 32)
 
        self.done(pad=0x200)
 

class CR80_FS2(ov.OctetView):

    def __init__(self, this):
        if not this.has_type("ileave2"):
            return
        if this[0x10] or this[0x11] != 0x2:
            return
        print("CRFS2", this)
        this.add_type("crfs2")
        super().__init__(this)

        self.sb = HomeBlock(self, 0x0)
        self.sb.insert()

        self.bfdloc = ((self.this[0x204] << 8) | self.this[0x205]) << 9
        print("BFDLOC", hex(self.bfdloc))
        bfd_dir = BasicFileDesc(self, 0, self.bfdloc)
        bfd_dir.insert()
        self.bfd = {}
        for n, i in enumerate(bfd_dir.iter_sectors()):
            if i << 9 == self.bfdloc:
                self.bfd[n] = bfd_dir
                continue
            try:
                j = BasicFileDesc(self, n, i << 9)
                j.insert()
                self.bfd[n] = j
            except Exception as err:
                print("BDF error", hex(i << 9), err)
                break

        for n, bfd in self.bfd.items():
            if bfd.type.val == 0x000a:
                for i in bfd.iter_sectors():
                    y = SfdSect(self, i << 9)
                    y.insert()

        for n, bfd in self.bfd.items():
            # print(n, bfd, bfd.sfd, list(bfd.iter_sectors()))
            img = bytearray()
            for ns, i in enumerate(bfd.iter_sectors()):
                off = i << 9
                img += this[off:off + 512]
                if bfd.nbr and bfd.type.val != 0x000a:
                    y = DataSect(self, off, bfd, ns)
                    y.insert()
            i = bfd.length.val
            if not len(img) or not i:
                continue
            if i >= len(img):
                pass
            elif i & 1:
                #print("ODD", i, len(img))
                j = img[:i - 1]
                j.append(img[i])
                img = j
            else:
                img = img[:i]
            bfd.that = this.create(bits=img)
            bfd.that.add_type("CR80FILE")
            bfd.that.byte_order = [1, 0]
            if bfd.sfd:
                bfd.that.set_name(bfd.sfd.fname.txt)

        this.add_interpretation(self, self.html_interpretation)
        self.render()

    def html_interpretation(self, fo, _this):
        fo.write("<H3>CR80FS2 DIRLIST</H3>\n")
        fo.write("<PRE>")
        for n, bfd in self.bfd.items():
            fo.write(str(bfd) + "\n")
        fo.write("</PRE>")

    def add_sfd(self, sfd):
        self.bfd[sfd.file.val].sfd = sfd