#!/usr/bin/env python3

'''
    AutoArchaeologist Artifact Class
    --------------------------------

    `ArtifactClass` is hidden by the function `Artifact` which
    ensures their uniqueness.
'''

import hashlib

import autoarchaeologist.excavation as excavation
import autoarchaeologist.generic.hexdump as hexdump

class DuplicateName(Exception):
    ''' Set names must be unique '''

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
        if isinstance(other, excavation.Excavation):
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

    def writetofile(self, fd):
        fd.write(self.body)

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

    def filename_for(self, *args, **kwargs):
        ''' ask excavation '''
        return self.top.filename_for(self, *args, **kwargs)

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
    assert isinstance(parent, (excavation.Excavation, ArtifactClass)), (type(parent), parent)
    digest = hashlib.sha256(bits).hexdigest()
    this = parent.top.hashes.get(digest)
    if not this:
        this = ArtifactClass(parent, digest, bits)
    else:
        this.add_parent(parent)
    return this
