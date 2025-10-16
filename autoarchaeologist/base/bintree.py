#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

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
    Base-class for the leaves of the tree
    -------------------------------------

    You will be creating a LOT of these, so keep them cheap.
    '''
    def __init__(self, lo: int, hi: int):
        assert lo < hi
        self.lo = lo
        self.hi = hi

    def __len__(self):
        return self.hi - self.lo

    def __repr__(self):
        return "<Leaf 0x%x-0x%x>" % (self.lo, self.hi)

    def __lt__(self, other):
        if self.lo != other.lo:
            return self.lo < other.lo
        return self.hi < other.hi

    def __eq__(self, other):
        if other is None:
            return False
        return self.lo == other.lo and self.hi == other.hi

    def __hash__(self):
        return super().__hash__()

    def __contains__(self, adr):
        return self.lo <= adr < self.hi

    def dot_node(self, _dot):
        ''' ... '''
        return None, None

    def dot_edges(self, _dot, _src=None):
        ''' ... '''

class BinTreeBranch():

    '''
    Root&branch class of the tree
    -----------------------------
    '''

    # Tuning: Do not create branches smaller than this.
    LOWER_LIMIT = 1<<16

    def __init__(self, lo, hi):
        self.lo = lo
        self.mid = (lo + hi) // 2
        self.hi = hi
        self.less = None
        self.more = None
        self.cuts = []
        self.isbranch = (hi - lo) > self.LOWER_LIMIT

    def __repr__(self):
        return "<Branch 0x%x-0x%x-0x%x>" % (self.lo, self.mid, self.hi)

    def insert(self, leaf):
        ''' You guessed it... '''
        assert isinstance(leaf, BinTreeLeaf)
        assert leaf.lo < leaf.hi
        if not self.isbranch:
            self.cuts.append(leaf)
            return leaf
        if leaf.hi <= self.mid:
            if self.less is None:
                self.less = BinTreeBranch(self.lo, self.mid)
            return self.less.insert(leaf)
        if leaf.lo >= self.mid:
            if self.more is None:
                self.more = BinTreeBranch(self.mid, self.hi)
            return self.more.insert(leaf)
        self.cuts.append(leaf)
        return leaf

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
            lst.sort(key=lambda i: (i.lo, i.hi))
            if cur.more:
                stk.append(cur.more)
            if cur.less:
                stk.append(cur.less)
            else:
                while lst and lst[0].lo < cur.mid:
                    yield lst.pop(0)
        yield from lst

class BinTree(BinTreeBranch):
    ''' The root of the tree '''

    def __init__(self, *args, leaf=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.adrwidth = len("%x" % self.hi)
        self.adrfmt = "%%0%dx" % self.adrwidth
        self.separators = []
        self.separators_width = 0
        self.todo = []
        self.leaf_class = leaf

    def __repr__(self):
        return "<Tree 0x%x-0x%x-0x%x>" % (self.lo, self.mid, self.hi)

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
            pad = self.leaf_class(self, lo, hi=i)
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
        ''' The address range on the rendered line '''

        if self.separators_width == 0:
            return "0x" + self.adrfmt % lo + "…" + self.adrfmt % hi
        while self.separators and self.separators[0][0] < lo:
            self.separators.pop(0)
        if self.separators and self.separators[0][0] == lo:
            i = self.separators.pop(0)[1]
        else:
            i = ""
        return "0x" + self.adrfmt % lo + "…" + self.adrfmt % hi + i.ljust(self.separators_width)

    def render(self, line_length=32):
        ''' Rendering iterator with padding '''

        prev_line = None
        repeat_line = 0
        pending = None
        pfx = "placeholder"
        for leaf in self.iter_padded(pad_width=line_length):
            if isinstance(leaf, self.leaf_class):
                for line in leaf.render():
                    if line == prev_line:
                        repeat_line += 1
                        pending = None
                        continue
                    if repeat_line > 0:
                        yield " " * len(pfx) + "[…0x%x…]" % repeat_line
                    if pending:
                        yield pending
                    pending = None
                    repeat_line = 0
                    prev_line = line
                    pfx = self.prefix(leaf.lo, leaf.hi) + " "
                    yield pfx + line
            else:
                print("BTP", type(leaf), [leaf])
                pending = "  " + leaf
        if repeat_line > 0:
            yield " " * len(pfx) + "[…0x%x…]" % repeat_line

    def points_to(self, lo, cls):
        ''' Used by pointer-like leaves to propagate without stack overflow '''

        for _i in self.find(lo, lo + 1):
            return
        first = len(self.todo) == 0
        self.todo.append((lo, cls))
        if not first:
            return
        while self.todo:
            # NB: Must stay on todo to prevent endless recursion
            lo, cls = self.todo[0]
            if not list(self.find(lo, lo + 1)):
                cls(self, lo).insert()
            self.todo.pop(0)

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
