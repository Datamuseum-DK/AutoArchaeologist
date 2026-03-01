#!/usr/bin/env python3

'''
   MS-DOS BACKUP
   =============

   XXX: Add proper multivolume support
'''

from ...base import octetview as ov
from ...base import namespace

class Head(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            next_=1,            # Length of struct
            magic_=ov.Text(8),
            vol_=ov.Octet,
            pad__=0x8b - 0xa,
        )

class Dir(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            next_=1,            # Length of struct
            fname_=ov.Text(63, rstrip=True),
            nent_=ov.Le16,      # Number of files
            ptrnxt_=ov.Le32,    # Offset of next dir
            more=True,
        )
        self.add_field(
            "files",
            ov.Array(self.nent.val, File, vertical=True),
        )
        self.done()

    def commit(self):
        l = list(x.offset.val for x in self.files)
        l.append(len(self.tree.backup))
        l.pop(0)
        for fil, end in zip(self.files, l):
            fil.commit(self, end)

class File(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            #vertical=True,
            next_=1,            # Length of struct
            fname_=ov.Text(12, rstrip=True),
            flag_=1,            # Flag of some sort (segmentation ?)
            size_=ov.Le32,      # Size
            seq_=ov.Le16,       # Sequence
            offset_=ov.Le32,    # Offset in BACKUP.%03d
            saved_=ov.Le32,     # Length in BACKUP.%03d
            attr_=1,            # File Attributes
            flag2_=1,           # Unknown
            time_=ov.Le16,      # Time
            date_=ov.Le16,      # Date
            more=True,
        )
        self.done(-34)

    def commit(self, pdir, end):
        if pdir.fname.txt:
            fname = pdir.fname.txt + "/" + self.fname.txt
        else:
            fname = self.fname.txt
        if self.seq.val > 1 or self.saved.val != self.size.val:
            fname += "_part_%02d" % self.seq.val
        if self.seq.val == 1:
            that = self.tree.backup.create(
                start=self.offset.val,
                stop=self.offset.val + self.saved.val,
            )
        else:
            that = self.tree.backup.create(
                start=self.offset.val,
                stop=end,
            )
        self.ns = NameSpace(
            name = fname,
            parent = self.tree.ns,
            priv = self,
            this = that,
        )


class NameSpace(namespace.NameSpace):
    ''' ... '''

    KIND = "MSDOS BACKUP.EXE volume"

class MsDosBackup(ov.OctetView):
    ''' BACKUP files '''

    def __init__(self, this):

        if this[:9] != b'\x8bBACKUP  ':
            return
        this.control = None
        for n in this.names:
            if n[:8].lower() == "control.":
                this.control = n
                break
        if not this.control:
            return
        bnam = "BACKUP." + this.control.split('.')[1]
        self.backup = None
        for name_space in this.namespaces:
            for i in name_space.ns_lookup(bnam):
                if i.ns_this:
                    self.backup = i.ns_this
                    break
        if not self.backup:
            return
        print(this, self.__class__.__name__, this.control, bnam, self.backup)
        super().__init__(this)
        this.add_note("MSDOS_Backup")

        self.head = Head(self, 0).insert()
        self.dirs = []
        adr = self.head.hi
        while adr < self.hi:
            y = Dir(self, adr).insert()
            self.dirs.append(y)
            adr = y.hi

        self.ns = NameSpace(
            name = '',
            separator = '',
            root = name_space.ns_root
        )

        for dir in self.dirs:
            dir.commit()

        self.add_interpretation()
        name_space.ns_root.add_interpretation(self, self.ns.ns_html_plain)
