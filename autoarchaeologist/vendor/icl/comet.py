'''
    Metanic/ICL Comet tapes
    -----------------------
'''

import crcmod

crcfunc = crcmod.predefined.mkPredefinedCrcFun("crc-16")

class Invalid(Exception):
    ''' Invalid format '''

class TapeBlock():
    def __init__(self, up, octets):
        self.up = up
        self.octets = bytearray(octets)
        self.body = None
        self.diag = self.is_valid()
        self.hexdump = self.up.this.type_case.hexdump

    def is_valid(self):
        if self.octets[0] != 0xaa:
            return "Bad Preamble"

        if self.octets[-1] == 0xaa:
            body = self.octets[1:-1]
        elif self.octets[-2] == 0xaa:
            body = self.octets[1:-2]
        else:
            return "Bad Postamble"
        if crcfunc(body):
            return "Bad CRC"
        self.body = body[:-2]
        return ""

    def render_tape_head(self):
        yield "TAPE HEAD"
        p = 0
        for field_length in (
            2,
            1,
            50,
            13,
            26,
        ):
            yield from self.hexdump(self.body[p:p + field_length], width=field_length)
            p += field_length
        while p < len(self.body):
            yield from self.hexdump(self.body[p:p + field_length], width=field_length)
            p += field_length

    def render_file_head(self):
        yield "FILE HEAD"
        p = 0
        for field_length in (
            2,
            13,
        ):
            yield from self.hexdump(self.body[p:p + field_length], width=field_length)
            p += field_length
        yield from self.hexdump(self.body[p:], width=len(self.body[p:]))


    def render(self, fo):
        fo.write("%4d [%s…%s] " % (len(self.octets), self.octets[:4].hex(), self.octets[-4:].hex()))
        if self.diag:
            fo.write(self.diag + "\n")
            for i in self.hexdump(self.octets):
                fo.write("        " + i + "\n")
            return
        fo.write("Record number %2d" % self.body[0])
        fo.write("  Record type %2d" % self.body[1])
        fo.write("\n")
        fo.write("\n")
        if self.body[1] == 0:
            for i in self.render_tape_head():
                fo.write("        " + i + "\n")
        elif self.body[1] == 1:
            for i in self.render_file_head():
                fo.write("        " + i + "\n")
        else:
            for i in self.hexdump(self.body):
                fo.write("        " + i + "\n")
        fo.write("\n")

class DirEnt():
    def __init__(self, this, octets):
        self.basename = this.type_case.decode(octets[:10].rstrip(b' '))
        self.ext = this.type_case.decode(octets[10:13].rstrip(b' '))
        self.name = self.basename + "." + self.ext
        self.something1 = octets[13]
        self.unknown1 = octets[14:17]
        self.something2 = octets[17]
        self.unknown2 = octets[18:]

    def __str__(self):
        return " ".join(
            (
                self.name.ljust(14),
                "0x%02x" % self.something1,
                "{" + str(self.unknown1.hex()) + "}",
                "0x%02x" % self.something2,
                "{" + str(self.unknown2.hex()) + "}",
            )
        )

class File(DirEnt):
    def __init__(self, up, octets):
        super().__init__(up.this, octets[:25])
        self.up = up
        self.octets = octets
        self.that = None
        self.first_block = octets[25]
        self.blocks = {}

        contents = []
        blkno = self.first_block
        while blkno < len(self.up.blocks):
            block = self.up.blocks[blkno]
            body = block.body
            if self.blocks and body and body[1] == 1:
                break
            self.blocks[blkno] = block
            if body is None:
                print("Block %d not found", blkno)
                return
            print("  B", self.name, blkno, body[0], body[1], len(body))
            if body[1] == 2:
                contents.append(body[2:])
            if body[1] == 3:
                break
            blkno += 1

        contents = b''.join(contents)
        if len(contents):
            self.that = self.up.this.create(contents)
            self.that.set_name(self.name)
            print("  -->", self.that)

    def render(self, fo):
        fo.write("\t" + str(self))
        if self.that:
            fo.write("\t" + self.that.summary())
        fo.write("\n")
        for blkno, block in self.blocks.items():
            fo.write("\t\tBlock %2d" % blkno)
            if blkno >= len(self.up.blocks):
                fo.write(" => Past end of tape")
            else:
                error = block.is_valid()
                if error:
                    fo.write(" => " + error)
                elif block.body:
                    fo.write(" [%4d] %02x %02x" % (len(block.body), block.body[0], block.body[1]))
                    if block.body[1] == 1:
                        fo.write(" " + str(DirEnt(self.up.this, block.body[2:])))
            fo.write('\n')

class TapeHead():
    def __init__(self, up, block):
        self.up = up
        self.block = block
        self.body = block.body

        if self.body[0] != 0x00:
            raise Invalid("Head Block number not zero (0x%02x)" % self.body[0])
        if self.body[1] != 0x00:
            raise Invalid("Head Block type not zero (0x%02x)" % self.body[1])

        self.label = self.up.this.type_case.decode(self.body[3:53].rstrip(b' '))
        self.files = []
        for i in range(3+50+13, len(self.body), 26):
            if not 0x20 < self.body[i] < 0x7e:
                break
            file = File(self.up, self.body[i:i+26])
            self.files.append(file)
            print("FILE", file.name, file.first_block)

    def render(self, fo):
        fo.write("Tape Header:\n")
        fo.write("\t{" + self.body[2:3].hex() + "}\n")
        fo.write("\tLabel: " + self.label + "\n")
        fo.write("\t{" + self.body[53:53+13].hex() + "}\n")
        for file in self.files:
            fo.write("\t" + str(file) + " %02d\n" % file.first_block)
            # file.render(fo)
        fo.write("\n")
        fo.write("Tape Files:\n")
        for file in self.files:
            fo.write("\n")
            file.render(fo)

class CometTape():

    def __init__(self, this):
        if not this.has_type("TAPE file"):
            return
        print("?COMET", this)
        self.this = this

        self.blocks = [TapeBlock(self, x) for x in this.iterrecords()]

        if not self.blocks:
            return

        if not self.blocks[0].body:
            this.add_interpretation(self, self.render_tcopy)
            return

        self.head = TapeHead(self, self.blocks[0])
        print("LABEL", self.head.label)
        this.add_interpretation(self, self.render_files)

        this.add_interpretation(self, self.render_tcopy)

    def render_files(self, fo, this):
        fo.write("<H3>ICL/Metanic Comet Tape</H3>\n")
        fo.write("<pre>\n")
        fo.write("%d Tape blocks\n" % len(self.blocks))
        fo.write("\n")
        self.head.render(fo)
        fo.write("</pre>\n")

    def render_tcopy(self, fo, this):
        fo.write("<H3>ICL/Metanic Comet Tape (RAW)</H3>\n")
        fo.write("<pre>\n")
        for block in self.blocks:
            block.render(fo)
        fo.write("</pre>\n")
