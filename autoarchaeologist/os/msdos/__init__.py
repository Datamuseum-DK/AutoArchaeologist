#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   MS-DOS default examiners
   ========================
'''

from . import mbr
from . import fatfs
from . import backup
from . import wordperfect

ALL = [
    mbr.Mbr,
    fatfs.FatFs,
    backup.MsDosBackup,
    wordperfect.WordPerfect,
]
