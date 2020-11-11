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
import mmap
import hashlib

import autoarchaeologist.generic.hexdump as hexdump

class DuplicateArtifact(Exception):
    ''' Top level artifacts should not be identical '''

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

        self.index = {}

        # Helper field for the HTML production
        self.html_dir = None
        self.digest_prefix = 8
        self.link_prefix = ""
        self.download_links = False
        self.hexdump_limit = 8192

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

        this = ArtifactClass(self, digest, bits)
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
        self.digest_prefix = 8
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
        hexdump_limit=None,     # How much of unrecognized artifacts should be  hexdumped
        link_prefix=None,       # HTML link prefix to reach the files
        downloads=False,   	# Create downloadable .bin files
        download_links=False,   # Include links to .bin files
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

        if download_links:
            downloads = True
            self.download_links = True

        self.link_prefix = link_prefix
        self.html_dir = html_dir
        if hexdump_limit:
            self.hexdump_limit = hexdump_limit

        self.polish()

        self.produce_front_page()

        for this in self.hashes.values():

            if downloads:
                binfile = self.html_dir + "/" + self.filename_for(this, suf=".bin")
                open(binfile, 'wb').write(this.body)
            fn = self.html_dir + "/" + self.filename_for(this)
            fo = open(fn, "w")
            self.html_prefix(fo, this)
            this.html_page(fo)
            self.html_suffix(fo)

    def produce_front_page(self):
        ''' Top level html page '''
        fn = self.html_dir + "/" + self.filename_for(self)
        fo = open(fn, "w")
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
            fo.write(", ".join(sorted({y for x, y in this.iter_notes(True)})))
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
        t += self.link_prefix + '/' + self.filename_for(this, **kwargs)
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
        self.html_prefix_banner(fo, this)
        fo.write("<pre>")
        fo.write(self.html_link_to(self, "top"))
        if not isinstance(this, Excavation) and self.download_links:
            fo.write(" - " + self.html_link_to(this, "download", suf=".bin"))
        fo.write("</pre>\n")

    def html_suffix(self, fo):
        ''' Tail of all the HTML pages '''
        fo.write("</html>\n")

    def html_derivation(self, _fo):
        ''' Duck-type as ArtifactClass '''
        return ""

class Slab():
    ''' A slice of an artifact '''
    def __init__(self, parent, offset, this):
        self.parent = parent
        self.offset = offset
        self.this = this

    def __lt__(self, other):
        return self.offset < other.offset

    def __str__(self):
        return "<SL 0x%x %s>" % (self.offset, str(self.this))

    def __repr__(self):
        return "<SL 0x%x %s>" % (self.offset, str(self.this))

    def overlaps(self, other):
        ''' Check overlap against another slab '''
        if self.offset >= other.offset + len(other.this):
            return False
        if other.offset >= self.offset + len(self.this):
            return False
        return True

    def overlaps_any(self, others):
        ''' Check overlap against multiple slab '''
        for i in others:
            if self.overlaps(i):
                return True
        return False

class DuplicateName(Exception):
    ''' Set names must be unique '''

