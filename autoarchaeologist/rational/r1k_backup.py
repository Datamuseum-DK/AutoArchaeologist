
import autoarchaeologist.generic.hexdump as hexdump

def fld(b, i):
    l = b[i]
    t = ""
    if not l:
        t += "-"
    else:
        t += b[i+1:i+1+l].hex()
    return l+1, t

def flds(this):
    l = None
    n = 0
    for i in this:
        if l is None:
            if not i:
                break
            l = i
            n = 0
        elif l > 0:
            n <<= 8
            n |= i
            l -= 1
        if l == 0:
            yield n
            l = None

class R1kObject():
    ''' whatever that is... '''

    def __init__(self, up, this, space_info):
        self.up = up
        self.this = this
        self.space_info = space_info
        self.n_block = space_info[6]
        self.block_list = space_info[13:]
        self.indir = None

    def resolve(self, iblock):
        l = []
        n = self.n_block
        if self.n_block >= 163:
            for j in self.block_list:
                if j:
                    l.append(iblock[j])
                    n -= 1
                else:
                    l.append(self.this[:0])
                if not n:
                    break
        elif self.n_block > 10 or (self.n_block > 1 and not max(self.block_list[1:])):
            # Indirect block
            # self.up.enough = True
            self.indir = iblock[self.block_list[0]]
            # l.append(self.indir)
            if not isinstance(self.indir, bytes):
                self.indir = self.indir.tobytes()
            for i in range(0x29 + 3, len(self.indir), 6):
                j = self.indir[i+2:i+8]
                if len(j) != 6:
                    print("SHORT", self.space_info)
                    print("BI", self.indir[:128].hex())
                    return
                k = j[0] << 24
                k |= j[1] << 16
                k |= j[2] << 8
                k |= j[3]
                k = (k >> 4) & 0xffffff
                # print("iy", n, j.hex(), "0x%x" % k, k in iblock)
                if k and k in iblock:
                    l.append(iblock[k])
                    n -= 1
                elif k:
                    print("K 0x%x not in iblock" % k, self.space_info)
                    print("BI", self.indir[:128].hex())
                    return
                else:
                    l.append(self.this[:0])
                if not n:
                    break
        else:
            for j in self.block_list:
                if j:
                    l.append(iblock[j])
                    n -= 1
                else:
                    l.append(self.this[:0])
                if not n:
                    break

        self.obj = self.this.create(records=l)
        # print("IX", self.obj, self.n_block, len(l))
        if self.obj.has_note("R1K_Object"):
            return
        if self.n_block >= 163:
            self.obj.add_note("R1K_ObjectHuge")
        if self.indir:
            self.obj.add_note("R1K_ObjectIndir")
        self.obj.add_note("R1K_Object")
        self.obj.add_interpretation(self, self.render_obj)
        self.obj.add_note("%x_marked" % self.space_info[8])

    def render_space_info(self):
        t = ""
        for j, w in zip(self.space_info, [2, 4, 2, 6, 14, 2, 4, 2, 2, 10, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]):
            t += ("%x" % j).rjust(w+1)
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
            fo.write("\n")
            fo.write("Block #0x%x\n" % n)
            hexdump.hexdump_to_file(i, fo)
        fo.write("</pre>\n")

