#!/usr/bin/env python3

'''
This class implements a basic recursive split-in-the-middle-interval-tree

An interval-tree is a tree of intervals (duh!) which is useful here
for keeping track of the bits we have taken apart.

Leafs must have numerical .lo and .hi attributes.

Instantiating the tree you must provide the valid [lo...hi] interval.

There is also an optional parameter to limit how narrow ranges we
create subtrees for.  If it ever needs changing, we should probably
change the algorithm to split trees based on actual number of nodes,
rather than the interval they cover, but for now it seems to work
pretty ok.
'''

class BinTreeLeaf():
    '''
    Leaves of the tree
    ------------------
    '''
    def __init__(self, lo, hi, name=None):
        assert isinstance(lo, int)
        assert isinstance(hi, int)
        assert lo < hi
        self.lo = lo
        self.hi = hi
        if name is None:
           name = self.__class__.__name__
        self.bt_name = name

    def __repr__(self):
        return "<BinTreeLeaf 0x%x-0x%x>" % (self.lo, self.hi)

    def __lt__(self, other):
        if self.lo != other.lo:
            return self.lo < other.lo
        return self.hi < other.hi

    def __eq__(self, other):
        if other is None:
            return False
        return self.lo == other.lo and self.hi == other.hi

    def dot_node(self, _dot):
        ''' ... '''

    def dot_edges(self, _dot, _src=None):
        ''' ... '''

class BinTree():

    '''
    Root/branch class of the tree
    -----------------------------
    '''

    def __init__(self, lo, hi, leaf=None, limit=128):
        # limit is only a performance parameter, it does not change
        # funcationality in any way.
        self.lo = lo
        self.mid = (lo + hi) // 2
        self.hi = hi
        self.limit = limit
        self.less = None
        self.more = None
        self.cuts = []
        self.gauge = 0
        self.adrwidth = len("%x" % self.hi)
        self.adrfmt = "%%0%dx" % self.adrwidth
        self.separators = []
        self.separators_width = 0
        self.base_leaf = leaf
        self.todo = []

    def __repr__(self):
        return "<BinTree 0x%x-0x%x-0x%x>" % (self.lo, self.mid, self.hi)

    def insert(self, leaf):
        ''' You guessed it... '''
        assert isinstance(leaf, BinTreeLeaf)
        assert leaf.lo < leaf.hi
        self.gauge += 1
        if self.hi - self.lo <= self.limit:
            self.cuts.append(leaf)
        elif leaf.hi <= self.mid:
            if self.less is None:
                self.less = BinTree(self.lo, self.mid, self.limit)
            self.less.insert(leaf)
        elif leaf.lo >= self.mid:
            if self.more is None:
                self.more = BinTree(self.mid, self.hi, self.limit)
            self.more.insert(leaf)
        else:
            self.cuts.append(leaf)

    def find(self, lo=None, hi=None):
        ''' Find leaves between lo and hi '''
        assert lo is not None or hi is not None
        if hi is None:
            hi = lo + 1
        if lo is None:
            lo = hi - 1
        if lo <= self.mid and self.less:
            yield from self.less.find(lo, hi)
        for i in self.cuts:
            if i.lo < hi and lo < i.hi:
                yield i
        if hi >= self.mid and self.more:
            yield from self.more.find(lo, hi)

    def __iter__(self):
        ''' Iterate in order of .lo and narrow before wider. '''
        stk = [self]
        lst = []
        while stk:
            cur = stk.pop()
            while lst and lst[0].lo < cur.lo:
                yield lst.pop(0)
            lst.extend(cur.cuts)
            lst.sort()
            if cur.more:
                stk.append(cur.more)
            if cur.less:
                stk.append(cur.less)
            else:
                while lst and lst[0].lo < cur.mid:
                    yield lst.pop(0)
        yield from lst

    def gaps(self):
        ''' Yield all the gaps in the tree '''
        last = 0
        for i in self:
            if i.lo > last:
                yield (last, i.lo)
            last = i.hi
        if last < self.hi:
            yield (last, self.hi)

    def pad_from_to(self, lo, hi, pad_width=5):
        ''' yield padding lines '''
        while hi > lo:
            i = lo + pad_width
            i -= i % pad_width
            i = min(i, hi)
            if self.separators and self.separators[0][0] > lo:
                i = min(i, self.separators[0][0])
            pad = self.base_leaf(self, lo, hi=i)
            yield pad
            lo = pad.hi

    def iter_padded(self, pad_width=16):
        ''' Render the tree with optional padding'''
        ptr = 0
        for leaf in self:
            if pad_width:
                yield from self.pad_from_to(ptr, leaf.lo, pad_width)
            yield leaf
            ptr = leaf.hi
        if pad_width:
            yield from self.pad_from_to(ptr, self.hi, pad_width)

    def prefix(self, lo, hi):
        if self.separators_width == 0:
            return "0x" + self.adrfmt % lo + "…" + self.adrfmt % hi
        while self.separators and self.separators[0][0] < lo:
            self.separators.pop(0)
        if self.separators and self.separators[0][0] == lo:
            i = self.separators.pop(0)[1]
        else:
            i = ""
        return "0x" + self.adrfmt % lo + "…" + self.adrfmt % hi + i.ljust(self.separators_width)

    def render(self, default_width=32):
        ''' Rendering iterator with padding '''
        prev_line = None
        repeat_line = 0
        pending = None
        for leaf in self.iter_padded(pad_width=default_width):
            if isinstance(leaf, self.base_leaf):
                for line in leaf.render():
                    if line == prev_line:
                        repeat_line += 1
                        pending = None
                        continue
                    if repeat_line > 0:
                        yield " " * (self.adrwidth + 4)  + "[…0x%x…]" % repeat_line
                    if pending:
                        yield pending
                    pending = None
                    repeat_line = 0
                    prev_line = line
                    yield self.prefix(leaf.lo, leaf.hi) + " " + line
            else:
                print("BTP", type(leaf), [leaf])
                pending = "  " + leaf
        if repeat_line > 0:
            yield " " * (self.adrwidth + 4)  + "[…0x%x…]" % repeat_line

    def points_to(self, lo, cls):
        for i in self.find(lo, lo + 1):
            return i
        first = len(self.todo) == 0
        self.todo.append((lo, cls))
        if not first:
            return
        while self.todo:
            lo, cls = self.todo[0]
            if not list(self.find(lo, lo + 1)):
                i = cls(self, lo).insert()
            self.todo.pop(0)

