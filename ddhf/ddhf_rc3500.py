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
from autoarchaeologist.generic import tapefiles
from autoarchaeologist.vendor.regnecentralen import rc489k_tape
from autoarchaeologist.vendor.regnecentralen import rc489k_binout
from autoarchaeologist.vendor.regnecentralen import rcsl
from autoarchaeologist.vendor.regnecentralen import rc3500_fs
from autoarchaeologist.generic import ansi_tape_labels

import ddhf

class Rc3500TypeCase(type_case.Ascii):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_slug(0x0, ' ', '«nul»', self.IGNORE)
        self.set_slug(0x0d, ' ', '', self.IGNORE)
        self.set_slug(0x19, ' ', '«eof»', self.EOF)
        self.set_slug(0x7f, ' ', '\t')


class Rc489kEvenPar(type_case.EvenPar):
    ''' Even parity version of type case '''
    def __init__(self):
        super().__init__(Rc3500TypeCase())
        self.set_slug(0xff, ' ', '«0xff»', self.IGNORE)

class TextFile(textfiles.TextFile):
    ''' Text files with even parity'''
    MAX_TAIL = 0x1f700

class TextFileEvenParity(TextFile):
    ''' Text files with even parity'''
    TYPE_CASE = Rc489kEvenPar()
    VERBOSE = True


class Rc489k(ddhf.DDHFExcavation):

    ''' All RC4000, RC8000 and RC9000 artifacts '''

    TYPE_CASE = Rc3500TypeCase()

    BITSTORE = (
        "RC/RC3500/TEST",
        "RC/RC3500/ALARMNET",
        "RC/RC3500/TAPE",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = Rc3500TypeCase()

        self.add_examiner(*rc489k_tape.examiners)
        self.add_examiner(*rc489k_binout.examiners)
        self.add_examiner(tapefiles.UnlovedTapes)
        self.add_examiner(rc3500_fs.Rc3500Filesystem)
        self.add_examiner(rcsl.RCSL)
        self.add_examiner(textfiles.TextFileVerbose)
        self.add_examiner(TextFileEvenParity)
        self.add_examiner(ansi_tape_labels.AnsiTapeLabels)
        self.add_examiner(samesame.SameSame)

if __name__ == "__main__":
    ddhf.main(
        Rc489k,
        html_subdir="rc3500",
        ddhf_topic = "RC3500",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC3500',
	downloads=True,
        download_limit= 40<<20,
    )
