#!/usr/bin/env python3

'''
    AutoArchaeologist Artifact
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

import hashlib
import html

from itertools import zip_longest

from . import bintree
from . import octetview as ov
from . import result_page

class Record(bintree.BinTreeLeaf):
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
        super().__init__(low, high)
        self.frag = frag
        self.key = key
        self.artifact = None
        self.undefined = False

    def __str__(self):
        return "<R 0x%x…0x%x=0x%x %s>" % (self.lo, self.hi, self.hi - self.lo, str(self.key))

    def __len__(self):
        return self.hi - self.lo

    def __getitem__(self, idx):
        return self.frag[idx]

class ArtifactBase(result_page.ResultPage):

    '''
        ArtifactBase
        ------------

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

        self.parents = set()
        self.children = []

        self.notes = set()
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
        self._reclen = 0

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
        assert lo is None
        assert hi is None
        assert width is None
        lo = 0
        hi = len(self) << 3
        retval = []
        for chunk in self.iter_chunks():
            for i in chunk:
                retval.append(bin(256 | i)[-8:])
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
        assert rec.key not in self._keys
        self._keys[rec.key] = rec
        self._reclen += len(rec)
        rec.artifact = self
        return rec

    def num_rec(self):
        ''' Get number of records '''
        return len(self._keys)

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
        self.namespaces.setdefault(namespace.ns_root, []).append(namespace)
        if namespace.ns_name not in self.names:
            self.names.add(namespace.ns_name)

    def add_name(self, name):
        ''' Add a name '''
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
        self.types.add(typ)

    def has_type(self, note):
        ''' Check if not already exists '''
        return note in self.types

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
        yield from [(self, i) for i in self.notes]
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
        that = None
        if records:
            assert bits is None
            that = ArtifactFragmented(records)
            digest = that.digest
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
            digest = hashlib.sha256(bits).hexdigest()
        assert digest[:9] != "1db831043"
        this = self.top.hashes.get(digest)
        if not this:
            if that:
                this = that
            else:
                this = Artifact(digest, bits)
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
        link=True,
        ident=True,
        notes=False,
        types=True,
        descriptions=True,
        names=False,
    ):
        ''' Produce a one-line summary '''
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
        if names:
            txt += ["»" + html.escape(x) + "«" for x in sorted(self.names)]
        if types:
            for i in sorted(self.iter_types(False)):
                if i not in j:
                    txt.append(i)
                    j.add(i)
        if notes:
            txt += self.top.dotdotdot(sorted({y for _x, y in self.iter_notes(True)}))
        if not link or not ident or not types or not descriptions:
            return nam + ", ".join(txt)
        return nam + ", ".join(txt)

    def html_page_head(self, file):
        ''' Produce HTML page header '''
        file.write("<H2>" + self.summary(link=False) + "</H2>\n")
        file.write("<pre>\n")
        file.write("    Length: %d (0x%x)\n" % (len(self), len(self)))
        for i in self.descriptions:
            file.write("    Description: " + i + "\n")
        if self.types:
            file.write("    Types: ")
            file.write(", ".join(sorted(self.types)) + "\n")
        if self.notes:
            file.write("    Notes: ")
            file.write(", ".join(sorted({y for x, y in self.iter_notes(True)}))+ "\n")
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

    def html_interpretation_children(self, file, _this):
        ''' Default interpretation list of children'''

        file.write("<H3>Children</H3>\n")
        file.write("<pre>\n")
        for start, stop, this in sorted(self.layout):
            file.write("  0x%08x" % start + "-0x%08x  " % stop)
            file.write(this.summary() + "\n")
        file.write("</pre>\n")

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
                    link = self.top.html_link_to(self)
                nsps = self.namespaces.get(parent)
                if nsps:
                    # Not quite: See CBM900 ⟦e681055fa⟧
                    for nsp in sorted(nsps):
                        file.write(txt + "└─ " + link)
                        file.write(" »" + html.escape(nsp.ns_path()) + "« " + desc + '\n')
                else:
                    file.write(txt + "└─" + link + " " + desc + '\n')
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
            width = 64
        file.write("<H3>Hex Dump</H3>\n")
        file.write("<pre>\n")
        tmp = ov.OctetView(this)
        if len(self._keys) > 0:
            file.write("Dumping the first 0x%x bytes of each record\n" % width)
            for rec in sorted(self._keys.values()):
                ov.Octets(tmp, lo = rec.lo, hi=rec.hi, width=width, maxlines=1).insert()
        for cnt, line in enumerate(tmp.render(**kwargs)):
            if max_lines and cnt > max_lines:
                file.write("[…truncated at %d lines…]\n" % max_lines)
                break
            file.write(html.escape(line) + '\n')
        file.write("</pre>\n")

