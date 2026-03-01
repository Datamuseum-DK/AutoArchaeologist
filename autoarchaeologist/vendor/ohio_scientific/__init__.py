#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Ohio Scientific ("OSI") default examiners
   =========================================

   Usage
   -----

   .. code-block:: none

      from autoarchaeologist.vendir import ohio_scientific

      ohio_scientific.defaults(self)

   Contents
   --------

   .. toctree::
       :maxdepth: 1

       os65u_fs.rst
       os65u_basic.rst


'''

from . import os65u_basic, os65u_fs

def defaults(exc):
    ''' ... '''

    exc.add_examiner(*os65u_fs.ALL)
    exc.add_examiner(*os65u_basic.ALL)
