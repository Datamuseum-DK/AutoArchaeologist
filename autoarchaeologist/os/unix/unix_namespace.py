#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Common "ls -l" style NameSpace for UNIX
'''

import time

from ...base import namespace as ns

from . import unix_stat

class NameSpace(ns.NameSpace):
    ''' ... '''

    KIND = "Unix file"

    TABLE = [
        ("r", "mode"),
        ("r", "link"),
        ("r", "uid"),
        ("r", "gid"),
        ("r", "size"),
        ("l", "mtime"),
    ] + ns.NameSpace.TABLE

    def __init__(self, *args, flds=None, **kwargs):
        if flds:
            flds = list(flds)
            flds[0] = unix_stat.stat.mode_bits(flds[0])
            flds[5] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(flds[5]))
        super().__init__(*args, flds=flds, **kwargs)
