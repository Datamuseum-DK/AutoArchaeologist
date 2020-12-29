'''
   R1000 Segmented Heaps
   =====================

'''

import tempfile
import html

import autoarchaeologist.rational.r1k_linkpack as LinkPack
import autoarchaeologist.rational.r1k_bittools as BitTools

class R1kSegHeap():

    ''' A '97' segment from the backup tape '''

    def __init__(self, this):
        if not this.has_note("R1k_Segment"):
            return
        bits = bin(int.from_bytes(b'\xff' + this[:16].tobytes(), 'big'))[10:] 
        self.f0 = int(bits[:32], 2)
        self.f1 = int(bits[32:64], 2)
        self.f2 = int(bits[64:96], 2)
        self.f3 = int(bits[96:128], 2)
        if self.f0 > self.f3:
            return
        if self.f2:
            return
        if self.f1 & 0xfff != 0xfff:
            return
        if self.f3 & 0xfff != 0xfff:
            return
        # print("?R1KSH", this)

        self.this = this
        self.chunks = [
            BitTools.R1kSegChunk(0,
                bin(int.from_bytes(b'\xff' + this.tobytes(), 'big'))[10:10+self.f0+0x7f]
            )
        ]
        self.starts = {}
        self.starts[0] = self.chunks[-1]
     

        self.mkcut(0x20)
        self.mkcut(0x40)
        self.mkcut(0x60)
        self.mkcut(0x80)

        self.tfile = tempfile.TemporaryFile(mode="w+", dir=self.this.top.html_dir)

        if this[0x10:0x24].tobytes() == b'This is a Link Pack.':
            try:
                LinkPack.R1kSegLinkPack(self, self.mkcut(0x80))
            except BitTools.MisFit as e:
                print("FAIL LINKPACK", self.this, e)
                return
        else:
            return

        # Render to a temporary file so we can delete all the bitmaps
        # otherwise the memory footprint roughly doubles.
        self.render_chunks(self.tfile)
        self.tfile.flush()
        self.tfile.seek(0)

        this.add_interpretation(self, self.render_real)

        del self.starts
        del self.chunks

    def hunt_orphans(self):
        for chunk in self.chunks:
            if chunk.offset < 0x1000:
                continue
            cuts = self.hunt(bin((1<<32) + chunk.offset)[3:])
            for chunk2, offset, address in cuts:
                if chunk2.owner is not None:
                    continue
                print(chunk, "    pointer at 0x%x in " % offset, chunk2)
                if chunk.owner:
                    print("OWNED", chunk, self.this)
                    BitTools.BitPointer(self, address, ident="orphan " + chunk.owner.title)
                else:
                    BitTools.BitPointer(self, address, ident="orphan")
                    print("WHITE SPACE", chunk, self.this)
                     
    def hunt(self, pattern):
        cuts = []
        for chunk in self.chunks:
            offset = 0
            while True:
                j = chunk.bits[offset:].find(pattern)
                if j < 0:
                    break
                cuts.append((chunk, offset + j, chunk.offset + offset + j))
                offset += j + 1
        return cuts

    def __getitem__(self, idx):
        return self.starts[idx]

    def get(self, idx):
        return self.starts.get(idx)

    def mkcut(self, idx):
        t = self.starts.get(idx)
        if not t:
            t = self.cut(idx)
        return t

    def cut(self, where, length=-1):
        assert where or length == 0x400
        for index, chunk in enumerate(self.chunks):
            assert self.starts.get(chunk.offset) == chunk, "0x%x -> %s vs %s" % (chunk.offset, str(self.starts.get(chunk.offset)), str(chunk))
            if not chunk.offset <= where < chunk.offset + len(chunk):
                continue

            if chunk.owner:
                raise BitTools.MisFit("Has " + str(chunk) + " already owned " + str(chunk.owner) + " wanted 0x%x" % where)

            if chunk.offset == where and length in (-1, len(chunk)):
                return chunk
            if where > chunk.offset:
                i = where - chunk.offset
                c1 = BitTools.R1kSegChunk(chunk.offset, chunk.bits[:i])
                chunk.bits = chunk.bits[i:]
                chunk.offset += i
                self.starts[chunk.offset] = chunk
                self.chunks.insert(index, c1)
                self.starts[c1.offset] = c1
                index += 1
            if length in (-1, len(chunk)):
                return chunk
            if length > len(chunk):
                raise BitTools.MisFit("Has " + str(chunk) + " want 0x%x" % length)
            assert length < len(chunk)
            c1 = BitTools.R1kSegChunk(chunk.offset, chunk.bits[:length])
            self.chunks.insert(index, c1)
            self.starts[c1.offset] = c1
            chunk.bits = chunk.bits[length:]
            chunk.offset += length
            self.starts[chunk.offset] = chunk
            return c1
        raise BitTools.MisFit("Found nothing at 0x%x" % where)


    def render_chunks(self, fo):
        ocheck = 0
        for chunk in self.chunks:
            assert ocheck == chunk.offset
            ocheck += len(chunk)
            fo.write(str(chunk) + ":")
            if chunk.owner is None:
                fo.write(" ===================\n")
                BitTools.render_chunk(fo, chunk)
            else:
                chunk.owner.render(chunk, fo)
        assert ocheck == self.f0 + 0x7f

    def render_real(self, fo, _this):
        fo.write("<H3>Segmented Heap</H3>\n")
        fo.write("<pre>\n")
        fo.write("Segment length: 0x%x (0x%x) bits\n" % (self.f0, self.f0 + 0x7f))
        fo.write("Segment maxlength: 0x%x bits\n" % self.f1)
        fo.write("Unknown: 0x%x bits\n" % self.f2)
        fo.write("Segment allocated length: 0x%x bits\n" % self.f3)
        fo.write("\n")
        for i in self.tfile:
            fo.write(html.escape(i))
        fo.write("</pre>\n")

