'''
   UNIX Filesystem
   ---------------

   Invariant base class for (almost?) all UNIX filesystems

   Subclasses must provide three basic functions to
   read the superblock, an inode or a block.

   Directory parseing may need overridden (ie: FFS)

   Convenience functions provided for reading on disk
   structures (XXX: Should be made generic)

   The Superblock must provide the following fields:

       .fs_nindir       Number of blockno in an indirect block
       .fs_imax         Highest inode number
       .fs_bmax         Highest block number

   Inodes must provide the following fields:
        .di_db          List of direct block-numbers
        .di_ib          List of indirect, 2indir and 3indir block-numbers
        .di_mode        for S_IFDIR and S_IFREG (using S_ISFMT mask)

   Inodes can provide the following fields:
        di_nlink        Link count
        di_uid          Owner user id
        di_gid          Owner group id
        di_mtime        Modification time (POSIX time_t)
'''

import sys
import struct
import time

def swap_words(x):
    ''' swap two halves of a 32 bit word '''
    return (x >> 16) | ((x & 0xffff) << 16)

class Struct():
    ''' Brute force data-container class '''
    def __init__(self, **kwargs):
        self.name = ""
        self.__v = kwargs
        for i, j in kwargs.items():
            setattr(self, i, j)

    def __str__(self):
        return "<S "+", ".join([i+"="+str(j) for i,j in self.__v.items()])+">"

    def dump(self, fo=sys.stdout):
        ''' One element per line & hexadecimal for debugging '''
        fo.write("struct %s {\n" % self.name)
        for i, j in self.__v.items():
            if isinstance(j, int):
                fo.write("   %-16s 0x%x\n" % (i, j))
            else:
                fo.write("   %-16s %s\n" % (i, str(j)))
        fo.write("}\n")

