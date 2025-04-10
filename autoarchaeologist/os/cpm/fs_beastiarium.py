#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   CP/M filesystems - The weird ones
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

from . import fs_abc

INTERLEAVE_BEASTIARIUM = [
    # [ desc, interleave_order ]
    [ "CR7_Diplomat", [1, 2, 5, 6, 9, 10, 13, 14, 3, 4, 7, 8, 11, 12, 15, 16] ],
    [ "Butler3", [1, 4, 7, 10,  2, 5, 8,  3, 6, 9] ],
]

class CpmFSButler1a(fs_abc.CpmFileSystem):
    ''' Bogika Butler '''

    SECTOR_SIZE = 512
    SECTORS = [1, 4, 7, 10, 3, 6, 9, 2, 5, 8]
    TRACKS = [(c, c & 1) for c in range(2,160)]
    BLOCK_SIZE = 2048
    N_DIRENT = 6 * 16
    BLOCK_NO_WIDTH = 16

    def __init__(self, this, *args, **kwargs):
        if not this.has_rec((100, 0, 1)):
            raise fs_abc.Nonsense
        super().__init__(this, *args, **kwargs)

class CpmFSButler1b(fs_abc.CpmFileSystem):
    ''' Bogika Butler '''

    SECTOR_SIZE = 512
    SECTORS = [1, 4, 7, 10, 2, 5, 8, 3, 6, 9]
    TRACKS = [(c, c & 1) for c in range(2,160)]
    BLOCK_SIZE = 2048
    N_DIRENT = 80
    BLOCK_NO_WIDTH = 16

    def __init__(self, this, *args, **kwargs):
        if not this.has_rec((100, 0, 1)):
            raise fs_abc.Nonsense
        super().__init__(this, *args, **kwargs)

GEOMETRY_BEASTIARIUM = [
    CpmFSButler1a,
    CpmFSButler1b,
]