class Volume():
    ''' One (disk) volume of a backup '''

    def __init__(self, up, volno):
        self.up = up
        self.volno = volno
        self.space = []
        self.block = []

    def add_space_info(self, this):
        print("add_space_info", this)
        self.space_info = this
        this.add_interpretation(self, self.render_space_info)
        this.add_type("R1K_Backup_Space_Info")
        l = list(flds(this))
        self.space = [R1kObject(self.up, this, l[i:i+23]) for i in range(0, len(l), 23)]

    def add_block_info(self, this):
        print("add_block_info", this)
        self.block_info = this
        this.add_interpretation(self, self.render_block_info)
        this.add_type("R1K_Backup_Block_Info")
        l = list(flds(this))
        self.block = [l[i:i+4] for i in range(0, len(l), 4)]

    def add_block_data(self, this):
        print("add_block_data", this)
        self.block_data = this
        this.add_interpretation(self, self.render_block_data)
        this.add_type("R1K_Backup_Block_Data")
        self.iblock = {}
        n = 0
        for i in this.iterrecords():
            for j in range(0, len(i), 1<<10):
                self.iblock[self.block[n][0]] = i[j:j + (1<<10)]
                n += 1

        for i in self.space:
            i.resolve(self.iblock)
            if self.up.enough:
                break

    def render_space_info(self, fo, _this):
        fo.write("<H3>Space Info</H3>\n")
        fo.write("<pre>\n")
        for i in self.space:
            fo.write(i.render_space_info() + "\n")
        fo.write("</pre>\n")

    def render_block_info(self, fo, _this):
        fo.write("<H3>Block Info</H3>\n")
        fo.write("<pre>\n")
        for i in self.block:
            t = ""
            for j, w in zip(i, [8, 8, 8, 8]):
                t += ("%x" % j).rjust(w+1)
            fo.write(t + "\n")
        fo.write("</pre>\n")

    def render_block_data(self, fo, _this):
        fo.write("<H3>Block Info</H3>\n")
        fo.write("<pre>\n")
        for n, i in zip(self.block, self.block_data.iterrecords()):
            fo.write("0x%06x 0x%02x 0x%03x 0x%02x " % (n[0], n[1], n[2], n[3]))
            fo.write(i[:32].tobytes().hex() + "\n")
        fo.write("</pre>\n")

class R1kBackup():

    def __init__(self, this):
        '''
           This is very much a universe-of-one way to recognize an
           entire tape based on the ANSI-labels.  Eventually we may
           need something general, including support for multi-reel
           tape-sets, but I dont want to try to generalize that from
           a single one-reel example.
        '''

        self.enough = False
        self.expect_next = None
        self.volumes = {}

        us = this.parents[0].by_class.get(R1kBackup)
        if us:
            us.add_tape_file(this)
            return
        if this.parents[0].children[0] != this:
            # We only care for the first ANSI label on the tape
            return
        if not this.has_type("ANSI Tape Label"):
            return
        bits = 0
        for label in this.iterrecords():
            try:
                i = label.tobytes().decode("ASCII")
            except UnicodeDecodeError:
                return
            if i[:4] == "VOL1" and i[38:44] == "BACKUP":
                bits |= 1
            if i[:40] == "UVL1RATIONAL CHAINED TAPES, PRED VOL ID:":
                bits |= 2
            if i[:10] == "UVL2BACKUP":
                bits |= 4
            if i[:21] == "HDR1Space Info Vol 1 ":
                bits |= 8
            if i[:21] == "HDR3Space Info Vol 1 ":
                bits |= 16
            print("%02x" % bits, i)
        if bits != 0x1f:
            return
        this.parents[0].by_class[R1kBackup] = self
        print(this, "MATCH")
        self.add_tape_file(this)

    def add_tape_file(self, that):
        ''' Add a tape-file to our collection '''
        if that.has_type("ANSI Tape Label"):
            for label in that.iterrecords():
                i = label.tobytes().decode("ASCII")
                if i[:4] == "HDR1":
                    self.expect_next = i[4:21].split()
                    return
            self.expect_next = None
            return
        if not self.expect_next:
            print("GOT", that, that.parents, that.types, that.notes)
            for i in that.iterrecords():
                print("Got", len(i), i[:64].tobytes())
            return
        assert self.expect_next
        if self.expect_next[-1] in "1234":
            volno = int(self.expect_next[-1])
            self.expect_next.pop(-1)
            if volno not in self.volumes:
                self.volumes[volno] = Volume(self, volno)
            if self.expect_next == ["Space", "Info", "Vol"]:
                self.volumes[volno].add_space_info(that)
            elif self.expect_next == ["Block", "Info", "Vol"]:
                self.volumes[volno].add_block_info(that)
            elif self.expect_next == ["Block", "Data", "Vol"]:
                self.volumes[volno].add_block_data(that)
            else:
                print("unhandled", that, volno, self.expect_next)
        else:
            print("non-vol", that, self.expect_next)
