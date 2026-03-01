#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Commodore "PETSCII" Type-case
   =============================
'''

from ...base import type_case as tc

class PetScii(tc.TypeCase):
    ''' ... '''

    def __init__(self):
        super().__init__("PETSCII")
        self.set_slug(0x0d, ' ', '\n')

        for i in range(0x20, 0x40):
            self.set_slug(i, "%c" % i)

        self.set_slug(0x40, "@")
        for i in range(0x41, 0x5b):
            self.set_slug(i, "%c" % (i^0x20))
        self.set_slug(0x5b, "[")
        self.set_slug(0x5c, "£")
        self.set_slug(0x5d, "]")
        self.set_slug(0x5e, "↑")
        self.set_slug(0x5f, "←")

        self.set_slug(0x60, "─")
        for i in range(0x61, 0x7b):
            self.set_slug(i, "%c" % (i^0x20))
        self.set_slug(0x7b, "┼")
        self.set_slug(0x7c, "┼")
        self.set_slug(0x7d, "│")
        #self.set_slug(0x7e
        #self.set_slug(0x7f

        self.set_slug(0xa0, " ", flags=self.IGNORE)
        self.set_slug(0xa1, "▌")
        self.set_slug(0xa2, "▄")
        self.set_slug(0xa3, "▔")
        self.set_slug(0xa4, "▁")
        self.set_slug(0xa5, "▏")
        self.set_slug(0xa6, "▒")
        self.set_slug(0xa7, "▕")
        #self.set_slug(0xa8
        #self.set_slug(0xa9
        #self.set_slug(0xaa
        self.set_slug(0xab, "├")
        self.set_slug(0xac, "▗")
        self.set_slug(0xad, "└")
        self.set_slug(0xae, "┐")
        self.set_slug(0xaf, "▂")

        self.set_slug(0xb0, "┌")
        self.set_slug(0xb1, "┴")
        self.set_slug(0xb2, "┬")
        self.set_slug(0xb3, "┤")
        self.set_slug(0xb4, "▎")
        self.set_slug(0xb5, "▍")
        #self.set_slug(0xb6,
        #self.set_slug(0xb7,
        #self.set_slug(0xb8,
        self.set_slug(0xb9, "▃")
        self.set_slug(0xba, "✓")
        self.set_slug(0xbb, "▖")
        self.set_slug(0xbc, "▝")
        self.set_slug(0xbd, "┘")
        self.set_slug(0xbe, "▘")
        self.set_slug(0xbf, "▚")

        for i in range(0xc1, 0xdb):
            self.set_slug(i, "%c" % (i^0x80))
        self.set_slug(0xdb, "┼")
        self.set_slug(0xdd, "│")
        #self.set_slug(0xde
        #self.set_slug(0xdf
        self.set_slug(0xe0, " ")
        self.set_slug(0xe1, "▌")
        self.set_slug(0xe2, "▄")
        self.set_slug(0xe3, "▔")
        self.set_slug(0xe4, "▁")
        self.set_slug(0xe5, "▏")
        self.set_slug(0xe6, "▒")
        self.set_slug(0xe7, "▕")
        #self.set_slug(0xa8
        #self.set_slug(0xa9
        #self.set_slug(0xaa
        self.set_slug(0xeb, "├")
        self.set_slug(0xec, "▗")
        self.set_slug(0xed, "└")
        self.set_slug(0xee, "┐")
        self.set_slug(0xef, "▂")

        self.set_slug(0xf0, "┌")
        self.set_slug(0xf1, "┴")
        self.set_slug(0xf2, "┬")
        self.set_slug(0xf3, "┤")
        self.set_slug(0xf4, "▎")
        self.set_slug(0xf5, "▍")
        #self.set_slug(0xf6,
        #self.set_slug(0xf7,
        #self.set_slug(0xf8,
        self.set_slug(0xf9, "▃")
        self.set_slug(0xfa, "✓")
        self.set_slug(0xfb, "▖")
        self.set_slug(0xfc, "▝")
        self.set_slug(0xfd, "┘")
        self.set_slug(0xfe, "▘")
        #self.set_slug(0xff
