#!/usr/bin/env python3

'''
   Utilities for Disks
'''

import os
import subprocess

COLORS = [
   # https://betterfigures.org/2015/06/23/picking-a-colour-scale-for-scientific-graphics/
   [ 0, 0, 0],
   [ 230, 159, 0],
   [ 86, 180, 233],
   [ 0, 158, 115],
   [ 240, 228, 66],
   [ 0, 114, 178],
   [ 213, 94, 0],
   [ 204, 121, 167],
]

from ..base import octetview as ov

class Sector(ov.Octets):
    ''' A sector '''
    def __init__(self,
        tree,
        cyl=None,
        head=None,
        sect=None,
        lo=None,
        unread_note=None,
        **kwargs,
    ):
        if lo is None:
            lo = tree.seclo[(cyl, head, sect)]
        else:
            cyl, head, sect = tree.losec[lo]
        super().__init__(
            tree,
            lo,
            width=tree.width[(cyl, head, sect)],
            **kwargs,
        )
        self.cyl = cyl
        self.head = head
        self.sect = sect
        self.is_unread = self.this[self.lo:self.hi] == tree.unread_pattern
        if self.is_unread and unread_note:
            self.tree.this.add_note(unread_note)
        self.terse = False

    def picture(self, what):
        self.tree.picture[(self.cyl, self.head, self.sect)] = what

    def render(self):
        ''' Render respecting byte ordering '''
        if self.terse:
            yield self.ident
            return
        if self.is_unread:
            octets = self.octets()
        else:
            octets = self.iter_bytes()
        yield self.ident + " ┆" + self.this.type_case.decode(octets) + "┆"

    ident = "Sector"

class DataSector(Sector):
    ''' A data sector '''
    def __init__(self, tree, *args, namespace=None, **kwargs):
        super().__init__(
            tree,
            *args,
            unread_note="UNREAD_DATA_SECTOR",
            **kwargs
        )
        if namespace:
            self.ident = "DataSector[»" + namespace.ns_name + "«]"
        self.picture('·')
    ident = "DataSector"

    def render(self):
        yield self.ident

class UnusedSector(Sector):
    ''' An unused sector '''
    def __init__(self, tree, *args, **kwargs):
        super().__init__(
            tree,
            *args,
            unread_note="UNREAD_UNUSED_SECT",
            **kwargs
        )
        i = set(self.tree.this[self.lo:self.hi])
        if len(i) == 1:
            self.fill = " 0x%02x[%d]" % (self.tree.this[self.lo], self.hi - self.lo)
        else:
            self.fill = None

    ident = "UnusedSector"

    def render(self):
        if self.fill is not None:
            yield self.ident + self.fill
        else:
            yield from super().render()

