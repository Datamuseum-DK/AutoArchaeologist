#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Regnecentralen RC3600/RC7000 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case

from autoarchaeologist.vendor.regnecentralen import domus_fs
from autoarchaeologist.vendor.regnecentralen import rc3600_tape
from autoarchaeologist.vendor.regnecentralen import rc3600_fdtape
from autoarchaeologist.vendor.regnecentralen import rc3600_bootable_fd
from autoarchaeologist.vendor.regnecentralen import rc3600_fcopy
from autoarchaeologist.vendor.regnecentralen import rc7000_comal
from autoarchaeologist.vendor.regnecentralen import rc3600_ldfs
from autoarchaeologist.vendor.regnecentralen import rc3600_autoload
from autoarchaeologist.generic import bigtext
from autoarchaeologist.vendor.data_general import absbin
from autoarchaeologist.vendor.data_general import relbin
from autoarchaeologist.vendor.data_general import papertapechecksum
from autoarchaeologist.vendor.regnecentralen import rcsl
from autoarchaeologist.generic import samesame
from autoarchaeologist.generic import textfiles

import ddhf

class DomusDS2089(type_case.DS2089):
    ''' RC3600 typical use charset '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x00, ' ', '«nul»', self.EOF)
        self.set_slug(0x07, ' ', '«bel»')
        self.set_slug(0x0c, ' ', '«ff»\n')
        self.set_slug(0x0d, ' ', '')
        self.set_slug(0x0e, ' ', '«so»')
        self.set_slug(0x0f, ' ', '«si»')
        self.set_slug(0x19, ' ', '«eof»', self.EOF)
        self.set_slug(0x7f, ' ', '')

class TextFile(textfiles.TextFile):
    ''' Non-parity '''

    TYPE_CASE = DomusDS2089()
    MAX_TAIL=512*6

class TextFileEven(textfiles.TextFile):
    ''' Even-parity '''

    TYPE_CASE = type_case.EvenPar(DomusDS2089())
    MAX_TAIL=512*6

class TextFileOdd(textfiles.TextFile):
    ''' Odd-parity '''

    TYPE_CASE = type_case.OddPar(DomusDS2089())
    MAX_TAIL=512*6

class Rc3600(ddhf.DDHFExcavation):

    ''' All RC3600 artifacts '''

    BITSTORE = (
        "-30001762",		# Defective
        "RC/RC3600/COMAL",
        "RC/RC3600/DOMUS",
        "RC/RC3600/SW",
        "RC/RC3600/HW",
        "RC/RC3600/LOADER",
        "RC/RC3600/MUSIL",
        "RC/RC3600/PAPERTAPE",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = DomusDS2089()

        self.add_examiner(domus_fs.Domus_Filesystem)
        self.add_examiner(rc3600_tape.RC3600Tape)
        self.add_examiner(rc3600_fdtape.RC3600_FD_Tape)

        self.add_examiner(rc3600_fcopy.Domus_FCOPY)
        self.add_examiner(rc3600_ldfs.LdFs)
        self.add_examiner(rc3600_autoload.AutoLoad)
        self.add_examiner(rc3600_bootable_fd.BootableFd)
        self.add_examiner(rc7000_comal.ComalSaveFile)
        self.add_examiner(absbin.AbsBin)
        self.add_examiner(relbin.RelBin)
        self.add_examiner(bigtext.BigText)
        self.add_examiner(papertapechecksum.PaperTapeCheckSum)
        self.add_examiner(rcsl.RCSL)
        self.add_examiner(TextFile)
        self.add_examiner(TextFileEven)
        self.add_examiner(TextFileOdd)
        self.add_examiner(samesame.SameSame)


if __name__ == "__main__":
    ddhf.main(
        Rc3600,
        html_subdir="rc3600",
        ddhf_topic = "RegneCentralen RC3600/RC7000",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC/RC7000',
    )