class Struct():
    '''
        A composite data structure

        A trivial example:

                leaf = Struct(
                    tree,
                    some_address,
                    vertical=True,
                    first_field_=Le32,
                    second_field__=7,
                    last_field_=text_field(8),
                    size=0x100,
                )

        Note the trailing underscores which designates arguments
        as field names.

	The fields definition can be either an integer, which creates
	a predefined filed typ that wide or it can be a class which
	will be instantiated with arguments of

                Le32(tree, some_address + field_offset)

        Which allows fields to be defined with all the classes in
        this file, notably including subclasses of Struct itself.

        Each field creates an attribute without the trailing
        underscore, holding the instance of the class, so for
        instance:

                leaf.first_field.val

        is the 32 bit little-endian value and

                leaf.last_field.txt

        is the decoded text-string.

        The extra underscore on the second field name hides the
        field when rendering but still adds the attribute
        '.second_field_'

        The 'vertical' argument controls rendering (one line vs one
        line per field)

        The 'size' defines the total size for cases where the fields
        do not add up.

        Variant structs can be built incrementally, but must then be
        explicitly completed:

                leaf = Struct(
                    tree,
                    some_address,
                    n_elem_=Le16,
                    incomplete=True,
                )
                for i in range(leaf.n_elem.val):
                    leaf.add_field("f%d" % i, Le32)
                leaf.complete(size = 512);

    '''

    def __init__(self, tree, lo, vertical=False, more=False, pad=0, **kwargs):
        self.fields = []
        self.vertical = vertical
        self.lo = lo
        self.hi = lo
        self.tree = tree
        self.args = {}
        self.pseudofields = []
        self.bt_name = self.__class__.__name__
        for name, width in kwargs.items():
            if name[-1] == "_":
                self.add_field(name[:-1], width)
            else:
                self.args[name] = width
        if not more:
            self.done(pad=pad)

    def __getattr__(self, what):
        ''' Silence pylint E1101 '''
        raise AttributeError(
            "'" + self.__class__.__name__ + "' has no attribute '" + str(what) + "'"
        )

    def done(self, pad=0):
        ''' Struct is complete, finish up '''
        if pad:
            if (self.lo + pad) < self.hi:
                print(
                    self.bt_name,
                    [ hex(self.lo), hex(self.hi) ],
                    "Padding to less than current size",
                    hex(pad),
                    "vs",
                    hex(self.hi - self.lo),
                )
            assert self.lo + pad >= self.hi
            if self.lo + pad != self.hi:
                self.add_field("pad_at%x_" % self.hi, self.lo + pad - self.hi)
        self.base_init(**self.args)
        del self.args

    def add_field(self, name, what):
        ''' add a field to the structure '''
        assert hasattr(self, "args")
        if name is None:
            name = "at%04x" % (self.hi - self.lo)
        if isinstance(what, int):
            y = self.number_field(self.hi, what)
            z = y
        else:
            y = what(self.tree, self.hi)
            z = y
        self.hi = y.hi
        setattr(self, name, z)
        self.fields.append((name, y))
        return y

    def suffix(self, adr):
        ''' Suffix in vertical mode is byte offset of field '''
        return "\t// @0x%x" % (adr - self.lo)

    def render(self):
        assert not hasattr(self, "args")
        if not self.vertical:
            i = []
            for name, obj in self.pseudofields:
                if name[-1] != "_":
                    i.append(name + "=" + str(obj))
            for name, obj in self.fields:
                if name[-1] != "_":
                    i.append(name + "=" + "|".join(obj.render()))
            yield self.bt_name + " {" + ", ".join(i) + "}"
        else:
            yield self.bt_name + " {"
            for name, obj in self.fields:
                if name[-1] != "_":
                    j = list(obj.render())
                    j[0] += self.suffix(obj.lo)
                    yield "  " + name + " = " + j[0]
                    if len(j) > 1:
                        for i in j[1:-1]:
                            yield "    " + i
                        yield "  " + j[-1]
            yield "}"

    def dot_edges(self, dot, src=None):
        if src is None:
            src = self
        for name, fld in self.fields:
            fld.dot_edges(dot, src)

