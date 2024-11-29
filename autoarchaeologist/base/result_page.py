#!/usr/bin/env python3

'''
    AutoArchaeologist Result Page
    -----------------------------

    `ResultPage` is a base-class for `Excavation` and `Artifact`
    holding the common aspects related to HTML output generation
'''

from . import interpretation

class ResultPage():
    ''' ... '''

    top = None

    def __init__(self):
        self.rp_interpretations = []
        self.unique = 0
        self.ns_roots = []

    def get_unique(self):
        ''' Return a unique (increasing) number '''
        retval = self.unique
        self.unique += 1
        return retval

    def add_interpretation(self, owner, func, more=None):
        ''' Add an interpretation '''
        self.rp_interpretations.append((owner, func, more))

    def add_utf8_interpretation(self, title, **kwargs):
        ''' Add early UTF-8 interpretation '''
        return interpretation.Utf8Interpretation(self, title, **kwargs)

    def add_html_interpretation(self, title, **kwargs):
        ''' Add early HTML interpretation '''
        return interpretation.HtmlInterpretation(self, title, **kwargs)

    def tmpfile_for(self):
        ''' create a temporary file '''
        return self.top.filename_for(
            self,
            suf=".tmp.%d" % self.get_unique(),
            temp=True
        )

    def emit_interpretations(self, fo, domore=False):
        ''' emit registered interpretations '''
        retval = False
        for _owner, func, more in self.rp_interpretations:
            if more:
                retval = True
            if domore and more is  False:
                continue
            if not domore and more is True:
                continue
            fo.write('<div>\n')
            func(fo, self)
            fo.write('</div>\n')
        return retval
