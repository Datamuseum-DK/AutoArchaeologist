#!/usr/bin/env python3

'''
   Floppy Disk Helpers
   ~~~~~~~~~~~~~~~~~~~
'''

class Zone():
    '''
       A "rectangular" zone of a (floppy)disk medium
       ---------------------------------------------
    '''

    def __init__(
        self,
        first_cyl,
        last_cyl,
        first_head,
        last_head,
        first_sect,
        last_sect,
        sector_length,
    ):
        self.first_cyl = first_cyl
        self.last_cyl = last_cyl
        self.first_head = first_head
        self.last_head = last_head
        self.first_sect = first_sect
        self.last_sect = last_sect
        self.sector_length = sector_length
        self.n_cyl = 1 + last_cyl - first_cyl
        self.n_head = 1 + last_head - first_head
        self.n_sect = 1 + last_sect - first_sect
        self.sectors = self.n_cyl * self.n_head * self.n_sect

    def __str__(self):
        return "<Zone " + " ".join(
            [
                "c" + str(self.first_cyl) + "…" + str(self.last_cyl),
                "h" + str(self.first_head) + "…" + str(self.last_head),
                "s" + str(self.first_sect) + "…" + str(self.last_sect),
                str(self.sectors) + "*" + str(self.sector_length)
            ]
        ) + ">"

    def interleave(self, n):
        '''
           Calculate canonical interleave sequence
           ---------------------------------------
        '''
        sects = set(range(self.first_sect, self.last_sect+1))
        picks = [0] * self.first_sect
        cur = self.first_sect
        while sects:
            if cur > self.last_sect:
                cur -= self.last_sect
            if cur not in sects:
                cur += 1
                continue
            picks.append(cur)
            sects.discard(cur)
            cur += n
        #print("IL", self, picks)
        return picks

class Geometry():
    '''
       Determine relevant parameters of geometry
       -----------------------------------------
    '''

    def __init__(self, this):
        self.c = set()
        self.h = set()
        self.s = {}
        self.l = {}
        self.zones = None
        for rec in this.iter_rec():
            c, h, s = rec.key
            self.c.add(c)
            self.h.add(h)
            i = (c, h)
            if i not in self.s:
                self.s[i] = set()
                self.l[i] = set()
            self.s[i].add(s)
            self.l[i].add(len(rec.frag))

    def fits(self, zone):
        '''
           Test if a "rectangular" zone would fit
           --------------------------------------

           (Complicated by the need for some wiggle room for unread sectors)
        '''

        if not self.c:
            return False
        bad_track = 0
        good_track = 0
        saw_last_sector = 0
        for cyl in range(zone.first_cyl, zone.last_cyl + 1):
            for head in range(zone.first_head, zone.last_head + 1):
                i = (cyl, head)
                if not i in self.s:
                    bad_track += 1
                    continue
                l = self.l.get(i)
                if len(l) != 1:
                    return False
                if min(l) != zone.sector_length:
                    return False
                s = self.s.get(i)
                if min(s) < zone.first_sect:
                    return False
                if max(s) > zone.last_sect:
                    return False
                if max(s) == zone.last_sect:
                    saw_last_sector += 1
                good_track += 1
        if not saw_last_sector:
            return False
        if 5 + max(self.c) > zone.last_cyl * 2:
            return False
        return 5 + good_track > (zone.last_cyl - zone.first_cyl)

    def find_zones(self):
        ''' Summarize geometry in zones '''

        def rep(a):
            if not a:
                return "ø"
            if min(a) == max(a):
                return (min(a),)
            return min(a), max(a),

        tmpzones = []
        for head in sorted(self.h):
            for cyl in sorted(self.c):
                i = (cyl, head)
                if i not in self.s:
                    continue
                j = set()
                j.add(cyl)
                k = set()
                k.add(head)
                tmpzones.append([j, k, self.s.get(i), self.l.get(i)])

        tmpzones.sort(key=lambda x: (list(x[0]), list(x[1])))

        idx = 0
        while idx < len(tmpzones) - 1:
            z1 = tmpzones[idx]
            z2 = tmpzones[idx + 1]
            if z1[0] == z2[0] and z1[2:] == z2[2:]:
                z1[1] |= z2[1]
                tmpzones.pop(idx + 1)
            else:
                idx += 1

        tmpzones.sort(key=lambda x: (list(x[1]), list(x[0])))

        idx = 0
        while idx < len(tmpzones) - 1:
            z1 = tmpzones[idx]
            z2 = tmpzones[idx + 1]
            if z1[1:] == z2[1:]:
                z1[0] |= z2[0]
                tmpzones.pop(idx + 1)
            else:
                idx += 1

        tmpzones.sort(key=lambda x: (list(x[0]), list(x[1])))

        def rep(x):
            if not x:
                return "ø"
            i = min(x)
            j = max(x)
            if i == j:
                return x
            if 1 + j - i == len(x):
                return i, j
            return i, j, len(x)

        self.zones = []
        for z in tmpzones:
            self.zones.append((rep(z[0]), rep(z[1]), rep(z[2]), z[3]))
