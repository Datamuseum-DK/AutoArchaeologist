#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    SIMH-CRD file containers
    ------------------------

'''

from ..base import artifact
from . import plain_file

# Getting from a hole-pattern (aka "hollerith code") to text is totally messed up.
#
# Long story short: IBM made up shit as they went along and that did not go well.
#
# See also:
#
#       https://nvlpubs.nist.gov/nistpubs/Legacy/FIPS/fipspub14.pdf
#
# The following table comes from Open-SIMH (Much Appreciated!) and translates
# hollerith code to EBCDIC code, and Python3's built-in support for code-page
# "cp037" can take it from there.
#
# However, the way IBM handled national characters, like the Danish Æ, Ø and Å
# was to simply replace the graphical representation of some "unused" or "little
# used" EBCDIC characters as required, so "cp037" does not get us entirely home.
#
# The Danish substitutions were: #→Æ, @→Ø and $→Å, possibly more, but you will
# have to do that yourself with a string replacement.

HOLLERITH_TO_EBCDIC = {
    0b101100000011: 0x00, 0b100100000001: 0x01, 0b100010000001: 0x02, 0b100001000001: 0x03,
    0b100000100001: 0x04, 0b100000010001: 0x05, 0b100000001001: 0x06, 0b100000000101: 0x07,
    0b100000000011: 0x08, 0b100100000011: 0x09, 0b100010000011: 0x0a, 0b100001000011: 0x0b,
    0b100000100011: 0x0c, 0b100000010011: 0x0d, 0b100000001011: 0x0e, 0b100000000111: 0x0f,
    0b110100000011: 0x10, 0b010100000001: 0x11, 0b010010000001: 0x12, 0b010001000001: 0x13,
    0b010000100001: 0x14, 0b010000010001: 0x15, 0b010000001001: 0x16, 0b010000000101: 0x17,
    0b010000000011: 0x18, 0b010100000011: 0x19, 0b010010000011: 0x1a, 0b010001000011: 0x1b,
    0b010000100011: 0x1c, 0b010000010011: 0x1d, 0b010000001011: 0x1e, 0b010000000111: 0x1f,
    0b011100000011: 0x20, 0b001100000001: 0x21, 0b001010000001: 0x22, 0b001001000001: 0x23,
    0b001000100001: 0x24, 0b001000010001: 0x25, 0b001000001001: 0x26, 0b001000000101: 0x27,
    0b001000000011: 0x28, 0b001100000011: 0x29, 0b001010000011: 0x2a, 0b001001000011: 0x2b,
    0b001000100011: 0x2c, 0b001000010011: 0x2d, 0b001000001011: 0x2e, 0b001000000111: 0x2f,
    0b111100000011: 0x30, 0b000100000001: 0x31, 0b000010000001: 0x32, 0b000001000001: 0x33,
    0b000000100001: 0x34, 0b000000010001: 0x35, 0b000000001001: 0x36, 0b000000000101: 0x37,
    0b000000000011: 0x38, 0b000100000011: 0x39, 0b000010000011: 0x3a, 0b000001000011: 0x3b,
    0b000000100011: 0x3c, 0b000000010011: 0x3d, 0b000000001011: 0x3e, 0b000000000111: 0x3f,
    0b000000000000: 0x40, 0b101100000001: 0x41, 0b101010000001: 0x42, 0b101001000001: 0x43,
    0b101000100001: 0x44, 0b101000010001: 0x45, 0b101000001001: 0x46, 0b101000000101: 0x47,
    0b101000000011: 0x48, 0b100100000010: 0x49, 0b100010000010: 0x4a, 0b100001000010: 0x4b,
    0b100000100010: 0x4c, 0b100000010010: 0x4d, 0b100000001010: 0x4e, 0b100000000110: 0x4f,
    0b100000000000: 0x50, 0b110100000001: 0x51, 0b110010000001: 0x52, 0b110001000001: 0x53,
    0b110000100001: 0x54, 0b110000010001: 0x55, 0b110000001001: 0x56, 0b110000000101: 0x57,
    0b110000000011: 0x58, 0b010100000010: 0x59, 0b010010000010: 0x5a, 0b010001000010: 0x5b,
    0b010000100010: 0x5c, 0b010000010010: 0x5d, 0b010000001010: 0x5e, 0b010000000110: 0x5f,
    0b010000000000: 0x60, 0b001100000000: 0x61, 0b011010000001: 0x62, 0b011001000001: 0x63,
    0b011000100001: 0x64, 0b011000010001: 0x65, 0b011000001001: 0x66, 0b011000000101: 0x67,
    0b011000000011: 0x68, 0b001100000010: 0x69, 0b110000000000: 0x6a, 0b001001000010: 0x6b,
    0b001000100010: 0x6c, 0b001000010010: 0x6d, 0b001000001010: 0x6e, 0b001000000110: 0x6f,
    0b111000000000: 0x70, 0b111100000001: 0x71, 0b111010000001: 0x72, 0b111001000001: 0x73,
    0b111000100001: 0x74, 0b111000010001: 0x75, 0b111000001001: 0x76, 0b111000000101: 0x77,
    0b111000000011: 0x78, 0b000100000010: 0x79, 0b000010000010: 0x7a, 0b000001000010: 0x7b,
    0b000000100010: 0x7c, 0b000000010010: 0x7d, 0b000000001010: 0x7e, 0b000000000110: 0x7f,
    0b101100000010: 0x80, 0b101100000000: 0x81, 0b101010000000: 0x82, 0b101001000000: 0x83,
    0b101000100000: 0x84, 0b101000010000: 0x85, 0b101000001000: 0x86, 0b101000000100: 0x87,
    0b101000000010: 0x88, 0b101000000001: 0x89, 0b101010000010: 0x8a, 0b101001000010: 0x8b,
    0b101000100010: 0x8c, 0b101000010010: 0x8d, 0b101000001010: 0x8e, 0b101000000110: 0x8f,
    0b110100000010: 0x90, 0b110100000000: 0x91, 0b110010000000: 0x92, 0b110001000000: 0x93,
    0b110000100000: 0x94, 0b110000010000: 0x95, 0b110000001000: 0x96, 0b110000000100: 0x97,
    0b110000000010: 0x98, 0b110000000001: 0x99, 0b110010000010: 0x9a, 0b110001000010: 0x9b,
    0b110000100010: 0x9c, 0b110000010010: 0x9d, 0b110000001010: 0x9e, 0b110000000110: 0x9f,
    0b011100000010: 0xa0, 0b011100000000: 0xa1, 0b011010000000: 0xa2, 0b011001000000: 0xa3,
    0b011000100000: 0xa4, 0b011000010000: 0xa5, 0b011000001000: 0xa6, 0b011000000100: 0xa7,
    0b011000000010: 0xa8, 0b011000000001: 0xa9, 0b011010000010: 0xaa, 0b011001000010: 0xab,
    0b011000100010: 0xac, 0b011000010010: 0xad, 0b011000001010: 0xae, 0b011000000110: 0xaf,
    0b111100000010: 0xb0, 0b111100000000: 0xb1, 0b111010000000: 0xb2, 0b111001000000: 0xb3,
    0b111000100000: 0xb4, 0b111000010000: 0xb5, 0b111000001000: 0xb6, 0b111000000100: 0xb7,
    0b111000000010: 0xb8, 0b111000000001: 0xb9, 0b111010000010: 0xba, 0b111001000010: 0xbb,
    0b111000100010: 0xbc, 0b111000010010: 0xbd, 0b111000001010: 0xbe, 0b111000000110: 0xbf,
    0b101000000000: 0xc0, 0b100100000000: 0xc1, 0b100010000000: 0xc2, 0b100001000000: 0xc3,
    0b100000100000: 0xc4, 0b100000010000: 0xc5, 0b100000001000: 0xc6, 0b100000000100: 0xc7,
    0b100000000010: 0xc8, 0b100000000001: 0xc9, 0b101010000011: 0xca, 0b101001000011: 0xcb,
    0b101000100011: 0xcc, 0b101000010011: 0xcd, 0b101000001011: 0xce, 0b101000000111: 0xcf,
    0b011000000000: 0xd0, 0b010100000000: 0xd1, 0b010010000000: 0xd2, 0b010001000000: 0xd3,
    0b010000100000: 0xd4, 0b010000010000: 0xd5, 0b010000001000: 0xd6, 0b010000000100: 0xd7,
    0b010000000010: 0xd8, 0b010000000001: 0xd9, 0b110010000011: 0xda, 0b110001000011: 0xdb,
    0b110000100011: 0xdc, 0b110000010011: 0xdd, 0b110000001011: 0xde, 0b110000000111: 0xdf,
    0b001010000010: 0xe0, 0b011100000001: 0xe1, 0b001010000000: 0xe2, 0b001001000000: 0xe3,
    0b001000100000: 0xe4, 0b001000010000: 0xe5, 0b001000001000: 0xe6, 0b001000000100: 0xe7,
    0b001000000010: 0xe8, 0b001000000001: 0xe9, 0b011010000011: 0xea, 0b011001000011: 0xeb,
    0b011000100011: 0xec, 0b011000010011: 0xed, 0b011000001011: 0xee, 0b011000000111: 0xef,
    0b001000000000: 0xf0, 0b000100000000: 0xf1, 0b000010000000: 0xf2, 0b000001000000: 0xf3,
    0b000000100000: 0xf4, 0b000000010000: 0xf5, 0b000000001000: 0xf6, 0b000000000100: 0xf7,
    0b000000000010: 0xf8, 0b000000000001: 0xf9, 0b111010000011: 0xfa, 0b111001000011: 0xfb,
    0b111000100011: 0xfc, 0b111000010011: 0xfd, 0b111000001011: 0xfe, 0b111000000111: 0xff,
}

class BadCRDFile(Exception):
    ''' ... '''

class SimhCrdContainer(artifact.ArtifactFragmented):
    ''' Create an artifact from a SIMH-CRD file '''

    def __init__(self, top, octets=None, filename=None, verbose=False):

        super().__init__(top)

        if octets is None:
            octets = plain_file.PlainFileArtifact(filename).bdx
        if len(octets) % 160:
            raise BadCRDFile("Length not a multiple of 160")

        cards = []
        for i in range(0, len(octets), 160):
            h = []
            cards.append(h)
            for j in range(0, 160, 2):
                x = (octets[i + j + 1] << 8) | octets[i + j]
                if x & 0xf:
                    raise BadCRDFile("LSB not zero")
                h.append(x >> 4)

        ebcdic = []
        for c in cards:
            e = [HOLLERITH_TO_EBCDIC.get(x, None) for x in c]
            if None in e:
                ebcdic = None
                break
            ebcdic.append(e)

        if ebcdic is not None:
            for n, e in enumerate(ebcdic):
                r = artifact.Record(low=i, frag=bytes(e), key=(n,))
                self.add_fragment(r)
            self.completed()
            self.add_type('EbcdicCard')
            return

        cnt = 0
        for c in cards:
            if max(c) < 0x100:
                cnt += 1

        if cnt == len(cards):
            for i, c in enumerate(cards):
                r = artifact.Record(low=i, frag=bytes(c), key=(i,))
                self.add_fragment(r)
            self.completed()
            self.add_type('ByteCard')
            return

        for i, h  in zip(range(0, len(octets), 160), cards):
            r = artifact.Record(low=i, frag=octets[i:i+160], key=(i//160,))
            self.add_fragment(r)
            self._frags[-1].hollerith = h
        self.completed()
        self.add_type('HollorithCard')
