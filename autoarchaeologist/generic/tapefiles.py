#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Split unloved tapes into individual artifacts
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from ..base import namespace

class UnlovedTapes():

    ''' Split unloved tapes into individual artifacts '''

    def __init__(self, this):
        if not this.has_type("SimhTapContainer"):
            return
        if this.rp_interpretations:
            return
        print(this, self.__class__.__name__, len(this.rp_interpretations))
        self.this = this
        start = None
        recs = []
        nf = 0
        self.ns = namespace.NameSpace(name = '', root=this, separator='')
        for rec in this.iter_rec():
            if start is None:
                start = rec
                recs = [ rec ]
            elif rec.key[0] != start.key[0]:
                self.mkchild(recs)
                start = rec
                recs = [ rec ]
                nf += 1
            else:
                recs.append(rec)
        if recs and recs[0].lo > 0:
            self.mkchild(recs)
        if this.children:
            this.add_interpretation(self, self.ns.ns_html_plain)
            this.taken = True

    def mkchild(self, recs):
        ''' Complete one child artifact '''
        print(self.this, "tapefile", recs[0], recs[-1])
        that = self.this.create(records = recs)
        that.add_type("Tapefile")
        rs = set(len(r) for r in recs)
        that.add_note("%d*%s" % (len(recs), str(rs)))
        namespace.NameSpace(
            name = "%04d" % recs[0].key[0],
            parent = self.ns,
            this = that,
        )
