#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   WANG WPS text-files
   ===================

   Reverse-engineered from samples.

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor.wang import wang_text
       …
       self.add_examiner(*wang_text.ALL)

   Notes
   -----

   Test input
   ----------

   * CR/CR80/DOCS

   Documentation
   -------------

   None found.

'''

from ...base import type_case

class WangTypeCase(type_case.WellKnown):
    ''' ... '''

    def __init__(self, encoding):
        super().__init__(encoding)
        for i in range(0x20, 0x7f):
            self.set_slug(
                i | 0x80,
                self[i].short,
                "\u0332" + self[i].long,
            )

class WangText():
    ''' ... '''

    def __init__(self, this):
        if not this.has_type("Wang Wps File"):
            return
        self.this = this
        tn = this.add_html_interpretation('WangText')
        tabs = bytes()
        linelen = 80
        curtab = 0
        with open(tn.filename, "w", encoding="utf-8") as file:
            for line in self.iter_lines():
                if len(line) == 0:
                    file.write("<br/>\n")
                    continue
                pos = 0
                curtab = 0
                if line[0] in (0x06, 0x86):
                    if line[0] == 0x86:
                        file.write("<hr/><br/>\n")
                    # print("LL", hex(line[0]), line[1], len(line), [line])
                    tabs = line[2:]
                    try:
                        linelen = line[1] + tabs.find(b'\x02')
                    except Exception as err:
                        print(this, "WANTTEXT", "linelen", err)
                    if False:
                        for i in tabs:
                            if i == 0x20:
                                file.write("-")
                            elif i == 0x02:
                                file.write("|")
                            else:
                                file.write("…%02x…" % i)
                        file.write("[0x%02x]" % linelen)
                        file.write("<br/>\n")
                    continue
                if line[0] in (0x01,):
                    width = len(line[1:])
                    pos = (linelen - width) // 2
                    file.write("&nbsp;" * pos)
                    line = line[1:]
                for char in line:
                    if char in (0xa0, 0x20) and pos > linelen:
                        file.write("<br/>\n")
                        file.write("&nbsp;" * (curtab - 1))
                        pos = curtab - 1
                    if 0xa0 == char:
                        file.write("&nbsp;\u0332")
                        pos += 1
                    elif 0xa0 <= char <= 0xfe:
                        if char == 0xbc:
                            file.write("&lt;")
                        else:
                            file.write("%c" % (char & 0x7f))
                        file.write('\u0332')
                        pos += 1
                    elif 0x20 == char:
                        file.write("&nbsp;")
                        pos += 1
                    elif 0x20 < char <= 0x7e:
                        file.write("%c" % char)
                        pos += 1
                    elif char == 4:
                        file.write("&nbsp;")
                        pos += 1
                        while tabs[pos:pos+1] not in (b'', b'\x02'):
                            file.write("&nbsp;")
                            pos += 1
                        curtab = pos
                    else:
                        file.write("…%02x…" % char)
                file.write("<br/>\n")

    def iter_lines(self):
        ''' ... '''

        b = bytes()
        for chunk in self.this.iter_chunks():
            lines = chunk.tobytes().split(b'\x03')
            if len(lines) == 1:
                b = b + lines[0]
            else:
                yield b + lines[0]
                if len(lines) > 2:
                    yield from lines[1:-1]
                b = lines[-1]
        yield b

ALL = [
    WangText,
]
