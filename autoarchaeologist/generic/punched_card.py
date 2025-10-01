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

class PunchedCard():
    ''' Render an image of unloved punched cards '''

    def __init__(self, this):
        if not this.has_type("PunchedCard"):
            return
        if this.children:
            return

        with this.add_utf8_interpretation("Punched Cards") as file:
            for r in this.iter_rec():
                file.write('=' * 80 + "\n")
                m = 11
                while m:
                    l = "".join("-#"[(x >> m) & 1] for x in r.hollerith)
                    file.write(l + "\n")
                    m -= 1
