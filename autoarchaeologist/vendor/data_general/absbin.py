#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Data General "Absolute Binary" object file format
'''

import struct

class Invalid(Exception):
    ''' Invalid AbsBin record '''

class AbsBinRec():
    '''
       An AbsBin record
       ----------------
       Zero bytes between records are allowed, we count them and
       print them in a paranthesis in front of the record.

    '''

    def __init__(self, this, i):
        self.padlen = 0
        while i < len(this) and not this[i]:
            self.padlen += 1
            i += 1
        if len(this[i:]) < 6:
            raise Invalid("Too short (%d)" % len(this[i:]))
        words = struct.unpack("<h", this[i:i + 2])
        if words[0] <= -17:
            n_words = 4
        elif -16 <= words[0] <= -1:
            n_words = 3 + -words[0]
        elif words[0] == 1:
            n_words = 3
        else:
            raise Invalid("Bad Count (%d @0x%x)" % (words[0], i))
        if len(this[i:]) < n_words * 2:
            raise Invalid("Insufficient bytes")
        self.words = struct.unpack("<%dH" % n_words, this[i:i + n_words*2])
        s = sum(self.words) & 0xffff
        if s:
            #print("" + " ".join(["%04x" % x for x in self.words]))
            raise Invalid("Checksum error (0x%04x @0x%x)" % (s, i))

    def __repr__(self):
        return "<ABR " + " ".join(["%04x" % j for j in self.words]) + ">"

    def length(self):
        ''' Source length of record incl padding '''
        return self.padlen + 2 * len(self.words)

    def ascii(self, endian, pfx):
        t = ""
        t += pfx * (20 - len(self.words))
        t += "|"
        for i in self.words[3:]:
            for j in endian(i):
                if j == 0x26:
                    t += "&amp;"
                elif j == 0x3c:
                    t += "&lt;"
                elif 32 < j < 126:
                    t += "%c" % j
                else:
                    t += " "
        t += "|"
        return t

    def html_as_interpretation(self, fo):
        ''' Render as hex words '''
        t = "    "
        if self.padlen:
            t += "(%3d) " % self.padlen
        else:
            t += "      "
        t += " ".join(["%04x" % j for j in self.words])
        def big_endian(i):
            yield i >> 8
            yield i & 0xff
        def little_endian(i):
            yield i & 0xff
            yield i >> 8
        t += self.ascii(big_endian, "     ")
        t += self.ascii(little_endian, "  ")

        fo.write(t + '\n')

class AbsBin():
    '''
       An AbsBin file
       --------------

       Leading zeros are ignored.
       File ends with record having first word == 1
    '''

    def __init__(self, this):
        if this.has_type("AbsBin"):
            return

        idx = 0
        while idx < len(this) and not this[idx]:
            idx += 1

        pfx = idx
        records = []
        while idx < len(this):
            try:
                j = AbsBinRec(this, idx)
            except Invalid as error:
                if records:
                    txt = "AbsBin matched %d records," % len(records)
                    txt += " but then ran into %s" % str(error)
                    this.add_comment(txt)
                return
            records.append(j)
            idx += j.length()
            if j.words[0] == 1:
                break

        if len(records) < 2:
            return

        this = this.create(start=pfx, stop=idx)
        if not this.has_type("AbsBin"):
            this.add_type("AbsBin")
            self.this = this
            self.records = records
            self.this.add_interpretation(self, self.html_as_interpretation)

    def html_as_interpretation(self, fo, _this):
        ''' Let the records render themselves '''
        fo.write("<H3>AbsBin</H3>\n")
        fo.write("<pre>\n")
        for i in self.records:
            i.html_as_interpretation(fo)
        fo.write("</pre>\n")
