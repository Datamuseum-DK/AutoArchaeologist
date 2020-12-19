
import sys
import html
import autoarchaeologist.generic.hexdump as hexdump
import autoarchaeologist.generic.bitdata as bitdata

fof = open("/tmp/_fof", "w")


class R1kE3Objects(bitdata.BitRecord):
    def __init__(self, this):
        if not this.has_note("e3_tag"):
            return

        self.this = this
        self.verbose = False
        this.add_interpretation(self, self.render_text)
        this.add_interpretation(self, self.render_meta)
        this.add_interpretation(self, self.render_unclaimed)
        self.this.add_type("Ada Source")
        if len(self.this) > 1<<16:
            self.this.add_note("Long Ada Source")

        pb = bitdata.PackedBits(this[:0x400])
        super().__init__(
            (
                ("nblk1", 19, True),
                ("hdr0", 77, False),
                ("nblk2", 19, False),
                ("hdr1", 8, False),
                ("hdr2", 63, False),
                ("hdr3", 12, False),
                ("nid", 16, True),
                ("hdr5", 17, False),
                ("hdr6", 16, True),
            ),
            bits=pb,
        )
        assert self.hdr0 == 0x1f81ffffffff00000000
        assert self.hdr1 == 0xff
        assert self.hdr2 == 0x7c0511030fa00010
        assert self.hdr5 == 0x00002
        assert self.nblk1 == self.nblk2
        assert self.nblk1 + 1 == self.hdr3
        self.recs = []
        for i in range(100):
            j = bitdata.BitRecord(
                (
                    ("rec0", 8, True),
                    ("rec1", 8, True),
                    ("rec2", 8, True),
                    ("rec3", 11, True),
                ),
                bits=pb,
            )
            self.recs.append(j)
        self.tail0 = pb.get(82)
        assert not pb.get(3495)
        self.tail1 = pb.get(68)
        assert not pb.get(800)
        assert not len(pb)
        self.done = {}

    def render_meta(self, fo, _this):
        if self.nblk1 > 100:
            print("LONG SOURCE", self.this, self.nblk1)
        fo.write("<H3>E3 Meta Data</H3>\n")
        fo.write("<pre>\n")
        fo.write(self.render(show_tag=True, one_per_line=True) + "\n")
        for i in range(min(100, self.nblk1)):
            fo.write("        [0x%02x] " % i)
            fo.write(self.recs[i].render(show_tag=True, fixed_width=True))
            fo.write("\n")
        fo.write("    tail 0x%x 0x%x" % (self.tail0, self.tail1))
        fo.write("\n")
        if self.nid:
            fo.write("Free Block Chain:\n")
            i = self.nid
            while i:
                self.done[i] = True
                fo.write("  0x%x: " % i)
                that = self.this[i<<10:(i<<10)+16]
                hexdump.hexdump_to_file(that, fo)
                i = (that[0] << 8) | that[1]
 
        fo.write("</pre>\n")

    def render_block(self, fo, nbr):
        adr = nbr << 10
        that = self.this[adr:adr+0x400].tobytes()
        # hexdump.hexdump_to_file(that, fo)
        next = (that[0] << 8) | that[1]
        end = (that[2] << 8) | that[3]
        if self.verbose:
            fo.write(" next=0x%x length=0x%x\n" % (next, end))
        end += 4
        ptr = 4
        while ptr < end:
            flag = that[ptr]
            if not flag and not self.verbose:
                fo.write("\n")
            length = that[ptr + 1]
            length2 = that[ptr + length + 2]
            if length != length2:
                print("LL MISMATCH", self.this, "0x%x" % ptr, flag, length, length2)
                fo.write("\nXXX LL mismatch @0x%x: 0x%x 0x%x\n" % (ptr, length, length2))
                hexdump.hexdump_to_file(that, fo)
                return 0
            if self.verbose:
                fo.write("%04x 0x%02x [%02x] " % (ptr, flag, length))
            t = ""
            ptr += 2
            for a in that[ptr:ptr+length]:
                if 0x20 <= a <= 0x7e:
                    t += "%c" % a
                else:
                    t += "\\x%02x" % a
            fo.write(html.escape(t))
            if self.verbose:
                fo.write("\n")
            ptr += length + 1
        return next
                
    def render_text(self, fo, _this):
        fo.write("<H3>E3 Source Code</H3>\n")
        fo.write("<pre>\n")
        next = self.recs[0].rec2
        while next:
            # print(self.this, "0x%x" % next, self.done.get(next))
            assert next not in self.done
            self.done[next] = True
            if self.verbose:
                 fo.write("\n[0x%02x] " % next)
            try:
                next = self.render_block(fo, next)
            except Exception as e:
                fo.write(" FAILED: 0x%x" % next + str(e) + "\n")
                print("EEE", self.this, next, e)
                next = 0
        fo.write("</pre>\n")

    def render_unclaimed(self, fo, _this):
        l = []
        for i in range(1, len(self.this) >> 10):
            if not i in self.done:
                print("UNCLAIMED BLOCK", self.this, "0x%x" % i)
                l.append(i)
        if not l:
            return
        fo.write("<H3>E3 Unclaimed Blocks</H3>\n")
        fo.write("<pre>\n")
        for i in l:
            fo.write("Unclaimed sector 0x%x\n" % i)
            hexdump.hexdump_to_file(self.this[i<<10:(i+1)<<10], fo)
        fo.write("</pre>\n")
