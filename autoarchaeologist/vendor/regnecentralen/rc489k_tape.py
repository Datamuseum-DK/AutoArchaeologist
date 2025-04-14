#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC4000/RC8000/RC9000 VOL1 labeled tapes 
   ---------------------------------------

'''

from . import rc489k_tape_dump
from . import rc489k_tape_save

class Rc489kTape():
    ''' General RC489K tape handler - splits tape into tape files '''

    def __init__(self, this):
        if not this.top in this.parents:
            return

        self.this = this
        self.recs = []
        self.label = None

        for rec in this.iter_rec():
            if rec.key == (0, 0):
                if rec[:4] != b'VOL1':
                    return
                print(this, self.__class__.__name__)
                self.label = rec
                continue
            if not self.label:
                return
            if rec.key[1] == 0:
                self.proc_recs()
            self.recs.append(rec)
        if not self.label:
            return
        self.proc_recs()
        if self.label:
            this.add_interpretation(self, self.label_interpretation)
        this.add_interpretation(self, this.html_interpretation_children)

    def proc_recs(self):
        if len(self.recs) > 0:
            that = self.this.create(
                start = self.recs[0].lo,
                stop = self.recs[-1].hi,
                records = self.recs,
            )
            that.add_type("Rc489k_TapeFile")
        self.recs = []

    def label_interpretation(self, file, _this):
        file.write("<H3>Label</H3>\n")
        file.write("<pre>\n")
        file.write(str(bytes(self.label)) + "\n")
        file.write("</pre>\n")

examiners = (
    Rc489kTape,
    rc489k_tape_dump.Rc489kDumpTapeFile,
    rc489k_tape_save.Rc489kSaveTapeFile,
)
