'''
    TAP files
    ---------

    Break SIMH-TAP files (http://simh.trailing-edge.com/docs/simh_magtape.pdf) into
    tape files, and those tape-files into records.
'''
import struct

import autoarchaeologist

class TAPtapefile():
    '''
        A Single tape file
    '''

    def __init__(self, this):
        self.this = this
        self.recs = []
        self.rls = []

    def iter_recs(self):
        ''' build payload from record posistions '''
        this = bytearray()
        for a, b in self.recs:
            this += self.this[a:a + b]
        return this

    def commit(self):
        ''' Slice out our part, and build record-ified sub-artifact '''
        if not self.recs:
            return
        idx0 = self.recs[0][0] - 4
        idxn = sum(self.recs[-1]) + 4
        this = self.this.slice(idx0, idxn - idx0)
        this.add_note("TAP tapefile")

        that = autoarchaeologist.Artifact(this, self.iter_recs())
        that.records = [y for x, y in self.recs]

        for _i, j in self.recs:
            if not self.rls or j != self.rls[-1][0]:
                self.rls.append([j, 0])
            self.rls[-1][1] += 1

        this.add_interpretation(self, self.html_interpretation)

        txt = "+".join(["%d*%d" % (y,x) for x,y in self.rls])
        that.add_note("TAP file records (%s)" % txt)

    def html_interpretation(self, fo, _this):
        ''' Render block-list summary '''
        fo.write("<H3>TAP file</H3>\n")
        fo.write("<pre>\n")
        for i, j in self.rls:
            fo.write("%d records of %d bytes\n" % (j, i))
        fo.write("</pre>\n")

class TAPfile():
    '''
       SIMH TAP format
       ---------------

       Split into tape-files, and split those into tape-records
    '''

    def __init__(self, this):

        if this.has_note("TAP tapefile") or this.has_note("TAP tape"):
            return

        self.files = []

        i = 0
        self.files.append(TAPtapefile(this))
        while i + 4 <= len(this):
            j = i

            preword = struct.unpack("<L", this[i:i+4])[0]
            i += 4

            if preword == 0xffffffff:
                break

            if preword > 128*1024:
                if j:
                    print(this, "TAP Preposterous blocksize", preword)
                return

            if not preword:
                if self.files[-1].recs:
                    self.files.append(TAPtapefile(this))
                continue

            i += preword + (preword & 1)

            if i + 4 > len(this):
                if j:
                    print("TAP Ran out of data", j, i, preword, this)
                return

            postword = struct.unpack("<L", this[i:i+4])[0]
            i += 4
            if preword != postword:
                if j:
                    print("TAP pre/post-word mismatch at 0x%x (0x%x/0x%x)" % (i, preword, postword))
                return

            self.files[-1].recs.append([j + 4, preword])

        if not self.files[-1].recs:
            self.files.pop(-1)
        if not self.files:
            return
        for i in self.files:
            i.commit()
        this.add_note("TAP tape")