class Inode(Struct):
    ''' Inode in a UNIX filesystem '''

    def __init__(self, ufs, **kwargs):
        self.ufs = ufs

        # Used by .get_block
        self.di_db = []
        self.di_ib = []

        # Used by .__str__
        self.di_mode = 0
        self.di_size = 0
        self.di_inum = 0
        self.di_nlink = 0
        self.di_uid = 0
        self.di_gid = 0
        self.di_mtime = 0

        super().__init__(**kwargs)

        self.di_type = self.di_mode & self.ufs.S_ISFMT

    def __iter__(self):
        if self.di_type not in (0, self.ufs.S_IFDIR, self.ufs.S_IFREG):
            return
        block_no = 0
        yet = self.di_size
        while yet:
            b = self.get_block(block_no)
            if b is None or len(b) == 0:
                return None
            if len(b) > yet:
                b = b[:yet]
            yield b
            yet -= len(b)
            block_no += 1

    def __str__(self):
        txt = "%5d" % self.di_inum

        typ = {
            self.ufs.S_IFPIP: "p",
            self.ufs.S_IFCHR: "c",
            self.ufs.S_IFDIR: "d",
            self.ufs.S_IFBLK: "b",
            self.ufs.S_IFREG: "-",
        }.get(self.di_type)

        mode = self.di_mode

        if typ is None:
            txt += " %10o" % mode
        elif not mode & self.ufs.S_IXUSR and mode & self.ufs.S_ISUID:
            txt += " %10o" % mode
        elif not mode & self.ufs.S_IXGRP and mode & self.ufs.S_ISGID:
            txt += " %10o" % mode
        else:
            txt += " " + typ
            txt += "r" if mode & self.ufs.S_IRUSR else '-'
            txt += "w" if mode & self.ufs.S_IWUSR else '-'
            if mode & self.ufs.S_IXUSR and mode & self.ufs.S_ISUID:
                txt += "s"
            elif mode & self.ufs.S_IXUSR:
                txt += "x"
            else:
                txt += "-"
            txt += "r" if mode & self.ufs.S_IRGRP else '-'
            txt += "w" if mode & self.ufs.S_IWGRP else '-'
            if mode & self.ufs.S_IXGRP and mode & self.ufs.S_ISGID:
                txt += "s"
            elif mode & self.ufs.S_IXUSR:
                txt += "x"
            else:
                txt += "-"
            txt += "r" if mode & self.ufs.S_IROTH else '-'
            txt += "w" if mode & self.ufs.S_IWOTH else '-'
            if mode & self.ufs.S_ISVTX and mode & self.ufs.S_IXOTH:
                txt += "t"
            elif mode & self.ufs.S_ISVTX:
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

    def indir_get(self, blk, idx):
        ''' Pick a block number out of an indirect block '''
        blk = blk[idx * 4:(idx + 1) * 4]
        if len(blk) != 4:
            return None
        nblk = struct.unpack(self.ufs.ENDIAN + "L", blk)[0]
        return self.ufs.get_block(nblk)

    def get_block(self, block_no):
        '''
           Get a datablock from this inode

           We use FFS's di_db/di_ib variables to make this
           implementation if indirect, 2indir and 3indir
           portable.
        '''

        if block_no < len(self.di_db):
            return self.ufs.get_block(self.di_db[block_no])

        block_no -= len(self.di_db)

        nindir = self.ufs.sblock.fs_nindir

        if block_no < nindir:
            iblk = self.ufs.get_block(self.di_ib[0])
            return self.indir_get(iblk, block_no)

        block_no -= nindir
        if block_no < nindir * nindir:
            iiblk = self.ufs.get_block(self.di_ib[1])
            iblk = self.indir_get(iiblk, block_no // nindir)
            if not iblk:
                return iblk
            return self.indir_get(iblk, block_no % nindir)

        block_no -= nindir * nindir

        iiiblk = self.ufs.get_block(self.di_ib[2])
        iiblk = self.indir_get(iiiblk, block_no // (nindir * nindir))
        if not iiblk:
            return iiblk
        iblk = self.indir_get(iiblk, (block_no // nindir) % nindir)
        if not iblk:
            return iblk
        return self.indir_get(iblk, block_no % nindir)

class DirEnt():
    ''' Directory Entry in a UNIX filesystem '''

    def __init__(self, ufs, parent, name, inum, inode):
        self.ufs = ufs
        self.parent = parent
        self.path = self.parent.path + [name]
        self.inum = inum
        self.inode = inode
        self.directory = None
        self.artifact = None

    def __lt__(self, other):
        return self.path < other.path

    def __repr__(self):
        return "<DE %s " % self.inum + "/".join(self.path) + ">"

    def commit_file(self):
        ''' Create artifact, if possible '''
        if not self.inode:
            return
        if self.directory:
            self.directory.commit_files()
        elif self.inode.di_type == self.ufs.S_IFREG:
            self.ufs.inode_is[self.inode.di_inum] = self
            if not self.inode.di_size:
                return
            b = bytes()
            for i in self.inode:
                b += i
            if len(b) == 0:
                return
            self.artifact = self.ufs.this.create(bits=b)
            self.artifact.add_note("UNIX file")
            try:
                self.artifact.set_name("/".join(self.path))
            except autoarchaeologist.DuplicateName:
                self.artifact.add_note("/".join(self.path))

class Directory():
    ''' A directory in a UNIX filesystem '''

    def __init__(self, ufs, path, inode):
        self.ufs = ufs
        self.path = path
        self.inode = inode
        self.dirents = []
        self.ufs.inode_is[self.inode.di_inum] = self
        n = 0
        for inum, dname in self.parse():
            if n == 0 and dname != ".":
                return
            if n == 1 and dname != "..":
                return
            n += 1
            if inum <= self.ufs.sblock.fs_imax:
                dinode = self.ufs.get_inode(inum)
            else:
                dinode = None
            dirent = DirEnt(self.ufs, self, dname, inum, dinode)
            self.dirents.append(dirent)
        self.recurse()

    def __str__(self):
        return "<DIR %d " % self.inode.di_inum + str(self.inode) + ">"

    def recurse(self):
        ''' Recursively read tree under this directory '''
        for dirent in self.dirents:
            if not dirent.inode:
                continue
            if dirent.inode.di_type != self.ufs.S_IFDIR:
                continue
            if dirent.path[-1] in (".", "..",):
                continue
            inodeis = self.ufs.inode_is.get(dirent.inode.di_inum)
            if isinstance(inodeis, Directory):
                continue
            dirent.directory = self.ufs.DIRECTORY(
                self.ufs,
                dirent.path,
                dirent.inode
            )

    def commit_files(self):
        ''' Tell the autoarchaeologist about the files we found '''
        for dirent in sorted(self.dirents):
            dirent.commit_file()
        assert self.ufs.inode_is[self.inode.di_inum] == self

    def html_as_lsl(self, fo):
        ''' Recursively render as ls -l output '''
        for dirent in sorted(self.dirents):
            if dirent.inode:
                lead = str(dirent.inode)
            elif dirent.inum:
                lead = "BAD INODE# 0x%x" % dirent.inum
            else:
                lead = "DELETED"
            fo.write(lead.ljust(64) + " " + "/".join(dirent.path))
            if dirent.artifact:
                fo.write("     // " + dirent.artifact.summary())
            fo.write("\n")
            if dirent.directory:
                dirent.directory.html_as_lsl(fo)

    def parse(self):
        ''' Parse classical unix directory: 16bit inode + 14 char name '''
        for b in self.inode:
            b = b.tobytes()
            for j in range(0, len(b), 16):
                de_bytes = b[j:j+16]
                if not max(de_bytes):
                    continue
                words = struct.unpack(self.ufs.ENDIAN + "H14s", de_bytes)
                name = words[1].rstrip(b'\x00')
                if b'\x00' in name:
                    continue
                name = name.decode(self.ufs.CHARSET)
                yield words[0], name

class UnixFileSystem():
    ''' What it says on the tin '''

    FS_TYPE = "UNIX Filesystem"
    CHARSET = "ASCII"
    ENDIAN = ">"

    # i_mode bits
    S_ISFMT = 0o170000
    S_IFBLK = 0o060000
    S_IFDIR = 0o040000
    S_IFCHR = 0o020000
    S_IFPIP = 0o010000
    S_IFREG = 0o100000

    S_ISUID = 0o004000
    S_ISGID = 0o002000
    S_ISVTX = 0o001000
    S_IRUSR = 0o000400
    S_IWUSR = 0o000200
    S_IXUSR = 0o000100
    S_IRGRP = 0o000400
    S_IWGRP = 0o000200
    S_IXGRP = 0o000100
    S_IROTH = 0o000400
    S_IWOTH = 0o000200
    S_IXOTH = 0o000100

    DIRECTORY = Directory

    def __init__(self, this):
        if len(this) < 20480:
            return
        self.this = this
        self.sblock = None
        self.inode_is = {}
        self.suspect_inodes = {}
        self.analyse()
        if self.sblock:
            print("Speculate", self.this)
            self.speculate()
            print("Speculation over", self.this)

    def analyse(self):
        ''' What it says on the tin '''
        self.get_superblock()
        if not self.sblock:
            return
        self.rootdir = self.DIRECTORY(self, [], self.get_inode(2))
        self.rootdir.commit_files()
        self.this.add_interpretation(self, self.html_as_lsl)
        self.this.add_type(self.FS_TYPE)

    def speculate(self):
        ''' Look for orphan inodes '''
        for inum in range(2, self.sblock.fs_imax + 1):
            if inum in self.inode_is:
                continue
            inode = self.get_inode(inum)
            if not inode or not inode.di_size or not max(inode.di_db):
                continue
            if inode.di_size >= len(self.this):
                continue
            if inode.di_type not in (0, self.S_IFDIR, self.S_IFREG):
                continue
            self.suspect_inodes[inum] = inode
            print("?", inode)

        if not self.suspect_inodes:
            return

        print("Found", len(self.suspect_inodes), "suspect inodes")
        for tour in range(2):
            while self.speculate_ifdir(tour):
                self.clear_suspects()

        if not self.suspect_inodes:
            return
        self.speculate_ifreg()
        self.clear_suspects()
        if not self.suspect_inodes:
            return
        print("Remaining suspect inodes:")
        for _inum, inode in self.suspect_inodes.items():
            print(inode)

    def clear_suspects(self):
        ''' Eliminate suspects now accounted for '''
        for inum in list(self.suspect_inodes.keys()):
            if inum in self.inode_is:
                del self.suspect_inodes[inum]

    def speculate_ifdir(self, tour):
        ''' Try to reattach directory inodes '''
        for inum, inode in self.suspect_inodes.items():
            if not tour and inode.di_type != self.S_IFDIR:
                continue
            if tour and inode.di_type not in (0, self.S_IFDIR):
                continue
            if inode.di_size % 0x10:
                continue
            try:
                specdir = self.DIRECTORY(self, [], inode)
            except Exception as err:
                print("TRIED", inum, tour, err)
                continue
            if len(specdir.dirents) < 2:
                continue
            print(type(specdir.dirents))
            print(len(specdir.dirents))
            print(specdir.dirents)
            pdino = specdir.dirents[1].inode.di_inum
            pdir = self.inode_is.get(pdino)
            if pdir is None:
                pdino = 2
                pdir = self.inode_is.get(pdino)
            if not isinstance(pdir, self.DIRECTORY):
                continue
            name = "~ORPHAN_%d" % inum
            fpath = pdir.path + [name]
            print("  Reattach ", inode, "as", "/".join(fpath) )
            specdir = self.DIRECTORY(self, pdir.path + [name], inode)
            dirent = DirEnt(self, pdir, name, inum, inode)
            dirent.directory = specdir
            pdir.dirents.append(dirent)
            specdir.commit_files()
            return True

    def speculate_ifreg(self):
        ''' Reattach regular files '''
        pdir = self.inode_is.get(2)
        for inum, inode in self.suspect_inodes.items():
            if inode.di_type not in (0, self.S_IFREG):
                continue
            if not inode.di_size:
                continue
            name = "~ORPHAN_%d" % inum
            fpath = pdir.path + [name]
            print("  Reattach ", inode, "as", "/".join(fpath) )
            styp = inode.di_type
            inode.di_type = self.S_IFREG
            dirent = DirEnt(self, pdir, name, inum, inode)
            pdir.dirents.append(dirent)
            dirent.commit_file()
            inode.di_type = styp

    def html_as_lsl(self, fo, _this):
        ''' Render as recursive ls -l '''
        fo.write("<H3>ls -l</H3>\n")
        fo.write("<pre>\n")
        self.rootdir.html_as_lsl(fo)

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
        args["_size"] = size
        return args

    def get_superblock(self):
        '''
           Sub-class provided
           Shall set self.sblock if a filesystem is found
        '''
        return None

    def get_inode(self, _inum):
        '''
           Sub-class provided
           Return inode by number
        '''
        return None

    def get_block(self, _blockno):
        '''
           Sub-class provided
           Return disk-block by number
        '''
        return None
