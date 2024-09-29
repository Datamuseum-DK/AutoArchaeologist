#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   HTML decorator class
'''

class Decorator():
    ''' Class which decorates the HTML output '''

    def __init__(self, excavation):
        self.top = excavation

    def produce_html(self):
        ''' Produce default HTML pages '''

        self.produce_front_page()

        for this in self.top.hashes.values():
            self.produce_artifact_page(this)

        return self.top.filename_for(self.top).link

    def produce_artifact_page(self, this):
        if self.top.downloads and len(this) < self.top.download_limit:
            binfile = self.top.filename_for(this, suf=".bin")
            this.writetofile(open(binfile.filename, 'wb'))

        fnt = self.top.filename_for(this)
        fmt = None
        with open(fnt.filename, "w") as fot:
            self.html_prefix(fot, this)
            self.html_artifact_head(fot, this)
            more = this.html_page(fot)
            if more:
                fmt = self.top.filename_for(this, suf="_more.html")
                fot.write("<H3>More…</H3>\n")
                fot.write('<A href="%s">Full View</A>\n' % fmt.link)
            self.html_suffix(fot, this)
        if not fmt:
            return
        with open(fmt.filename, "w") as fot:
            self.html_prefix(fot, this)
            self.html_artifact_head(fot, this)
            this.html_page(fot, domore=True)
            fot.write("<H3>Less…</H3>\n")
            fot.write('<A href="%s">Reduced view</A>\n' % fnt.link)
            self.html_suffix(fot, this)

    def produce_front_page(self):
        ''' Top level html page '''
        fn = self.top.filename_for(self.top, suf=".css")
        with open(fn.filename, "w") as file:
            file.write(self.CSS)
        fn = self.top.filename_for(self.top)
        fo = open(fn.filename, "w")
        self.html_prefix(fo, self.top)

        fo.write("<pre>\n")
        fo.write(self.html_link_to(self.top, "top"))
        fo.write("</pre>\n")
        self.top.index.Index(self.top).produce(fo)

        fo.write("<H2>Top level artifacts</H2>")
        fo.write("<table>\n")
        fo.write("<thead>\n")
        fo.write("<th>Artifact</th>\n")
        fo.write("<th>Unique</th>\n")
        fo.write("<th>Description<th>\n")
        fo.write("</thead>\n")
        for n, this in enumerate(self.top.children):
            if n & 1:
                fo.write('<tr class="stripe">\n')
            else:
                fo.write('<tr>\n')
            fo.write('<td>' + self.top.html_link_to(this) + '</td>\n')
            fo.write('<td>' + this.metrics.terse() + '</td>\n')
            fo.write('<td>' + this.html_description() + "</td>\n")
            fo.write("</tr>\n")
            fo.write("<tr>\n")
            fo.write("<td></td>")
            fo.write("<td></td>")
            fo.write('<td style="font-size: 70%;">')
            fo.write(", ".join(self.dotdotdot(sorted({y for x, y in this.iter_notes(True)}))))
            fo.write("</td>\n")
            fo.write("</tr>\n")
        fo.write("</table>\n")

        self.top.emit_interpretations(fo, domore=True)

        self.html_suffix(fo, self)

    def html_link_to(self, this, link_text=None, anchor=None, **kwargs):
        ''' Return a HTML link to an artifact '''
        t = '<A href="'
        t += self.top.filename_for(this, **kwargs).link
        if anchor:
            t += "#" + anchor
        t += '">'
        if link_text:
            t += link_text
        else:
            t += str(this)
        t += '</a>'
        return t

    def html_prefix_head(self, fo, this):
        ''' meta lines inside <head>…</head> '''
        fo.write('<meta charset="utf-8">\n')
        if this == self.top:
            fo.write('<title>AutoArchaeologist</title>\n')
        elif isinstance(this, str):
            fo.write('<title>' + this + '</title>\n')
        else:
            fo.write('<title>' + str(this) + '</title>\n')

    def html_prefix_banner(self, _fo, _this):
        ''' Top of pages banner '''
        return

    def html_prefix(self, fo, this):
        ''' Top of the HTML pages '''
        fo.write("<!DOCTYPE html>\n")
        fo.write("<html>\n")
        fo.write("<head>\n")
        self.html_prefix_head(fo, this)
        self.html_prefix_style(fo, this)
        fo.write("</head>\n")
        fo.write("<body>\n")
        self.html_prefix_banner(fo, this)

    def html_artifact_head(self, fo, this):
        fo.write("<pre>")
        fo.write(self.html_link_to(self.top, "top"))
        if this != self.top and self.top.download_links and self.top.download_limit > len(this):
            fo.write(" - " + self.html_link_to(this, "download", suf=".bin"))
        fo.write("</pre>\n")
        if this.ns_roots:
            self.top.index.Index(this).produce(fo)

    def html_suffix(self, fo, _this):
        ''' Tail of all the HTML pages '''
        fo.write("</body>\n")
        fo.write("</html>\n")

    def html_derivation(self, _fo, target=False):
        ''' Duck-type as Artifact'''
        return ""

    def html_prefix_style(self, fo, _target):
        ''' Duck-type as Artifact '''
        rdir = self.top.filename_for(self.top, suf=".css").link
        fo.write('<link rel="stylesheet" href="%s">\n' % rdir)

    def dotdotdot(self, gen, limit=35):
        ''' Return a limited number of elements, and mark as truncated if so. '''
        for n, i in enumerate(gen):
            if n == limit:
                yield "[…]"
                return
            yield i


    CSS = '''
        body {
            font-family: "Inconsolata", "Courier New", mono-space;
        }
        td,th {
            padding: 0 10px 0;
        }
        th {
            position: sticky; top: 0; background-color: #eeeeee;
            border-bottom: 1px solid black;
            padding: 5px;
        }
        th.v { writing-mode: sideways-rl; vertical-align: bottom;}
        th.l { vertical-align: bottom; text-align: left; }
        th.r { vertical-align: bottom; text-align: right; }
        th.c { vertical-align: bottom; text-align: center; }
        td.l { vertical-align: top; text-align: left; }
        td.r { vertical-align: top; text-align: right; }
        td.c { vertical-align: top; text-align: center; }
        td.s, th.s { font-size: .8em; }
        tr.stripe:nth-child(2n+1) { background-color: #ddffdd; }
    '''