class Disk(ov.OctetView):
    ''' ... '''

    SECTOR_OFFSET = 1

    def __init__(self, this, geometry, physsect=None, unread_pattern=None):
        self.geometry = geometry	# [ [C, H, S, B], ...]
        self.seclo = {}
        self.losec = {}
        self.width = {}
        self.picture = {}
        self.picture_legend = {
            "?": "Unclaimed",
            "·": "Data",
        }
        lo = 0
        for cyl, head, sec, nbyte in self.iter_chsb():
            chs = (cyl, head, sec)
            self.seclo[chs] = lo
            self.width[chs] = nbyte
            self.picture[chs] = "?"
            self.losec[lo] = chs
            lo += nbyte
        if physsect is None:
            physsect = 128
        self.physsect = physsect
        if unread_pattern is None:
            unread_pattern = b'_UNREAD_' * (physsect // 8)
        self.unread_pattern = unread_pattern
        super().__init__(this, default_width=physsect)

    def iter_chsb(self):
        ''' Iterate all CHSB '''
        for ncyl, nhd, nsec, nbyte in self.geometry:
            for cyl in range(ncyl):
                for head in range(nhd):
                    for sec in range(self.SECTOR_OFFSET, nsec + self.SECTOR_OFFSET):
                        yield cyl,head,sec,nbyte

    def prefix(self, lo, hi):
        ''' Line prefix is hex off set + CHS '''
        i = super().prefix(lo, hi)
        j = self.losec.get(lo)
        if j:
            j = " %d,%d,%d" % j
            return i + j.ljust(9)
        return i + " " * 9

    def fill_gaps(self, cls=UnusedSector):
        ''' Fill the gaps with UnusedSector '''
        for lo, hi in list(self.gaps()):
            for i, adr in self.losec.items():
                j = i + self.width[adr]
                if i >= lo and j <= hi:
                    cls(self, lo=i, hi=j).insert()

    def set_picture(self, what, cyl=None, head=None, sect=None, lo=None):
        if lo is not None:
            cyl, head, sect = self.losec[lo]
        self.picture[(cyl, head, sect)] = what

    def disk_picture_p6(self, file, this):

        cmap = {}
        for i, j in zip(self.picture_legend.keys(), COLORS):
            cmap[i] = bytes(j)
        p6f = this.filename_for(".png")
        ncyl = max(chsb[0] for chsb in self.iter_chsb()) + 1
        nhd = max(chsb[1] for chsb in self.iter_chsb()) + 1
        minsect = min(chsb[2] for chsb in self.iter_chsb()) + 1
        maxsect = max(chsb[2] for chsb in self.iter_chsb()) + 1
        nsect = 1 + maxsect - minsect
        print(self.this, p6f.filename)
        with open(p6f.filename + "_", "wb") as pfile:
            pfile.write(b'P6\n')
            pfile.write(b'%d %d\n' % (ncyl, nhd * (nsect + 1)))
            pfile.write(b'255\n')
            for hd in range(nhd):
                for sec in range(nsect):
                    for cyl in range(ncyl):
                        chs = (cyl, hd, sec + minsect)
                        col = self.picture.get(chs, '?')
                        pfile.write(cmap[col])
                for cyl in range(ncyl):
                    pfile.write(bytes((255,255,255)))
                
        if ncyl < 220 and nhd * nsect < 220:
            zoom="400%"
        elif ncyl < 440 and nhd * nsect < 440:
            zoom="200%"
        else:
            zoom="100%"
        subprocess.run(
            [
                "convert",
                "-scale", zoom,
                p6f.filename + "_",
                p6f.filename,
            ]
        )
        os.remove(p6f.filename + "_")
        file.write('<img src="%s"/>\n' % p6f.link)
        file.write('<table>\n')
        for i, j in sorted(self.picture_legend.items()):
            c = cmap[i]    
            file.write('<tr>\n')
            file.write('<td style="background-color: #')
            file.write('%02x%02x%02x' % (c[0], c[1], c[2]))
            file.write('">&nbsp;</td>\n')
            file.write('<td>' + j + '</td>\n')
            file.write('</tr>\n')
        file.write('<table>\n')

    def disk_picture(self, file, this):
        ''' Draw a UTF-8-art picture of the disk '''
        for j in self.picture.values():
            if j not in self.picture_legend:
                self.picture_legend[j] = '?'
        file.write("<H3>Disk picture</H3>\n")
        self.disk_picture_p6(file, this)
        return
        file.write("<pre>\n")
        ncyl = max(chsb[0] for chsb in self.iter_chsb()) + 1
        file.write("   c ")
        for i in range(0, ncyl, 10):
            file.write(("%d" % (i//10)).ljust(10))
        file.write("\n     ")
        for i in range(ncyl):
            file.write("%d" % (i % 10))
        file.write('\nh, s┌' + '─' * ncyl)
        lhead = 0
        lsec = None
        for head, sec, cyl in sorted(
            (chsb[1],chsb[2],chsb[0]) for chsb in self.iter_chsb()
        ):
            if head != lhead or sec != lsec:
                if head != lhead:
                    file.write("\n")
                    lhead = head
                    lsec = None
                if sec != lsec:
                    file.write("\n%d,%2d│" % (head, sec))
                    lsec = sec

            file.write(self.picture[(cyl, head, sec)])

        got = set(self.picture.values())

        file.write("\n\nLegend:\n")
        for i, j in sorted(self.picture_legend.items()):
            if i in got:
                file.write('    ' + i + '  ' + j + '\n')
        file.write("\n<pre>\n")
