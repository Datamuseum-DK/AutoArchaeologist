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

    def __str__(self):
        return "«%d %s %s»" % (
            self.level,
            str([self.term]),
            "-".join("%02x" % x for x in self.tbl)
        )

    def __getitem__(self, key):
        return self.tbl[key]

    def get(self, key):
        ''' Goto next branch '''
        return self.tbl.get(key)

    def glyph_pattern(self, octets, txt):
        ''' Add sequence of octets as glyph '''
        tree = self
        for n, i in enumerate(octets):
            if i not in tree.tbl:
                tree.tbl[i] = Tree()
                tree.tbl[i].level = n
            tree = tree[i]
        tree.term = txt

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
        self.glyph_pattern(octets, txt)

class Hit():
    ''' A hit of one or more glyphs '''

    def __init__(self, up, first, last, txt):
        self.up = up
        self.first = first
        self.last = last
        self.txt = txt
        self.lead = up.lead(self.first)
        self.tail = up.tail(self.last)

    def __str__(self):
        return '…'.join((
            hex(self.first),
            hex(self.last),
            str([self.txt]),
            str(self.lead),
            str(self.tail),
        ))

    def merge(self, other):
        ''' merge two hits, possibly with unrecognized stuff between '''
        between = bytes(self.up.this[self.last+1:other.first])
        self.last = other.last
        if max(between):
            self.txt += '?'
        self.txt += other.txt
        self.tail = other.tail

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
                self.txt += '@'
                return

    def render(self):
        ''' render as Unicode '''
        bit = 0x01
        yield '─' * (self.last - self.first)
        while bit < 0x100:
            if bit == 0x08:
                yield '◦' * (self.last - self.first)
            l = []
            for i in self.up.this[self.first:self.last]:
                if i & bit:
                    l.append('●')
                else:
                    l.append(' ')
            yield ''.join(l)
            bit <<= 1
        yield '─' * (self.last - self.first)

    def commit(self):
        ''' Commit this hit as a new artifact '''
        this = self.up.this
        that = this.create(start = self.first, stop = self.last)
        that.add_type('BigText')
        that.add_note(self.txt)
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
    MIN_LEADER = 16		# Minimum blank leader on either side
    GIVE_UP_AFTER = 1024	# Bail if nothing found by this much input
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
        if not self.hits:
            return

        for hit in self.hits:
            if self.VERBOSE:
                print(this, self.__class__.__name__, "COMMIT", hit)
            hit.commit()

    def find_hits(self):
        ''' Find all glyphs '''
        first = 0
        climb = self.TREE
        for pos, i in enumerate(self.this):
            j = climb.get(i)
            if j:
                if first == 0:
                    first = pos
                climb = j
            else:
                if climb.term:
                    self.hits.append(Hit(self, first, pos, climb.term))
                first = 0
                climb = self.TREE
            if pos > self.GIVE_UP_AFTER and not self.hits:
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
                if self.hits[n + 1].first - here.last > self.MAX_UNKNOWN_LEN:
                    break
                here.merge(self.hits.pop(n+1))

            # and a blank leader after
            here.find_trailer(self.MIN_LEADER)
            if not here.tail:
                self.hits.pop(n)
                continue

            # Must be this wide to ride
            if len(here.txt) < self.MIN_LENGTH:
                self.hits.pop(0)
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

DEFAULT_GLYPH_TREE.add_drawn_glyph( '0',
    ' xx ',
    'x  x',
    'x  x',
    'x  x',
    'x  x',
    'x  x',
    'x  x',
    ' xx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '1',
    'xx ',
    ' x ',
    ' x ',
    ' x ',
    ' x ',
    ' x ',
    ' x ',
    'xxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '2',
    'xxx ',
    '   x',
    '   x',
    '  x ',
    ' x  ',
    'x   ',
    'x   ',
    'xxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '3',
    'xxxx',
    '  x ',
    ' x  ',
    'xxx ',
    '   x',
    '   x',
    '   x',
    'xxx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '4',
    '   x',
    '  xx',
    ' x x',
    'xxxx',
    '   x',
    '   x',
    '   x',
    '   x',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '5',
    'xxxx',
    'x   ',
    'x   ',
    'xxx ',
    '   x',
    '   x',
    '   x',
    'xxxx',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '6',
    ' xxx',
    'x   ',
    'x   ',
    'xxx ',
    'x  x',
    'x  x',
    'x  x',
    ' xx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '7',
    'xxxx',
    '   x',
    '   x',
    '  x ',
    ' x  ',
    'x   ',
    'x   ',
    'x   ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '8',
    ' xx ',
    'x  x',
    'x  x',
    ' xx ',
    'x  x',
    'x  x',
    'x  x',
    ' xx ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '9',
    ' xx ',
    'x  x',
    'x  x',
    ' xxx',
    '   x',
    '   x',
    '  x ',
    'xx  ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '-',
    '   ',
    '   ',
    '   ',
    'xxx',
    '   ',
    '   ',
    '   ',
    '   ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '-',
    '    ',
    '    ',
    '    ',
    'xxxx',
    '    ',
    '    ',
    '    ',
    '    ',
)

DEFAULT_GLYPH_TREE.add_drawn_glyph( '*',
    '    ',
    '    ',
    '    ',
    'x  x',
    ' xx ',
    'xxxx',
    ' xx ',
    'x  x',
)

class BigText(BigTextBase):
    '''
       Recognize visual text punched in paper-tape
    '''

    TREE = DEFAULT_GLYPH_TREE
