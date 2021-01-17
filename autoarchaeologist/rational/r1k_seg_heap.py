'''
   R1000 Segmented Heaps
   =====================

'''

import time
import os
import subprocess

import autoarchaeologist.rational.r1k_linkpack as LinkPack
import autoarchaeologist.rational.r1k_bittools as bittools
import autoarchaeologist.rational.r1k_97seg as seg97

class TreeNode():
    ''' A binary tree of bits (literally) and pieces of an artifact '''

    def __init__(self, shift):
        self.shift = shift
        self.branches = [None] * 16

    def __iter__(self):
        for i in self.branches:
            if i is None:
                pass
            elif isinstance(i, TreeNode):
                yield from i
            else:
                yield i

    def insert(self, value, payload):
        ''' Recursively insert new foilage '''
        i = (value >> self.shift) & 0xf
        j = self.branches[i]
        if j is None:
            self.branches[i] = (value, payload)
        elif isinstance(j, TreeNode):
            j.insert(value, payload)
        else:
            self.branches[i] = TreeNode(self.shift - 4)
            self.branches[i].insert(*j)
            self.branches[i].insert(value, payload)

    def delete(self, value, payload):
        ''' Remove foilage, but do not prune '''
        i = (value >> self.shift) & 0xf
        j = self.branches[i]
        assert j is not None
        if isinstance(j, TreeNode):
            j.delete(value, payload)
        else:
            assert j[0] == value
            assert j[1] == payload
            self.branches[i] = None

    def last(self):
        ''' Return the last leaf in this branch '''
        for j in reversed(self.branches):
            if j is None:
                pass
            elif isinstance(j, TreeNode):
                rva, rvv = j.last()
                if rva is not None:
                    return rva, rvv
            else:
                return j
        return None, None

    def find(self, value):
        ''' Find the leaf containing value '''
        i = (value >> self.shift) & 0xf
        j = self.branches[i]
        if j is None:
            pass
        elif isinstance(j, TreeNode):
            rva, rvv = j.find(value)
            if rva is not None:
                return rva, rvv
        elif j[0] <= value:
            return j
        i -= 1
        while i >= 0:
            j = self.branches[i]
            if j is None:
                pass
            elif isinstance(j, TreeNode):
                rva, rvv = j.last()
                if rva is not None:
                    return rva, rvv
            elif j[0] <= value:
                return j
            i -= 1
        return None, None

class HeapHead(bittools.R1kSegBase):
    ''' Head of all non code-segments '''
    def __init__(self, seg, chunk, **kwargs):
        super().__init__(seg, chunk, title="SegHeapHead", **kwargs)
        self.compact = True
        self.get_fields(
            ("first_free_bit", 32),
            ("max_bits", 32),
            ("zero", 32),
            ("alloced_bits", 32),
        )

class DotPlot():
    ''' Optional GraphWiz Plot '''
    def __init__(self, seg):
        self.seg = seg
        self.dotfn = seg.this.filename_for(suf=".dot")
        self.svgfn = seg.this.filename_for(suf=".svg")
        self.dotf = open(self.dotfn.filename, "w")
        self.dotf.write('digraph {\n')
        self.empty = self.dotf.tell()
        self.seg.this.add_interpretation(self, self.render_dot)
        self.enabled = False

    def enable(self):
        ''' Produce the dot graphic '''
        self.enabled = True

    def node(self, seg, *args):
        ''' Set node attributes '''
        if args:
            self.dotf.write("X_0x%x\t[" % seg.begin)
            self.dotf.write(",".join(args))
            self.dotf.write("]\n")

    def edge(self, fm, to, *args):
        ''' Create an edge with optional attributes '''
        self.dotf.write("X_0x%x ->" % fm.begin)
        self.dotf.write(" X_0x%x" % to.begin)
        if args:
            self.dotf.write("\t[")
            self.dotf.write(",".join(args))
            self.dotf.write("]")
        self.dotf.write("\n")

    def finish(self):
        ''' run dot(1) '''
        if self.dotf.tell() == self.empty:
            self.enabled = False
        self.dotf.write('}\n')
        self.dotf.close()
        if not self.enabled:
            os.remove(self.dotfn.filename)
            return
        subprocess.run(
            [
                 "dot",
                 "-Tsvg",
                 self.dotfn.filename,
                 "-o",
                 self.svgfn.filename
            ]
        )

    def render_dot(self, fo, _this):
        ''' inline image '''
        if not self.enabled:
            return
        fo.write("<H3>Dot plot</H3>\n")
        fo.write('<img src="%s" width="100%%"/>\n' % self.svgfn.link)

