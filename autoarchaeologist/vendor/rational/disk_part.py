
#
# See:
#    file:///critter/aa/r1k_dfs/34/344289524.html

import struct

from ...generic import hexdump

class R1K_DFS():

    def __init__(self, this, sb):
        self.this = this
        self.sb = sb
        print("SB", sb)

        for i in range(2, len(self.sb), 2):
            j = int.from_bytes(self.sb[i:i+2], 'big')
            if j in (0x00, 0x0d,):
                break
            print("SBF", i, j)

class R1K_Disk_Partition():

    def __init__(self, this):
        if this.top not in this.parents:
            return
        print("?R1KDP", this)

        self.bootcode = this.create(start=0x000, stop=0x400)
        self.bootcode.add_type("R1K_Bootcode")

        self.bootdir = this.create(start=0x400, stop=0x800)
        self.bootdir.add_type("R1K_Bootdir")

        self.label = this.create(start=0x800, stop=0x1000)
        self.label.add_type("R1K_PartitionTable")

        self.dfs_sb = this.create(start=0x1000, stop=0x1400)
        self.dfs_sb.add_type("R1K_DFS_Superblock")

        if self.label[0:0x400].tobytes() != self.label[0x400:0x800].tobytes():
            print("NB: Labels differ")
        self.label.add_interpretation(self, self.render_label)
        b = self.label[:0x400]
        self.geom = [struct.unpack(">HBB", b[x:x+4]) for x in range(0x08, 0x34, 4)]
        self.secsize = 512
        self.nsect = self.geom[0][2]
        self.nhead = self.geom[0][1]
        self.ncyl = self.geom[0][0]
        self.partitions = []
        for i in range(1, len(self.geom) - 1, 2):
            g_start = self.geom[i]
            start = self.calc_lba(g_start)
            g_stop = self.geom[i + 1]
            stop = self.calc_lba(g_stop) + self.secsize
            print(g_start, start, g_stop, stop)
            y = this.create(start=start, stop=stop)
            y.add_type("R1K_Partition_%d" % (i // 2))
            self.partitions.append((g_start, g_stop,y))

        R1K_DFS(this, self.dfs_sb)
        if False:
            for i in (0x2be8, 0x2984, 0x2884, 0x2784, 0x2684, 0x2584, 0x2484, 0x2384, 0x2284, 0x1801, 0x3dd6):
                y = this.create(start = i<<10, stop = (i+1)<<10)
                y.add_type("FSB")
                y.add_note("at 0x%x" % i)
                R1K_DFS(this, y)

    def calc_lba(self, g):
        rv = g[0] * self.nhead * self.nsect * self.secsize
        rv += g[1] * self.nsect * self.secsize
        rv += g[2] * self.secsize
        return rv

    def render_chs(self, g, extra=0):
        return "[%04dc %02dh %02ds 512b] = 0x%08x" % (g[0], g[1], g[2], self.calc_lba(g) + extra)

    def render_label(self, fo, _this):
        fo.write("<H3>R1K Disk Label</H3>\n")
        fo.write("<pre>\n")
        hexdump.hexdump_to_file(self.label[0x000:0x008], fo)
        fo.write("\n")
        fo.write("Disk Geometry:       " + self.render_chs(self.geom[0]) + "\n")
        for g_start, g_stop, part in self.partitions:
            fo.write("Partition:       " + self.render_chs(g_start))
            fo.write(" to " + self.render_chs(g_stop, self.secsize))
            fo.write(" // " + part.summary() + "\n")
        fo.write("\n")
        hexdump.hexdump_to_file(self.label[0x036:0x400], fo)
        fo.write("</pre>\n")
