'''
   UNIX v7 style filesystem
   ------------------------

   Quite, but probably not sufficiently configurable by subclassing.

'''

import struct
import time

import autoarchaeologist

def swap_words(x):
    ''' swap two halves of a 32 bit word '''
    return (x >> 16) | ((x & 0xffff) << 16)

class Struct():
    ''' Brute force data-container class '''
    def __init__(self, **kwargs):
        self.__v = kwargs
        for i, j in kwargs.items():
            setattr(self, i, j)

    def __str__(self):
        return "<S "+", ".join([i+"="+str(j) for i,j in self.__v.items()])+">"

class Dinode(Struct):
    ''' Disk Inode (as opposed to in-core inodes)'''

    def __init__(self, fs, di_inum, **kwargs):
        self.fs = fs
        self.di_inum = di_inum
        super().__init__(**kwargs)
        self.di_type = self.di_mode & self.fs.S_ISFMT

    def __iter__(self):
        assert self.di_type in (self.fs.S_IFDIR, self.fs.S_IFREG), self
        block_no = 0
        yet = self.di_size
        while yet:
            b = self.fs.inode_get_block(self, block_no)
            assert len(b) > 0, (str(self))
            if yet < self.fs.SECTOR_SIZE:
                b = b[:yet]
            yield b
            yet -= len(b)
            block_no += 1

    def __str__(self):
        txt = "%5d" % self.di_inum

        typ = {
            self.fs.S_IFPIP: "p",
            self.fs.S_IFCHR: "c",
            self.fs.S_IFDIR: "d",
            self.fs.S_IFBLK: "b",
            self.fs.S_IFREG: "-",
        }.get(self.di_type)

        mode = self.di_mode

        if typ is None:
            txt += " %10o" % mode
        elif not mode & self.fs.S_IXUSR and mode & self.fs.S_ISUID:
            txt += " %10o" % mode
        elif not mode & self.fs.S_IXGRP and mode & self.fs.S_ISGID:
            txt += " %10o" % mode
        else:
            txt += " " + typ
            txt += "r" if mode & self.fs.S_IRUSR else '-'
            txt += "w" if mode & self.fs.S_IWUSR else '-'
            if mode & self.fs.S_IXUSR and mode & self.fs.S_ISUID:
                txt += "s"
            elif mode & self.fs.S_IXUSR:
                txt += "x"
            else:
                txt += "-"
            txt += "r" if mode & self.fs.S_IRGRP else '-'
            txt += "w" if mode & self.fs.S_IWGRP else '-'
            if mode & self.fs.S_IXGRP and mode & self.fs.S_ISGID:
                txt += "s"
            elif mode & self.fs.S_IXUSR:
                txt += "x"
            else:
                txt += "-"
            txt += "r" if mode & self.fs.S_IROTH else '-'
            txt += "w" if mode & self.fs.S_IWOTH else '-'
            if mode & self.fs.S_ISVTX and mode & self.fs.S_IXOTH:
                txt += "t"
            elif mode & self.fs.S_ISVTX:
                txt += "T"
            else:
                txt += "-"

        txt += " %4d" % self.di_nlink
        txt += " %5d" % self.di_uid
        txt += " %5d" % self.di_gid
        txt += " %8d" % self.di_size
        mtime = time.gmtime(self.di_mtime)
        txt += time.strftime(" %Y-%m-%dT%H:%M:%SZ", mtime)
        return txt

class DirEnt():
    ''' A directory entry '''
    def __init__(self, fs, path, name, inum):
        self.fs = fs
        self.path = path
        self.name = name
        self.inum = inum
        self.subdir = None
        self.artifact = None
        if self.fs.valid_inum(inum):
            self.fs.inode_is[inum] = self
            self.inode = self.fs.read_inode(inum)
        else:
            self.inode = None

    def __lt__(self, other):
        return self.name < other.name

    def commit_file(self):
        ''' Create artifact, if possible '''
        if not self.inode:
            return
        if self.inode.di_type == self.fs.S_IFREG and self.inode.di_size:
            b = bytes()
            for i in self.inode:
                b += i
            self.artifact = autoarchaeologist.Artifact(self.fs.this, b)
            self.artifact.add_note("UNIX file")
            try:
                self.artifact.set_name(self.path)
            except autoarchaeologist.core_classes.DuplicateName:
                self.artifact.add_note(self.path)