class R1kSegHeap():

    ''' A '97' segment from the backup tape '''

    def __init__(self, this):
        if len(this) > (1<<20):
            return
        if not this.has_note("R1k_Segment"):
            return
        for i in (
            "74_tag",        # CODE
            "75_tag",        # CODE
            "81_tag",        # 12MB, some strings incl TRIG_LIB
            "83_tag",        # 2.7MB, no strings
            "84_tag",        # 300KB, no strings
            "e3_tag",        # sources
            "R1k6ZERO",      # texts
        ):
            if this.has_note(i):
                return
        t0 = time.time()

        bits = bin(int.from_bytes(b'\xff' + this[:16].tobytes(), 'big'))[10:]

        x = int(bits[:32], 2)
        y = int(bits[32:64], 2)
        if int(bits[64:96], 2):
            return
        z = int(bits[96:128], 2)

        if x > z:
            return
        if y & 0xfff != 0xfff:
            return
        if z & 0xfff != 0xfff:
            return

        i = z
        j = 0
        while i > 15:
            i >>= 4
            j += 4
        self.tree = TreeNode(j)

        self.this = this
        self.end = x + 0x7f
        self.type_case = this.type_case
        self.fdot = None
        print("?R1SH", this)

        self.dot = DotPlot(self)

        chunk = bittools.R1kSegChunk(
            0,
            bin(int.from_bytes(b'\xff' + this.tobytes(), 'big'))[10:10+self.end]
        )
        assert len(chunk) > 0
        self.tree.insert(0, chunk)


        self.starts = {}
        self.starts[0] = chunk

        self.tfn = this.add_utf8_interpretation("Segmented Heap")
        self.tfile = open(self.tfn.filename, "w")

        self.head = HeapHead(self, self.cut(0x0, 0x80))

        try:
            self.ponder()
        except Exception as err:
            print("PONDERING FAILED", this, err)
            raise

	# Render to a temporary file while parsing, so we can delete
	# all the bitmaps, otherwise the memory footprint roughly
	# doubles.

        self.render_chunks(self.tfile)
        self.tfile.close()

        self.dot.enable()
        self.dot.finish()

        del self.starts
        del self.tree
        dt = time.time() - t0
        if dt > 20:
            print(this, "SH Pondering took %.1f" % dt)

    def __getitem__(self, idx):
        return self.starts[idx]

    def get(self, idx):
        ''' Look for chunk at specific address '''
        return self.starts.get(idx)

    def label(self, adr):
        ''' return a representation of what is at this address '''
        i = self.starts.get(adr)
        if not adr or not i:
            return "0x%x" % adr
        return str(i)

    def ponder(self):
        ''' Ponder the contents of this segment '''
        if self.this[0x10:0x24].tobytes() == b'This is a Link Pack.':
            try:
                LinkPack.R1kSegLinkPack(self, self.mkcut(0x80))
            except bittools.MisFit as err:
                print("FAIL LINKPACK", self.this, err)
                raise
            return # no hunting, dissector is fairly competent.

        if self.this.has_note('97_tag'):
            try:
                seg97.R1kSeg97(self)
            except bittools.MisFit as err:
                print("FAIL SEG97", self.this, err)
            return

        # Make copy of chunks list, because it will be modified along the way
        for chunk in list(y for _x, y in self.tree):
            if not chunk.owner:
                bittools.hunt_array_strings(self, chunk)

        if len(self.this) > 100000:
            return
        # Make copy of chunks list, because it will be modified along the way
        for chunk in list(y for _x, y in self.tree):
            if not chunk.owner:
                bittools.hunt_strings(self, chunk)

    def hunt_orphans(self, width=32, verbose=True):
        ''' Hut for `width` bit pointers to start of existing chunks '''
        for _i, chunk in self.tree:
            if chunk.begin < 0x1000: # Too many false positives with small numbers
                continue
            cuts = self.hunt(bin((1<<width) + chunk.begin)[3:])
            for chunk2, offset, address in cuts:
                if chunk2.owner is not None:
                    continue
                if verbose:
                    print(
                        "Orphan ptr from %s+0x%x" % (str(chunk2), offset),
                        "to", chunk
                    )
                bittools.BitPointer(self, address, size=width, ident="orphan")

    def hunt(self, pattern):
        ''' hunt for particular pattern '''
        cuts = []
        for _i, chunk in self.tree:
            offset = 0
            while True:
                j = chunk.bits[offset:].find(pattern)
                if j < 0:
                    break
                cuts.append((chunk, offset + j, chunk.begin + offset + j))
                offset += j + 1
        return cuts

    def mkcut(self, idx):
        ''' Return cut at address, make anonymous cut if there is none '''
        t = self.starts.get(idx)
        if not t:
            t = self.cut(idx)
        return t

    def cut(self, where, length=-1):
        ''' Cut out a chunk '''
        assert where or length == 0x80
        if where >= self.end:
            raise bittools.MisFit("0x%x is past end of allocation (0x%x)" % (where, self.end))

        chunk = self.starts.get(where)
        if not chunk:
            offset, chunk = self.tree.find(where)
            assert offset is not None
            assert offset == chunk.begin
            assert chunk.begin <= where
            assert chunk.begin + len(chunk) > where

        assert self.starts.get(chunk.begin) == chunk

        if chunk.owner:
            raise bittools.MisFit(
                "At 0x%x " % where + " has " + str(chunk)
            )

        if chunk.begin == where and length in (-1, len(chunk)):
            return chunk

        if where > chunk.begin:
            self.tree.delete(chunk.begin, chunk)

            i = where - chunk.begin
            newchunk = bittools.R1kSegChunk(chunk.begin, chunk.bits[:i])
            chunk.bits = chunk.bits[i:]
            chunk.begin += i

            self.starts[chunk.begin] = chunk
            assert len(chunk) > 0
            self.tree.insert(chunk.begin, chunk)

            self.starts[newchunk.begin] = newchunk
            assert len(newchunk) > 0
            self.tree.insert(newchunk.begin, newchunk)

        if length in (-1, len(chunk)):
            return chunk

        if length > len(chunk):
            raise bittools.MisFit("Has " + str(chunk) + " want 0x%x" % length)

        assert length < len(chunk)

        self.tree.delete(chunk.begin, chunk)

        newchunk = bittools.R1kSegChunk(chunk.begin, chunk.bits[:length])

        self.starts[newchunk.begin] = newchunk
        assert len(newchunk) > 0
        self.tree.insert(newchunk.begin, newchunk)

        chunk.bits = chunk.bits[length:]
        chunk.begin += length

        self.starts[chunk.begin] = chunk
        assert len(chunk) > 0
        self.tree.insert(chunk.begin, chunk)

        return newchunk

    def render_chunks(self, fo):
        ''' Ask all the chunks to chime in '''
        loffset = 0
        for offset, chunk in self.tree:
            assert offset == loffset
            loffset += len(chunk)
            fo.write(str(chunk) + ":")
            if chunk.owner is None:
                fo.write(" ===================\n")
                bittools.render_chunk(fo, chunk)
            else:
                chunk.owner.render(chunk, fo)
        assert loffset == self.end