class ArtifactClass():

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
        self.body = bytes(bits)

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
        self.slabs = []
        self.slicings = []
        self.taken = False
        self.myslab = None

        self.add_parent(up)
        self.top = up.top
        self.top.add_artifact(self)

        self.index_representation = None
        self.link_to = ""

    def __str__(self):
        return "{A %d %s}" % (len(self), self.name())

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.body)

    def __hash__(self):
        return int(self.digest[:8], 16)

    def __getitem__(self, idx):
        return self.body[idx]

    def __lt__(self, other):
        if isinstance(other, Excavation):
            return 1
        return self.name() < other.name()

    def find(self, *args, **kwargs):
        return self.body.find(*args, **kwargs)

    def rfind(self, *args, **kwargs):
        return self.body.rfind(*args, **kwargs)

    def rstrip(self, *args, **kwargs):
        return self.body.rstrip(*args, **kwargs)

    def split(self, *args, **kwargs):
        return self.body.split(*args, **kwargs)

    def decode(self, *args, **kwargs):
        return self.body.decode(*args, **kwargs)

    def name(self):
        ''' Get the canonical name of the artifact '''
        if self.named:
            return "\u27e6" + self.named + "\u27e7"
        return "\u27e6" + self.digest[:self.top.digest_prefix] + "\u27e7"

    def add_parent(self, parent):
        ''' Attach to parent, and vice-versa '''
        assert self != parent
        self.parents.append(parent)
        parent.children.append(self)

    def set_name(self, name, fallback=True):
        ''' Set a unique name '''
        if self.named == name:
            return
        if self.named is not None:
            if fallback:
                self.add_note(name)
                self.top.add_to_index(name, self)
                return
            raise DuplicateName("Name clash '%s' vs '%s'" % (self.named, name))
        if name in self.top.names:
            if fallback:
                self.add_note(name)
                self.top.add_to_index(name, self)
                return
            raise DuplicateName("Name already used '%s'" % name)
        self.top.names.add(name)
        self.named = name
        self.top.add_to_index(name, self)

    def add_type(self, typ):
        ''' Add type designation (also as note) '''
        self.types.add(typ)
        self.top.add_to_index(typ, self)

    def has_type(self, note):
        ''' Check if not already exists '''
        return note in self.types

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
        self.top.add_to_index(note, self)

    def has_note(self, note):
        ''' Check if not already exists '''
        return note in self.notes

    def iter_types(self, recursive=False):
        ''' Return all notes that apply to this artifact '''
        yield from self.types
        if recursive:
            for child in self.children:
                assert child != self, (child, self)
                yield from child.iter_types(recursive)

    def iter_notes(self, recursive=False):
        ''' Return all notes that apply to this artifact '''
        yield from [(self, i) for i in self.notes]
        if recursive:
            for child in self.children:
                assert child != self, (child, self)
                yield from child.iter_notes(recursive)

    def slice(self, offset, size):
        ''' Return a new artifact which is a subset of this one '''

        if not offset and size == len(self):
            return self

        assert offset + size <= len(self), ("OSZ", offset, size)
        this = Artifact(self, self[offset:offset + size])

        # Record where new slice was taken from
        this.myslab = Slab(self, offset, this)
        self.slabs.append(this.myslab)

        return this

    def puzzle(self):
        ''' Resolve overlapping slabs. '''

        # Find the set of slabs which overlap any another slab
        overlaps = set()
        for i in range(len(self.slabs)):
            sln = self.slabs[i]
            for j in range(i+1, len(self.slabs)):
                if sln.overlaps(self.slabs[j]):
                    print("OVERLAP", self, sln, self.slabs[j])
                    overlaps.add(i)
                    overlaps.add(j)

        # We need at least one slicing.
        if not overlaps:
            overlaps.add(0)

        # Creat a slicing for each of the overlapping slabs, add
        # all slabs not overlapping another.
        for i in sorted(overlaps):
            sl0 = self.slabs[i]
            slicing = [sl0]
            self.slicings.append(slicing)
            for n, slab in enumerate(self.slabs):
                if n not in overlaps:
                    slicing.append(slab)

        # Add any other slice which can fit in the slicing:
        for slab in self.slabs:
            for slicing in self.slicings:
                if not slab.overlaps_any(slicing):
                    slicing.append(slab)

        # Flesh out the slicings with new slabs
        for slicing in self.slicings:
            offset = 0
            for slab in sorted(slicing):
                if offset < slab.offset:
                    new_slab = self.slice(offset, slab.offset - offset)
                    slicing.append(Slab(self, offset, new_slab))
                    offset += len(new_slab)
                offset += len(slab.this)
            if offset < len(self):
                new_slab = self.slice(offset, len(self) - offset)
                slicing.append(Slab(self, offset, new_slab))
            assert sum([len(x.this) for x in slicing]) == len(self)

    def examined(self):
        ''' Examination of this artifact is complete '''

        if self.slabs:
            self.puzzle()

        if self.slabs and self.myslab and len(self.parents) == 1:
            # If this artifact was itself a slice, adopt the slabs away
            self.myslab.parent.adopt(self)

        elif self.slabs:
            # First sliced artifact in a new "slice-tree", render properly.
            self.add_interpretation(self, self.html_interpretation_sliced)

    def adopt(self, orphan):
        ''' Hoist slabs of one of our own slabs up '''
        assert len(self.slicings) > 0
        assert len(orphan.parents) == 1, orphan.parents
        assert len(orphan.slicings) == 1, orphan.slicings
        newoff = orphan.myslab.offset

        # Hoist the orphan's slabs up
        # .puzzle will have fleshed out orphan.slabs
        for slab in sorted(orphan.slicings[0]):
            offset = slab.offset + orphan.myslab.offset
            assert newoff == offset, (self, orphan, newoff, offset, orphan.slabs)
            slab.this.parents.remove(orphan)
            slab.this.parents.append(self)
            orphan.children.remove(slab.this)
            self.children.append(slab.this)
            slab.this.myslab = Slab(self, newoff, slab.this)
            self.slabs.append(slab.this.myslab)
            newoff += len(slab.this)
            # Add to all slicings orphan is in
            for sln in self.slicings:
                for slac in sln:
                    if slac.this == orphan:
                        sln.append(slab.this.myslab)
        assert newoff == orphan.myslab.offset + len(orphan)

        # If there is nothing left, kill the orphan
        # XXX: Should also check notes, comments etc.
        if not orphan.interpretations:
            self.slabs.remove(orphan.myslab)
            self.children.remove(orphan)
            orphan.parents.remove(self)
            del self.top.hashes[orphan.digest]
            # Remove from all slicings
            for sln in self.slicings:
                for slab in sln:
                    if slab.this == orphan:
                        sln.remove(slab)
                        break

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
            j = set()
            for i in self.iter_types(True):
                if i not in j:
                    txt.append(i)
                    j.add(i)
            if self.descriptions:
                txt += sorted(self.descriptions)
            if notes:
                nn = sorted({y for _x, y in self.iter_notes(True)})
                txt += nn[:35]
                if len(nn) > 35:
                    txt.append("…")
            if not link or not ident:
                return nam + ", ".join(txt)
            self.index_representation = nam + ", ".join(txt)
        return self.index_representation

    def html_page(self, fo):
        ''' Produce HTML page '''
        fo.write("<H2>" + self.summary(link=False) + "</H2>\n")
        fo.write("<pre>\n")
        fo.write("    Length: %d (0x%x)\n" % (len(self), len(self)))
        for i in self.descriptions:
            fo.write("    Description: " + i + "\n")
        if self.types:
            fo.write("    Types: " + ", ".join(sorted(self.types)) + "\n")
        if self.notes:
            fo.write("    Notes: " + ", ".join(sorted({y for x, y in self.iter_notes(True)}))+ "\n")
        fo.write("</pre>\n")

        fo.write("<H4>Derivation</H4>\n")
        fo.write("<pre>\n")
        self.html_derivation(fo)
        fo.write("</pre>\n")

        if self.children and not self.slabs and not self.interpretations:
            self.html_interpretation_children(fo, self)

        if self.comments:
            fo.write("<H4>NB: Comments at End</H4>\n")

        if self.interpretations:
            for _owner, func in self.interpretations:
                func(fo, self)
        else:
            self.html_interpretation_hexdump(fo, self)

        if self.comments:
            fo.write("<H4>Comments</H4>\n")
            fo.write("<pre>\n")
            for i in self.comments:
                fo.write(i + "\n")
            fo.write("</pre>\n")

    def html_interpretation_children(self, fo, _this):
        ''' Default interpretation list of children'''

        fo.write("<H4>Children</H4>\n")
        fo.write("<pre>\n")
        for p in sorted(self.children):
            fo.write("  " + p.summary() + "\n")
        fo.write("</pre>\n")

    def html_interpretation_hexdump(self, fo, _this):
        ''' Default interpretation as hexdump '''
        fo.write("<H4>HexDump</H4>\n")
        fo.write("<pre>\n")

        if not self.records:
            if len(self) > self.top.hexdump_limit:
                hexdump.hexdump_to_file(self[:self.top.hexdump_limit], fo)
                fo.write("[…]\n")
            else:
                hexdump.hexdump_to_file(self, fo)
        else:
            done = 0
            idx = 0
            for n, r in enumerate(self.records):
                fo.write("Record #0x%x\n" % n)
                hexdump.hexdump_to_file(self[idx:idx+r], fo)
                fo.write("\n")
                idx += r
                done += r
                if done > self.top.hexdump_limit:
                    break

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
        ''' Produce table of slicings '''
        # XXX: slices may overlap
        assert this == self
        fo.write("<H3>Sliced</H3>\n")
        fo.write("<pre>\n")
        for sln in self.slicings:
            for slab in sorted(sln):
                fo.write("0x%05x-0x%05x " % (slab.offset, slab.offset + len(slab.this)))
                fo.write(slab.this.summary(notes=True) + "\n")
            fo.write("\n")
        fo.write("</pre>\n")

def Artifact(parent, bits):
    ''' Return a new or old artifact for some bits '''
    assert isinstance(parent, (Excavation, ArtifactClass)), (type(parent), parent)
    digest = hashlib.sha256(bits).hexdigest()
    this = parent.top.hashes.get(digest)
    if not this:
        this = ArtifactClass(parent, digest, bits)
    else:
        this.add_parent(parent)
    return this
