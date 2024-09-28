#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license text

'''
   IBM mainframe and midrange
'''

from .ga21_9128 import Ga21_9182
from .midrange.s34_form import S34Form
from .midrange.s34_library import S34Library

examiners = (
    Ga21_9182,
    S34Form,
    S34Library,
)