class Directory():
    ''' A directory '''
    def __init__(self, fs, path, inode):
        self.fs = fs
        self.path = path
        self.inode = inode
        self.dirents = []

        for i in self.inode:
            for j in range(0, len(i), 16):
                de_bytes = i[j:j+16]
                if not max(de_bytes):
                    continue
                words = struct.unpack(self.fs.ENDIAN + "H14s", de_bytes)
                name = words[1].split(b'\x00')[0].decode(self.fs.CHARSET)
                dirent = DirEnt(
                    self.fs,
                    self.path + name,
                    name,
                    words[0],
                )
                self.dirents.append(dirent)

    def commit_files(self):
        ''' Tell the autoarchaeologist about the files we found '''
        for dirent in sorted(self.dirents):
            dirent.commit_file()

    def subdirs(self):
        ''' Process subdirectories '''
        for dirent in sorted(self.dirents):
            if not dirent.inode or not dirent.inum:
                continue
            if dirent.name in ('.', '..',):
                continue
            if dirent.inode.di_type == self.fs.S_IFDIR:
                dirent.subdir = Directory(
                    self.fs,
                    self.path + dirent.name + '/',
                    dirent.inode
                )
                yield dirent.subdir

    def html_as_lsl(self, fo, pfx=""):
        ''' Recursively render as ls -l output '''
        for dirent in sorted(self.dirents):
            if dirent.inode:
                lead = str(dirent.inode)
            elif dirent.inum:
                lead = "BAD INODE# 0x%04x" % dirent.inum
            else:
                lead = "DELETED"
            fo.write(lead.ljust(64) + " " + pfx + dirent.name)
            if dirent.artifact:
                fo.write("     // " + dirent.artifact.summary())
            fo.write("\n")
            if dirent.subdir:
                dirent.subdir.html_as_lsl(fo, pfx=pfx + dirent.name + "/")

