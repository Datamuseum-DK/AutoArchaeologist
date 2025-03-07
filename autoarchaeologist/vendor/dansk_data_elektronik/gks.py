#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

import struct

from ...generic import iso8632_gcm as gcm

class DDE_GKSFile(gcm.CGM_Data):

    def gdp_3(self, oper, elem):
        if oper == 0:
            e = elem.priv[-1]
            if len(e) != 16:
                self.error = "Wrong data length" + str(elem)
            d = struct.unpack(">dd", e)
            elem.priv = (*elem.priv[:-1], d)
        elif oper == 1:
            self.fdo.write(' GDP3 ' + str(elem.priv))
        elif oper == 2:
            self.gdp_polyline(elem)

class GKS_File():

    def __init__(self, this):
        if b'GKS metafile' in this[:64].tobytes():
            this.add_type("GKS")
            this.add_interpretation(self, self.render_gks)
            self.this = this

    def render_gks(self, fo, this):
        print("CGM Render", this)
        cgm = DDE_GKSFile(this)
        if cgm.error:
            print("CGM Error", this, cgm.error)
        fn = self.this.filename_for(suf=".svg")
        cgm.render_svg(open(fn.filename, "w"))
        fo.write("<H3>GKS Metafile</H3>\n")
        fo.write('<img src="%s"/>\n' % fn.link)
        fo.write("<pre>\n")
        cgm.list(fo)
        fo.write("</pre>\n")
