#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   R1kSystem - a set of volumes (=disks)
   =====================================

   Untangling disks from different systems in the same excavation
   should be trivial, in theory the volume identifiers should be
   able to do it on their own.

   Untangle disks from multiple generations of the the same system
   not so much.

   Primary volumes are easy to distinguish on volume id, boot number,
   snapshot etc.

   There is no way to spelunk all worlds on a secondary volume
   in isolation, which means that there is no way to find the
   highest snapshot number in isolation either and the boot number
   lives only on the primary, so that is also no help.

   The only way to assign secondaries to primaries would be a
   brute-force try-score-filter exercise.

   We can imagine several good bail early tests, such as dangling
   world pointers, too high snapshot numbers and colliding segment
   IDs, but it is still fundamentally a brute-force match.

   Given the current setof artifacts, that does not seem worth
   the effort.
 
'''

from .world import World

class R1kSystem():
    ''' A R1K System consisting of a set of volumes (=disks) '''

    def __init__(self, ident):
        self.ident = ident
        self.volumes = [None] * 16
        self.worldptrs = {}
        self.worlds = []
        self.volnos = set((1,))
        self.segments = {}

    def add_volume(self, volume):
        ''' Add volume to system, continue once we have them all '''

        assert self.volumes[volume.sblk.volnbr.val] is None
        self.volumes[volume.sblk.volnbr.val] = volume

        if volume.worldindex:
            for world in volume.worldindex:
                assert world.world.val not in self.worldptrs
                self.worldptrs[world.world.val] = world
                self.volnos.add(world.volume.val)

        for vol in self.volnos:
            if self.volumes[vol] is None:
                return

        self.complete()

    def add_segment(self, seg):
        ''' Add a segment to the system '''
        i = self.segments.get(seg.name)
        if i is None:
            i = {}
            self.segments[seg.name] = i
        if seg.version in i:
            print("Segment version collision", seg, list(i.keys()))
            assert False
        i[seg.version] = seg

    def complete(self):
        ''' With all volumes, we can really excavate '''

        for worldptr in self.worldptrs.values():
            world = World(self.volumes[worldptr.volume.val], worldptr.lba.val)
            self.worlds += list(world.iter_worlds())

        for world in self.worlds:
            world.commit_segments(self)

        print("#segs", len(self.segments))

        for vol in self.volnos:
            self.volumes[vol].completed()

def add_volume(excavation, volume):
    ''' Join volumes into systems '''

    sysid = volume.sblk.bootvolid.val
    r1ksys = excavation.multivol.get(sysid)
    if r1ksys is None:
        r1ksys = R1kSystem(sysid)
        excavation.multivol[sysid] = r1ksys
    r1ksys.add_volume(volume)
    return r1ksys
