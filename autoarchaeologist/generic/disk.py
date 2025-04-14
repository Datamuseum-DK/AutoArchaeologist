#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Utility classes for dealing with artifacts representing
   or organized as some kind of disk, ie: A cyl/hd/sect type
   of layout.

   By convention, a sector containing b'_UNREAD_' repeatedly
   is considered invalid because they were not read from the
   original media.
'''

from ..base import octetview as ov
from ..base import category_colors
from ..toolbox import png

COLORS = category_colors.COLORS

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
        ''' paint this sector '''
        self.tree.set_picture(what, lo = self.lo, width = self.hi - self.lo)

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

    SECTOR_OFFSET = 1		# Sectors are usually numbered 1, 2, 3…

    def __init__(self, this, geometry, physsect=None, unread_pattern=None):
        self.geometry = geometry	# [ [C, H, S, B], ...]
        self.seclo = {}
        self.losec = {}
        self.width = {}
        self.picture = {}
        self.picture_legend = {
            "?": "Unclaimed",	# Black
            "U": "Unread",	# Orange
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

    def fill_gaps(self, cls=UnusedSector):
        ''' Fill the gaps with UnusedSector '''
        for lo, hi in list(self.gaps()):
            for i, adr in self.losec.items():
                j = i + self.width[adr]
                if i >= lo and j <= hi:
                    cls(self, lo=i, hi=j).insert()

    def set_picture(self, what, cyl=None, head=None, sect=None, lo=None, width=None, legend = None):
        if lo is None:
            lo = self.seclo[(cyl, head, sect)]
        chs = self.losec[lo]
        if width is None:
            width = self.width[chs]
        hi = lo + width
        if legend:
            self.picture_legend[what] = legend

        while lo < hi:
            try:
                chs = self.losec[lo]
            except KeyError:
                print(self.this, "Disk-picture failed at", hex(lo), what)
                return
            if self.picture[chs] not in ('?', what):
                print(self.this, "Picture Changed", hex(lo), chs, self.picture[chs], what)
            self.picture[chs] = what
            lo += self.width[chs]

    def disk_picture(self, file, this):
        ''' Draw a UTF-8-art picture of the disk '''
        for j in self.picture.values():
            if j not in self.picture_legend:
                self.picture_legend[j] = '?'
        file.write("<H3>Disk picture</H3>\n")

        cmap = {}
        for i, j in zip(self.picture_legend.keys(), COLORS):
            cmap[i] = bytes(j)
        ncyl = max(chsb[0] for chsb in self.iter_chsb()) + 1
        nhd = max(chsb[1] for chsb in self.iter_chsb()) + 1
        minsect = min(chsb[2] for chsb in self.iter_chsb())
        maxsect = max(chsb[2] for chsb in self.iter_chsb())
        nsect = 1 + maxsect - minsect

        img = png.PalettePNG(ncyl, nhd * (nsect + 1) - 1)
        img.set_color(0, (0, 0, 0))
        img.set_color(255, (255, 255, 255))

        y = 0
        colmap = {}
        ncol = 1
        for hd in range(nhd):
            if y:
                for cyl in range(ncyl):
                    Img.set_pixel(cyl, y, 255)
                y += 1
            for sec in range(nsect):
                for cyl in range(ncyl):
                    chs = (cyl, hd, sec + minsect)
                    col = self.picture.get(chs, '?')
                    if col not in colmap:
                        img.set_color(ncol, cmap[col])
                        colmap[col] = ncol
                        ncol += 1
                    img.set_pixel(cyl, y, colmap[col])
                y += 1
        pngf = this.filename_for(".png")
        img.write(pngf.filename)

        file.write('<img src="%s" class="diskimage"/>\n' % pngf.link)
        file.write('<table>\n')
        for i, j in sorted(self.picture_legend.items()):
            if i not in colmap:
                continue
            c = cmap[i]
            file.write('<tr>\n')
            file.write('<td style="background-color: #')
            file.write('%02x%02x%02x' % (c[0], c[1], c[2]))
            file.write('">&nbsp;</td>\n')
            file.write('<td>' + j + '</td>\n')
            file.write('</tr>\n')
        file.write('<table>\n')
