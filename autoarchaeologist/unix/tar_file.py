'''
   TAR(1) format
'''

from .. import namespace
from . import unix_stat

class Invalid(Exception):
    ''' invalid tar file '''

class NameSpace(namespace.NameSpace):
    ''' ... '''

    KIND = "Tar file"

    TABLE = (
        ("l", "mode"),
        ("r", "link"),
        ("r", "uid"),
        ("r", "gid"),
        ("r", "size"),
        ("l", "mtime"),
        ("l", "name"),
        ("l", "artifact"),
    )

    stat = unix_stat.UnixStat()

    def ns_render(self):
        if self.ns_name[-1] == '/':
            sfmt = "d"
        else:
            sfmt = "-"
        return [
            sfmt + self.stat.mode_bits(self.ns_priv.mode),
            self.ns_priv.link,
            self.ns_priv.uid,
            self.ns_priv.gid,
            self.ns_priv.size,
            self.stat.timestamp(self.ns_priv.mtime),
        ] + super().ns_render()

class TarEntry():
    ''' One tar(1) file entry '''

    def __init__(self, up, that, offset):
        self.up = up
        self.hdr = that[offset:offset+512].tobytes()
        self.parse_header()
        self.filename = that.type_case.decode(self.filename)
        self.namespace = NameSpace(
            name = self.filename,
            parent = up.namespace,
            separator = "",
            priv = self,
        )
        if self.target:
            self.target = that.type_case.decode(self.target)
        hdrchild = that.create(start=offset, stop=offset + 512)
        hdrchild.by_class[TarFile] = that
        if self.link == 0 and self.size:
            self.this = that.create(start=offset + 512, stop=offset + 512 + self.size)
            # self.this.set_name(self.filename)
            self.namespace.ns_set_this(self.this)
        else:
            self.this = None
        if self.link:
            self.size = 0
        self.next = offset + 512 * (1 + (self.size + 511) // 512)

    def parse_header(self):
        ''' Parse the tar header '''
        self.csum = self.oct(148, 8)
        if self.csum != sum(self.hdr[:148]) + sum(self.hdr[156:]) + 8 * 32:
            raise Invalid("Checsum does not match")
        self.filename = self.hdr[:100].split(b'\x00')[0]
        self.link = self.oct(156, 1)
        self.mode = 0
        self.uid = 0
        self.gid = 0
        self.size = 0
        self.mtime = 0
        try:
            self.mode = self.oct(100, 8)
            self.uid = self.oct(108, 8)
            self.gid = self.oct(116, 8)
            self.size = self.oct(124, 12)
            self.mtime = self.oct(136, 12)
        except Invalid:
            if not self.link:
                raise
        if self.link:
            self.target = self.hdr[157:257].split(b'\x00')[0]
        else:
            self.target = None

    def oct(self, offset, width):
        ''' Return numeric value of octal field '''
        try:
            retval = self.hdr[offset:offset + width]
            retval = retval.split(b'\x00')[0]
            retval = retval.decode('ascii')
            if len(retval) == 0:
                return 0
            retval = int(retval, 8)
            return retval
        except:
            raise Invalid(
                "Bad octal field [%d:%d] %s" % (
                    offset,
                    offset + width,
                    str(self.hdr[offset:offset + width]
                    )
                )
            )

class TarFile():

    ''' A UNIX tar(1) file '''

    def __init__(self, this):
        if len(this) <= 512:
            return
        if TarFile in [*this.parents][0].by_class:
            return
        self.namespace = NameSpace(
            name = "",
            separator = "",
            root = this,
        )
        try:
            entry = TarEntry(self, this, 0)
        except Invalid as e:
            # print("TAR", this, e)
            return
        self.children = [entry]
        this.type = "Tar_file"
        this.add_note("Tar_file")
        while entry.next < len(this) and this[entry.next]:
            entry = TarEntry(self, this, entry.next)
            self.children.append(entry)
        this.add_interpretation(self, self.namespace.ns_html_plain)
        this.taken = True
