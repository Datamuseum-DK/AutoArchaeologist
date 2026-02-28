#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Zilog MCZ default examiners
   ===========================

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor import zilog
       …
       zilog.mcz_defaults(self)

   Contents
   --------

   .. toctree::
       :maxdepth: 1

       mcz_floppy.rst
       mcz_basic.rst
   
'''

from . import mcz_floppy
from . import mcz_basic

def mcz_defaults(exc):
    exc.add_examiner(mcz_floppy.MczFloppy)
    exc.add_examiner(mcz_basic.MczBasic)
