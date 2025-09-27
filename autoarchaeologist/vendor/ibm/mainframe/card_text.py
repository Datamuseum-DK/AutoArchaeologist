#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Punched card text
   =================
'''

class CardText():

    def __init__(self, this):
        if len(this) % 80:
            return

        v, _i = this.type_case.is_valid(this)
        if not v:
            return

        this.add_type("PunchedCardText")

        with this.add_utf8_interpretation("Punched Card Text") as file:
            for n, a in enumerate(range(0, len(this), 80)):
                file.write("%06d|" % n)
                file.write(this.type_case.decode_long(this[a:a+80]))
                file.write("\n")
