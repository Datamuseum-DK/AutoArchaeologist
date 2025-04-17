#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   HTML decorator class
   ~~~~~~~~~~~~~~~~~~~~

   This is an attempt to make it easier to control the visual look of
   the HTML which AA produces.

'''

import os
import html

class HtmlFile():
    '''
       A single HTML file
       ~~~~~~~~~~~~~~~~~~

       This class controls three parts of all HTML pages:
       
       .html_prefix()  Up to and including the <body> tag

       .html_banner()  Comes right after <body>

       .html_suffix()  </body> and everything after

       Also:

       .path_to() produce tag with relative paths to other output file.
       .link_to() produce <A> link to other output file.

    '''

    def __init__(self, top, relpath, filepath, title):
        self.top = top
        self.relpath = relpath
        self.reldir = os.path.split(relpath)[0]
        self.filepath = filepath
        self.title = title
        self.depth = len(os.path.split(relpath)) - 1
        self.fd = None

    def __enter__(self):
        self.fd = open(self.filepath, "w", encoding="utf8")
        self.html_prefix()
        self.html_banner()
        return self

    def __exit__(self,ex_type, ex_value, ex_traceback):
        self.html_suffix()
        self.fd.close()
        return False

    def path_to(self, tag, other):
        ''' Tag with relative path to another file '''
        self.write(tag + '="' + os.path.relpath(other, self.reldir) + '"')

    def link_to(self, other, text):
        ''' <A> Link to another file '''
        self.write('<A ')
        self.path_to("href", other)
        self.write('>' + text + '</A>')

    def write(self, what):
        ''' ... '''
        self.fd.write(what)

    def html_prefix(self):
        ''' Prefix on all HTML pages '''

        self.write("<!DOCTYPE html>\n")
        self.write("<html>\n")
        self.write("<head>\n")
        self.write('  <title>' + self.title + '</title>\n')
        self.write('  <meta charset="utf-8">\n')
        self.write('  <link rel="stylesheet" ')
        self.path_to('href', 'style.css')
        self.write('>\n')
        self.write("</head>\n")
        self.write("<body>\n")

    def html_suffix(self):
        ''' Suffix on all HTML pages '''

        self.write("</body>\n")
        self.write("</html>\n")

    def html_banner(self):
        ''' Top of page banner '''

        self.write('Excavated with: ')
        self.write(' <A href="https://github.com/Datamuseum-DK/AutoArchaeologist">')
        self.write('AutoArchaeologist</A> - Free &amp; Open Source Software.\n')

class Decorator():
    ''' Class which produces/decorates the HTML output '''

    COPY_FILES = (
        "style.css",
        "Inconsolata-Regular.ttf",
        "Inconsolata-Bold.ttf",
    )

    HTML_FILE = HtmlFile

    def __init__(self, excavation):
        self.top = excavation
        self.html_dir = excavation.html_dir

    def produce_html(self):
        '''
           Produce default HTML pages
           ~~~~~~~~~~~~~~~~~~~~~~~~~~

           This entry point called once the excavation is complete.
        '''

        self.copy_aux_files()

        self.produce_front_page()

        for this in self.top.hashes.values():
            self.produce_artifact_page(this)

        return self.top.filename_for(self.top).link

    def html_file(self, relpath, title):
        ''' file-like HTML file object '''

        return self.HTML_FILE(
            self.top,
            relpath,
            os.path.join(self.html_dir, relpath),
            html.escape(title),
        )

    def produce_artifact_page(self, this):
        relpath = self.top.basename_for(this)

        if self.top.downloads and len(this) < self.top.download_limit:
            binfile = self.top.basename_for(this, suf=".bin")
        else:
            binfile = None

        if binfile:
            with open(os.path.join(self.html_dir, binfile), 'wb') as file:
                this.writetofile(file)

        fmt = None
        with self.html_file(relpath, str(this)) as fot:
            self.html_artifact_head(fot, this, binfile)
            more = this.html_page(fot)
            if more:
                fmt = self.top.basename_for(this, suf="_more.html")
                fot.write('<H3>')
                fot.link_to(fmt, 'Full view')
                fot.write('</H3>\n')
        if not fmt:
            return
        with self.html_file(fmt, str(this)) as fot:
            self.html_artifact_head(fot, this, binfile)
            this.html_page(fot, domore=True)
            fot.write('<H3>')
            fot.link_to(relpath, 'Reduced view')
            fot.write('</H3>\n')

    def produce_front_page(self):
        ''' Top level html page '''
        with self.html_file("index.html", "Top") as fo:

            fo.write("<pre>\n")
            #fo.write(self.html_link_to(self.top, "top"))
            fo.link_to("index.html", "top")
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
                fo.write('<td>')
                where, desc = this.metrics.terse()
                if where:
                    fo.link_to(where, desc)
                else:
                    fo.write(desc)
                fo.write('</td>')
                fo.write('<td>' + this.html_description() + "</td>\n")
                fo.write("</tr>\n")
                fo.write("<tr>\n")
                fo.write("<td></td>")
                fo.write("<td></td>")
                fo.write('<td style="font-size: 70%;">')
                fo.write(", ".join(self.dotdotdot(sorted({y for _x, y, _z in this.iter_notes(True)}))))
                fo.write("</td>\n")
                fo.write("</tr>\n")
            fo.write("</table>\n")

            self.top.emit_interpretations(fo, domore=True)

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

    def html_artifact_head(self, fo, this, binfile):
        fo.write("<pre>")
        fo.link_to(self.top.basename_for(self.top), "top")
        fo.write(" - ")
        fo.link_to(this.basename_for("_metrics.html"), "metrics")
        if self.top.download_links and binfile:
            fo.write(" - ")
            fo.link_to(binfile, "download")
        fo.write("</pre>\n")
        if this.ns_roots:
            self.top.index.Index(this).produce(fo)

    def html_derivation(self, _fo, target=False):
        ''' Duck-type as Artifact'''
        return ""

    def dotdotdot(self, gen, limit=35):
        ''' Return a limited number of elements, and mark as truncated if so. '''
        for n, i in enumerate(gen):
            if n == limit:
                yield "[…]"
                return
            yield i

    def copy_aux_files(self):
        ''' copy css, fonts, etc '''
        srcdir = os.path.dirname(__file__)
        for fname in self.COPY_FILES:
            b = open(os.path.join(srcdir, fname), "rb").read()
            open(os.path.join(self.html_dir, fname), "wb").write(b)
