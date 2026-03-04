#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Word Perfect files
   ==================

'''

import subprocess

class WordPerfect():
    ''' ... '''

    def __init__(self, this):

        if bytes(this[:4]) != b'\xff\x57\x50\x43':
            return

        if this[9] != 0x0a:
            this.add_note("WordPerfect-New")
            return

        open("/tmp/_.wpd", "wb").write(bytes(this))
        sp = subprocess.run(
            [ "wpd2html", "/tmp/_.wpd" ],
            capture_output=True,
            check=False,
        )
        if sp.returncode != 0:
            print(this, "WPB", bytes(this[:16]).hex(), this[9], sp.stderr)
            return
        with this.add_html_interpretation('Word Perfect') as out:
            out.write('<div>\n')
            out.write(sp.stdout.decode('utf8'))
            out.write('</div>\n')
        this.add_note("WordPerfect")