class Unix_Filesystem():
    ''' What it says on the tin '''
    def __init__(self, this):
        self.fs_type = "UNIX UFS Filesystem"
        self.this = this
        self.sblock = None
        self.rootdir = None
        self.orphan_dirs = []
        self.orphan_files = []
        self.inode_is = {}
        self.CHARSET = "ASCII"

        # i_mode bits
        self.S_ISFMT = 0o170000
        self.S_IFBLK = 0o060000
        self.S_IFDIR = 0o040000
        self.S_IFCHR = 0o020000
        self.S_IFPIP = 0o010000
        self.S_IFREG = 0o100000

        self.S_ISUID = 0o004000
        self.S_ISGID = 0o002000
        self.S_ISVTX = 0o001000
        self.S_IRUSR = 0o000400
        self.S_IWUSR = 0o000200
        self.S_IXUSR = 0o000100
        self.S_IRGRP = 0o000400
        self.S_IWGRP = 0o000200
        self.S_IXGRP = 0o000100
        self.S_IROTH = 0o000400
        self.S_IWOTH = 0o000200
        self.S_IXOTH = 0o000100

        self.ENDIAN = "<"
        self.NICFREE = 50
        self.NICINOD = 100
        self.NADDR = 13		# addresses in di_addr
        self.NINDEX = 15
        self.DISK_OFFSET = 0x0
        self.SECTOR_SIZE = 0x200
        self.SUPERBLOCK_OFFSET = self.SECTOR_SIZE
        self.INODE_SIZE = 0x40
        self.NINDIR = self.SECTOR_SIZE // 4

        self.sblock_layout = (
            ("s_isize", "1H"),
            ("s_fsize", "1X"),
            ("s_free", "%dX" % self.NICFREE),
            ("s_inode", "1H"),
            ("s_inode", "%dH" % self.NICINOD),
            ("s_flock", "1B"),
            ("s_ilock", "1B"),
            ("s_fmod", "1B"),
            ("s_ronly", "1B"),
        )

        self.inode_layout = (
            ("di_mode", "1H"),
            ("di_nlink", "1H"),
            ("di_uid", "1H"),
            ("di_gid", "1H"),
            ("di_size", "1X"),
            ("di_addr", "40B"),
            ("di_atime", "1X"),
            ("di_mtime", "1X"),
            ("di_ctime", "1X"),
        )


    def discover(self):
        ''' Start spelunking '''
        if len(self.this) < 10240:
            return
        self.sblock = self.read_superblock()
        if not self.sblock.s_isize or not self.sblock.s_fsize:
            return
        if self.sblock.s_isize > self.sblock.s_fsize:
            return

        if self.sblock.s_fsize * self.SECTOR_SIZE > len(self.this):
            return

        self.dblock0 = self.sblock.s_isize * self.SECTOR_SIZE
        iroot = self.read_inode(2)
        if iroot.di_type != self.S_IFDIR:
            return
        self.this.add_type(self.fs_type)
        self.this.add_interpretation(self, self.html_as_lsl)
        for d in iroot:
            for i in (0, 1, 16, 17):
                if d[i] not in (0, 2):
                    return
            if d[2] != 0x2e and d[3] != 0x00:
                return
            if d[18] != 0x2e and d[19] != 0x2 and d[20] != 0x00:
                return
            break

        self.inode_is[2] = iroot
        self.rootdir = Directory(self, "/", iroot)
        self.rootdir.commit_files()
        dlist = list(self.rootdir.subdirs())
        while dlist:
            d = dlist.pop(0)
            dlist += d.subdirs()
            d.commit_files()
        return
        while self.hunt_orphan_directories():
            dlist = self.orphan_dirs[-1:]
            while dlist:
                d = dlist.pop(0)
                dlist += d.subdirs()
                d.commit_files()
        self.hunt_orphan_files()

    def hunt_orphan_directories(self):
        ''' Find the first unclaimed inode which looks like a directory '''
        for inum in self.iter_inodes():
            if not self.valid_inum(inum):
                break
            if inum in self.inode_is:
                continue
            inode = self.read_inode(inum)
            if not inode.di_mode and not inode.di_size:
                continue
            if inode.di_type == self.S_IFDIR:
                self.orphan_dirs.append(
                    Directory(self, "/ORPHANS/%d/" % inum, inode)
                )
                return True
        return False

    def hunt_orphan_files(self):
        ''' Find all unclaimed inodes which looks like files '''
        for inum in self.iter_inodes():
            if not self.valid_inum(inum):
                break
            if inum in self.inode_is:
                continue
            inode = self.read_inode(inum)
            if not inode.di_size:
                continue
            if inode.di_type != self.S_IFREG:
                continue
            b = bytearray()
            for i in inode:
                b += i
            j = autoarchaeologist.Artifact(self.this, b)
            j.add_note("UNIX file")
            j.add_note("Orphan File")
            self.orphan_files.append((inode, j))

    def read_struct(self, layout, where):
        '''
            Read an on-disk structure

            We cannot use straight struct.unpack because we
            need support for 32 bits with swapped halves ('X')

            Go the full way and pack into a nice Struct while
            at it anyway.
        '''
        fmt = self.ENDIAN + "".join([j for i, j in layout])
        fmt = fmt.replace('X', 'L')
        size = struct.calcsize(fmt)

        data = struct.unpack(fmt, self.this[where:where+size])
        data = list(data)
        args = {}
        for i, j in layout:
            n = int(j[:-1])
            args[i] = data[:n]
            data = data[n:]
            if j[-1] == 'X':
                args[i] = [swap_words(x) for x in args[i]]
            if n == 1:
                args[i] = args[i][0]
        assert len(data) == 0
        return args

    def read_superblock(self):
        ''' Read the superblock '''
        return Struct(
            **self.read_struct(
                self.sblock_layout,
                self.DISK_OFFSET + self.SUPERBLOCK_OFFSET
            )
        )

    def iter_inodes(self):
        ''' Iterate over all inode numbers '''
        yield from range(
            2,
            (1 + self.sblock.s_isize) * self.SECTOR_SIZE // self.INODE_SIZE
        )

    def valid_inum(self, inum):
        ''' Return true if inode number is valid '''
        inoa = 2 * self.SECTOR_SIZE
        inoa += (inum - 1) * self.INODE_SIZE
        return inum >= 2 and inoa < self.dblock0

    def read_inode(self, inum):
        ''' Read an inode '''
        inoa = self.DISK_OFFSET
        inoa += 2 * self.SECTOR_SIZE
        inoa += (inum - 1) * self.INODE_SIZE
        dinode = Dinode(self, inum, **self.read_struct(self.inode_layout, inoa))
        dinode.di_addr = self.fix_di_addr(dinode.di_addr)
        return dinode

    def fix_di_addr(self, raw):
        ''' convert Dinode.di_addr to block numbers '''
        retval = []
        for i in range(1, len(raw), 3):
            retval.append((raw[i + 2] << 16) | (raw[i + 1] << 8) | raw[i])
        return retval

    def inode_get_block(self, dinode, block_no):
        ''' Get a datablock from an inode '''
        def getblk(naddr):
            offset = dinode.di_addr[naddr] + self.DISK_OFFSET
            offset *= self.SECTOR_SIZE
            return self.this[offset:offset + self.SECTOR_SIZE]

        def indir(blk, baddr):
            blk = blk[baddr * 4:(baddr + 1) * 4]
            offset = struct.unpack(self.ENDIAN + "HH", blk)
            offset = (offset[0] << 16) | offset[1]
            offset *= self.SECTOR_SIZE
            return self.this[offset:offset + self.SECTOR_SIZE]

        if block_no < self.NADDR - 3:
            return getblk(block_no)
        block_no -= (self.NADDR -3)

        if block_no < self.NINDIR:
            iblk = getblk(self.NADDR - 3)
            return indir(iblk, block_no)
        block_no -= self.NINDIR

        if block_no < self.NINDIR * self.NINDIR:
            iiblk = getblk(self.NADDR - 2)
            iblk = indir(iiblk, block_no // self.NINDIR)
            return indir(iblk, block_no % self.NINDIR)

        assert False, "XXX: 3Indir blocks"

    def html_as_lsl(self, fo, _this):
        ''' Render as recusive ls -l '''
        fo.write("<H3>ls -l</H3>\n")
        fo.write("<pre>\n")
        self.rootdir.html_as_lsl(fo)
        if self.orphan_dirs:
            fo.write("<H3>Orphan directory inodes</H3>\n")
            for orphan in self.orphan_dirs:
                fo.write("\n")
                orphan.html_as_lsl(fo)
        if self.orphan_files:
            fo.write("<H3>Orphan files</H3>\n")
            for inode, j in self.orphan_files:
                fo.write("\n")
                lead = str(inode)
                fo.write(lead.ljust(64) + " // " + j.summary())
        fo.write("</pre>\n")

class V7_Filesystem(Unix_Filesystem):
    ''' The default parameters match V7/PDP '''
    def __init__(self, this):
        super().__init__(this)
        self.fs_type = "UNIX V7 Filesystem"
        self.discover()
