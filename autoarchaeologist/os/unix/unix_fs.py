#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

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

   FindUnixFs()
   ============

   This class attempts to find any UNIX filesystems

   The strategy is:

   1) Locate potential root inodes

   2) Eliminate non-sensical block-no byte orders

   3) Eliminate block-sizes which do not lead to
      credible root directory content.
   
'''

import time

from ...base import namespace
from ...base import octetview as ov

class NotCredible(Exception):
    ''' dont trust this '''

class NameSpace(namespace.NameSpace):
    ''' Unix NameSpace '''

    def __init__(self, dirent, *args, **kwargs):
        kwargs.setdefault("separator", "/")
        super().__init__(*args, **kwargs)
        self.dirent = dirent

    def ns_render(self):
        retval = []
        if self.dirent.inode:
            retval += self.dirent.inode.ls()
        else:
            retval += ["0", None, None, None, None, None, None]
        return retval + super().ns_render()

    TABLE = (
        ("r", "inode"),
        ("c", "permissions"),
        ("r", "links"),
        ("r", "uid"),
        ("r", "gid"),
        ("r", "size"),
        ("c", "mtime"),
        ("l", "path"),
        ("l", "artifact"),
    )

class Inode(ov.Struct):
    ''' Inode in a UNIX filesystem '''

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

    def __init__(self, *args, **kwargs):

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
        self.that = None
        self.badblocks = 0

        super().__init__(*args, **kwargs)

        self.bogus = self.octets() == b'_UNREAD_' * (len(self) // 8)
        if self.bogus:
            print(self.tree.this, "INO @0x%x unread" % self.lo)

        self.di_type = self.di_mode & self.S_ISFMT
        self.fix_di_addr()

    def __iter__(self):
        if self.di_type not in (0, self.S_IFDIR, self.S_IFREG):
            return
        block_no = 0
        yet = self.di_size
        while yet:
            #print("Ino", self.di_inum, "bno", block_no)
            b = self.get_block(block_no)
            if b is None or len(b) == 0:
                return
            b.insert()
            #b.rendered = "Inode " + str(self.di_inum) + " block " + str(block_no)
            b.rendered = "Inode " + str(self.di_inum) + " datablock"
            if len(b) > yet:
                b = ov.Opaque(b.tree, lo=b.lo, width=yet)
            yield b
            yet -= len(b)
            block_no += 1

    def __str__(self):
        return " ".join(str(x) for x in self.ls())

    def ls(self):
        ''' Return list of columns in "ls -li" like output '''

        retval = []
        retval.append("%6d" % self.di_inum)

        typ = {
            self.S_IFPIP: "p",
            self.S_IFCHR: "c",
            self.S_IFDIR: "d",
            self.S_IFBLK: "b",
            self.S_IFREG: "-",
        }.get(self.di_type)

        mode = self.di_mode

        if self.bogus:
            txt = "bogus"
        elif typ is None:
            txt = "%10o" % mode
        elif not mode & self.S_IXUSR and mode & self.S_ISUID:
            txt = "%10o" % mode
        elif not mode & self.S_IXGRP and mode & self.S_ISGID:
            txt = "%10o" % mode
        else:
            txt = typ
            txt += "r" if mode & self.S_IRUSR else '-'
            txt += "w" if mode & self.S_IWUSR else '-'
            if mode & self.S_IXUSR and mode & self.S_ISUID:
                txt += "s"
            elif mode & self.S_IXUSR:
                txt += "x"
            else:
                txt += "-"
            txt += "r" if mode & self.S_IRGRP else '-'
            txt += "w" if mode & self.S_IWGRP else '-'
            if mode & self.S_IXGRP and mode & self.S_ISGID:
                txt += "s"
            elif mode & self.S_IXUSR:
                txt += "x"
            else:
                txt += "-"
            txt += "r" if mode & self.S_IROTH else '-'
            txt += "w" if mode & self.S_IWOTH else '-'
            if mode & self.S_ISVTX and mode & self.S_IXOTH:
                txt += "t"
            elif mode & self.S_ISVTX:
                txt += "T"
            else:
                txt += "-"
        retval.append(txt)
        retval.append(self.di_nlink)
        retval.append(self.di_uid)
        retval.append(self.di_gid)
        retval.append(self.di_size)
        mtime = time.gmtime(self.di_mtime)
        retval.append(time.strftime("%Y-%m-%dT%H:%M:%S", mtime))
        return retval

    def fix_di_addr(self):
        ''' Implemented by specific filesystems as needed '''

    def indir_get(self, blk, idx):
        ''' Pick a block number out of an indirect block '''
        if blk.octets()[4*idx:4*idx+4] in (b'_UNR', b'EAD_'):
            if not self.badblocks:
                print(self.tree.this, self, "Badblock file (indir)")
                print(type(blk))
                self.badblocks += 1
            return None
        y = self.long(self.tree, blk.lo + 4 * idx)
        return self.ufs.get_block(y.val)

    def get_block(self, block_no):
        '''
           Get a datablock from this inode

           We use FFS's di_db/di_ib variables to make this
           implementation of indirect, 2indir and 3indir
           portable.
        '''

        if block_no < len(self.di_db):
            return self.ufs.get_block(self.di_db[block_no])

        block_no -= len(self.di_db)

        nindir = self.ufs.sblock.fs_nindir
        #nindir = 512 // 4

        if block_no < nindir:
            iblk = self.ufs.get_block(self.di_ib[0])
            #print(iblk.octets()[:64].hex())
            return self.indir_get(iblk, block_no)

        block_no -= nindir
        if block_no < nindir * nindir:
            # print("Really big 1", "0x%05x" % block_no, hex(nindir), hex(nindir*nindir), self.bogus, self)
            iiblk = self.ufs.get_block(self.di_ib[1])
            iblk = self.indir_get(iiblk, block_no // nindir)
            if not iblk:
                return iblk
            return self.indir_get(iblk, block_no % nindir)

        # print("Really big 2", hex(block_no), hex(nindir), hex(nindir*nindir), self)
        block_no -= nindir * nindir

        iiiblk = self.ufs.get_block(self.di_ib[2])
        iiblk = self.indir_get(iiiblk, block_no // (nindir * nindir))
        if not iiblk:
            return iiblk
        iblk = self.indir_get(iiblk, (block_no // nindir) % nindir)
        if not iblk:
            return iblk
        return self.indir_get(iblk, block_no % nindir)

    def commit(self):
        ''' Create artifact, if possible '''

        if self.that:
            return self.that

        if self.di_type != self.S_IFREG:
            return None

        if not self.di_size:
            return None

        l = list()
        for y in self:
            l.append(y)
        if len(l) == 0:
            # Diagnostic ?
            return None
        ll = []
        for x in l:
            ll.append(x.octets())
            if len(ll[-1]) == 0:
                print(self.tree.this, self, "Sparse file?", ",".join("%04x" % len(x.octets()) for x in l))
                return None
            elif ll[-1][:32] == b'_UNREAD_' * 4:
                if not self.badblocks:
                    print(self.tree.this, self, "Badblock file", hex(x.lo))
                self.badblocks += 1
        self.that = self.ufs.this.create(records=ll)
        self.that.add_note("UNIX file")
        if self.badblocks:
            self.that.add_note("Bad_blocks")
        return self.that

class DirEnt():
    ''' Directory Entry in a UNIX filesystem '''

    def __init__(self, ufs, parent, name, inum, inode):
        self.parent = parent
        self.namespace = NameSpace(self, name)
        self.parent.namespace.ns_add_child(self.namespace)
        self.ufs = ufs
        self.path = self.parent.path + [name]
        self.inum = inum
        self.inode = inode
        self.directory = None
        self.artifact = None
        self.sanity_check()

    def sanity_check(self):
        if self.inode.di_type in (self.inode.S_IFREG, self.inode.S_IFDIR):
            for _y in self.inode:
                continue

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
        elif self.inode.di_type == self.inode.S_IFREG:
            self.ufs.inode_is[self.inode.di_inum] = self
            self.artifact = self.inode.commit()
            self.namespace.ns_set_this(self.artifact)

class Directory():
    ''' A directory in a UNIX filesystem '''

    def __init__(self, ufs, path, namespace, inode, parent_ino=None):
        self.ufs = ufs
        self.path = path
        self.inode = inode
        self.dirents = []
        self.ufs.inode_is[self.inode.di_inum] = self
        self.namespace = namespace
        n = 0
        for inum, dname in self.ufs.parse_directory(self.inode):
            if n == 0 and dname != ".":
                return
            if n == 0 and inum != inode.di_inum:
                raise NotCredible("'.' does not point back")
                return
            if n == 1 and dname != "..":
                return
            if parent_ino and n == 1 and inum != parent_ino:
                raise NotCredible("'..' does not point back")
                return
            n += 1
            if inum == 0:
                continue
            if not 2 <= inum <= self.ufs.sblock.fs_imax:
                raise NotCredible("Inode " + hex(inum))
            dinode = self.ufs.get_inode(inum)
            if dname in (".", "..") and dinode.ifmt != dinode.S_IFDIR:
                return
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
            if dirent.inode.di_type != dirent.inode.S_IFDIR:
                continue
            if dirent.path[-1] in (".", "..",):
                continue
            inodeis = self.ufs.inode_is.get(dirent.inode.di_inum)
            if isinstance(inodeis, Directory):
                continue
            dirent.directory = self.ufs.DIRECTORY(
                self.ufs,
                dirent.path,
                dirent.namespace,
                dirent.inode,
                self.inode.di_inum,
            )

    def commit_files(self):
        ''' Tell the autoarchaeologist about the files we found '''
        for dirent in sorted(self.dirents):
            dirent.commit_file()
        assert self.ufs.inode_is[self.inode.di_inum] == self

class UnixFileSystem(ov.OctetView):
    ''' What it says on the tin '''

    FS_TYPE = "UNIX Filesystem"

    DIRECTORY = Directory

    VERBOSE = True

    def __init__(self, this):
        if len(this) < 20480:
            return
        super().__init__(this)
        self.sblock = None
        self.rootdir = None
        self.inode_is = {}
        self.suspect_inodes = {}
        self.good = False
        try:
            if self.VERBOSE:
                print(self.this, "Start analyse")
            self.analyse()
            if self.VERBOSE:
                print(self.this, "End analyse", self.rootdir)
        except NotCredible as err:
            if self.VERBOSE:
                print("\tNot Credible", err)
            return
        print(self.this, "GOOD", self.rootdir)
        self.good = True
        if 0 and self.sblock:
            print("Speculate", self.this)
            self.speculate()
            print("Speculation over", self.this)

    def analyse(self):
        ''' What it says on the tin '''
        self.get_superblock()
        if not self.sblock:
            return
        if self.VERBOSE:
            print("\tGot SB", self.sblock)
        rootino = self.get_inode(2)
        if self.VERBOSE:
            print("\tGot root-inode", rootino)
            #print("\t", ",".join(str(x) for x in rootino.di_db))
            #print("\t", ",".join(str(x) for x in rootino.di_ib))
            #for i in rootino:
                #print("\t", i.octets().hex())
        self.rootdir = self.DIRECTORY(
            self,
            [],
            NameSpace(None, name="", separator="", root=self.this),
            rootino,
        )
        if self.VERBOSE:
            print("\tGot RootDir", self.rootdir)

    def commit(self):
        self.this.add_interpretation(self, self.rootdir.namespace.ns_html_plain)
        self.rootdir.commit_files()
        self.this.add_description(self.FS_TYPE)

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
            if inode.di_type not in (0, inode.S_IFDIR, inode.S_IFREG):
                continue
            self.suspect_inodes[inum] = inode

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
            if not tour and inode.di_type != inode.S_IFDIR:
                continue
            if tour and inode.di_type not in (0, inode.S_IFDIR):
                continue
            if inode.di_size % 0x10:   # XXX: Only SysV
                continue
            try:
                specdir = self.DIRECTORY(self, [], NameSpace(""), inode)
            except Exception as err:
                print("TRIED", inum, tour, err)
                continue
            if len(specdir.dirents) < 2:
                continue
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
            dirent = DirEnt(self, pdir, name, inum, inode)
            specdir = self.DIRECTORY(self, pdir.path + [name], dirent.namespace, inode)
            return True

    def speculate_ifreg(self):
        ''' Reattach regular files '''
        return
        pdir = self.inode_is.get(2)
        for inum, inode in self.suspect_inodes.items():
            if inode.di_type not in (0, inode.S_IFREG):
                continue
            if not inode.di_size:
                continue
            name = "~ORPHAN_%d" % inum
            fpath = pdir.path + [name]
            print("  Reattach ", inode, "as", "/".join(fpath) )
            styp = inode.di_type
            inode.di_type = inode.S_IFREG
            dirent = DirEnt(self, pdir, name, inum, inode)
            pdir.dirents.append(dirent)
            dirent.commit_file()
            inode.di_type = styp

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


class Daddr40(ov.Opaque):
    ''' The daddr field of on-disk inodes is weird '''

    def __init__(self, up, lo):
        super().__init__(up, lo, width=40)

    def render(self):
        yield '-'.join("%02x" % x for x in self.octets())

class Inode64(Inode):
    ''' The classic 64 byte UNIX inode '''

    SIZE = 64

    def __init__(self, up, lo, short, long, byte_order=None):
        if lo + 64 > len(up.this):
            raise NotCredible("Inode at " + hex(lo))
        super().__init__(
            up,
            lo,
            vdi_mode_=short,
            vdi_nlink_=short,
            vdi_uid_=short,
            vdi_gid_=short,
            vdi_size_=long,
            vdi_addr_=Daddr40,
            vdi_atime_=long,
            vdi_mtime_=long,
            vdi_ctime_=long,
        )
        self.ifmt = self.vdi_mode.val & Inode.S_ISFMT
        if self.ifmt == 0:
            return

        self.di_type = self.vdi_mode.val & Inode.S_ISFMT
        self.di_mode = self.vdi_mode.val
        self.di_nlink = self.vdi_nlink.val
        self.di_size = self.vdi_size.val
        self.ufs = up
        self.long = long

        if byte_order is None:
            byte_order = (0, 1, 2)

        i = list(self.bnos(byte_order))

        self.di_db = i[:-3]
        self.di_ib = i[-3:]

    def bnos(self, byte_order):
        ''' Interpret vdi_addr according to byte order '''
        adr = self.vdi_addr.octets()
        if len(byte_order) == 3:
            a,b,c = byte_order
            for i in range(0, len(adr)-3, 3):
                yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]
        elif len(byte_order) == 4:
            a,b,c,d = byte_order
            for i in range(0, len(adr)-4, 4):
                yield (adr[i+a] << 24) | (adr [i+b] << 16) | (adr[i+c] << 8) | adr[i+d]
        else:
            a,b,c,d,e,f = byte_order
            for i in range(0, len(adr)-6, 6):
                yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]
                yield (adr[i+d] << 16) | (adr [i+e] << 8) | adr[i+f]
            yield (adr[i+a] << 16) | (adr [i+b] << 8) | adr[i+c]

    def is_dir(self):
        if (self.vdi_mode.val & 0o170000) != 0o040000:
            return False
        if self.vdi_size.val >= len(self.this):
            return False
        if self.vdi_size.val & 0xf:
            return False
        # Directories cannot be sparse, check that non-zero block count
        # is credible for di_size.
        if sum(self.vdi_addr.octets()[:4]) == 0:
            return False
        bn3 = [self.bnos((0, 1, 2))]
        bn4 = [self.bnos((0, 1, 2, 3))]
        nbn3 = len(bn3) - bn3.count(0)
        nbn4 = len(bn4) - bn4.count(0)
        if not nbn3 and not nbn4:
            return False
        bpb3 = self.vdi_size.val / nbn3
        bpb4 = self.vdi_size.val / nbn4
        if bpb3 > (1<<16) and bpb4 > (1<<16):
            return False
        return True

    def has_blocks(self):
        return self.ifmt in (
            UnixFileSystem.S_IFBLK,
            UnixFileSystem.S_IFREG,
        )

    def credible(self):
        if self.ifmt == UnixFileSystem.S_IFDIR:
            return self.is_dir()

        return self.ifmt in (
            UnixFileSystem.S_IFCHR,
            UnixFileSystem.S_IFBLK,
            UnixFileSystem.S_IFDIR,
            UnixFileSystem.S_IFCHR,
            UnixFileSystem.S_IFPIP,
            UnixFileSystem.S_IFREG,
        )

class DirBlock(ov.Struct):
    def __init__(self, tree, lo, hi, short):

        class DirEnt(ov.Struct):
            def __init__(self, tree, lo):
                super().__init__(
                    tree,
                    lo,
                    inum_=short,
                    fnam_=ov.Text(14),
                )

        super().__init__(
            tree,
            lo,
            dents_=ov.Array((hi-lo) // 16, DirEnt, vertical=True),
            vertical=True,
        )

    def __iter__(self):
        for dent in self.dents:
            if dent.inum.val:
                yield dent.inum.val, dent.fnam.full_text()

class UnixFsSblock():
    # Interface with unix_fs until that is redone
    fs_imax = 1<<20

class UnusedBlock(ov.Opaque):
    ''' ... '''

class UnixFs(UnixFileSystem):
    ''' Parameterized UNIX filesystem '''

    VERBOSE = True

    def __init__(
        self,
        up,
        byte_order,
        block_size,
        block_offset,
    ):
        this = up.this
        self.fsname = up.__class__.__name__
        self.byte_order = byte_order
        self.block_size = block_size
        self.block_offset = block_offset
        self.inode2_offset = up.root_inode.lo
        self.short = up.SHORT
        self.long = up.LONG
        self.inode_class = up.inode_class
        self.params = up.params
        if self.VERBOSE:
            print(this, str(self), "?")
        super().__init__(this)
        if not self.good:
            print(this, "no good")
            return
        self.rootdir.namespace.KIND = str(self)
        if self.VERBOSE:
            print(this, "commit", self)
        else:
            print(this, self)
        super().commit()

        for lo, hi in self.gaps():
            lo += self.block_size - 1
            lo &= ~(self.block_size - 1)
            while lo + self.block_size <= hi:
                y = UnusedBlock(self, lo=lo, width=self.block_size).insert()
                lo = y.hi
        self.add_interpretation(more=True, title=str(self))

    def __str__(self):
        return "UnixFS(" + ", ".join(
            (
                str(self.byte_order),
                hex(self.block_size),
                hex(self.block_offset),
                hex(self.inode2_offset),
                self.fsname,
            ) ) + ")"

    def get_inode(self, inum):
        ''' Get inode number inum '''
        lo = self.inode2_offset + (inum - 2) * self.inode_class.SIZE
        if lo + self.inode_class.SIZE > len(self.this):
            raise NotCredible("Inode past this ", hex(inum))
        ino = Inode64(
            self,
            lo,
            self.short,
            self.long,
            self.byte_order,
        )
        ino.di_inum = inum

        # Sanity-check
        if not ino.ifmt:
            raise NotCredible(
                "Inode has no ifmt " + str(inum) + " " + str(ino)
            )

        if ino.ifmt in (ino.S_IFDIR, ino.S_IFREG):
            # Block numbers must be credible
            for blockno in ino.di_db + ino.di_ib:
                if blockno:
                    hi = self.block_offset + (blockno + 1) * self.block_size
                    if hi > len(self.this):
                        raise NotCredible(
                            "Inode has block_no past this " + str(inum) + " " + str(ino)
                        )

            hasblocks = sum(ino.di_db) + sum(ino.di_ib)
            if ino.di_size:
                if not hasblocks:
                    raise NotCredible(
                        "Inode has size but no blocks " + str(inum) + " " + str(ino)
                    )

                # If there are too many block numbers, the blocksize is too large.
                nblk = (ino.di_size + self.block_size - 1) // self.block_size
                i = list(ino.di_db)
                while i and i[-1] == 0:
                    i.pop(-1)
                if 0 and nblk < len(i) and max(ino.di_db[nblk:]) > 0:
                    raise NotCredible(
                        "Inode has too many direct blocks " + str(inum) + " " + str(ino)
                    )
            elif 0 and hasblocks:
                raise NotCredible(
                    "Inode has no size but has blocks " + str(inum) + " " + str(ino)
                )

        ino.insert()
        return ino

    def get_superblock(self):
        # Interface with unix_fs until that is redone
        self.sblock = UnixFsSblock()
        self.sblock.fs_nindir = self.block_size // 4
        #self.sblock.fs_nindir = 512 // 4

    def get_block(self, blockno):
        ''' Get a logical disk block '''

        lo = self.block_offset + blockno * self.block_size
        hi = lo + self.block_size
        if hi > len(self.this):
            raise NotCredible("Block_no past this " + str(self) + " " +hex(blockno))
        return ov.Opaque(self, lo=lo, hi=hi)

    def parse_directory(self, inode):
        ''' Parse classical unix directory: 16bit inode + 14 char name '''
        n = 0
        for b in inode:
            if b.octets()[:8] == b'_UNREAD_':
                n += len(b) // 16
                continue
            db = self.params.DIR_CLASS(self, b.lo, b.hi, self.short).insert()
            for inum, fnam in db:
                if n == 0 and fnam != ".":
                    print(db)
                    raise NotCredible("First dirent not '.' " + str(inode))
                if n == 1 and fnam != "..":
                    print(db)
                    raise NotCredible("Second dirent not '..' " + str(inode))
                n += 1
                yield inum, fnam

class UnixFsLittleEndian(ov.OctetView):
    '''
       Attempt to instantiate a filesystem given a potential root inode
    '''

    ''' Little endian, sensible longs '''
    SHORT = ov.Le16
    LONG = ov.Le32

    DOT = b'.'.ljust(14, b'\x00')
    DOTDOT = b'..'.ljust(14, b'\x00')

    def __init__(self, up, this, params, inode_class, root_inode):
        self.params = params
        self.inode_class = inode_class
        self.root_inode = root_inode
        super().__init__(this)

        for byte_order in up.params.POSSIBLE_BYTE_ORDERS:
            bnos = list(self.root_inode.bnos(byte_order))
            if max(bnos) * min(self.params.BLOCK_SIZES) >= len(self.this):
                continue
            while bnos and bnos[-1] == 0:
                bnos.pop(-1)
            if 0 in bnos:
                # Directories cannot be sparse
                continue
            # print("\tByte order could be", byte_order, bnos)
            for bsize, offset in self.find_rootdir(bnos):
                print("\tBootblocks could be", hex(offset), "with block size", hex(bsize))
                UnixFs(
                    self,
                    byte_order,
                    bsize,
                    offset,
                )

    def find_rootdir(self, bnos):
        ''' Knowing what we know, can we find the root directory ? '''

        for bsize in sorted(self.params.BLOCK_SIZES):
            adr0 = self.root_inode.lo & ~(bsize - 1)
            off0 = self.root_inode.lo & (bsize - 1)
            if off0 > max(self.params.ROOTINO_INDEX) * self.inode_class.SIZE:
                # Root inode is too far into this block (= wrong block size)
                continue
            for boot_off in range(0, self.params.MAX_BOOTBLOCKS):
                adrr = adr0 + (bnos[0] - boot_off) * bsize
                # print("\tbsize", hex(bsize), "boot_off", hex(boot_off), hex(adr0), hex(adrr))
                if not 0 <= adrr < len(self.this):
                    continue

                # This stuff belongs in params.DIR_CLASS
                y = self.SHORT(self, adrr)
                if y.val != 2:
                    continue
                y = self.SHORT(self, adrr + 16)
                if y.val != 2:
                    continue
                if self.this[adrr + 2:adrr + 16] != self.DOT:
                    continue
                if self.this[adrr + 18:adrr + 32] != self.DOTDOT:
                    continue
                yield bsize, adr0 - boot_off * bsize

class UnixFsLittleEndianBogus(UnixFsLittleEndian):
    ''' Little endian bogus longs '''
    LONG = ov.L1032

class UnixFsBigEndian(UnixFsLittleEndian):
    ''' Big endian sensible longs '''
    SHORT = ov.Be16
    LONG = ov.Be32

class UnixFsBigEndianBogus(UnixFsBigEndian):
    ''' Big endian bogus longs '''
    LONG = ov.L2301

class UnixFsParams():
    ''' Parameters constraining the search for UNIX filesystems '''

    MAX_BOOTBLOCKS = 16			# Number of blocks counted before first inode block
    BLOCK_SIZES = (512, 1024, 2048, 4096)
    ROOTINO_INDEX = (0, 1, 2)		# Where in first inode block is the root-inode
    POSSIBLE_BYTE_ORDERS = (		# How the on-disk inode stores block numbers
            (0, 1, 2),			# Can be 3, 4 or 6 (= 2*3) long
            (0, 1, 2, 3),
            (3, 2, 1, 0),
            (0, 2, 1),
            (1, 2, 0),
            (2, 1, 0),
            (2, 3, 1, 0),
            (1, 0, 2, 3),
            (1, 0, 2),
            (2, 0, 1),
    )
    MIN_ROOT_DIR_LEN = 32
    INODE_CLASSES = (Inode64,)		# Inode classes
    DIR_CLASS = DirBlock		# Directory class

    FS_CLASSES = (
        UnixFsLittleEndian,
        UnixFsBigEndian,
        UnixFsLittleEndianBogus,
        UnixFsBigEndianBogus,
    )

class FindUnixFs(ov.OctetView):
    '''
       Find UNIX filesystems
       ---------------------
    '''

    def __init__(self, this):

        if this.top in this.parents and this.children:
            # we only look at top level artifacts if they are not partitioned
            return

        # The parameters of our search can be set per excavation and artifact
        self.params = getattr(this.top, "UNIX_FS_PARAMS", None)
        self.params = getattr(this, "UNIX_FS_PARAMS", self.params)
        if self.params is None:
            self.params = UnixFsParams()

        super().__init__(this)

        for off in self.possible_root_inode_offsets():
            for fcls in self.params.FS_CLASSES:
                for icls in self.params.INODE_CLASSES:
                    # Inodes must be aligned
                    if off % icls.SIZE != 0:
                        continue

                    #print(this, "Try", hex(off), fcls.__name__, icls.__name__, )
                    try:
                        root_inode = icls(self, off, fcls.SHORT, fcls.LONG)
                    except NotCredible:
                        continue
                    if root_inode.ifmt != root_inode.S_IFDIR:
                        continue
                    if root_inode.vdi_nlink.val < 2:
                        continue
                    if root_inode.vdi_size.val < self.params.MIN_ROOT_DIR_LEN:
                        continue
                    if not root_inode.is_dir():
                        continue

                    # print(this, "MAYBE", hex(off), fcls.__name__, icls.__name__, )
                    # print("\t", root_inode.vdi_addr)
                    fcls(self, self.this, self.params, icls, root_inode)

    def possible_root_inode_offsets(self):
        ''' Offsets where a root inode might be found '''

        if self.this.top in self.this.parents:
            # Unpartitioned top level artifacts might use unknown partitioning
            # so we search all of them.
            upper_limit = len(self.this)
        else:
            # Filesystems in partitions start after a small number of
            # reserved bootblocks.
            upper_limit = self.params.MAX_BOOTBLOCKS * max(self.params.BLOCK_SIZES)

        # We only need to check the ROOTINO_INDEX positions in each block
        # but we know neither the size of inodes nor blocks yet, so we test
        # to their extreme values.

        smallest_blocksize = min(self.params.BLOCK_SIZES)
        smallest_inode = min(x.SIZE for x in self.params.INODE_CLASSES)
        largest_inode = max(x.SIZE for x in self.params.INODE_CLASSES)
        largest_offset_in_block = largest_inode * max(self.params.ROOTINO_INDEX)

        for block in range(0, upper_limit, smallest_blocksize):
            for ioff in range(block, block + largest_offset_in_block, smallest_inode):
                yield ioff
