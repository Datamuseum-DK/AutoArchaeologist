#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' Minimal class to write a palette PNG image '''

import struct
import zlib

class PalettePNG():

    ''' Minimal class to write a palette PNG image '''

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.palette = bytearray(256 * 3)
        # The extra byte is the compression subtype
        self.pixels = bytearray((width + 1) * height)

    def set_color(self, color_index, rgb):
        ''' Define RGB color for index '''
        for i, j in enumerate(rgb):
            self.palette[color_index * 3 + i] = j

    def set_pixel(self, x, y, color_index):
        ''' Set pixel (x,y) to color_index '''
        self.pixels[y * (self.width + 1) + 1 + x] = color_index

    def write(self, fn):
        ''' Write the PNG to a file '''
        with open(fn, "wb") as file:
            file.write(b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a')

            ihdr = b'IHDR' + struct.pack(
                ">LLBBBBB",
                self.width,
                self.height,
                8, # bits per sample (= wdith of index in palette)
                3, # format=Palette
                0, # Compression
                0, # Filter
                0, # Non-Interlace
            )
            file.write(struct.pack(">L", len(ihdr) - 4))
            file.write(ihdr)
            file.write(struct.pack(">L", zlib.crc32(ihdr)))

            plte = b'PLTE' + self.palette
            file.write(struct.pack(">L", len(plte) - 4))
            file.write(plte)
            file.write(struct.pack(">L", zlib.crc32(plte)))

            idat = b'IDAT' + zlib.compress(self.pixels)
            file.write(struct.pack(">L", len(idat) - 4))
            file.write(idat)
            file.write(struct.pack(">L", zlib.crc32(idat)))

            iend = b'IEND'
            file.write(struct.pack(">L", len(iend) - 4))
            file.write(iend)
            file.write(struct.pack(">L", zlib.crc32(iend)))

def main():
    ''' A small test function '''
    p = PalettePNG(150, 100)
    p.set_color(0, (0x80, 0x80, 0x80))
    p.set_color(1, (0xff, 0x00, 0x00))
    p.set_color(2, (0x00, 0xff, 0x00))
    p.set_color(3, (0x00, 0x00, 0xff))
    p.set_color(4, (0xff, 0xff, 0x00))

    for x in range(150):
        for y in range(100):
            r2 = (x-75)**2 + (y-50)**2
            if r2 < 100:
                p.set_pixel(x, y, 1)
            elif 200 <= r2 <= 230:
                p.set_pixel(x, y, 2)
            elif (x^y) & 15 == 0:
                p.set_pixel(x, y, 3)
            elif (x^y^0xf) & 15 == 0:
                p.set_pixel(x, y, 4)

    p.write("/tmp/_.png")

if __name__ == "__main__":
    main()
