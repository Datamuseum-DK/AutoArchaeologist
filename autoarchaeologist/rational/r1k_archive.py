
import html

from ..base import namespace
from ..base import octetview as ov

class NameSpace(namespace.NameSpace):
    def __init__(self, **kwargs):
        kwargs['separator'] = "."
        super().__init__(**kwargs)
        self.lines = []

    def more_lines(self, lines):
        ''' ... '''
        for i in lines:
            if i not in self.lines:
                self.lines.append(i)

class R1K_Archive_Pair():

    def __init__(self, index, data):

        self.indexfile = index
        self.datafile = data
        self.datatree = ov.OctetView(self.datafile)

        # This is semi-evil...
        index.interpretations = []
        data.interpretations = []
        index.taken = self
        data.taken = self

        try:
            b = self.indexfile.tobytes().split(b'\n', 1)[0].decode("ASCII").split()
        except UnicodeDecodeError:
            return
        if len(b) != 3 or b[0] != "***" or b[2] != "***":
            return

        self.datafile.add_interpretation(self, self.html_partner)
        self.indexfile.add_interpretation(self, self.html_partner)

        self.indexfile.namespace = namespace.NameSpace(
            name = "",
            separator = "",
            root = self.indexfile
        )
        self.indexfile.add_interpretation(self, self.indexfile.namespace.ns_html_plain)

        tf1 = self.indexfile.add_utf8_interpretation('FOO')
        with open(tf1.filename, "w", encoding="utf-8") as file:
            self.parse_index(file, self.indexfile.tobytes().decode("ASCII").split("\n"))

        for i, j in self.datatree.gaps():
            print(self.datafile, "GAP", j - i, i, j)
        self.datatree.add_interpretation()

    def html_partner(self, fo, _this):
        fo.write("<H3>ARCHIVE PAIR</H3>\n")
        fo.write("<pre>\n")
        fo.write("INDEX: " + self.indexfile.summary() + "\n")
        fo.write("DATA:  " + self.datafile.summary() + "\n")
        fo.write("</pre>\n")

    def parse_index(self, file, lines):
        self.file = file
        self.lines = lines
        self.file.write("MAGIC " + self.lines.pop(0) + '\n')
        self.file.write("PATTERN " + self.lines.pop(0) + '\n')
        while self.lines:
            if self.lines[0] == '':
                self.lines.pop(0)
                continue
            if self.lines[0][:1] != '!':
                print(self.indexfile, "BAD", self.lines[0])
                self.file.write("BAD »" + self.lines[0] + "«\n")
                self.lines.pop(0)
                continue
            self.path = self.lines.pop(0)
            self.ns = self.indexfile.namespace.ns_find(names=self.path[1:].split('.'), cls=NameSpace)
            if not self.lines:
                break
            nxt = self.lines[0]
            if nxt[:1] == "!":
                continue
            if nxt[:2] == "A|":
                self.do_a()
                continue
            if nxt[:1] == "B" and nxt[1:2].isdigit():
                self.do_bnum()
                continue
            if nxt[:1] == "D":
                self.do_dnum()
                continue
            if nxt[:1] == "E" and nxt[1:2].isdigit():
                self.do_enum()
                continue
            if nxt[:1] == "F":
                self.do_fnum()
                continue
            if nxt[:1] == "G":
                self.do_gnum()
                continue
            if nxt[:2] == "H|":
                self.do_h()
                continue
            if nxt[:2] == "I|":
                self.do_i()
                continue
            if nxt[:1] == "J" and nxt[1:2].isdigit():
                self.do_jnum()
                continue
            if nxt == "K":
                self.do_k()
                continue
            if nxt[:1] == "L":
                self.do_lnum()
                continue
            if nxt[:2] == "N|":
                self.do_n()
                continue
            if nxt[:2] == "O|":
                self.do_o()
                continue
            if nxt[:1] == "P" and nxt[1:2].isdigit():
                self.do_pnum()
                continue
            if nxt[:1] == "Q" and nxt[1:2].isdigit():
                self.do_qnum()
                continue
            if nxt[:2] == "U|":
                self.do_u()
                continue
            if nxt[:2] == "V|":
                self.do_v()
                continue
            if nxt[:1] == "V" and nxt[1:2].isdigit():
                self.do_vnum()
                continue
            if nxt[:2] == "W|":
                self.do_w()
                continue
            if nxt == "Y":
                self.do_y()
                continue
            if nxt[:1] in "0123456789":
                self.do_num()
                continue
            print(self.indexfile, "PATH", self.path)
            print(self.indexfile, "NXT", self.lines[0])
            file.write("PATH " + self.path + "\n")
            file.write("NXT »" + nxt + "«\n")

    def what(self, a, b):
        self.file.write(a + " " + b + "\n")

    def pop(self, _n=None):
        i = self.lines.pop(0)
        self.file.write("   »" + i + "«\n")
        return i

    def GenericNum(self, line):
        if line[0] != "F":
            ns = self.ns.ns_find([line[0]], cls=NameSpace)
        else:
            ns = self.ns
        i = line[1:].split('|')
        if i[0]:
            low = int(i[0])
        else:
            low = 0
        if i[1]:
            width = int(i[1])
            if width < 0:
                width = -width
            else:
                width = (width + 7) // 8
            if ns.ns_this:
                that = ov.Opaque(self.datatree, lo = low, width = width).insert()
                self.file.write('   ⇒ ' + str(ns.ns_this) + ' (DUP)\n')
            else:
                that = ov.This(self.datatree, lo = low, width = width).insert()
                ns.ns_set_this(that.that)
                self.file.write('   ⇒ ' + str(that.this) + '\n')
        self.pop(0)

    def do_a(self):
        self.what("A ", self.path)
        self.pop(0)
        self.pop(0)
        self.file.write('   ')
        while self.lines[0] != '' or self.lines[1] != '' or self.lines[2] != '':
            self.file.write('.')
            self.lines.pop(0)
        self.file.write('\n')

    def do_bnum(self):
        self.what("B#", self.path)
        self.GenericNum(self.pop())

    def do_dnum(self):
        self.what("D#", self.path)
        self.GenericNum(self.pop())

    def do_enum(self):
        self.what("E#", self.path)
        self.GenericNum(self.pop())

    def do_fnum(self):
        self.what("F#", self.path)
        self.GenericNum(self.pop())

    def do_gnum(self):
        self.what("G#", self.path)
        self.GenericNum(self.pop())

    def do_h(self):
        self.what("H ", self.path)
        self.pop(0)
        self.pop(0)
        self.file.write('   ')
        while self.lines[0] != '':
            self.file.write('.')
            self.lines.pop(0)
            self.lines.pop(0)
        self.file.write('\n')
        self.pop(0)

    def do_i(self):
        self.what("I ", self.path)
        self.pop(0)
        self.pop(0)
        self.file.write('   ')
        while self.lines[0] != '':
            self.file.write('.')
            self.lines.pop(0)
            self.lines.pop(0)
        self.file.write('\n')
        self.pop(0)

    def do_jnum(self):
        self.what("J#", self.path)
        self.GenericNum(self.pop())

    def do_k(self):
        self.what("K ", self.path)
        self.pop(0)
        self.pop(0)

    def do_lnum(self):
        self.what("L#", self.path)
        self.GenericNum(self.pop())

    def do_n(self):
        self.what("N ", self.path)
        self.pop(0)
        self.pop(0)

    def do_o(self):
        self.what("O ", self.path)
        self.pop(0)
        self.pop(0)
        while self.lines[0] != '':
            self.pop(0)
        self.pop(0)

    def do_pnum(self):
        self.what("P#", self.path)
        self.GenericNum(self.pop())

    def do_qnum(self):
        self.what("Q#", self.path)
        self.GenericNum(self.pop())

    def do_u(self):
        self.what("U ", self.path)
        self.pop(0)
        self.pop(0)
        self.pop(0)

    def do_v(self):
        self.what("V ", self.path)
        self.GenericNum(self.pop())

    def do_vnum(self):
        self.what("V#", self.path)
        self.GenericNum(self.pop())

    def do_w(self):
        self.what("W ", self.path)
        self.pop(0)
        self.pop(0)

    def do_y(self):
        self.what("Y ", self.path)
        self.pop(0)
        self.pop(0)
        self.file.write('   ')
        while self.lines[0] != '':
            self.file.write('.')
            self.lines.pop(0)
            self.lines.pop(0)
        self.file.write('\n')

    def do_num(self):
        self.what(self.lines[0][0] + "#", self.path)
        self.GenericNum(self.pop())

class R1K_Archive():
    '''
       R1K archives consisting of pairs of *INDEX and *DATA files. 
    '''

    def __init__(self, this):
        for index, data in self.find_index_data_pairs(this):
            if index is None and data is None:
                continue
            if index is None:
                print("R1K_Archive", "DATA", data, "has no matching INDEX")
                continue
            if data is None:
                print("R1K_Archive", "INDEX", index, "has no matching DATA")
                continue
            if index.has_type("R1K_ARCHIVE_INDEX"):
                continue
            if data.has_type("R1K_ARCHIVE_DATA"):
                continue
            index.add_type("R1K_ARCHIVE_INDEX")
            data.add_type("R1K_ARCHIVE_DATA")
            print(self.__class__.__name__, index, data)
            R1K_Archive_Pair(index, data)

    def find_index_data_pairs(self, this):
        ''' Find INDEX+DATA pairs '''
        for spaces in this.namespaces.values():
            for names in spaces:
                if names.ns_name[-5:] != "INDEX":
                    continue
                assert names.ns_this == this
                pfx = names.ns_name[:-5]
                data = [x for x in names.ns_lookup_peer(pfx + "DATA")]
                if len(data) != 1:
                    return
                index = names.ns_this
                data = data[0].ns_this
                yield index, data
