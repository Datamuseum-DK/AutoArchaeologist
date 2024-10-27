#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Recognized human-readable characters punched into paper-tape like:

	────────────────────────────────────────────────────────────────────────────
	 ●●    ●●   ●●●          ●●    ●●    ●●    ●●   ●●    ●●●●         ●●   ●●●●
	●  ●  ●  ●     ●        ●  ●  ●  ●  ●  ●  ●  ●   ●       ●        ●  ●     ●
	●  ●  ●  ●     ●        ●  ●  ●  ●  ●  ●  ●  ●   ●       ●        ●  ●     ●
	◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦
	●  ●   ●●     ●   ●●●   ●  ●  ●  ●  ●  ●  ●  ●   ●      ●   ●●●   ●  ●    ● 
	●  ●  ●  ●   ●          ●  ●  ●  ●  ●  ●  ●  ●   ●     ●          ●  ●   ●  
	●  ●  ●  ●  ●           ●  ●  ●  ●  ●  ●  ●  ●   ●    ●           ●  ●  ●   
	●  ●  ●  ●  ●           ●  ●  ●  ●  ●  ●  ●  ●   ●    ●           ●  ●  ●   
	 ●●    ●●   ●●●●         ●●    ●●    ●●    ●●   ●●●   ●            ●●   ●   
	────────────────────────────────────────────────────────────────────────────

   The (limited set of) glyphs recognized are defined at the very bottom of this file.
