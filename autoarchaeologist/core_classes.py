#!/usr/bin/env python3

'''
    AutoArchaeologist Core Classes
    ------------------------------

    The two core classes are `Context` which is the global state
    for the excavation and `ArtifactClass` which is a unique sequence
    of bytes found or derived in the excavation.

    `Excavation` holds the global state so that a program can compare
    and characterize overlap between multiple excavation.

    `ArtifactClass` is hidden by the function `Artifact` which
    ensures their uniqueness.

    Many artifacts are concatenations of multiple independent
    sub-artifacts, for instance a punched-hole paper-tape which
    might contain a leader (all zeros), a boot-strap loader, a
    spacer (all zeros), the actual program, another spacer, the
    programs data and a trailer (all zeros).

    Such artifacts may not have a unique partitioning and the
    derivation of the possible partitioning often proceeds in a
    stepwise fashion. A bit of complexity has been expended on
    flattening the resulting chains of partitions.

'''

import os
import hashlib

import autoarchaeologist.generic.hexdump as hexdump

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

    def __init__(self):
        self.hashes = {}
        self.busy = True
        self.queue = []
        self.examiners = []
        self.names = set()

        # Helper field for the HTML production
        self.html_dir = None
        self.digest_prefix = 8
        self.link_prefix = ""

        # Duck-type as ArtifactClass
        self.top = self
        self.children = []

    def __lt__(self, other):
        # Duck-type as ArtifactClass
        return -1

    def add_artifact(self, this):
        ''' Add an artifact, and start examining it '''
        assert isinstance(this, ArtifactClass)
        assert this.digest not in self.hashes
        self.hashes[this.digest] = this
        self.queue.append(this)
        if not self.busy:
            self.examine()

    def add_examiner(self, ex):
        ''' Add an examiner function '''
        self.examiners.append(ex)

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
        self.digest_prefix = 4
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

    def filename_for(self, this, suf=".html"):
        ''' Come up with a suitable filename related to an artifact '''
        if this == self:
            return "index" + suf
        return this.digest[:self.digest_prefix] + suf

    def produce_html(
        self,
        html_dir,               # Where to dump the files
        hexdump_limit=8192,     # How much of unrecognized artifacts should be  hexdumped
        link_prefix=None,       # HTML link prefix to reach the files
    ):
        ''' Produce default HTML pages '''

        if link_prefix is None:
            # use "file://{abs path to html_dir}/"
            dir_fd = os.open(".", os.O_RDONLY)
            os.chdir(html_dir)
            abspath = os.getcwd()
            os.chdir(dir_fd)
            os.close(dir_fd)
            link_prefix = "file://" + abspath + "/"

        self.link_prefix = link_prefix
        self.html_dir = html_dir

        self.polish()

        self.produce_front_page()

        for this in self.hashes.values():

            fn = self.html_dir + "/" + self.filename_for(this)
            fo = open(fn, "w")
            self.html_prefix(fo)
            this.html_page(fo, hexdump_limit)
            self.html_suffix(fo)

    def produce_front_page(self):
        ''' Top level html page '''
        fn = self.html_dir + "/" + self.filename_for(self)
        fo = open(fn, "w")
        self.html_prefix(fo)

        index = {}
        index_keys = set()
        for x, y in self.iter_notes():
            index_keys.add(y[:1])
            t = index.get(y)
            if not t:
                index[y] = set([x])
            else:
                t.add(x)

        index_keys = sorted(list(index_keys))

        fo.write("<H2>Links to index</H2>")
        fo.write("<table>\n")
        cols = 8
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
            fo.write("<td><pre>")
            fo.write(", ".join(sorted({y for x, y in this.iter_notes(True)})))
            fo.write("</pre></td>\n")
            fo.write("</tr>\n")
        fo.write("</table>\n")

        fo.write("<H2>Index</H2>")
        for idxkey in index_keys:
            fo.write('<H3><A name="IDX_%s">%s</A></H3>\n' % (idxkey, idxkey))
            notes = {x for x in index if x[:1] == idxkey}
            for n in sorted(notes):
                fo.write('<H4><A name="IDX_%s">%s</A></H4>\n' % (n, n))
                fo.write('<pre>\n')
                for x in sorted(index[n]):
                    fo.write("   " + x.summary(notes=True) + "\n")
                fo.write('</pre>\n')

        self.html_suffix(fo)

    def html_link_to(self, this, link_text=None, anchor=None):
        ''' Return a HTML link to an artifact '''
        t = '<A href="'
        t += self.link_prefix + '/' + self.filename_for(this)
        if anchor:
            t += "#" + anchor
        t += '">'
        if link_text:
            t += link_text
        else:
            t += this.name()
        t += '</a>'
        return t

    def html_prefix(self, fo):
        ''' Top of the HTML pages '''
        fo.write("<!DOCTYPE html>\n")
        fo.write("<html>\n")
        fo.write("<head>\n")
        fo.write('<meta charset="utf-8">\n')
        fo.write("</head>\n")
        fo.write("<pre>" + self.html_link_to(self, "top") + "</pre>\n")

    def html_suffix(self, fo):
        ''' Tail of all the HTML pages '''
        fo.write("</html>\n")

    def html_derivation(self, _fo):
        ''' Duck-type as ArtifactClass '''
        return ""

