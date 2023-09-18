#/usr/bin/env python3

'''
   CR80 Filesystem type 1

   See https://ta.ddhf.dk/wiki/Bits:30004479
'''

import struct

import autoarchaeologist
from autoarchaeologist.generic import disk
from autoarchaeologist import type_case
import autoarchaeologist.generic.octetview as ov
import autoarchaeologist.christianrovsing.interleave as ileave

N_SECT = 26
N_TRACK = 77
SECTOR_LENGTH = 128
SECTOR_SHIFT = 9

UNREAD = b'_UNREAD_' * (SECTOR_LENGTH//8)

KINDS = {
    0x0000: "default",
    0x0002: "hack for 61b0d2eb6",
    0x0200: "text",
    0x0300: "binary",
    0x0600: "catalog",
}

class CR80S1_Ascii(type_case.Ascii):
    ''' ... '''
    def __init__(self):
        super().__init__()
        for i in range(0x80, 0xd0):
            self.set_slug(i, ' ', ' ' * (i - 0x80))
        self.set_slug(0x00, ' ', '«nul»', self.EOF)
        self.set_slug(0x19, ' ', '«eof»', self.EOF)
        self.set_slug(0xff, '░', '▉', self.INVALID)

class CR80_Text():

    def __init__(self, this):
        if len(this) >= 256256:
            return
        txt = []
        done = False
        for n in range(0, len(this) - 1, 2):
            for i in (this[n+1], this[n]):
                if 0x20 <= i <= 0x7e:
                    txt.append("%c" % i)
                elif i == 0x0a:
                    txt.append("\n")
                elif i in (0x00, 0x15,):
                    txt.append("\\x%02x" % i)
                elif i == 0x0c:
                    txt.append("«FF»")
                elif i == 0x7f:
                    txt.append("«DEL»")
                elif i == 0x19:
                    txt.append("«EOF»")
                    done = True
                    break
                elif 0x81 <= i <= 0xd0:
                    txt.append(' ' * (i - 0x80))
                #elif i in (0xff,):
                #    return
                else:
                    print("TXT", this, "%02x" % i)
                    return
            if done:
                break
        f = this.add_utf8_interpretation("Text")
        with open(f.filename, "w") as file:
            file.write(''.join(txt))
        this.add_type("text")

class Cr80SystemOneInterleave():

    def __init__(self, this):
        if not this.top in this.parents:
            return
        if len(this) != N_SECT * N_TRACK * SECTOR_LENGTH:
            return

        # Look for Dirent for the Root Directory
        if this[0x380:0x388] != b'\xff\xff\xff\xff\xff\xff\xf9\xff':
            return

        j = []
        for track_no in range(N_TRACK):
            for sector_no in range(N_SECT):
                i = sector_no + track_no * 6
                i = i % N_SECT
                i = (1 + i * 2)
                if i > (N_SECT - 1):
                    i -= (N_SECT + 1)
                lba = track_no * N_SECT + i
                off = lba * SECTOR_LENGTH
                b = bytearray(this[off:off+SECTOR_LENGTH])
                if b != UNREAD:
                    for x in range(SECTOR_LENGTH):
                        b[x] ^= 0xff;
                j.append(b)
        y = this.create(b''.join(j))
        y.add_type("ileave2,6")
        this.add_interpretation(self, this.html_interpretation_children)

class NameSpace(autoarchaeologist.NameSpace):

    def ns_render(self):
        dirent = self.ns_priv
        b = []
        b.append("0x%04x" % dirent.kind.val)
        b.append("0x%04x" % dirent.de04.val)
        b.append("0x%04x" % dirent.de05.val)
        b.append("0x%04x" % dirent.de06.val)
        b.append("0x%04x" % dirent.de07.val)
        b.append("0x%04x" % dirent.cluster.val)
        b.append("0x%04x" % dirent.de09.val)
        b.append("0x%04x" % dirent.de0a.val)
        b.append("0x%04x" % dirent.de0b.val)
        b.append("0x%04x" % dirent.nsect.val)
        b.append("0x%04x" % dirent.de0d.val)
        b.append("0x%04x" % dirent.cluster2.val)
        b += super().ns_render()
        return b

class DirEnt(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=False,
            filename_=ov.Text(6),
            kind_=ov.Be16,
            de04_=ov.Be16,
            de05_=ov.Be16,
            de06_=ov.Be16,
            de07_=ov.Be16,
            cluster_=ov.Be16,
            de09_=ov.Be16,
            de0a_=ov.Be16,
            de0b_=ov.Be16,
            nsect_=ov.Be16,
            de0d_=ov.Be16,
            cluster2_=ov.Be16,
            de0f_=ov.Be16,
            de10_=ov.Be16,
            de11_=ov.Be16,
            de12_=ov.Be16,
            de13_=ov.Be16,
            de14_=ov.Be16,
            de15_=ov.Be16,
            de16_=ov.Be16,
            de17_=ov.Be16,
            de18_=ov.Be16,
            de19_=ov.Be16,
            de1a_=ov.Be16,
            de1b_=ov.Be16,
            de1c_=ov.Be16,
            de1d_=ov.Be16,
            de1e_=ov.Be16,
            de1f_=ov.Be16,
        )
        self.filename.txt = self.filename.txt.rstrip()

        self.namespace = None
        if self.this[self.lo:self.hi] == UNREAD[:64]:
            print(up.this, "File has unread dir sector", self)
            self.up.this.add_note("BADSECT_DIR")
            
        self.dirents = []

    def iter_sectors(self):
        miss = (self.nsect.val +1)* SECTOR_LENGTH
        cluster = self.cluster.val * SECTOR_LENGTH
        nsect = 0
        for ptr in (
            self.de0f.val,
            self.de10.val,
            self.de11.val,
            self.de12.val,
            self.de13.val,
            self.de14.val,
            self.de15.val,
            self.de16.val,
            self.de17.val,
            self.de18.val,
        ):
            if miss <= 0:
                return
            track_no = ptr >> 8
            sector_no = (ptr & 0xff) - 1
            lbp = (track_no * N_SECT + sector_no) * SECTOR_LENGTH
            x = min(miss, cluster)
            if x <= 0:
                break
            for w in range(0, x, SECTOR_LENGTH):
                yield lbp + w
                miss -= SECTOR_LENGTH

    def commit(self, parent_ns=None, **kwargs):
        if self[0] == 0xff:
            return
        self.namespace = NameSpace(
            self.filename.txt,
            parent=parent_ns,
            priv=self,
            **kwargs,
        )
        if self.kind.val == 0x600:
            for x in self.iter_sectors():
                for i in range(0, SECTOR_LENGTH, 0x40):
                    y = DirEnt(self.up, x + i)
                    if y.kind.val not in KINDS:
                        y.insert()
                        # y = ov.Octets(self.up, x + i, width = 0x40).insert()
                    else:
                        y.insert()
                        self.dirents.append(y)
            for de in self.dirents:
                de.commit(self.namespace, separator='.')
        else:
            b = []
            for n, lba in enumerate(self.iter_sectors()):
                try:
                    y = disk.DataSector(
                        self.up,
                        lo=lba,
                        namespace = self.namespace,
                    ).insert()
                    b.append(self.up.this[lba:lba+SECTOR_LENGTH])
                    self.up.picture[(y.cyl, y.head, y.sect)] = '·'
                except Exception as err:
                    # Probably _UNREAD_
                    return
            b = b''.join(b)
            if len(b) > 0:
                y = self.up.this.create(bits = b)
                self.namespace.ns_set_this(y)


class Cr80SystemOneFs(disk.Disk):

    type_case = CR80S1_Ascii()

    def __init__(self, this):
        if this.has_type("ileave2,6"):
            pass
        elif this.has_type("inv"):
            return
            pass
        else:
            return
        if len(this) != N_SECT * N_TRACK * SECTOR_LENGTH:
            return

        super().__init__(
            this,
            [ [ N_TRACK, 1, N_SECT, SECTOR_LENGTH ] ],
        )
        self.this.type_case = self.type_case
        self.this.byte_order = [1, 0]
        self.this.add_note("Cr80S1Fs")

        self.super_block = DirEnt(self, 0x180).insert()
        if self.super_block.kind.val != 0x0600:
            return

        self.super_block.filename.txt = ""

        this.add_type("CRfs1")

        self.super_block.commit(root=this, separator='')
        this.add_interpretation(self, self.super_block.namespace.ns_html_plain)

        this.add_interpretation(self, self.disk_picture)

        self.fill_gaps()

        self.render()
