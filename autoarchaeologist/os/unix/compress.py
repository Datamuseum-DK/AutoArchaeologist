#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Compress(1) format
'''

import subprocess
import os
import tempfile

class Compress():

    ''' A compress(1)'ed file '''

    def __init__(self, this):
        if len(this) <= 8:
            return
        if this[0] != 0x1f or this[1] != 0x9d:
            return

        tmpfilename = tempfile.NamedTemporaryFile().name

        open(tmpfilename, "wb").write(this.tobytes())
        s = subprocess.run(
            [ "uncompress", "-f" ],
            stdin=open(tmpfilename, "rb"),
            capture_output=True
        )
        self.that = this.create(octets=s.stdout)
        os.remove(tmpfilename)
        this.add_type("Compressed file")
        self.that.add_note("Uncompressed file")
        if s.stderr:
            self.that.add_note("Uncompression error: " + s.stderr.decode('utf-8'))
        this.add_interpretation(self, this.html_interpretation_children)
