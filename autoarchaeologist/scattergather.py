#!/usr/bin/env python3

'''
    AutoArchaeologist ScatterGather Class
    -------------------------------------

'''

import hashlib

class ScatterGather():

    def __init__(self, records):
        self.sgx = list(records)
        self.length = sum([len(x) for x in self.sgx])

    def __str__(self):
        return "<SG %d %d>" % (self.length, len(self.sgx))

    def __repr__(self):
        return "<SG %d %d>" % (self.length, len(self.sgx))

    def __len__(self):
        return self.length

    def __iter__(self):
        for i in self.sgx:
            yield from i

    def iterrecords(self):
        yield from self.sgx

    def block(self, n):
        return self.sgx[n]

    def subsection(self, start, stop):
        ''' yields pieces of a subrange '''
        assert start >= 0
        assert start <= stop
        assert stop <= self.length
        offset = 0
        for src in self.sgx:
            istart = max(0, start - offset)
            istop = min(len(src), stop - offset)
            if istart < istop:
                yield src[istart:istop]
            offset += len(src)
            if stop < offset:
                return

    def __getitem__(self, idx):
        if not isinstance(idx, slice):
            if idx < 0 or idx > self.length:
                raise IndexError()
            for src in self.subsection(idx, idx + 1):
                return src[0]
        start, stop, step = idx.indices(len(self))
        if step != 1:
            raise IndexError("Only step=1 allowed")
        if start == 0 and stop == len(self):
            return self
        x = self.subsection(start, stop)
        v = ScatterGather(x)
        return v

    def sha256(self):
        i = hashlib.sha256()
        for j in self.sgx:
            i.update(j.tobytes())
        return i.hexdigest()

    def writetofile(self, fd):
        for i in self.sgx:
            if isinstance(i, ScatterGather):
                i.writetofile(fd)
            else:
                fd.write(i)

    def tobytes(self):
        return b''.join([x.tobytes() for x in self.sgx])
