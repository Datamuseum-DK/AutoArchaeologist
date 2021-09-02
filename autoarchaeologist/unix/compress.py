'''
   Compress(1) format
'''

import subprocess
import os
import tempfile

class Compress():

    ''' A UNIX tar(1) file '''

    def __init__(self, this):
        if len(this) <= 8:
            return
        if this[0] != 0x1f or this[1] != 0x9d:
            return

        tmpfilename = tempfile.NamedTemporaryFile().name

        open(tmpfilename + ".Z", "wb").write(this.tobytes())
        subprocess.run(["uncompress", "-f", tmpfilename + ".Z"])
        self.that = this.create(bits=open(tmpfilename, "rb").read())
        os.remove(tmpfilename)
        this.add_type("Compressed file")
        self.that.add_note("Unompressed file")
        this.add_interpretation(self, self.render)

    def render(self, fo, _this):
        ''' ... '''
        fo.write("<H3>Compress(1)'ed file</H3>\n")
        fo.write("<pre>\n")
        fo.write(self.that.summary())
        fo.write("</pre>\n")
