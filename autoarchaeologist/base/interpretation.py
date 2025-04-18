#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    Interpretations
    ---------------

'''

import os
import html


class HtmlInterpretation():
    '''
       Some examinations can output a HTML representation during
       the examination and we can save VM by storing it in a temporary
       file.

       It is important that the HTML does not contain any links to
       other artifacts, as those may not have been fully examined yet.

       Using Pythons tempfile does not work, because the open file(handle)
       hangs around.
    '''

    def __init__(self, this, title, more=None):
        self.this = this
        self.title = title
        self.filename = this.tmpfile_for().filename
        with open(self.filename, 'w', encoding="utf8") as file:
            file.write("Content generation probably failed\n")
        self.file = None
        this.add_interpretation(self, self.html_interpretation, more=more)

    def __enter__(self):
        self.file = open(self.filename, 'w', encoding="utf8")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        self.file = None

    def __del__(self):
        os.remove(self.filename)

    def write(self, *args, **kwargs):
        ''' ... '''
        if self.file is None:
            raise SyntaxError("Not inside with … as …:")
        self.file.write(*args, **kwargs)

    def html_interpretation(self, fo, _this):
        ''' ... '''
        with open(self.filename, encoding="utf8") as file:
            fo.write("<H3>" + self.title + "</H3>\n")
            for i in file:
                fo.write(i)

class Utf8Interpretation(HtmlInterpretation):
    '''
       Some examinations can output a UTF8 representation during
       the examination and we can save VM by storing it in a temporary
       file.

       The UTF8 is html.escape()'d and wrapped in a <pre>

       Using Pythons tempfile does not work, because the open file(handle)
       hangs around.
    '''

    def html_interpretation(self, fo, _this):
        ''' ... '''
        with open(self.filename, encoding="utf8") as file:
            fo.write("<H3>" + self.title + "</H3>\n")
            fo.write("<pre>\n")
            for i in file:
                fo.write(html.escape(i))
            fo.write("</pre>\n")
