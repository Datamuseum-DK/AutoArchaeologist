#!/usr/bin/env python3

'''
    AutoArchaeologist Excavation
    ----------------------------

    `Excavation` holds the global state for analyzing a set
    of related artifacts, so that programs can juggle
    multiple excavation (if need be)
'''

import os
import mmap
import hashlib
import tempfile
import html

from . import artifact
from . import index
from . import type_case
from . import result_page
from . import metrics
from . import decorator

class DuplicateArtifact(Exception):
    ''' Top level artifacts should not be identical '''

    def __init__(self, that, description):
        t = "Artifact:\n\t" + description
        t += "\nis identical to\n\t"
        t += that.summary(False)
        super().__init__("\n" + t + "\n")
        self.that = that

class OutputFile():
    ''' Output files have a physical filename and a html reference '''

    def __init__(self, filename, link):
        self.filename = filename
        self.link = link

    def __repr__(self):
        return "<OutputFile '" + self.filename + "'>"

class TempFile():
    ''' Self deleting temporary file '''
    def __init__(self, filename):
        self.filename = filename

    def __del__(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def __repr__(self):
        return "<TmpFile '" + self.filename + "'>"


class Excavation(result_page.ResultPage):

    '''
        Excavation
        ----------

	Holds the index of artifacts, and can produce a pile of
	HTML files to present the finds.

        All artifacts have their `.top` member pointing here.

	Excavation objects also duck-types as `Artifact` to
	make the linkage 'just work'.

    '''

    # How much to hexdump of unexplored artifacts
    MAX_LINES = 200

    def __init__(
        self,
        digest_prefix=9,           # SHA256 length in links/filenames
        downloads=False,   	   # Create downloadable .bin files
        download_links=False,      # Include links to .bin files
        download_limit=15 << 20,   # Only produce downloads if smaller than
        html_dir="/tmp/aa",	   # Where to put HTML output
        link_prefix=None,	   # Default is file://[…]
        spill_index=10,		   # Spill limit for index lines
        cache_dir=None,		   # Cache directory for collections
    ):

        super().__init__()
        # Sanitize parameters

        if cache_dir is None:
            cache_dir = os.environ.get("AUTOARCHAEOLOGIST_CACHE_DIR", None)
        if cache_dir is None:
            cache_dir = tempfile.gettempdir()
        self.cache_dir = cache_dir

        os.makedirs(html_dir, exist_ok=True)

        if link_prefix is None:
            # use "file://{abs path to html_dir}/"
            dir_fd = os.open(".", os.O_RDONLY)
            os.chdir(html_dir)
            abspath = os.getcwd()
            os.chdir(dir_fd)
            os.close(dir_fd)
            link_prefix = "file://" + abspath

        if download_links:
            downloads = True

        # Parameters
        self.digest_prefix = digest_prefix
        self.downloads = downloads
        self.download_links = download_links
        self.download_limit = download_limit
        self.html_dir = html_dir
        self.link_prefix = link_prefix
        self.spill_index = spill_index

        self.decorator = None

        self.hashes = {}
        self.busy = True
        self.queue = []
        self.examiners = []
        self.names = set()

        # Free for all dictionary for joining multi-volume artifacts.
        self.multivol = {}

        # Duck-type as Artifact
        self.top = self
        self.children = []
        self.by_class = {} # Experimental extension point

        self.type_case = type_case.Ascii()

    def __lt__(self, other):
        # Duck-type as Artifact
        return -1

    def adopt(self, this):
        this.top = self
        self.add_artifact(this)

    def add_artifact(self, this):
        ''' Add an artifact, and start examining it '''
        assert isinstance(this, artifact.ArtifactBase)
        assert this.digest not in self.hashes
        self.hashes[this.digest] = this
        self.queue.append(this)
        if this.type_case is None:
            this.type_case = self.type_case
        if not self.busy:
            self.examine()

    def add_examiner(self, *args):
        ''' Add an examiner function(s) '''
        for i in args:
            self.examiners.append(i)

    def add_top_artifact(self, what, description=None):
        ''' Add a top-level artifact '''

        if not description:
            description = "Top-level Artifact"

        if isinstance(what, artifact.ArtifactBase):
            that = what
        else:
            that = artifact.ArtifactStream(what)
        that.set_digest()
        # print("ATA", that, that.digest)
        digest = that.digest

        this = self.hashes.get(digest)
        if this:
            this.add_description(description)
            raise DuplicateArtifact(this, description)
        else:
            this = that
            this.add_description(description)
            self.adopt(this)
            this.add_parent(self)
        return this

    def add_file_artifact(self, filename, description=None, **kwargs):
        ''' Add a file as top-level artifact '''

        if not description:
            description = filename

        fi = open(filename, "rb")
        mapped = mmap.mmap(
            fi.fileno(),
            0,
            access=mmap.ACCESS_READ,
        )
        return self.add_top_artifact(mapped, description=description, **kwargs)

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

    def basename_for(self, this, suf=".html"):
        ''' Come up with a suitable filename related to an artifact '''
        if this == self:
            base = "index" + suf
        elif isinstance(this, str):
            base = this + suf
        else:
            basedir = this.digest[:2]
            os.makedirs(os.path.join(self.html_dir, basedir), exist_ok=True)
            base = os.path.join(basedir, this.digest[:self.digest_prefix] + suf)
        return base

    def filename_for(self, this, suf=".html", temp=False):
        ''' Come up with a suitable file for an artifact '''
        base = self.basename_for(this, suf)
        if temp:
            return TempFile(os.path.join(self.html_dir, base))
        return OutputFile(
            os.path.join(self.html_dir, base),
            os.path.join(self.link_prefix, base),
        )

    def produce_html(self):
        ''' Produce default HTML pages '''

        self.polish()

        self.calculate_metrics()

        if self.decorator is None:
            self.decorator = decorator.Decorator(self)

        self.decorator.produce_html()

        return self.filename_for(self).link

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
            t += str(this)
        t += '</a>'
        return t

    def html_prefix(self, fo, this):
        self.decorator.html_prefix(fo, this)

    def html_artifact_head(self, fo, this):
        self.decorator.html_artifact_head(fo, this)

    def html_suffix(self, fo, this):
        self.decorator.html_suffix(fo, this)

    def html_derivation(self, _fo, target=False):
        ''' Duck-type as Artifact'''
        return ""

    def iter_types(self):
        ''' Duck-type as Artifact '''
        if False:
            yield None

    def iter_notes(self):
        ''' Duck-type as Artifact '''
        if False:
            yield None

    def summary(self, *args, **kwargs):
        return "The entire excavation"

    def calculate_metrics(self):
        for that in self.children:
            that.metrics = metrics.Metrics(that)
        for that in self.children:
            that.metrics.reduce(self.children)

    def dotdotdot(self, *args, **kwargs):
        yield from self.decorator.dotdotdot(*args, **kwargs)

    def get_cache_subdir(self, subdir):
        ''' Get a cache_dir subdirectory (for collections) '''
        path = os.path.join(self.cache_dir, subdir)
        os.makedirs(path, exist_ok=True)
        return path
