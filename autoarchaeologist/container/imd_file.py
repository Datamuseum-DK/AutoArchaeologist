#!/usr/bin/env python3

'''
    IMD file containers
    -------------------

'''

from ..base import artifact
from ..base import type_case
from ..base import octetview as ov
from . import plain_file

class BadIMDFile(Exception):
    ''' ... '''

class ImdTrack(ov.Struct):
    ''' IMD's track descriptor '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            mode_=ov.Octet,
            cyl_=ov.Octet,
            head_=ov.Octet,
            nsect_=ov.Octet,
            sect_size_=ov.Octet,
        )

class ImdContainer(artifact.ArtifactFragmented):
    ''' Create an artifact from an IMD file '''

    def __init__(self, octets=None, filename=None, verbose=False):
        super().__init__()
        if octets is None:
             fcont = plain_file.PlainFileArtifact(filename)
        else:
             fcont = artifact.ArtifactStream(octets)

        fcont.type_case = type_case.ascii

        if fcont[:4] != b'IMD ':
            raise BadIMDFile("No 'IMD ' at start")

        for ptr, i in enumerate(fcont):
            if i == 0x1a:
                 ptr += 1
                 break

        ovt = ov.OctetView(fcont)
        y = ov.Text(ptr)(ovt, 0).insert()
        if verbose:
            print(y)

        self.separators = []
        recs = []
        while ptr < len(fcont):
            track = ImdTrack(ovt, ptr).insert()
            ptr = track.hi
            if verbose:
                print("T", track)

            if track.head.val & 0x3f > 1:
                raise BadIMDFile("Track[%d] head %d > 1" % (track.cyl.val, track.head.val & 0x3f))

            if track.mode.val > 5:
                raise BadIMDFile("Track[%d] mode %d > 5" % (track.cyl.val, track.mode.val))

            if track.sect_size.val > 6:
                raise BadIMDFile("Track[%d] sect_size %d > 6" % (track.cyl.val, track.sect_size.val))
            if track.nsect.val == 0:
                continue

            sect_size = 1 << (7 + track.sect_size.val)

            sec_map = ov.HexOctets(ovt, ptr, width = track.nsect.val).insert()
            if verbose:
                print("SM", sec_map)
            ptr = sec_map.hi

            if track.head.val & 0x80:
                cyl_map = ov.HexOctets(ovt, ptr, width = track.nsect.val).insert()
                ptr = cyl_map.hi
                track.head.val &= ~0x80
                if verbose:
                    print("CM", cyl_map)
            else:
                cyl_map = [track.cyl.val] * track.nsect.val
 
            if track.head.val & 0x40:
                head_map = ov.HexOctets(ovt, ptr, width = track.nsect.val).insert()
                ptr = head_map.hi
                track.head.val &= ~0x40
                if verbose:
                    print("HM", head_map)
            else:
                head_map = [track.head.val] * track.nsect.val

            for sect in range(track.nsect.val):
                chs = (cyl_map[sect], head_map[sect], sec_map[sect])
                y = ov.HexOctets(ovt, ptr, width = 1).insert()
                ptr = y.hi
                mode = y[0]
                if mode > 8:
                    raise BadIMDFile("Sector mode %d > 8" % mode)
                if mode == 0:
                    continue
                if mode & 1:
                    ov.Opaque(ovt, ptr, width=sect_size).insert()
                    data = fcont[ptr:ptr + sect_size]
                    ptr += sect_size
                else:
                    data = bytes([fcont[ptr]] * sect_size)
                    ptr += 1
                if mode >= 5:
                    continue
                if not sum(chs):
                    continue
                recs.append((chs, data, mode > 2))

        for key, data, deleted in sorted(recs):
            rec = artifact.Record(len(self), frag=data, key=key)
            self.add_fragment(rec)
            rec.deleted = deleted
            if deleted:
                self.separators.append((rec.lo, "@c%d,h%d,s%d (deleted)" % key))
            else:
                self.separators.append((rec.lo, "@c%d,h%d,s%d" % key))

        self.completed()
