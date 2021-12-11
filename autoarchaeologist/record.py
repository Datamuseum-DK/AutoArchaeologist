'''
   Generic struct reading/parseing facility
   ----------------------------------------

   Pythons `struct` is great and we base this on it, but it has no
   provisions for extensibility.

   We need things like "Two 16 bit words in native order (whatever that is)
   combined to 32 bits as big-endian" (= 'X'), so we roll our own.
'''

import sys
import struct

def swap_words(x):
    ''' swap two halves of a 32 bit word '''
    return (x >> 16) | ((x & 0xffff) << 16)

class Record():
    ''' Brute force data-container class '''
    def __init__(self, **kwargs):
        self.name = ""
        self.__v = kwargs
        for i, j in kwargs.items():
            setattr(self, i, j)

    def __str__(self):
        return "<S "+", ".join([i+"="+str(j) for i,j in self.__v.items()])+">"

    def add(self, name, val):
        self.__v[name] = val
        setattr(self, name, val)

    def __iter__(self):
        yield from self.__v.items()

    def dump(self, fo=sys.stdout):
        ''' One element per line & hexadecimal for debugging '''
        fo.write("struct %s {\n" % self.name)
        for i, j in self.__v.items():
            if isinstance(j, int):
                fo.write("   %-16s 0x%x\n" % (i, j))
            else:
                fo.write("   %-16s %s\n" % (i, str(j)))
        fo.write("}\n")

def Extract_Record(
    this,
    layout,
    offset=0,
    endian="<",
    use_type=Record,
    **kwargs
):
    '''
        Read an on-disk structure

        We cannot use straight struct.unpack because we
        need support for 32 bits with swapped halves ('X')

        Go the full way and pack into a nice Struct while
        at it anyway.
    '''
    fmt = endian + "".join([j for i, j in layout])
    fmt = fmt.replace('X', 'L')
    size = struct.calcsize(fmt)

    data = struct.unpack(fmt, this[offset:offset+size].tobytes())
    data = list(data)
    args = {}
    for i, j in layout:
        n = int(j[:-1])
        args[i] = data[:n]
        data = data[n:]
        if j[-1] == 'X':
            args[i] = [swap_words(x) for x in args[i]]
        if n == 1:
            args[i] = args[i][0]
    assert len(data) == 0
    args["_size"] = size
    args["_offset"] = offset
    return use_type(**kwargs, **args)