class ArtifactStream(ArtifactBase):

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

    def deprecated_getblock(self, idx):
        ''' Deprecated '''

    def deprecated_iterrecords(self):
        ''' Deprecated '''

    def tobytes(self):
        ''' Return as bytes '''
        return self.bdx.tobytes()

    def writetofile(self, file):
        ''' Write to file as bytes '''
        file.write(self.bdx)

class ArtifactFragmented(ArtifactBase):
    '''
       Artifact consisting of fragments of other artifact(s)
    '''

    def __init__(self, fragments=None):
        super().__init__()
        self._frags = []
        self._keys = {}
        self._tree = None
        self._len = 0
        self._reclen = 0
        if fragments:
            for i in fragments:
                assert len(i) > 0
                self.add_fragment(i)
            assert len(self._frags) > 0
            self.completed()

    def __len__(self):
        return self._len

    def __getitem__(self, idx):
        if isinstance(idx, int):
            i = [*self._tree.find(lo = idx, hi = idx + 1)]
            assert len(i) == 1
            return i[0][idx - i[0].lo]
        if not isinstance(idx, slice):
            return self._keys[idx].frag
        start = idx.start
        if start is None:
            start = 0
        stop = idx.stop
        if stop is None:
            stop = self._len
        i = [*self._tree.find(lo = start, hi = stop)]
        #print("GI", self, idx.start, idx.stop, start, stop, i)
        if len(i) == 1:
            start = max(0, start - i[0].lo)
            stop = min(len(i[0]), stop - i[0].lo)
            return i[0][start:stop]
        retval = bytearray()
        for j in i:
            #print("  ", start, stop, j.lo, j.hi, type(j))
            if start < j.lo and stop >= j.hi:
                retval += j.frag
                continue
            tstart = max(0, start - j.lo)
            tstop = min(len(j), stop - j.lo)
            retval += j[tstart:tstop]
        return retval

    def __iter__(self):
        for rec in self._frags:
            yield from rec.frag

    def iter_chunks(self):
        for rec in self._frags:
            yield rec.frag

    def tobytes(self):
        ''' Return as bytes '''
        i = bytearray()
        for j in self:
            i.append(j)
        return i

    def add_fragment(self, frag):
        ''' Append a fragment '''
        if not isinstance(frag, Record):
            frag = Record(self._len, frag=frag, key=(len(self._frags),))
        else:
            frag = Record(self._len, frag=frag.frag, key=frag.key)
        assert frag.lo == self._len
        self._frags.append(frag)
        frag.artifact = self
        self._len += len(frag)
        if frag.key is not None:
            self.define_rec(frag)

    def completed(self):
        ''' Build the tree and digest '''
        self._tree = bintree.BinTree(0, self._len)
        i = hashlib.sha256()
        for leaf in self._frags:
            self._tree.insert(leaf)
            i.update(leaf.frag)
        self.set_digest(i.hexdigest())

    def writetofile(self, file):
        for rec in self._frags:
            file.write(rec.frag)

class Artifact(ArtifactStream):
    ''' ... '''

    def __init__(self, digest, payload):
        super().__init__(payload)
        self.set_digest(digest)
