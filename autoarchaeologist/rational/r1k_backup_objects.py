'''
   R1K Backup Tapes
   ----------------

   This file contains the "object-aspects" of taking a backup apart.
   The "tape-aspects" are handled in `r1k_bakcup.py`
'''

import tempfile
import mmap

import autoarchaeologist.generic.hexdump as hexdump
import autoarchaeologist.generic.bitdata as bitdata

def make_void():
    tf = tempfile.TemporaryFile()
    tf.write(b'\x00' * 1024)
    tf.flush()
    return memoryview(mmap.mmap(tf.fileno(), 0, access=mmap.ACCESS_READ))
void = make_void()

class IndirBlock(bitdata.BitRecord):
    '''
    Indirect Block
    '''

    def __init__(self, vol, blockno):
        octets = vol[blockno]
        assert vol.binfo(blockno)[1][1], vol.binfo(blockno)
        pb = bitdata.PackedBits(octets)
        super().__init__(
            (
                ("hdr0", 1, False),
                ("objid", 64, True),
                ("diskvol", 5, True),
                ("hdr1", 4, False),
                ("blockno", 20, True),
                ("hdr2", 8, False),
                ("hdr3", 56, False),
                ("hdr4", 32, False),
                ("hdr5", 28, False),
                ("indir_level", 2, True),
                ("hdr6", 64, False),
                ("hdr7", 32, False),
                ("nblocks", 32, False),
            ),
            "IndirBlock",
            bits=pb,
        )
        vol.block_use[blockno] = "objid 0x%x indir%d" % (self.objid, self.indir_level)
        self.vol = vol
        assert blockno == self.blockno, "blockno 0x%x vs. 0x%x" % (blockno, self.blockno)
        # These fields are constant & woo-doo
        assert self.hdr0 == 0, "hdr0=0x%x" % self.hdr0
        assert self.hdr1 == 0, "hdr1=0x%x" % self.hdr2
        assert self.hdr2 == 1, "hdr2=0x%x" % self.hdr2
        assert self.hdr3 == 0, "hdr3=0x%x" % self.hdr3
        assert self.hdr4 == 0x8144, "hdr4=0x%x" % self.hdr4
        assert self.hdr5 in (0x0, 0x28), "hdr5=0x%x" % self.hdr5
        assert self.hdr6 == 0x4000001ea0, "hdr6=0x%x" % self.hdr6
        assert self.hdr7 == 1, "hdr7=0x%x" % self.hdr7
        assert self.nblocks == 0xa2, "nblocks=0x%x" % self.nblocks

        self.blocks = []
        for _i in range(self.nblocks):
            x = pb.get(28)
            y = pb.get(20)
            self.blocks.append((x, y))

    def __iter__(self):
        if self.indir_level == 1:
            for _i, j in self.blocks:
                self.vol.block_use[j] = "objid 0x%x data via indir%d @0x%05x" % (
                    self.objid, self.indir_level, self.blockno
                )
                yield j
        else:
            for _i, j in self.blocks:
                assert j
                yield from IndirBlock(self.vol, j)


class R1kBackupObject():
    ''' whatever that is... '''

    def __init__(self, up, vol, this, space_info):
        self.up = up
        self.vol = vol
        self.this = this
        self.space_info = space_info
        self.n_block = space_info[6]
        self.block_list = space_info[13:]
        self.indir = None
        self.obj = None

    def get_data(self):
        for block1 in self.block_list:
            if not block1:
                yield None
                continue
            if not self.vol.binfo(block1)[1][1]:
                self.vol.block_use[block1] = "objid 0x%x data" % self.space_info[4]
                yield block1
                continue
            yield from IndirBlock(self.vol, block1)

    def resolve(self):
        if self.space_info[8] != 0x97:
            return
        i = 0
        blocks = []
        sparse = False
        for j in self.get_data():
            if j:
                blocks.append(self.vol[j])
                i += 1
                if i == self.n_block:
                    break
            else:
		# XXX: This should probably be zero bytes.
                blocks.append(void[:1024])
                sparse = True
        self.obj = self.vol.space_info.this.create(records=blocks)
        if sparse:
            self.obj.add_note("Sparse_R1k_Segment")
        self.obj.add_note("R1k_Segment")
        self.obj.add_note("%02x_tag" % self.space_info[8])
        self.obj.add_interpretation(self, self.render_obj)

    def render_space_info(self):
        t = ""
        for j, w in zip(self.space_info, [2, 4, 2, 6, 14, 2, 4, 2, 2, 10, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]):
            t += ("%x" % j).rjust(w+1)
        if self.obj:
            t += " [" + self.obj[:20].tobytes().hex()
            t += "] // " + self.obj.summary()
        return t

    def render_obj(self, fo, this):
        if len(this.interpretations) > 1:
            return
        fo.write("<H3>R1K Object</H3>\n")
        fo.write("<pre>\n")
        fo.write(self.render_space_info() + "\n")
        for n, i in enumerate(self.obj.iterrecords()):
            if n > 10:
                fo.write("\nTruncated…\n")
                break
            fo.write("\n")
            fo.write("Block #0x%x\n" % n)
            hexdump.hexdump_to_file(i, fo)
        fo.write("</pre>\n")