def Array(struct_class, count, what, vertical=None):
    ''' An array of things '''

    if count > 0:

        class Array_Class(struct_class):
            WHAT = what
            COUNT = count

            def __init__(self, *args, **kwargs):
                if vertical:
                    kwargs["vertical"] = vertical
                super().__init__(*args, more = True, **kwargs)
                self.array = []
                for i in range(self.COUNT):
                    f = self.add_field("f%d" % i, self.WHAT)
                    self.array.append(f)
                self.done()

            def __getitem__(self, idx):
                return self.array[idx]

            def __iter__(self):
                yield from self.array

            def render(self):
                if not self.vertical:
                    yield '[' + ", ".join("".join(x.render()) for x in self.array) + "]"
                else:
                    yield '['
                    i = len("%x" % len(self.array))
                    fmt = "  [0x%%0%dx]: " % i
                    for n, i in enumerate(self.array):
                        for j in i.render():
                            yield fmt % n + j
                    yield ']'

            def dot_edges(self, dot, src=None):
                if src is None:
                    src = self
                for fld in self.array:
                    fld.dot_edges(dot, src)

        return Array_Class

    class Array_Class():
        WHAT = what
        COUNT = count

        def __init__(self, tree, lo, *args, **kwargs):
            self.tree = tree
            self.lo = lo
            self.hi = lo
            self.array = []

        def __getitem__(self, idx):
            return self.array[idx]

        def __iter__(self):
            yield from self.array

        def render(self):
            yield '[]'

    return Array_Class

def test_tree():
    ''' Minimal test cases '''

    print("Testing tree class")
    oak = BinTree(0, 0x500)

    # Super items
    oak.insert(BinTreeLeaf(0x100, 0x400))
    oak.insert(BinTreeLeaf(0x100, 0x300))
    oak.insert(BinTreeLeaf(0x200, 0x400))

    # Same items
    oak.insert(BinTreeLeaf(0x200, 0x300))

    # Sub items
    oak.insert(BinTreeLeaf(0x210, 0x290))
    oak.insert(BinTreeLeaf(0x200, 0x299))
    oak.insert(BinTreeLeaf(0x201, 0x300))

    # Skew items
    oak.insert(BinTreeLeaf(0x100, 0x299))
    oak.insert(BinTreeLeaf(0x201, 0x400))

    low = 0
    length = 0
    slo = set()
    shi = set()
    dlo = {}
    dhi = {}

    for i in oak:
        assert i.lo > low or i.hi - i.lo >= length
        low = i.lo
        length = i.hi - i.lo
        slo.add(i.lo)
        shi.add(i.hi)
        if i.lo not in dlo:
            dlo[i.lo] = 1
        else:
            dlo[i.lo] += 1
        if i.hi not in dhi:
            dhi[i.hi] = 1
        else:
            dhi[i.hi] += 1

    print("  .__iter__() OK")

    for j in oak.find(0x200, 0x299):
        assert j.lo < 0x299
        assert j.hi > 0x200
    print("  .find() OK")

    print("Happy")

if __name__ == "__main__":

    test_tree()
