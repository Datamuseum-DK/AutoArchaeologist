#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    AutoArchaeologist Artifact
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

import os
import hashlib
import html
import mmap

from itertools import zip_longest

from . import octetview as ov
from . import result_page

class Record():
    '''
       A piece of an artifact
       ----------------------

       Used for both fragments and records
    '''

    def __init__(self, low, high=None, frag=None, key=None):
        if high is None:
            assert frag is not None
            high = low + len(frag)
        elif frag is not None:
            assert high == low + len(frag)
        self.lo = low
        self.hi = high
        self.frag = frag
        self.key = key
        self.artifact = None
        self.undefined = False

    def __lt__(self, other):
        return self.lo < other.lo

    def __str__(self):
        return "<R 0x%x…0x%x=0x%x %s>" % (self.lo, self.hi, self.hi - self.lo, str(self.key))

    def __len__(self):
        return self.hi - self.lo

    def __getitem__(self, idx):
        return self.frag[idx]

class Artifact(result_page.ResultPage):

    '''
        Artifact
        --------

        Artifacts are just bytearrays with a high-school diploma,
        but they come in different flavours, for which this is
        the base class.

        Artifacts are always created relative to another artifact,
        or in the case of the top-level artifacts, relative to the
        excavation, which duck-types as an Artifact to make this work.

        Artifacts are somehow derived from their parent, typical
        examples being sections, like the first half of a paper-tape,
        subsets, like the concatenation of a file's blocks in from
        a filesystem or transformations like uncompression.

        The different subclasses implement different styles of
        artifacts, while trying to economize RAM.

    '''

    def __init__(self):

        super().__init__()

        self.digest = None
        self.relpath = None

        self.parents = set()
        self.children = []

        self.notes = {}
        self.types = set()
        self.descriptions = []
        self.comments = []
        self.taken = False
        self.layout = []

        self.type_case = None

        self.top = None

        self.link_to = ""
        self.byte_order = None
        self.namespaces = {}
        self.names = set()
        self.ns_roots = []

        self.by_class = {} # Experimental extension point
        self._keys = {}
        self._reclens = {}
        self._key_min = list()
        self._key_max = list()
        self._key_len = 0

        self.metrics = None # Used only for toplevel artifacts

    def __str__(self):
        if not self.digest:
            return "\u27e6…\u27e7"
        if not self.top:
            return "\u27e6" + self.digest[:7] + "\u27e7"
        return "\u27e6" + self.digest[:self.top.digest_prefix] + "\u27e7"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return int(self.digest[:8], 16)

    def __lt__(self, other):
        if other == self.top:
            return 1
        return self.digest < other.digest

    def iter_bytes(self):
        ''' iterate bytes in byte-order '''

        if self.byte_order is None:
            yield from self
            return

        def group(data, chunk):
            i = [iter(data)] * chunk
            return zip_longest(*i, fillvalue=0)

        for chunk in self.iter_chunks():
            for i in group(chunk, len(self.byte_order)):
                for j in self.byte_order:
                    yield i[j]

    def bits(self, lo=None, width=None, hi=None):
        ''' Get all bits as bitstring '''
        if lo is None:
            lo = 0
        if hi is None and width is not None:
            hi = lo + width
        if hi is None:
            hi = len(self) << 3
        assert lo & 7 == 0
        assert hi & 7 == 0
        retval = []
        yet = 0
        for chunk in self.iter_chunks():
            cbits = len(chunk) * 8
            if yet + cbits < lo:
                yet += cbits
                continue
            for i in chunk:
                if yet + 8 < lo:
                    yet += 8
                    continue
                retval.append(bin(256 | i)[-8:])
                yet += 8
                if yet >= hi:
                    break
            if yet >= hi:
                break
        return "".join(retval)[lo & 7:hi - (lo & ~7)]

    def writetofile(self, file):
        ''' write artifact to a file '''
        raise NotImplementedError

    def iter_chunks(self):
        ''' iterate artifact in whatever chunks are convenient '''
        raise NotImplementedError

    def define_rec(self, rec):
        ''' Define a record '''
        assert isinstance(rec, Record)
        if rec.key in self._keys:
            print("Duplicate key:", rec.key)
            assert rec.key not in self._keys
        if len(self._keys) == 0:
            self._key_len = len(rec.key)
            self._key_min = list(rec.key)
            self._key_max = list(rec.key)
        else:
            if self._key_len != len(rec.key):
                print(self, "Records have different key lengths:", self._key_len, len(rec.key), rec.key)
                assert self._key_len == len(rec.key)
            for i in range(self._key_len):
                self._key_min[i] = min(self._key_min[i], rec.key[i])
                self._key_max[i] = max(self._key_min[i], rec.key[i])
        self._keys[rec.key] = rec
        self._reclens[len(rec)] = self._reclens.get(len(rec), 0) + 1
        rec.artifact = self
        return rec

    def num_rec(self):
        ''' Get number of records '''
        return len(self._keys)

    def has_rec(self, key):
        ''' Get a Record (or None) '''
        if key not in self._keys:
            return None
        return self._keys[key]

    def get_rec(self, key):
        ''' Get a Record '''
        return self._keys[key]

    def iter_rec(self):
        ''' Iterate Records '''
        yield from self._keys.values()

    def set_digest(self, digest=None):
        ''' Calculate the SHA256 digest '''
        if digest is None:
            i = hashlib.sha256()
            for j in self.iter_chunks():
                i.update(j)
            self.digest = i.hexdigest()
        else:
            self.digest = digest

    def add_parent(self, parent):
        ''' Attach to parent, and vice-versa '''
        assert self != parent
        self.parents.add(parent)
        parent.children.append(self)

    def add_namespace(self, namespace):
        ''' Add a namespace reference '''
        self.namespaces.setdefault(namespace.ns_parent, []).append(namespace)
        if namespace.ns_name not in self.names:
            self.names.add(namespace.ns_name)

    def add_name(self, name):
        ''' Add a name '''
        assert len(name) > 0
        self.names.add(name)

    def has_name(self, name):
        ''' Return False, True or a NameSpace '''
        if name not in self.names:
            return False
        for nsl in self.namespaces.values():
            for ns in nsl:
                if ns.ns_name == name:
                    return ns
        return True

    def add_type(self, typ):
        ''' Add type designation (also as note) '''
        assert len(typ) > 0
        self.types.add(typ)

    def has_type(self, note):
        ''' Check if not already exists '''
        return note in self.types

    def add_description(self, desc):
        ''' Add a description '''
        assert len(desc) > 0
        self.descriptions.append(desc)

    def add_comment(self, comment):
        ''' Add a comment '''
        assert len(comment) > 0
        self.comments.append(comment)
        self.add_note("Has Comment")

    def add_note(self, note, info=True):
        ''' Add a note '''
        assert len(note) > 0
        self.notes[note] = info

    def has_note(self, note):
        ''' Check if not already exists '''
        return self.notes.get(note, None)

    def iter_all_children(self):
        ''' Recursively iterate all children once '''
        done = set()
        todo = [ self ]
        while todo:
            this = todo.pop(0)
            if this in done:
                continue
            done.add(this)
            yield this
            for child in this.children:
                if child not in done:
                    todo.append(child)

    def iter_types(self, recursive=False):
        ''' Return all notes that apply to this artifact '''
        yield from self.types
        if recursive:
            for child in self.children:
                assert child != self, (child, self)
                yield from child.iter_types(recursive)

    def iter_notes(self, recursive=False):
        ''' Return all notes that apply to this artifact '''
        yield from [(self, i, j) for i,j in self.notes.items()]
        if recursive:
            for child in self.children:
                assert child != self, (child, self)
                yield from child.iter_notes(recursive)

    def part(self):
        ''' Instantiate any interstitial child artifacts '''
        if self.rp_interpretations:
            return
        if not self.children:
            return
        a0 = 0
        for lo, hi, _this in sorted(self.layout):
            if a0 < lo:
                self.create(start=a0, stop=lo)
            a0 = hi
        if a0 < len(self):
            self.create(start=a0, stop=len(self))

    def basename_for(self, *args, **kwargs):
        ''' ask excavation '''
        return self.top.basename_for(self, *args, **kwargs)

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

    def create(self, octets=None, start=None, stop=None, records=None, **kwargs):
        ''' Return a new or old artifact for some octets '''
        that = None
        if records:
            assert octets is None
            that = ArtifactFragmented(self.top, records, **kwargs)
            digest = that.digest
        elif isinstance(octets, memoryview):
            digest = hashlib.sha256(octets.tobytes()).hexdigest()
        elif octets:
            digest = hashlib.sha256(octets).hexdigest()
        else:
            assert stop > start
            assert stop <= len(self)
            if not start and stop == len(self):
                return self
            octets = self[start:stop]
            digest = hashlib.sha256(octets).hexdigest()
        assert digest[:9] != "1db831043"
        this = self.top.hashes.get(digest)
        if not this:
            if that:
                this = that
            else:
                this = ArtifactStream(octets)
                this.set_digest(digest)
            this.type_case = self.type_case
            self.top.adopt(this)
            this.add_parent(self)
        elif this != self:
            this.add_parent(self)
        if start or stop:
            self.layout.append((start, stop, this))
        else:
            self.layout.append((0, len(self), this))
        this.byte_order = self.byte_order
        return this

    def summary(
        self,
        notes=False,
        types=True,
        descriptions=True,
        names=False,
    ):
        ''' Produce a one-line summary '''
        txt = []
        nam = ""
        j = set()
        if descriptions:
            if self.descriptions:
                txt += sorted(self.descriptions)
        if names:
            txt += ["»" + html.escape(x) + "«" for x in sorted(self.names)]
        if types:
            for i in sorted(self.iter_types(False)):
                if i not in j:
                    txt.append(i)
                    j.add(i)
        if notes:
            txt += self.top.dotdotdot(sorted({y for _x, y, _z in self.iter_notes(True)}))
        return nam + ", ".join(txt)

    def html_page_head(self, file):
        ''' Produce HTML page header '''
        file.write("<H2>" + str(self) + " " + self.summary() + "</H2>\n")
        file.write("<pre>\n")
        file.write("    Length: %d (0x%x)\n" % (len(self), len(self)))
        for i in self.descriptions:
            file.write("    Description: " + i + "\n")
        if self.types:
            file.write("    Types: ")
            file.write(", ".join(sorted(self.types)) + "\n")
        if self.notes:
            file.write("    Notes: ")
            file.write(", ".join(sorted({y for _x, y, _z in self.iter_notes(True)}))+ "\n")
        if self.names:
            file.write("    Names: ")
            file.write(", ".join('»' + x + '«' for x in sorted(self.names))+ "\n")
        file.write("</pre>\n")

    def html_page(self, file, domore=False):
        ''' Produce HTML page '''
        retval = False
        self.html_page_head(file)

        if self.top not in self.parents or len(self.parents) > 1:
            file.write("<H3>Derivation</H3>\n")
            file.write("<pre>\n")
            self.html_derivation(file)
            file.write("</pre>\n")

        if self.comments:
            file.write("<H3>NB: Comments at End</H3>\n")

        if not self.rp_interpretations:
            if self.children:
                self.add_interpretation(self, self.html_interpretation_children)
            else:
                self.add_interpretation(self, self.html_default_interpretation)

        if self.emit_interpretations(file, domore):
            retval = True

        if self.comments:
            file.write("<H3>Comments</H3>\n")
            file.write("<pre>\n")
            for i in self.comments:
                file.write(i + "\n")
            file.write("</pre>\n")

        return retval

    def html_interpretation_children(self, *args, **kwargs):
        ''' Interpretation: List of children'''
        self.top.decorator.html_interpretation_children(*args, **kwargs)

    def html_derivation(self, file, target=True):
        ''' Recursively document how this artifact came to be '''
        prefix = ""
        for parent in sorted(self.parents):
            descs = self.descriptions
            if not descs:
                descs = ("",)
            for desc in descs:
                txt = parent.html_derivation(file, target=False)
                if len(txt) > len(prefix):
                    prefix = txt

                if target:
                    link = "\u27e6this\u27e7"
                else:
                    link = file.str_link_to_that(self)

                paths = []
                for key, nsps in self.namespaces.items():
                    if key.ns_root != parent:
                        continue
                    # Not quite: See CBM900 ⟦e681055fa⟧
                    paths += list(nsp.ns_path() for nsp in nsps)
                if not paths:
                    file.write(txt + "└─" + link + " " + desc + '\n')
                else:
                    for path in sorted(paths):
                        file.write(txt + "└─" + link)
                        file.write(" »" + html.escape(path) + "« " + desc + '\n')
        return prefix + "    "

    def html_description(self):
        ''' Descriptions, one per line '''
        return "<br>\n".join(sorted(self.descriptions))

    def hexdump(self, lo, hi, width=32, fmt="%02x"):
        ''' General (hex)dump helper '''
        n = (hi - lo) // width
        for _i in range(n):
            octets = self.type_case.decode(self[lo:lo+width])
            dump = " ".join(fmt % x for x in self[lo:lo+width])
            yield dump + "   ┆" + octets + "┆"
            lo += width
        if lo == hi:
            return
        octets = self.type_case.decode(self[lo:hi])
        dump = " ".join(fmt % x for x in self[lo:hi])
        pad = " " * (len(fmt % 0xff) + 1) * (width - (hi - lo))
        yield dump + pad + "   ┆" + octets + "┆"

    def html_default_interpretation(self, file, this, max_lines=None, width=None, **kwargs):
        ''' Default interpretation is a hexdump '''

        if max_lines is None:
            max_lines = self.top.MAX_LINES
        if width is None:
            width = 32
        file.write("<H3>Hex Dump</H3>\n")
        file.write("<pre>\n")
        tmp = ov.OctetView(this)
        if len(self._keys) > max_lines:
            file.write("Dumping the first 0x%x bytes of each record\n" % width)
            for rec in sorted(self._keys.values()):
                ov.Octets(tmp, lo = rec.lo, hi=rec.hi, width=width, maxlines=1).insert()
        for cnt, line in enumerate(tmp.render(**kwargs)):
            if max_lines and cnt > max_lines:
                file.write("[…truncated at %d lines…]\n" % max_lines)
                break
            file.write(html.escape(line) + '\n')
        file.write("</pre>\n")

    def adopted(self):
        ''' ... '''

