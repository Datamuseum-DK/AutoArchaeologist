#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Wang WPS default examiners
   ==========================

   Usage
   -----

   .. code-block:: none

      from autoarchaeologist.vendir import wang

      wang.wps_defaults(self)

   Contents
   --------

   .. toctree::
      :maxdepth: 1

      wang_wps.rst
      wang_text.rst

'''

from . import wang_wps
from . import wang_text

def wps_defaults(exc):
   ''' ... '''
   exc.add_examiner(*wang_wps.ALL)
   exc.add_examiner(*wang_text.ALL)