'''

class Tree():
    ''' A node in the search tree '''

    def __init__(self):
        self.tbl = {}
        self.term = None
        self.level = 0
        self.mirror = 0

    def __str__(self):
        return "«%d %s %s»" % (
            self.level,
            str([self.term]),
            "-".join("%02x" % x for x in sorted(self.tbl))
        )

    def __getitem__(self, key):
        return self.tbl[key]

    def get(self, key):
        ''' Goto next branch '''
        return self.tbl.get(key)

    def glyph_pattern(self, octets, txt, mirror=-1):
        ''' Add sequence of octets as glyph '''
        tree = self
        for n, i in enumerate(octets):
            if i not in tree.tbl:
                tree.tbl[i] = Tree()
                tree.tbl[i].level = n
            tree = tree[i]
        tree.term = txt
        tree.mirror += mirror

    def match(self, octets, depth=0):
        ''' Attempt to match one of the glyphs '''
        if len(octets) == 0:
            return(depth, None, None)
        i = self.tbl.get(octets[0])
        if i:
            return i.match(octets[1:], depth+1)
        return (depth, self.term, self.mirror)

    def add_drawn_glyph(self, txt, *args):
        ''' Add a glyph to the recognizer tree '''
        # see bottom of this file for example use

        octets = [0] * len(args[0])
        bit = 1
        for i in args:
            for n, j in enumerate(i):
                if j != ' ':
                    octets[n] |= bit
            bit <<= 1
        self.glyph_pattern(octets, txt, mirror=-1)

        octets = [0] * len(args[0])
        bit = 1
        for i in reversed(args):
            for n, j in enumerate(i):
                if j != ' ':
                    octets[n] |= bit
            bit <<= 1
        self.glyph_pattern(octets, txt, mirror=1)

class Hit():
    ''' A hit of one or more glyphs '''

    def __init__(self, up, first, last, txt, mirror):
        self.up = up
        self.first = first
        self.last = last
        self.txt = txt
        self.mirror = mirror
        self.lead = up.lead(self.first)
        self.tail = up.tail(self.last)

    def __repr__(self):
        return '…'.join((
            hex(self.first),
            hex(self.last),
            str([self.txt]),
            str(self.lead),
            str(self.tail),
        ))

    def __len__(self):
        return len(self.txt)

    def cadence(self):
        ''' estimate the width of the glyphs '''
        return (self.last - self.first) / len(self.txt)

    def merge(self, other):
        ''' merge two hits, possibly with unrecognized stuff between '''
        between = bytes(self.up.this[self.last+1:other.first])
        self.last = other.last
        if between and max(between):
            self.txt += '?'
        self.txt += other.txt
        self.tail = other.tail
        self.mirror += other.mirror

    def find_leader(self, howfar):
        ''' Try to find a proper leader to the left '''
        if self.lead:
            return
        for i in range(howfar):
            if self.up.lead(self.first - i):
                self.first -= i
                self.lead = True
                self.txt = '!' + self.txt
                return

    def find_trailer(self, howfar):
        ''' Try to find a proper trailer to the right '''
        # Try to find a proper leader to the right
        if self.tail:
            return
        for i in range(howfar):
            if self.up.tail(self.last + i):
                self.last += i
                self.tail = True
                return

    def render(self):
        ''' render as Unicode '''
        bit = 0x01
        first = self.first - 10
        last = self.last + 10
        yield '─' * (last - first)
        if self.mirror > 0:
            order = (0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01)
            xport = 0x04
        else:
            order = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80)
            xport = 0x08
        for bit in order:
            if bit == xport:
                yield '◦' * (last - first)
            l = []
            for i in self.up.this[first:last]:
                if i & bit:
                    l.append('●')
                else:
                    l.append(' ')
            yield ''.join(l)
        yield '─' * (last - first)

    def commit(self):
        ''' Commit this hit as a new artifact '''
        this = self.up.this
        first = self.first
        while first > 0 and not this[first - 1]:
            first -= 1
        last = self.last
        while last < len(this) and not this[last]:
            last += 1
        that = this.create(start = first, stop = last)
        that.add_type('BigText')
        that.add_note(self.txt)
        that.add_type('»' + self.txt + '«')
        with that.add_utf8_interpretation("BigText") as file:
            for i in self.render():
                file.write(i + '\n')

class BigTextBase():
    '''
       Recognize visual text punched in paper-tape
       (Base class with no built in glyphs)
    '''

    MIN_LENGTH = 3		# Minimum length of text
    MAX_UNKNOWN_LEN = 20	# Maximum amount of unrecognized input data
    MIN_LEADER = 8		# Minimum blank leader on either side
    GIVE_UP_AFTER = 8192	# Bail if nothing found by this much input
    VERBOSE = 0

    TREE = Tree()

    def __init__(self, this):
        if this.has_type("BigText"):
            return

        self.this = this
        self.hits = []

        self.find_hits()
        if not self.hits:
            return

        if self.VERBOSE > 1:
            for hit in self.hits:
                print(self.this, self.__class__.__name__, "HIT", hit)

        self.filter_hits()

        if self.VERBOSE > 1:
            for hit in self.hits:
                print(self.this, self.__class__.__name__, "FILTERED", hit)

        if not self.hits:
            return

        for hit in self.hits:
            if self.VERBOSE:
                print(this, self.__class__.__name__, "COMMIT", hit)
            # Gobble up blank tape before/after ?
            hit.commit()
            if self.VERBOSE > 1:
                for i in hit.render():
                    print(i)

    def find_hits(self):
        ''' Find all glyphs '''
        for pos in range(len(self.this)):
            if pos > 0 and self.this[pos-1] != 0:
                continue
            i, j, mirror = self.TREE.match(self.this[pos:])
            #print("T", pos, i, j, self.GIVE_UP_AFTER, self.hits)
            if j:
                h = Hit(self, pos, pos + i, j, mirror)
                self.hits.append(h)
            elif pos > self.GIVE_UP_AFTER and len(self.hits) < self.MIN_LENGTH:
                return

    def filter_hits(self):
        ''' Filter hits '''

        n = 0
        while n < len(self.hits):
            here = self.hits[n]

            # A sequence must have a blank leader before
            here.find_leader(self.MIN_LEADER)
            if not here.lead:
                self.hits.pop(n)
                continue

            # Try to merge with subsequent hits
            while n < len(self.hits) - 1:
                between = self.this[here.last:self.hits[n + 1].first]
                if between and max(between) > 0 and len(between) > self.MAX_UNKNOWN_LEN:
                    break
                if between and max(between) == 0:
                    here.txt += " " * int((len(between) / here.cadence()))
                here.merge(self.hits.pop(n+1))

            # and a blank leader after
            here.find_trailer(self.MIN_LEADER)
            if not here.tail and len(here) < self.MIN_LENGTH:
                self.hits.pop(n)
                continue

            # Must be this wide to ride
            if len(here.txt) < self.MIN_LENGTH:
                self.hits.pop(n)
                continue

            n += 1

    def lead(self, pos):
        ''' is there a blank leader before this position '''
        if pos == 0:
            return False
        return max(self.this[max(0, pos - self.MIN_LEADER):pos]) == 0

    def tail(self, pos):
        ''' is there a blank trailer after this position '''
        return max(self.this[pos:pos+self.MIN_LEADER]) == 0

DEFAULT_GLYPH_TREE = Tree()

DEFAULT_GLYPH_TREE.add_drawn_glyph('.',
    '        ',
    '        ',
    '        ',
    '        ',
    '        ',
    '        ',
    '  xx    ',
    '  xx    ',
)
DEFAULT_GLYPH_TREE.add_drawn_glyph('/',
    '       x',
    '      xx',
    '     xx ',
    '    xx  ',
    '   xx   ',
    ' xx     ',
    'xx      ',
    'x       ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('0',
    ' xx ',
    'x  x',
    'x  x',
    'x  x',
    'x  x',
    'x  x',
    'x  x',
    ' xx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('0',
    '  xx  ',
    ' x  x ',
    'xx  xx',
    'xx  xx',
    'xx  xx',
    'xx  xx',
    ' x  x ',
    '  xx  ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('1',
    'xx ',
    ' x ',
    ' x ',
    ' x ',
    ' x ',
    ' x ',
    ' x ',
    'xxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('1',
    '   x  ',
    '  xx  ',
    ' xxx  ',
    'x xx  ',
    '  xx  ',
    '  xx  ',
    '  xx  ',
    'xxxxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('2',
    'xxx ',
    '   x',
    '   x',
    '  x ',
    ' x  ',
    'x   ',
    'x   ',
    'xxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('2',
    '  xxxxx ',
    ' xx   xx',
    '      xx',
    '      xx',
    '     xx ',
    ' x      ',
    'xx      ',
    'xxxxxxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('3',
    'xxxx',
    '  x ',
    ' x  ',
    'xxx ',
    '   x',
    '   x',
    '   x',
    'xxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('3',
    'xxxx',
    '  x ',
    '    ',
    'x x ',
    ' x x',
    '   x',
    '   x',
    'xxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('3',
    ' xxxxx ',
    'xx   xx',
    '     xx',
    '     xx',
    '    xx ',
    '     xx',
    'xx   xx',
    ' xxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('4',
    '   x',
    '  xx',
    ' x x',
    'xxxx',
    '   x',
    '   x',
    '   x',
    '   x',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('4',
    'xx   xx ',
    'xx   xx ',
    'xx   xx ',
    'xx   xx ',
    'xxxxxxxx',
    '     xx ',
    '     xx ',
    '     xx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('5',
    'xxxx',
    'x   ',
    'x   ',
    'xxx ',
    '   x',
    '   x',
    '   x',
    'xxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('5',
    'xxxxxxxx',
    'xx      ',
    'xx      ',
    'xx xxx  ',
    'xxx   x ',
    '      xx',
    '      xx',
    ' xxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('6',
    ' xxx',
    'x   ',
    'x   ',
    'xxx ',
    'x  x',
    'x  x',
    'x  x',
    ' xx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('6',
    '  xxxxxx',
    ' xx     ',
    'xx      ',
    'xx xxx  ',
    'xxx   x ',
    'xx    xx',
    'xx    xx',
    ' xxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('7',
    'xxxx',
    '   x',
    '   x',
    '  x ',
    ' x  ',
    'x   ',
    'x   ',
    'x   ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('7',
    'xxxxxxxx',
    'xx    xx',
    '      xx',
    '     xx ',
    '     xx ',
    '    xx  ',
    '    xx  ',
    '    xx  ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('8',
    ' xx ',
    'x  x',
    'x  x',
    ' xx ',
    'x  x',
    'x  x',
    'x  x',
    ' xx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('8',
    ' xxxxxx ',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    ' xxxxxx ',
    'xx    xx',
    'xx    xx',
    ' xxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('9',
    ' xx ',
    'x  x',
    'x  x',
    ' xxx',
    '   x',
    '   x',
    '  x ',
    'xx  ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('9',
    ' xxxxxx ',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    ' xxxxxxx',
    '      xx',
    '      x ',
    ' xxxxx  ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('-',
    '   ',
    '   ',
    '   ',
    'xxx',
    '   ',
    '   ',
    '   ',
    '   ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('-',
    '    ',
    '    ',
    '    ',
    'xxxx',
    '    ',
    '    ',
    '    ',
    '    ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('*',
    '    ',
    '    ',
    '    ',
    'x  x',
    ' xx ',
    'xxxx',
    ' xx ',
    'x  x',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('A',
    ' xxxxxx ',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xxxxxxxx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('B',
    'xxxxxxx ',
    'xxxxxxxx',
    'xx    xx',
    'xx    xx',
    'xxxxxxx ',
    'xx    xx',
    'xxxxxxxx',
    'xxxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('C',
    ' xxxxxx ',
    'xx    xx',
    'xx      ',
    'xx      ',
    'xx      ',
    'xx      ',
    'xx    xx',
    ' xxxxxx ',
)
DEFAULT_GLYPH_TREE.add_drawn_glyph('D',
    'xxxxxxx ',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xxxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('E',
    'xxxxxxxx',
    'xx      ',
    'xx      ',
    'xx      ',
    'xxxxxx  ',
    'xx      ',
    'xx      ',
    'xxxxxxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('F',
    'xxxxxxxx',
    'xx      ',
    'xx      ',
    'xx      ',
    'xxxxxx  ',
    'xx      ',
    'xx      ',
    'xx      ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('G',
    ' xxxxxx ',
    'xx    xx',
    'xx      ',
    'xx      ',
    'xx  xxxx',
    'xx    xx',
    'xx    xx',
    ' xxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('I',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('J',
    '      xx',
    '      xx',
    '      xx',
    '      xx',
    '      xx',
    '      xx',
    'xx    xx',
    ' xxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('L',
    'xx      ',
    'xx      ',
    'xx      ',
    'xx      ',
    'xx      ',
    'xx      ',
    'xx      ',
    'xxxxxxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('M',
    'x      x',
    'xx    xx',
    'xxx  xxx',
    'xxxxxxxx',
    'xx xx xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('N',
    'xx    xx',
    'xxx   xx',
    'xxxx  xx',
    'xx xx xx',
    'xx  xxxx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('O',
    ' xxxxxx ',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    ' xxxxxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('P',
    'xxxxxxx ',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xxxxxxx ',
    'xx      ',
    'xx      ',
    'xx      ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('S',
    ' xxxxxx ',
    'xx      ',
    'xx      ',
    'xx      ',
    ' xxxxxx ',
    '      xx',
    '      xx',
    ' xxxxxx ',
)
DEFAULT_GLYPH_TREE.add_drawn_glyph('R',
    'xxxxxxx ',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xxxxxxx ',
    'xx  xx  ',
    'xx   xx ',
    'xx    xx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('T',
    'xxxxxxxx',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph('U',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    'xx    xx',
    ' xxxxxx ',
)


DEFAULT_GLYPH_TREE.add_drawn_glyph('Y',
    'x      x',
    'xx    xx',
    ' xx  xx ',
    '  xxxx  ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
    '   xx   ',
)

class BigText(BigTextBase):
    '''
       Recognize visual text punched in paper-tape
    '''

    TREE = DEFAULT_GLYPH_TREE
