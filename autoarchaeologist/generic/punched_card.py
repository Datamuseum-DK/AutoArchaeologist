#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   punched card
   ------------

   Render an image of unloved punched cards

'''

from ..base import type_case

class PunchedCard():
    ''' Render an image of unloved punched cards '''

    def __init__(self, this):
        if this.children:
            return
        if this.has_type("EbcdicCard"):
            self.ebcdic(this)
        elif this.has_type("HollorithCard"):
            self.hollerith(this)

    def ebcdic(self, this):
        ''' print text/hex '''
        this.type_case = type_case.WellKnown("cp037")
        with this.add_utf8_interpretation("EBCDIC Cards") as file:
            mixed = False
            hasline = False
            for r in this.iter_rec():
                t = list(this.type_case.slugs[x] for x in r.frag)
                good = True
                for i in t:
                    if i.flags & this.type_case.INVALID:
                        good = False
                if good:
                    file.write("".join(x.short for x in t) + "\n")
                    hasline = False
                else:
                    if not hasline:
                        file.write('─' * 80 + "\n")
                    file.write("".join(x.short for x in t) + "\n")
                    file.write("".join("%x" % (x >> 4) for x in r.frag) + "\n")
                    file.write("".join("%x" % (x & 0xf) for x in r.frag) + "\n")
                    file.write('─' * 80 + "\n")
                    hasline = True
                    mixed = True

            if mixed:
                this.add_type("MixedCard")

    def hollerith(self, this):
        ''' print picture '''
        with this.add_utf8_interpretation("Punched Cards") as file:
            for r in this.iter_rec():
                file.write('━' * 80 + "\n")
                m = 11
                while m:
                    l = "".join("-#"[(x >> m) & 1] for x in r.hollerith)
                    file.write(l + "\n")
                    m -= 1
            file.write('━' * 80 + "\n")
