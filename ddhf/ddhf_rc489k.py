#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Regnecentralen RC4000/RC8000/RC9000 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case

from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame
from autoarchaeologist.vendor.regnecentralen import rc489k_tape
from autoarchaeologist.vendor.regnecentralen import rc489k_binout
from autoarchaeologist.vendor.regnecentralen import rcsl
from autoarchaeologist.vendor.regnecentralen import gier_text

import ddhf

class Rc489kTypeCase(type_case.DS2089):
    ''' RC489k default type case '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x00, ' ', '', self.IGNORE)
        self.set_slug(0x08, ' ', '«bs»')
        self.set_slug(0x19, ' ', '▶EOF◀', self.EOF)
        self.set_slug(0x1f, ' ', '▶EOF◀', self.EOF)

class Rc489kEvenPar(type_case.EvenPar):
    ''' Even parity version of type case '''
    def __init__(self):
        super().__init__(Rc489kTypeCase())

class TextFile(textfiles.TextFile):
    ''' Text files with even parity'''
    MAX_TAIL = 0x1f700

class TextFileEvenParity(TextFile):
    ''' Text files with even parity'''
    TYPE_CASE = Rc489kEvenPar()

class Rc489k(ddhf.DDHFExcavation):

    ''' All RC4000, RC8000 and RC9000 artifacts '''

    BITSTORE = (
        "RC/RC8000/DISK",
        "RC/RC8000/PAPERTAPE",
        "RC/RC8000/TAPE",
        "RC/RC4000/SW",
        "RC/RC4000/TEST",
        "RC/RC9000",
        "RC/RC9000/TAPE",
        "RC/RC3500/TAPE",
        "30003100",
        "30007477",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = Rc489kTypeCase()

        self.add_examiner(*rc489k_tape.examiners)
        self.add_examiner(*rc489k_binout.examiners)
        self.add_examiner(rcsl.RCSL)
        self.add_examiner(TextFile)
        self.add_examiner(TextFileEvenParity)
        self.add_examiner(samesame.SameSame)
        self.add_examiner(gier_text.GIER_Text)

if __name__ == "__main__":
    ddhf.main(
        Rc489k,
        html_subdir="rc489k",
        ddhf_topic = "RC4000/8000/9000",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC4000,_RC8000_and_RC9000',
	downloads=True,
    )