class ArtifactStream(Artifact):

    '''
       A simple artifact consisting of a sequence of octets
       ----------------------------------------------------
    '''

    def __init__(self, octets):
        super().__init__()
        assert len(octets) > 0
        self.bdx = memoryview(octets).toreadonly()

    def __len__(self):
        return len(self.bdx)

    def __getitem__(self, idx):
        return self.bdx[idx]

    def __iter__(self):
        yield from self.bdx

    def iter_chunks(self):
        yield self.bdx

    def bits(self, lo=None, width=None, hi=None):
        ''' Get a slice as a bitstring '''
        if lo is None:
            lo = 0
        if hi is None and width is None:
            hi = len(self) << 3
        if hi is None:
            assert width is not None
            hi = lo + width
        retval = []
        i = self.bdx[lo >> 3 : (hi + 7) >> 3]
        for j in i:
            retval.append(bin(256 | j)[-8:])
        return "".join(retval)[lo & 7:hi - (lo & ~7)]

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

    def tobytes(self):
        ''' Return as bytes '''
        return self.bdx.tobytes()

    def writetofile(self, file):
        ''' Write to file as bytes '''
        file.write(self.bdx)

class ArtifactFragmented(Artifact):
    '''
       Artifact consisting of fragments of other artifact(s)
    '''

    def __init__(self, top, fragments=None, define_records=True):
        super().__init__()
        self._frags = []
        self._keys = {}
        self._len = 0
        self._backing = top.filename_for(top, temp=True)
        self._file = open(self._backing.filename, "wb")
        self._map = None
        self._binfile = False
        if fragments:
            for i in fragments:
                assert len(i) > 0
                self.add_fragment(i, define_record=define_records)
            assert len(self._frags) > 0
            self.completed()

    def __len__(self):
        return self._len

    def __getitem__(self, idx):
        if isinstance(idx, (int, slice)):
            return self._map.__getitem__(idx)
        return self._keys[idx].frag

    def __iter__(self):
        yield from self._map

    def iter_chunks(self):
        for rec in self._frags:
            yield rec.frag

    def tobytes(self):
        ''' Return as bytes '''
        return bytes(self._map)

    def add_fragment(self, frag, define_record=True):
        ''' Append a fragment '''
        if not isinstance(frag, Record):
            frag = Record(self._len, frag=frag, key=(len(self._frags),))
        else:
            frag = Record(self._len, frag=frag.frag, key=frag.key)
        assert frag.lo == self._len
        self._frags.append(frag)
        frag.artifact = self
        self._len += len(frag)
        self._file.write(frag.frag)
        if define_record:
            self.define_rec(frag)

    def completed(self):
        ''' Build the tree and digest '''
        assert self._len > 0
        self._file.flush()
        self._file.close()
        del self._file
        with open(self._backing.filename, 'rb') as file:
             if self._len < (1<<16):
                 self._map = memoryview(file.read()).toreadonly()
             else:
                 self._map = memoryview(
                     mmap.mmap(
                         file.fileno(),
                         0,
                         access=mmap.ACCESS_READ,
                         #XXX: Python3.13 and forward use: trackfd=False,
                     )
                 ).toreadonly()
        i = hashlib.sha256()
        off = 0
        for frag in self._frags:
            l = len(frag)
            frag.frag = self._map[off:off+l]
            off += l
            i.update(frag.frag)
        self.set_digest(i.hexdigest())

    def adopted(self):
        bn = self.top.filename_for(self, suf=".back")
        os.rename(self._backing.filename, bn.filename)
        self._backing = bn

    def writetofile(self, file):
        file.write(self._map)
