#!/usr/bin/env python3

'''
    AutoArchaeologist Excavation Class
    ----------------------------------

    `Excavation` holds the global state for analyzing a set
    of related artifacts, so that programs can juggle
    multiple excavation.
'''

import os
import mmap
import hashlib

import autoarchaeologist.artifact as artifact
import autoarchaeologist.type_case as type_case

def dotdotdot(gen, limit=35):
    ''' Return a limited number of elements, and mark as truncated if so. '''
    for n, i in enumerate(gen):
        if n == limit:
            yield "[…]"
            return
        yield i

class DuplicateArtifact(Exception):
    ''' Top level artifacts should not be identical '''

class OutputFile():
    ''' Output files have a physical filename and a html reference '''

    def __init__(self, filename, link):
        self.filename = filename
        self.link = link

class TempFile():
    ''' Self deleting temporary file '''
    def __init__(self, filename):
        self.filename = filename

    def __del__(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

class Excavation():

    '''
        Excavation
        ----------

	Holds the index of artifacts, and can produce a pile of
	HTML files to present the finds.

        All artifacts have their `.top` member pointing here.

	Excavation objects also duck-types as `ArtifactClass` to
	make the linkage 'just work'.

    '''

    def __init__(
        self,
        digest_prefix=9,           # SHA256 length in links/filenames
        downloads=False,   	   # Create downloadable .bin files
        download_links=False,      # Include links to .bin files
        download_limit=15 << 20,   # Only produce downloads if smaller than
        hexdump_limit=8192,	   # How many bytes to hexdump
        html_dir="/tmp/aa",	   # Where to put HTML output
        subdir=None,		   # Subdir under html_dir
        link_prefix=None,	   # Default is file://[…]
    ):

        # Sanitize parameters

        if subdir:
            html_dir = os.path.join(html_dir, subdir)

        os.makedirs(html_dir, exist_ok=True)

        if link_prefix is None:
            # use "file://{abs path to html_dir}/"
            dir_fd = os.open(".", os.O_RDONLY)
            os.chdir(html_dir)
            abspath = os.getcwd()
            os.chdir(dir_fd)
            os.close(dir_fd)
            link_prefix = "file://" + abspath + "/"

        if download_links:
            downloads = True


        # Parameters
        self.digest_prefix = digest_prefix
        self.downloads = downloads
        self.download_links = download_links
        self.download_limit = download_limit
        self.hexdump_limit = hexdump_limit
        self.html_dir = html_dir
        self.link_prefix = link_prefix

        self.hashes = {}
        self.busy = True
        self.queue = []
        self.examiners = []
        self.names = set()

        self.index = {}

        # Duck-type as ArtifactClass
        self.top = self
        self.children = []
        self.by_class = {} # Experimental extension point

        # Default character set
        self.type_case = type_case.Ascii()

    def __lt__(self, other):
        # Duck-type as ArtifactClass
        return -1

    def add_artifact(self, this):
        ''' Add an artifact, and start examining it '''
        assert isinstance(this, artifact.ArtifactClass)
        assert this.digest not in self.hashes
        self.hashes[this.digest] = this
        self.queue.append(this)
        if this.type_case is None:
            this.type_case = self.type_case
        if not self.busy:
            self.examine()

    def add_examiner(self, ex):
        ''' Add an examiner function '''
        self.examiners.append(ex)

    def add_top_artifact(self, bits, description=None):
        ''' Add a top-level artifact '''

        if not description:
            description = "Top-level Artifact"

        digest = hashlib.sha256(bits).hexdigest()

        this = self.hashes.get(digest)
        if this:
            t = "Artifact " + description
            t += "\n\tis identical to\n"
            t += this.summary(False)
            raise DuplicateArtifact("\n" + t + "\n")

        this = artifact.ArtifactClass(self, digest, bits)
        this.add_description(description)
        return this

    def add_file_artifact(self, filename, description=None):
        ''' Add a file as top-level artifact '''

        if not description:
            description = filename

        fi = open(filename, "rb")
        mapped = mmap.mmap(
            fi.fileno(),
            0,
            access=mmap.ACCESS_READ,
        )
        return self.add_top_artifact(mapped, description)

    def add_to_index(self, key, this):
        ''' Add things to the index '''
        i = self.index.setdefault(key[0], dict())
        j = i.setdefault(key, set())
        j.add(this)

    def start_examination(self):
        ''' As it says on the tin... '''
        self.busy = False
        self.examine()

    def examine(self):
        ''' Explore all artifacts serially '''
        assert not self.busy
        self.busy = True
        while self.queue:
            this = self.queue.pop(0)
            for ex in self.examiners:
                ex(this)
                if this.taken:
                    break
            this.examined()
        self.busy = False

    def polish(self):
        ''' Polish things up before HTML production '''

        # Find the shortest unique digest length
        while True:
            if len({x[:self.digest_prefix] for x in self.hashes}) == len(self.hashes):
                break
            self.digest_prefix += 1

        # Reset summaries to pick it up
        for this in self.hashes.values():
            this.index_representation = None

    def iter_notes(self):
        ''' Return all notes '''
        for child in self.children:
            yield from child.iter_notes(True)

    def filename_for(self, this, suf=".html", temp=False):
        ''' Come up with a suitable filename related to an artifact '''
        if this == self:
            base = "index" + suf
        else:
            basedir = this.digest[:2]
            os.makedirs(os.path.join(self.html_dir, basedir), exist_ok=True)
            base = os.path.join(basedir, this.digest[:self.digest_prefix] + suf)
        if temp:
            return TempFile(os.path.join(self.html_dir, base))
        return OutputFile(
            os.path.join(self.html_dir, base),
            os.path.join(self.link_prefix, base),
        )

    def produce_html(
        self,
    ):
        ''' Produce default HTML pages '''

        self.polish()

        self.produce_front_page()

        for this in self.hashes.values():

            if self.downloads and len(this) < self.download_limit:
                binfile = self.filename_for(this, suf=".bin")
                this.writetofile(open(binfile.filename, 'wb'))
            fn = self.filename_for(this)
            fo = open(fn.filename, "w")
            self.html_prefix(fo, this)
            this.html_page(fo)
            self.html_suffix(fo)

        return self.filename_for(self).link

    def produce_front_page(self):
        ''' Top level html page '''
        fn = self.filename_for(self)
        fo = open(fn.filename, "w")
        self.html_prefix(fo, self)

        fo.write("<H2>Links to index</H2>")
        fo.write("<table>\n")
        cols = 48
        index_keys = sorted(self.index)
        for row in [index_keys[i:i + cols] for i in range(0, len(index_keys), cols)]:
            fo.write("<tr>\n")
            for cell in row:
                fo.write("<td>" + self.html_link_to(self, cell, anchor="IDX_" + cell) + "</td>\n")
            fo.write("</tr>\n")
        fo.write("</table>\n")

        fo.write("<H2>Top level artifacts</H2>")
        fo.write("<table>\n")
        for this in self.children:
            fo.write("<tr>\n")
            fo.write("<td>" + self.html_link_to(this) + '</td>\n')
            fo.write("<td>" + this.summary(ident=False) + '</td>\n')
            fo.write("</tr>\n")
            fo.write("<tr>\n")
            fo.write("<td></td>")
            fo.write('<td style="font-size: 70%;">')
            fo.write(", ".join(dotdotdot(sorted({y for x, y in this.iter_notes(True)}))))
            fo.write("</td>\n")
            fo.write("</tr>\n")
        fo.write("</table>\n")

        fo.write("<H2>Index</H2>")
        for idxkey in index_keys:
            fo.write('<H3><A name="IDX_%s">Index: %s</A></H3>\n' % (idxkey, idxkey))
            fo.write("<table>\n")
            for i, j in sorted(self.index[idxkey].items()):
                fo.write('<tr>\n')
                fo.write('<td style="font-size: 80%; vertical-align: top;">\n')
                fo.write('<A name="IDX_%s">%s</A>' % (i, i))
                fo.write('</td>\n')
                fo.write('<td style="font-size: 80%;">')
                for x in sorted(j):
                    fo.write("   " + x.summary(notes=True) + "<br>\n")
                fo.write('</td>\n')
            fo.write("</table>\n")

        self.html_suffix(fo)

    def html_link_to(self, this, link_text=None, anchor=None, **kwargs):
        ''' Return a HTML link to an artifact '''
        t = '<A href="'
        t += self.filename_for(this, **kwargs).link
        if anchor:
            t += "#" + anchor
        t += '">'
        if link_text:
            t += link_text
        else:
            t += this.name()
        t += '</a>'
        return t

    def html_prefix_head(self, fo, this):
        ''' meta lines inside <head>…</head> '''
        fo.write('<meta charset="utf-8">\n')
        if isinstance(this, Excavation):
            fo.write('<title>AutoArchaeologist</title>\n')
        else:
            fo.write('<title>' + this.name() + '</title>\n')

    def html_prefix_banner(self, _fo, _this):
        ''' Top of pages banner '''
        return

    def html_prefix(self, fo, this):
        ''' Top of the HTML pages '''
        fo.write("<!DOCTYPE html>\n")
        fo.write("<html>\n")
        fo.write("<head>\n")
        self.html_prefix_head(fo, this)
        fo.write("</head>\n")
        fo.write("<body>\n")
        self.html_prefix_banner(fo, this)
        fo.write("<pre>")
        fo.write(self.html_link_to(self, "top"))
        if not isinstance(this, Excavation) and self.download_links and self.download_limit > len(this):
            fo.write(" - " + self.html_link_to(this, "download", suf=".bin"))
        fo.write("</pre>\n")

    def html_suffix(self, fo):
        ''' Tail of all the HTML pages '''
        fo.write("</body>\n")
        fo.write("</html>\n")

    def html_derivation(self, _fo):
        ''' Duck-type as ArtifactClass '''
        return ""
