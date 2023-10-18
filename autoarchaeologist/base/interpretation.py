#!/usr/bin/env python3

'''
    Interpretations
    ---------------

'''

import os
import html

class Utf8Interpretation():
    '''
       Some examinations can output a HTML representation during
       the examination and we can save VM by storing it in a temporary
       file.

       Using Pythons tempfile does not work, because the file(handle)
       hangs around.
    '''

    def __init__(self, this, title):
        self.this = this
        self.title = title
        self.filename = this.tmpfile_for().filename
        this.add_interpretation(self, self.html_interpretation)

    def html_interpretation(self, fo, this):
        try:
            fi = open(self.filename)
        except FileNotFoundError as err:
            print(this, "Could not open output file:", err)
            return
        fo.write("<H3>" + self.title + "</H3>\n")
        fo.write("<pre>\n")
        for i in fi:
            fo.write(html.escape(i))
        os.remove(self.filename)


class HtmlInterpretation():
    '''
       Some examinations can output a HTML representation during
       the examination and we can save VM by storing it in a temporary
       file.

       It is important that the HTML does not contain any links to
       other artifacts, as those may not have been fully examined yet.

       Using Pythons tempfile does not work, because the file(handle)
       hangs around.
    '''

    def __init__(self, this, title):
        self.this = this
        self.title = title
        self.filename = this.tmpfile_for().filename
        this.add_interpretation(self, self.html_interpretation)

    def html_interpretation(self, fo, this):
        try:
            fi = open(self.filename)
        except FileNotFoundError as err:
            print(this, "Could not open output file:", err)
            return
        fo.write("<H3>" + self.title + "</H3>\n")
        for i in fi:
            fo.write(i)
        os.remove(self.filename)
