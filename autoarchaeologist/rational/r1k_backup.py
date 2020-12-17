'''
   R1K Backup Tapes
   ----------------

   This file contains the "tape-aspects" of taking a backup tape apart.
   The companion 'r1k_backup_objects' handles the "object-aspects"
'''

import html

import autoarchaeologist.rational.r1k_backup_objects as objects


def byte_length_int(this):
    '''
    Split `this` into integers, each prefixed its length in a byte
    '''
    length = None
    number = 0
    for octet in this:
        if length is None:
            # Length byte
            if not octet:
                break
            length = octet
        elif length > 0:
            # Content byte
            number <<= 8
            number |= octet
            length -= 1
        if length == 0:
            # Field complete
            yield number
            length = None
            number = 0

def byte_length_bytes(this):
    '''
    Split `this` into bytes, each prefixed its length in a byte
    '''
    length = None
    data = bytearray()
    for octet in this:
        if length is None:
            # Length byte
            if not octet:
                break
            length = octet
        elif length > 0:
            # Content byte
            data.append(octet)
            length -= 1
        if length == 0:
            # Field complete
            yield bytes(data)
            length = None
            data = bytearray()

class MetaTapeFile():
    '''
       All metadata tapefiles (all but "Block Data" are encoded as:

		<length byte> {<length byte> bytes}
    '''
    def __init__(self, this, name, length, fmt=bytes):
        self.this = this
        self.name = name
        self.fmt = fmt
        if fmt == int:
            l = list(byte_length_int(this))
        else:
            l = list(byte_length_bytes(this))
        self.items = [l[i:i+length] for i in range(0, len(l), length)]
        this.add_type(name)

    def __iter__(self):
        yield from self.items

    def render_html(self, fo, _this):
        ''' Brute force rendering '''
        fo.write("<H3>" + self.name + "</H3>\n")
        fo.write("<pre>\n")
        for i in self.items:
            fo.write("    " + html.escape(str(i)) + "\n")
        fo.write("</pre>\n")

class SpaceInfo(MetaTapeFile):
    def __init__(self, vol, this):
        super().__init__(this, "R1K Backup Space Info", 23, fmt=int)
        self.vol = vol
        self.space = [objects.R1kBackupObject(self, vol, this, i) for i in self]
        this.add_interpretation(self, self.render_space_info)

    def process(self):
        for i in self.space:
            i.resolve()

    def render_space_info(self, fo, _this):
        fo.write("<H3>" + self.name + "</H3>\n")
        fo.write("<pre>\n")
        for i in self.space:
            fo.write(i.render_space_info() + "\n")
        fo.write("</pre>\n")

class BlockInfo(MetaTapeFile):
    def __init__(self, vol, this):
        super().__init__(this, "R1K Backup Block Info", 4, fmt=int)
        self.vol = vol
        this.add_interpretation(self, self.render_block_info)

    def render_block_info(self, fo, _this):
        fo.write("<H3>" + self.name + "</H3>\n")
        fo.write("<pre>\n")
        for i in self:
            t = ""
            for j, w in zip(i, [8, 8, 8, 8]):
                t += ("%x" % j).rjust(w+1)
            fo.write(t + "\n")
        fo.write("</pre>\n")

class VolInfo(MetaTapeFile):
    def __init__(self, this):
        super().__init__(this, "R1K Vol Info", 6)
        this.add_interpretation(self, self.render_html)

class VpInfo(MetaTapeFile):
    def __init__(self, this):
        super().__init__(this, "R1K VP Info", 10)
        this.add_interpretation(self, self.render_html)

class DbBackups(MetaTapeFile):
    def __init__(self, this):
        super().__init__(this, "R1K DB Backups", 12)
        this.add_interpretation(self, self.render_html)

class DbProcessors(MetaTapeFile):
    def __init__(self, this):
        super().__init__(this, "R1K DB Processors", 4)
        this.add_interpretation(self, self.render_html)

class DbDiskVolumes(MetaTapeFile):
    def __init__(self, this):
        super().__init__(this, "R1K Disk Volumes", 8)
        this.add_interpretation(self, self.render_html)

class DbTapeVolumes(MetaTapeFile):
    def __init__(self, this):
        super().__init__(this, "R1K Tape Volumes", 6)
        this.add_interpretation(self, self.render_html)


##############################################################################################

class Volume():
    ''' One (disk) volume of a backup '''

    def __init__(self, up, volno):
        self.up = up
        self.volno = volno
        self.space_info = None
        self.block_info = None
        self.block_data = None
        self.block_use = {}
        self.rblock = {
            0: (None, None),
        }

    def __getitem__(self, idx):
        rb = self.rblock[idx][0]
        b = self.block_data.getblock(rb // 3)
        j = (rb % 3) << 10
        return b[j:j+1024]

    def binfo(self, idx):
        return self.rblock[idx]

    def add_space_info(self, this):
        self.space_info = SpaceInfo(self, this)
        self.process()

    def add_block_info(self, this):
        self.block_info = BlockInfo(self, this)
        for i, j in enumerate(self.block_info):
            self.rblock[j[0]] = (i, j)
        self.process()

    def add_block_data(self, this):
        self.block_data = this
        this.add_type("R1K Backup Block Data")
        this.add_interpretation(self, self.render_block_data)
        self.process()

    def process(self):
        if None in (self.space_info, self.block_info, self.block_data):
            return
        self.space_info.process()

    def render_block_data(self, fo, _this):
        fo.write("<H3>R1K Backup Block Data</H3>\n")
        fo.write("<pre>\n")
        for n, i in zip(self.block_info, self.block_data.iterrecords()):
            fo.write("0x%06x 0x%02x 0x%03x 0x%02x " % (n[0], n[1], n[2], n[3]))
            fo.write(i[:32].tobytes().hex())
            j = self.block_use.get(n[0])
            if j:
                fo.write("  " + j)
            fo.write("\n")
        fo.write("</pre>\n")

##############################################################################################

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
        elif self.expect_next == ["Vol", "Info"]:
            VolInfo(that)
        elif self.expect_next == ["VP", "Info"]:
            VpInfo(that)
        elif self.expect_next == ["DB", "Backups"]:
            DbBackups(that)
        elif self.expect_next == ["DB", "Processors"]:
            DbProcessors(that)
        elif self.expect_next == ["DB", "Disk", "Volumes"]:
            DbDiskVolumes(that)
        elif self.expect_next == ["DB", "Tape", "Volumes"]:
            DbTapeVolumes(that)
        else:
            print("non-vol", that, self.expect_next)
            for i in byte_length_bytes(that):
                print("    ", len(i), i[:64])
