#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    AutoArchaeologist Metrics
    ----------------------------

    Calculate various metrics such as uniqueness and overlap
    for top-level artifacts.
'''

class Metrics():

    def __init__(self, this):
        self.this = this
        self.children = set(x for x in this.iter_all_children() if x.metrics is not False)
        self.overlaps = {}
        if len(self.children) > 1:
            self.children.remove(this)
        self.unique = set(self.children)
        self.relpath = self.this.basename_for(suf="_metrics.html")

    def reduce(self, peers):
        for that in peers:
            if that != self.this:
                xsect = that.metrics.children & self.children
                self.overlaps[that] = xsect
                self.unique -= xsect

    def terse(self):
        n_overlaps_shown = 5
        l_children = len(self.children)
        l_unique = len(self.unique)
        if l_children == l_unique:
            return (None, "%d" % l_unique)
        title = str(self.this) + " Metrics"
        with self.this.top.decorator.html_file(self.relpath, title) as file:
            file.write("<pre>")
            file.link_to(self.this.top.basename_for(self.this.top), "top")
            file.write("</pre>")

            file.write("<H2>")
            file.link_to_that(self.this)
            file.write(" Metrics</H2>\n")
            file.write("<table>\n")
            file.write("<thead>\n")
            file.write("<tr>\n")
            file.write("<th>Overlaps</th>\n")
            file.write("<th>Artifact</th>\n")
            file.write("</tr>\n")
            file.write("</thead>\n")
            if l_unique:
                file.write("<tr>")
                file.write("<td>%6d</td>" % l_unique)
                file.write("<td>Unique</td>")
                file.write("</tr>\n")
                file.write("\n")
            for that, overlap in sorted(self.overlaps.items(), key=lambda x: -len(x[1])):
                if len(overlap) == 0:
                    break
                file.write("<tr>")
                file.write("<td>%6d</td>" % len(overlap))
                file.write("<td>")
                file.link_to_that(that)
                file.write(" ")
                file.write(that.summary(names=True, notes=True) + "</td>")
                file.write("</tr>\n")
            file.write("</table>\n")
            if l_unique:
                file.write("<H2>Unique</H2>\n")
                file.write("<table>\n")
                for that in sorted(self.unique):
                    file.write("<tr><td>")
                    file.link_to_that(that)
                    file.write(that.summary(names=True, notes=True) + "</td></tr>")
                file.write("</table>\n")

        return (self.relpath, "%d/%d" % (l_unique, l_children))
