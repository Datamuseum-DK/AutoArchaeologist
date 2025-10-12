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
        self.this = this
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

    def octets(self, endian):
        ''' Allow for valid even parity '''
        for i in self.words[3:]:
            for j in endian(i):
                if j < 0x80:
                    yield j
                elif bin(j)[2:].count('1') & 1:
                    # Odd parity
                    yield j
                else:
                    # Even parity
                    yield j & 0x7f

    def text(self, endian):
        ''' Render as text with given endianess '''
        return self.this.type_case.decode(self.octets(endian))

    def render(self):
        ''' Render as hex words '''
        t = "    "
        if self.padlen:
            t += "(%3d) " % self.padlen
        else:
            t += "      "
        t += (" ".join(["%04x" % j for j in self.words])).ljust(5*19)
        def big_endian(i):
            yield i >> 8
            yield i & 0xff
        def little_endian(i):
            yield i & 0xff
            yield i >> 8
        t += " ┊" + self.text(big_endian).ljust(2*16)
        t += "┊" + self.text(little_endian).ljust(2*16) + "┊"

        return t

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

        that = this.create(start=pfx, stop=idx)
        if not that.has_type("AbsBin"):
            that.add_type("AbsBin")
            with that.add_utf8_interpretation("AbsBin") as file:
                for i in records:
                    file.write(i.render() + "\n")
