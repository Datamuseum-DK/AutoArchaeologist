#!/usr/bin/env python3

'''
   Systems of a set of disks/volumes
   =================================
'''

from ...base import bitview as bv

from .defs import SECTBITS
from .segment import Segment
from .world import World

systems = {}

class R1kSystem():
    ''' A R1K System with a set of disks/volumes '''

    def __init__(self, ident):
        self.ident = ident
        self.volumes = [None] * 16
        self.worldptrs = {}
        self.worlds = []
        self.volnos = set()

    def add_volume(self, volume):
        assert self.volumes[volume.sblk.volnbr.val] is None
        self.volumes[volume.sblk.volnbr.val] = volume
        if volume.worldindex:
            for world in volume.worldindex:
                assert world.world.val not in self.worldptrs
                self.worldptrs[world.world.val] = world
                self.volnos.add(world.volume.val)
        if self.volumes[1] is None:
            return
        for vol in self.volnos:
            if self.volumes[vol] is None:
                return
        self.complete()

    def complete(self):
        print("CPL", self.volnos)
        for worldptr in self.worldptrs.values():
            if worldptr.snapshot.val == 0:
                continue
            world = World(self.volumes[worldptr.volume.val], worldptr.lba.val)
            self.worlds.append(world)

        for vol in self.volumes:
            if vol:
                vol.completed()

def add_volume(volume):
    sysid = volume.sblk.bootvolid.val
    if sysid not in systems:
        systems[sysid] = R1kSystem(sysid)
    systems[sysid].add_volume(volume)
