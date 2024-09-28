#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   IBM mainframe and midrange
'''

from ....base import type_case
from ..ga21_9128 import Ga21_9182
from .s34_form import S34Form
from .s34_library import S34Library

examiners = (
    Ga21_9182,
    S34Form,
    S34Library,
)

def midrange_excavation(exc):
    ''' Configure excavation for IBM midrange systems '''

    # There are national variations of EBCDIC, (See: # GA21-9247-6 pdf pg 103ﬀ)
    # but Python only knows about the US/Netherlands variant under the name of
    # code page 37.
    exc.type_case = type_case.WellKnown("cp037")

    exc.add_examiner(*examiners)
