#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Rational R1000/400 DFS Tapes from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.generic import sccs_id
from autoarchaeologist.base import type_case
from autoarchaeologist.vendor.rational import dfs_tape
from autoarchaeologist.vendor.rational import r1k_assy
from autoarchaeologist.vendor.rational import r1k_configuration
from autoarchaeologist.vendor.rational import r1k_ucode
from autoarchaeologist.vendor.rational import r1k_m200
from autoarchaeologist.vendor.rational import r1k_experiment

from autoarchaeologist.generic import samesame
from autoarchaeologist.generic import textfiles

import ddhf

class TextFile(textfiles.TextFile):
    ''' Custom credibility '''

    def credible(self):
        if len(self.txt) < 5:
            return False
        if len(self.txt) < 10 and '\n' not in self.txt:
            return False
        if len(self.this) - len(self.txt) >= 1024:
            return False
        return True

class TypeCase(type_case.Ascii):
    ''' ... '''

    def __init__(self):
        super().__init__()
        self.set_slug(0, ' ', '«nul»', self.EOF)

class R1KDFS(ddhf.DDHFExcavation):
    ''' Rational R1000/400 DFS tapes '''

    BITSTORE = (
        "30000744",   # precise file sizes
        "30000407",   # precise file sizes
        "30000528",   # file sizes rounded up
        "30000743",   # file sizes rounded up
        "30000750",   # file sizes rounded up
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(dfs_tape.R1K_DFS_Tape)
        self.add_examiner(r1k_configuration.R1kM200ConfigFile)
        self.add_examiner(r1k_assy.R1kAssyFile)
        self.add_examiner(*r1k_ucode.ALL)
        self.add_examiner(r1k_m200.R1kM200File)
        self.add_examiner(r1k_experiment.R1kExperiment)
        self.add_examiner(TextFile)
        self.add_examiner(sccs_id.SccsId)
        self.add_examiner(samesame.SameSame)

        self.type_case = TypeCase()

if __name__ == "__main__":
    ddhf.main(
        R1KDFS,
        html_subdir="r1k_dfs",
        ddhf_topic = "Rational R1000/400 DFS Tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
