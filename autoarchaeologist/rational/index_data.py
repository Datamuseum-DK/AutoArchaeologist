
import autoarchaeologist
import html

BLACKLIST = {
    "THIS_IS_THE_ROOT_OF_A_VIEW",
    "THIS_IS_THE_ROOT_OF_A_SUBSYSTEM",
    "LAST_RELEASE_NAME",
    "SUBPATH_NAME",
    "048d6221", 	# EXPORTS = "?'spec"
    "31f20053",		# TEST'SPEC = "procedure Test;"
}

class R1K_Index_Stanza():

    def __init__(self, up, lines):
        self.up = up
        self.lines = lines.split('\n')

    def __lt__(self, other):
        return self.lines[0] < other.lines[0]

    def dump(self):
        if len(self.lines) <= 1 or len(self.lines[1]) == 0:
            return
        self.cmd = self.lines[1][0]
        self.flds = self.lines[1][1:].split("|")
        if len(self.flds) == 1:
            return
        if self.flds[4] == "SWITCH":
            return
        try:
            self.offset = int(self.flds[0], 10)
            self.length = int(self.flds[1], 10)
        except ValueError:
            return
        if self.offset >= 0 and self.length < 0 and self.offset - self.length <= len(self.up.datafile):
            self.up.slices.append((self.offset, -self.length, self))
            return
        print(self.lines[0], len(self.lines), self.cmd, self.flds)
        for i in self.lines[2:]:
            if not i:
                continue
            if i[0] == 'A' and "=>" in i:
                continue
            print("   ", i)

    def render(self):
        t = html.escape(self.lines[0]) + " " + html.escape(self.lines[1])
        return t

class R1K_Index_Data_Class():

    def __init__(self, indexfile, datafile):
        self.indexfile = indexfile
        self.datafile = datafile
        self.slices = []

        try:
            b = self.indexfile.split(b'\n', 1)[0].decode("ASCII").split()
        except UnicodeDecodeError:
            return
        if len(b) != 3 or b[0] != "***" or b[2] != "***":
            return

        self.stanzas = []
        for i in self.indexfile.decode("ASCII").split("\n!"):
            self.stanzas.append(R1K_Index_Stanza(self, i))

        for i in sorted(self.stanzas):
            i.dump()

        offset = 0
        last = None
        self.sl2 = []
        for x, y, z in sorted(self.slices):
            if offset > x:
                print("Overlap", offset, x)
                print("\t", x, y, z.lines[0])
                print("\t", last[0], last[1], last[2].lines[0])
            if offset < x:
                a = autoarchaeologist.Artifact(self.datafile, self.datafile[offset:x])
                a.add_note("Gap")
                self.sl2.append((offset, x - offset, None, a))
            offset = x + y
            last = (x,y,z)
            if y > 0:
                a = autoarchaeologist.Artifact(self.datafile, self.datafile[x:x+y])
                fn = z.lines[0].split('.')
                if fn[-1] not in BLACKLIST and a.digest[:8] not in BLACKLIST:
                    a.add_note(html.escape(z.lines[0]))
                self.sl2.append((x, y, z, a))
            else:
                print("Empty", offset, x)
                print("\t", x, y, z.lines[0])
        self.datafile.add_interpretation(self, self.html_slice)

    def html_slice(self, fo, _this):
        fo.write("<H3>DATA as INDEXED</H3>\n")
        fo.write("<pre>\n")
        offset = 0
        for x, y, z, a in sorted(self.sl2):
            assert offset == x
            fo.write("0x%06x-0x%06x " % (x, x + y))
            fo.write(a.summary())
            if z:
                 fo.write("  // " + z.render())
            fo.write("\n")
            offset = x + y
        if offset < len(self.datafile):
            fo.write("0x%06x-0x%06x\n" % (offset, len(self.datafile)))
        fo.write("</pre>\n")

def hunt_up(some, want_type):
    for i in some.parents:
        if i.has_type(want_type):
             yield i
             return
        yield from hunt_up(i, want_type)

def hunt_down(some, want_type):
    for i in some.children:
        if i.has_type(want_type):
             yield i
        yield from hunt_down(i, want_type)


class R1K_Index_Data():

    def __init__(self, this):
        if not this.has_type("R1K_tapefile"):
            return
        # print("?R1ID", this)

        mytapefile = list(hunt_up(this, "TAPE file"))
        assert len(mytapefile) == 1
        mytapefile = mytapefile[0]
        print("I am", mytapefile)

        mytape = list(hunt_up(mytapefile, "TAP tape"))
        assert len(mytape) == 1
        tape = mytape[0]

        vol=None
        filename=None
        files={}
        for i in tape.children:
            #print("  i ", i)
            for j in i.notes:
                if j[:5] == "File=":
                    filename=j[5:]
                if j[:7] == "Volume=":
                    vol=j[7:]
            j = list(hunt_down(i, "R1K_tapefile"))
            if len(j):
                assert len(j) == 1
                #print("  j", j)
                files[vol + "." + filename] = (i, j[0])

        for i, j in sorted(files.items()):
            tapefile, r1ktapefile = j
            if tapefile != mytapefile:
                continue
            if i[-6:] != ".INDEX":
                return
            #print("This is Me", r1ktapefile, r1ktapefile.types)
            x = files.get(i[:-6] + ".DATA")
            if x is None:
                print("No partner .DATA found")
                return
            #print("This is my data", x[1], x[1].types)
            R1K_Index_Data_Class(r1ktapefile, x[1])
            return
