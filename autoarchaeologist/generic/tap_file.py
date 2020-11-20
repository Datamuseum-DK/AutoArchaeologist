'''
    TAP files
    ---------

    SIMH-TAP files (http://simh.trailing-edge.com/docs/simh_magtape.pdf)
'''

import struct

class TapeFile():

    ''' One data file on the tape '''

    def __init__(self, this):
        self.this = this
        self.records = []
        self.sizes = []

    def add_record(self, start, stop):
        self.sizes.append(stop-start)
        self.records.append(self.this[start:stop])

    def commit(self, parent):
        ''' Register the artifact '''
        self.a = parent.create(
            start=self.records[0][0] - 4,
            stop=self.records[-1][1] + 4,
            records=self.records
        )
        self.a.add_type("TAPE file")

    def __str__(self):
        return "<TF " + str(self.records) + ">"

    def html_summary(self):
        ''' Summary of block-sizes'''
        summ = [[self.sizes[0], 0]]
        for i in self.sizes:
            if summ[-1][0] != i:
                summ.append([i, 1])
            else:
                summ[-1][1] += 1
        summ = " + ".join(["0x%x*0x%x" % (y,x) for x,y in summ])
        return self.a.summary() + " // [" + summ + "]"

class TAPfile():
    '''
       SIMH TAP format
       ---------------

       Split into tape-files with record info
    '''

    def __init__(self, this):

        if this.has_type("TAP tape"):
            return

        # We only allow TAP on top-level artifacts
        if not this.top in this.parents:
            return

        self.parts = []

        i = 0
        while i + 4 <= len(this):
            preword = struct.unpack("<L", this[i:i+4])[0]
            i += 4

            if preword == 0xffffffff:
                self.parts.append(preword)
                break

            if not preword:
                self.parts.append(preword)
                continue

            if preword > 128*1024:
                if self.parts:
                    print(this, "TAP Preposterous blocksize", preword)
                return

            if not self.parts or not isinstance(self.parts[-1], TapeFile):
                self.parts.append(TapeFile(this))

            self.parts[-1].add_record(i, i + preword)

            i += preword + (preword & 1)

            if i + 4 > len(this):
                if self.parts:
                    print("TAP Ran out of data", i, preword, this)
                return

            postword = struct.unpack("<L", this[i:i+4])[0]
            i += 4
            if preword != postword:
                if self.parts:
                    print("TAP pre/post-word mismatch at 0x%x (0x%x/0x%x)" % (i, preword, postword))
                return

        this.add_type("TAP tape")
        for i in self.parts:
            if isinstance(i, TapeFile):
                i.commit(this)
        this.add_interpretation(self, self.html_tap_index)

    def html_tap_index(self, fo, _this):
        ''' Listing of tape files and marks '''
        fo.write("<H4>TAP file contents</H4>\n")
        fo.write("<pre>\n")
        for i in self.parts:
            if isinstance(i, TapeFile):
                fo.write("    " + i.html_summary() + "\n")
            elif not i:
                fo.write("    tape-mark\n")
            elif i == 0xffffffff:
                fo.write("    end-of-medium\n")
            else:
                fo.write("    0x%08x\n" % i)
        fo.write("<pre>\n")
