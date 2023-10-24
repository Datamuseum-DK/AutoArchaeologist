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
    def __init__(self, lo, hi):
        assert isinstance(lo, int)
        assert isinstance(hi, int)
        assert lo < hi
        self.lo = lo
        self.hi = hi

    def __repr__(self):
        return "<BinTreeLeaf 0x%x-0x%x>" % (self.lo, self.hi)

    def __lt__(self, other):
        if self.lo != other.lo:
            return self.lo < other.lo
        return self.hi < other.hi

    def __eq__(self, other):
        return self.lo == other.lo and self.hi == other.hi

class BinTree():

    '''
    Root/branch class of the tree
    -----------------------------
    '''

    def __init__(self, lo, hi, limit=128):
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
