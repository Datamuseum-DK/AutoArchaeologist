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
        self.children = set(this.iter_all_children())
        self.dups = {}
        self.overlaps = {}
        self.unique = None
        if len(self.children) > 1:
            self.children.remove(this)

    def reduce(self, peers):
        for that in peers:
            if that == self.this:
                continue
            xsect = that.metrics.children & self.children
            self.overlaps[that] = xsect
            for i in xsect:
                j = self.dups.get(i, 0)
                self.dups[i] = j + 1
        self.unique = self.children - set(self.dups)

    def terse(self):
        n_overlaps_shown = 5
        l_children = len(self.children)
        l_unique = len(self.unique)
        if l_children == l_unique:
            return "%d" % l_unique
        ff = self.this.filename_for(suf="_metric.html")
        with open(ff.filename, "w") as file:
            self.this.top.html_prefix(file, self.this)
            self.this.top.html_artifact_head(file, self.this)
            self.this.html_page_head(file)
            file.write("<H2>Metrics</H2>\n")
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
                file.write("<td>" + that.summary(names=True, notes=True) + "</td>")
                file.write("</tr>\n")
            file.write("</table>\n")
            if l_unique:
                file.write("<H2>Unique</H2>\n")
                file.write("<table>\n")
                for that in sorted(self.unique):
                    file.write("<tr><td>" + that.summary(names=True, notes=True) + "</td></tr>")
                file.write("</table>\n")
            if l_unique != l_children:
                file.write("<H2>Overlaps</H2>\n")
                file.write("<table>\n")
                for that, count in sorted(self.dups.items(),key= lambda x: x[1]):
                    file.write("<tr>")
                    file.write("<td>%d</td>" % count)
                    file.write("<td>" + that.summary(names=True, notes=True) + "</td>")
                    file.write("</tr>")
                file.write("</table>\n")
            self.this.top.html_suffix(file, self.this)
        return self.this.top.html_link_to(
            self.this,
            "%d/%d" % (l_unique, l_children),
            suf="_metric.html",
        )
