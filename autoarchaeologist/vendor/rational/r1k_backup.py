#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   R1K Backup Tapes
   ----------------

   This file contains the "tape-aspects" of taking a backup tape apart.
   The companion 'r1k_backup_objects' handles the "object-aspects"
'''

import html

from ...base import namespace
from . import r1k_backup_objects as objects

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
       All metadata tapefiles (all but "Block Data") are encoded as:

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
        widths = [2, 4, 2, 6, 14, 2, 4, 2, 2, 10, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
        for i, j in zip(
            widths, (
                "?1",
                "?2",
                "?3",
                "?4",
                "?5",
                "?6",
                "NBLK",
                "?8",
                "TAG",
                "CLS+SEG",
                "?11",
                "?12",
                "?13",
                "BLK0",
                "BLK1",
                "BLK2",
                "BLK3",
                "BLK4",
                "BLK5",
                "BLK6",
                "BLK7",
                "BLK8",
                "BLK9",
            )
        ):
            fo.write(j.rjust(i + 1))
        fo.write("\n")
        for i in self.space:
            t = ""
            for j, w in zip(i.space_info, widths):
                t += ("%x" % j).rjust(w+1)
            t += i.render_space_info() + "\n"
            fo.write(t)
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
        #print("BDK", self.block_data._keys)
        #b = self.block_data.get_rec(rb // 3)
        #j = (rb % 3) << 10
        return self.block_data[(rb<<10):(rb+1)<<10]

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
        return
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
           This is complicated...
        '''

        self.volumes = {}

        ns = this.has_name('Block Data Vol 1')
        if not isinstance(ns, namespace.NameSpace):
            return
        tape_ns = ns.ns_parent
        for ns in tape_ns:
            i = {
                "Vol Info": VolInfo,
                "VP Info": VpInfo,
                "DB Backups": DbBackups,
                "DB Processors": DbProcessors,
                "DB Disk Volumes": DbDiskVolumes,
                "DB Tape Volumes": DbTapeVolumes,
            }.get(ns.ns_name)
            if i:
                i(ns.ns_this)
                continue
            volno = ns.ns_name[-1]
            if volno not in self.volumes:
                self.volumes[volno] = Volume(self, volno)
            i = {
                "Space Info Vol ": self.volumes[volno].add_space_info,
                "Block Info Vol ": self.volumes[volno].add_block_info,
                "Block Data Vol ": self.volumes[volno].add_block_data,
            }.get(ns.ns_name[:-1])
            if i:
                i(ns.ns_this)
                continue
            print("R1K_Backup: Unknown tapefile", ns)
