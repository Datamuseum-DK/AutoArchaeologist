#!/usr/bin/env python3

'''
    AutoArchaeologist Artifact Class
    --------------------------------

    `ArtifactClass` is hidden by the function `Artifact` which
    ensures their uniqueness.
'''

import os
import hashlib
import html

from itertools import zip_longest

from . import excavation
from . import record
from . import scattergather

class DuplicateName(Exception):
    ''' Set names must be unique '''

class Utf8Interpretation():
    '''
       Some examinations output a UTF8 representation, containing
       no references to other artifacts during the examination phase.
       That output can be stored in a temporary file until the html
       production phase, saving VM.
       Using Pythons tempfile is not a good idea, because the file
       hang around.
    '''

    def __init__(self, this, title):
        self.this = this
        self.title = title
        self.filename = this.tmpfile_for().filename
        this.add_interpretation(self, self.html_interpretation)

    def html_interpretation(self, fo, this):
        try:
            fi = open(self.filename)
        except FileNotFoundError as err:
            print(this, "Could not open output file:", err)
            return
        fo.write("<H3>" + self.title + "</H3>\n")
        fo.write("<pre>\n")
        for i in fi:
            fo.write(html.escape(i))
        os.remove(self.filename)


class HtmlInterpretation():
    '''
       Some examinations output a HTML representation to a file
       That output can be stored in a temporary file until the html
       production phase, saving VM.
       Using Pythons tempfile is not a good idea, because the file
       hang around.
    '''

    def __init__(self, this, title):
        self.this = this
        self.title = title
        self.filename = this.tmpfile_for().filename
        this.add_interpretation(self, self.html_interpretation)

    def html_interpretation(self, fo, this):
        try:
            fi = open(self.filename)
        except FileNotFoundError as err:
            print(this, "Could not open output file:", err)
            return
        fo.write("<H3>" + self.title + "</H3>\n")
        for i in fi:
            fo.write(i)
        os.remove(self.filename)

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
        if isinstance(bits, (memoryview, scattergather.ScatterGather)):
            self.bdx = bits
        else:
            self.bdx = memoryview(bits)

        self.digest = digest

        self.parents = set()
        self.children = []

        self.named = None
        self.interpretations = []
        self.unique = 0
        self.notes = set()
        self.types = set()
        self.descriptions = []
        self.comments = []
        self.taken = False
        self.layout = []

        self.type_case = None

        self.add_parent(up)
        self.top = up.top
        self.top.add_artifact(self)

        self.index_representation = None
        self.link_to = ""
        self.byte_order = None
        self.namespaces = {}
        self.names = set()

        self.by_class = {} # Experimental extension point

    def __str__(self):
        return "\u27e6" + self.digest[:self.top.digest_prefix] + "\u27e7"

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.bdx)

    def __hash__(self):
        return int(self.digest[:8], 16)

    def __getitem__(self, idx):
        return self.bdx[idx]

    def __lt__(self, other):
        if isinstance(other, excavation.Excavation):
            return 1
        return self.digest < other.digest

    def __iter__(self):
        yield from self.bdx

    def iter_bytes(self):
        if self.byte_order is None:
            yield from self.bdx
            return

        def group(input, chunk):
            i = [iter(input)] * chunk
            return zip_longest(*i, fillvalue=0)

        for i in group(self.bdx, len(self.byte_order)):
            for j in self.byte_order:
                yield i[j]

    def bits(self, lo, width=None, hi=None):
        ''' Get a slice as a bitstring '''
        if hi is None:
            assert width is not None
            hi = lo + width
        retval = []
        i = self.bdx[lo >> 3 : (hi + 7) >> 3]
        for j in i:
            retval.append(bin(256 | j)[-8:])
        return("".join(retval)[lo & 7:hi - (lo & ~7)])

    def bitint(self, lo, width=None, hi=None):
        ''' Get a slice as integer '''
        if hi is None:
            assert width is not None
            hi = lo + width
        a = (lo) >> 3
        b = (hi + 7) >> 3
        c = self.bdx[a:b]
        d = int.from_bytes(c, 'big')
        if hi & 7:
            e = d >> (8 - (hi & 7))
        else:
            e = d
        f = e & ((1 << (hi - lo)) - 1)
        return f

    def get_unique(self):
        ''' Return a unique (increasing) number '''
        rv = self.unique
        self.unique += 1
        return rv

    def getblock(self, idx):
        if isinstance(self.bdx, scattergather.ScatterGather):
            return self.bdx.block(idx)
        return None

    def iterrecords(self):
        if isinstance(self.bdx, scattergather.ScatterGather):
            yield from self.bdx.iterrecords()
        else:
            yield self.bdx

    def tobytes(self):
        return self.bdx.tobytes()

    def writetofile(self, fo):
        if isinstance(self.bdx, scattergather.ScatterGather):
            self.bdx.writetofile(fo)
        else:
            fo.write(self.bdx)

    def add_parent(self, parent):
        ''' Attach to parent, and vice-versa '''
        assert self != parent
        self.parents.add(parent)
        parent.children.append(self)

    def add_namespace(self, namespace):
        ''' Add a namespace reference '''
        self.namespaces.setdefault(namespace.ns_root, []).append(namespace)
        if namespace.ns_name not in self.names:
            self.names.add(namespace.ns_name)
            self.top.add_to_index(namespace.ns_name, self)

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

    def add_utf8_interpretation(self, title):
        return Utf8Interpretation(self, title)

    def add_html_interpretation(self, title):
        return HtmlInterpretation(self, title)

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

    def record(self, layout, **kwargs):
        ''' Extract a compound record '''
        return record.Extract_Record(self, layout, **kwargs)

    def filename_for(self, *args, **kwargs):
        ''' ask excavation '''
        return self.top.filename_for(self, *args, **kwargs)

    def tmpfile_for(self):
        ''' create a temporary file '''
        return self.top.filename_for(
            self,
            suf=".tmp.%d" % self.get_unique(),
            temp=True
        )

    def create(self, bits=None, start=None, stop=None, records=None):
        ''' Return a new or old artifact for some bits '''
        if records:
            assert bits is None
            assert len(records) > 0
            bits = scattergather.ScatterGather(records)
            digest = bits.sha256()
        elif isinstance(bits, memoryview):
            digest = hashlib.sha256(bits.tobytes()).hexdigest()
        elif bits:
            digest = hashlib.sha256(bits).hexdigest()
        else:
            assert stop > start
            assert stop <= len(self)
            if not start and stop == len(self):
                return self
            bits = self[start:stop]
            digest = hashlib.sha256(bits.tobytes()).hexdigest()
        this = self.top.hashes.get(digest)
        if not this:
            this = ArtifactClass(self, digest, bits)
            this.type_case = self.type_case
        elif this != self:
            this.add_parent(self)
        if start or stop:
            self.layout.append((start, stop, this))
        else:
            self.layout.append((0, len(self), this))
        this.byte_order = self.byte_order
        return this

    def examined(self):
        ''' Examination of this artifact is complete '''
        # XXX: create left over slices
        lst = []
        offset = 0
        for start, stop, _src in sorted(self.layout):
            if start is None or stop is None:
                continue
            if offset < start:
                lst.append((offset, start))
            offset = stop
        if not offset:
            return
        if offset != len(self):
            lst.append((offset, len(self)))
        for start, stop in lst:
            self.create(start=start, stop=stop)

    def summary(
        self,
        link=True,
        ident=True,
        notes=False,
        types=True,
        descriptions=True,
        names=False,
    ):
        ''' Produce a one-line summary '''
        if not link or not ident or not self.index_representation:
            txt = []
            nam = ""
            if ident:
                if link:
                    nam = self.top.html_link_to(self) + " "
                else:
                    nam = str(self) + " "
            j = set()
            if descriptions:
                if self.descriptions:
                    txt += sorted(self.descriptions)
            if types:
                for i in sorted(self.iter_types(False)):
                    if i not in j:
                        txt.append(i)
                        j.add(i)
            if names:
                txt += ["»" + x + "«" for x in sorted(self.names)]
            if notes:
                txt += excavation.dotdotdot(sorted({y for _x, y in self.iter_notes(True)}))
            if not link or not ident or not types or not descriptions:
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
        if self.names:
            fo.write("    Names: " + ", ".join('»' + x + '«' for x in sorted(self.names))+ "\n")
        fo.write("</pre>\n")

        if self.top not in self.parents or len(self.parents) > 1:
            fo.write("<H3>Derivation</H3>\n")
            fo.write("<pre>\n")
            self.html_derivation(fo)
            fo.write("</pre>\n")

        if self.children and not self.interpretations:
            self.html_interpretation_children(fo, self)

        if self.comments:
            fo.write("<H3>NB: Comments at End</H3>\n")

        if self.interpretations:
            for _owner, func in self.interpretations:
                fo.write('<div>\n')
                func(fo, self)
                fo.write('</div>\n')
        else:
            self.html_interpretation_hexdump(fo, self)

        if self.comments:
            fo.write("<H3>Comments</H3>\n")
            fo.write("<pre>\n")
            for i in self.comments:
                fo.write(i + "\n")
            fo.write("</pre>\n")

    def html_interpretation_children(self, fo, _this):
        ''' Default interpretation list of children'''

        fo.write("<H3>Children</H3>\n")
        fo.write("<pre>\n")
        for start, stop, this in sorted(self.layout):
            fo.write("  0x%08x" % start + "-0x%08x  " % stop)
            fo.write(this.summary() + "\n")
        fo.write("</pre>\n")

    def html_interpretation_hexdump(self, fo, _this):
        ''' Default interpretation as hexdump '''
        # XXX: should respect .byte_order
        fo.write("<H3>HexDump</H3>\n")
        fo.write("<pre>\n")

        if not isinstance(self.bdx, scattergather.ScatterGather):
            if len(self) > self.top.hexdump_limit:
                self.type_case.hexdump_html(
                    self.bdx[:self.top.hexdump_limit],
                    fo,
                )
                fo.write("[…]\n")
            else:
                self.type_case.hexdump_html(self.bdx, fo)
        else:
            done = 0
            for n, r in enumerate(self.iterrecords()):
                fo.write("Record #0x%x\n" % n)
                self.type_case.hexdump_html(r.tobytes(), fo)
                fo.write("\n")
                done += len(r)
                if done > self.top.hexdump_limit:
                    break

    def html_derivation(self, fo, target=True):
        ''' Recursively document how this artifact came to be '''
        prefix = ""
        for p in sorted(self.parents):
            descs = self.descriptions
            if not descs:
                descs = ("",)
            for desc in descs:
                t = p.html_derivation(fo, target=False)
                if len(t) > len(prefix):
                    prefix = t

                if target:
                    link = "\u27e6this\u27e7"
                else:
                    link = self.top.html_link_to(self)
                v = self.namespaces.get(p)
                if v:
                    # Not quite: See CBM900 ⟦e681055fa⟧
                    for ns in sorted(v):
                        fo.write(t + "└─ " + link + " »" + ns.ns_path() + "« " + desc + '\n')
                else:
                    fo.write(t + "└─" + link + " " + desc + '\n')
        return prefix + "    "

    def html_description(self):
        return "<br>\n".join(sorted(self.descriptions))