class DuplicateName(Exception):
    ''' Set names must be unique '''

class ArtifactClass(bytearray):

    '''
        Artifact[Class]
        ---------------

        Artifacts are just bytearrays with a high-school diploma.

        Artifacts are always created relative to another artifact,
        or in the case of the top-level artifacts, relative to the
        excavation, which duck-types as an Artifact to make this work.

        Artifacts are somehow derived from their parent, typical
        examples being sections, like the first half of a paper-tape,
        subsets, like the concatenation of a file's blocks in from
        a filesystem or transformations like uncompression.

        XXX

    '''

    def __init__(self, up, digest, bits):
        assert len(bits) > 0
        super().__init__(bits)

        self.digest = digest
        self.records = []		# For TAP files etc.

        self.parents = []
        self.children = []

        self.named = None
        self.interpretations = []
        self.notes = set()
        self.types = set()
        self.descriptions = []
        self.comments = []
        self.slices = []
        self.taken = False
        self.sliced_from = None
        self.sliced_at = None

        self.add_parent(up)
        self.top = up.top
        self.top.add_artifact(self)

        self.index_representation = None
        self.link_to = ""

    def __str__(self):
        return "{A %d %s}" % (len(self), self.name())

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return int(self.digest[:8], 16)

    def __lt__(self, other):
        if isinstance(other, Excavation):
            return 1
        return self.digest < other.digest

    def name(self):
        ''' Get the canonical name of the artifact '''
        if self.named:
            return "\u27e6" + self.named + "\u27e7"
        return "\u27e6" + self.digest[:self.top.digest_prefix] + "\u27e7"

    def add_parent(self, parent):
        ''' Attach to parent, and vice-versa '''
        self.parents.append(parent)
        parent.children.append(self)

    def set_name(self, name):
        ''' Set a unique name '''
        if self.named == name:
            return
        if self.named is not None:
            raise DuplicateName("Name clash '%s' vs '%s'" % (self.named, name))
        if name in self.top.names:
            raise DuplicateName("Name already used '%s'" % name)
        self.top.names.add(name)
        self.named = name

    def add_type(self, typ):
        ''' Add type designation (also as note) '''
        self.notes.add(typ)
        self.types.add(typ)

    def add_interpretation(self, owner, func):
        ''' Add an interpretation '''
        self.interpretations.append((owner, func))

    def add_description(self, desc):
        ''' Add a description '''
        self.descriptions.append(desc)

    def add_comment(self, desc):
        ''' Add a comment '''
        self.comments.append(desc)
        self.notes.add("Has Comment")

    def add_note(self, note):
        ''' Add a note '''
        self.notes.add(note)

    def has_note(self, note):
        ''' Check if not already exists '''
        return note in self.notes

    def iter_notes(self, recursive=False):
        ''' Return all notes that apply to this artifact '''
        yield from [(self, i) for i in self.notes]
        if recursive:
            for child in self.children:
                yield from child.iter_notes(recursive)

    def slice(self, offset, size):
        ''' Return a new artifact which is a subset of this one '''

        this = Artifact(self, self[offset:offset + size])

        if this.sliced_from:
            # Matched an existing slice of some artifact
            return this

        # Record where new slice was taken from
        this.sliced_from = self
        this.sliced_at = offset
        self.slices.append((offset, this))

        return this

    def examined(self):
        ''' Examination of this artifact is complete '''

        if self.slices:
            # If slices were taken out of this artifact create
            # new slices to cover all of this artifact.
            next_offset = 0
            leftovers = []
            for offset, this in sorted(self.slices):
                if offset > next_offset:
                    a = Artifact(self, self[next_offset:offset])
                    a.sliced_from = self
                    a.sliced_at = next_offset
                    leftovers.append((next_offset, a))
                    next_offset += len(a)
                assert offset == next_offset
                next_offset += len(this)
            if next_offset < len(self):
                a = Artifact(self, self[next_offset:])
                a.sliced_from = self
                a.sliced_at = next_offset
                leftovers.append((next_offset, a))
            self.slices += leftovers
            assert len(self) == sum([len(j) for i, j in self.slices])

        if self.slices and self.sliced_from:
            # If this artifact was itself a slice, adopt the slices away
            self.sliced_from.adopt(self)

        elif self.slices:
            # First sliced artifact in a new "slice-tree", render properly.
            self.add_interpretation(self, self.html_interpretation_sliced)

    def adopt(self, orphan):
        ''' Hoist slices of one of our own slices up '''
        newoff = orphan.sliced_at
        for offset, subslice in sorted(orphan.slices):
            offset += orphan.sliced_at
            assert newoff == offset
            subslice.parents.remove(orphan)
            subslice.parents.append(self)
            orphan.children.remove(subslice)
            self.children.append(subslice)
            subslice.sliced_from = self
            subslice.sliced_at = newoff
            self.slices.append((newoff, subslice))
            newoff += len(subslice)
        assert newoff == orphan.sliced_at + len(orphan)

        if not orphan.interpretations:
            # If there is nothing left, kill the subslice
            for i in self.slices:
                if i[0] == orphan.sliced_at and i[1] == orphan:
                    self.slices.remove(i)
                    break
            self.children.remove(orphan)
            orphan.parents.remove(self)
            del self.top.hashes[orphan.digest]

    def summary(self, link=True, ident=True, notes=False):
        ''' Produce a one-line summary '''
        if not link or not ident or not self.index_representation:
            txt = []
            nam = ""
            if ident:
                if link:
                    nam = self.top.html_link_to(self) + " "
                else:
                    nam = self.name() + " "
            if self.types:
                txt += sorted(self.types)
            if self.descriptions:
                txt += sorted(self.descriptions)
            if notes:
                txt += {y for x, y in self.iter_notes(True) if y not in self.types}
            if not link or not ident:
                return nam + ", ".join(txt)
            self.index_representation = nam + ", ".join(txt)
        return self.index_representation

    def html_page(self, fo, hexdump_limit):
        ''' Produce HTML page '''
        fo.write("<H2>" + self.summary(link=False) + "</H2>\n")

        fo.write("<H4>Derivation</H4>\n")
        fo.write("<pre>\n")
        self.html_derivation(fo)
        fo.write("</pre>\n")

        if self.children and not self.slices:
            fo.write("<H4>Children</H4>\n")
            fo.write("<pre>\n")
            for p in sorted(self.children):
                fo.write("  " + self.top.html_link_to(p) + "\n")
            fo.write("</pre>\n")

        if self.comments:
            fo.write("<H4>Comments</H4>\n")
            fo.write("<pre>\n")
            for i in self.comments:
                fo.write(i + "\n")
            fo.write("</pre>\n")

        if not self.interpretations:
            fo.write("<H4>HexDump</H4>\n")
            fo.write("<pre>\n")
            if len(self) > hexdump_limit:
                hexdump.hexdump_to_file(self[:hexdump_limit], fo)
                fo.write("[…]\n")
            else:
                hexdump.hexdump_to_file(self, fo)
            fo.write("</pre>\n")
        else:
            for _owner, func in self.interpretations:
                func(fo, self)

    def html_derivation(self, fo):
        ''' Recursively document how this artifact came to be '''
        prefix = ""
        for p in sorted(self.parents):
            t = p.html_derivation(fo)
            if len(t) > len(prefix):
                prefix = t
            fo.write(t + "└─" + self.summary() + '\n')
        return prefix + "    "

    def html_interpretation_sliced(self, fo, this):
        ''' Produce table of slices '''
        # XXX: slices may overlap
        assert this == self
        fo.write("<H3>Sliced</H3>\n")
        fo.write("<pre>\n")
        for offset, subslice in sorted(self.slices):
            fo.write("0x%05x-0x%05x " % (offset, offset + len(subslice)))
            fo.write(subslice.summary(notes=True) + "\n")
        fo.write("</pre>\n")

def Artifact(parent, bits):
    ''' Return a new or old artifact for some bits '''
    digest = hashlib.sha256(bits).hexdigest()
    this = parent.top.hashes.get(digest)
    if not this:
        this = ArtifactClass(parent, digest, bits)
    else:
        this.add_parent(parent)
    return this

class DuplicateArtifact(Exception):
    ''' Top level artifacts should not be identical '''

def Top_Artifact(ctx, bits, description=None):
    ''' Add a top-level artifact '''

    if not description:
        description = "Top-level Artifact"

    digest = hashlib.sha256(bits).hexdigest()

    this = ctx.hashes.get(digest)
    if this:
        t = "Artifact " + description
        t += "\n\tis identical to\n"
        t += this.summary(False)
        raise DuplicateArtifact("\n" + t + "\n")

    this = ArtifactClass(ctx, digest, bits)
    this.add_description(description)
    return this

def File_Artifact(ctx, filename, description=None):
    ''' Add a file as top-level artifact '''

    if not description:
        description = filename

    return Top_Artifact(ctx, open(filename, "rb").read(), description)
