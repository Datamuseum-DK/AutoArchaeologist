#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   TAR(1) format
'''

from ...base import namespace
from ...base import octetview as ov
from . import unix_stat

class Invalid(Exception):
    ''' invalid tar file '''

class End(Exception):
    ''' end of tar file '''

class FilePadding(ov.Opaque):
    ''' ... '''

class EndOfArchive(ov.Opaque):
    ''' ... '''

class NameSpace(namespace.NameSpace):
    ''' ... '''

    KIND = "Tar file"

    TABLE = (
        ("r", "mode"),
        ("r", "link"),
        ("r", "uid"),
        ("r", "gid"),
        ("r", "size"),
        ("l", "mtime"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        if hasattr(self.ns_priv, "ns_render"):
            return self.ns_priv.ns_render() + super().ns_render()
        return [""] * (len(self.TABLE)-2) + super().ns_render()

class TarEntry(ov.Struct):
    ''' One tar(1) file entry '''

    def __init__(self, tree, lo):
        if tree.this[lo] == 0:
            raise End()

        csf = tree.this[lo+148:lo+156]
        if csf[-1] not in (0x00, 0x20):
            if sum(tree.this[lo:lo+0x200]) == 0:
                raise End()
            raise Invalid("Checksum[-1] non-space (0x%02x)" % csf[-1])
        if csf[-2] not in (0x00, 0x20):
            raise Invalid("Checksum[-2] non-zero (0x%02x)" % csf[-1])

        for i in csf:
            if i not in b'01234567 \x00':
                raise Invalid("Checksum not valid (0x%02x) %s" % (i, str(csf)))

        csf = bytes(csf[:-2]).lstrip(b'\x20')
        try:
            rsum = int(csf, 8)
        except ValueError:
            raise Invalid("Checksum not octal %s" % str(csf))

        csum = 0
        for i in range(0x200):
            if 148 <= i < 156:
                csum += 0x20
            else:
                csum += tree.this[lo + i]

        if rsum != csum:
            raise Invalid(
                "Wrong checksum 0x%x != 0x%x (%s)" % (csum, rsum, str(csf))
            )

        super().__init__(
            tree,
            lo,
            name_=ov.Text(100),
            mode_=ov.Text(8),
            uid_=ov.Text(8),
            gid_=ov.Text(8),
            size_=ov.Text(12),
            mtime_=ov.Text(12),
            checksum_=ov.Text(8),
            flag_=ov.Text(1),
            linkname_=ov.Text(100),
            magic_=ov.Text(6),
            version_=ov.Text(2),
            uname_=ov.Text(32),
            gname_=ov.Text(32),
            devmajor_=ov.Text(8),
            devminor_=ov.Text(8),
            prefix_=ov.Text(155),
            pad__=12,
        )
        assert self.hi == lo + 0x200
        nm = bytes(self.name.octets()).rstrip(b'\x00')
        if 0 in nm:
            raise Invalid("NUL in name")
        self.filename = self.this.type_case.decode_long(nm)
        if sum(self.pad_.octets()):
            raise Invalid("Padding not zero")
        for fld in (
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.mtime,
            self.checksum,
        ):
            fld.val = int(fld.txt, 8)
            fld.txt = fld.txt.strip()

        for fld in (
            self.flag,
            self.linkname,
            self.magic,
            self.version,
            self.uname,
            self.gname,
            self.devmajor,
            self.devminor,
            self.prefix,
        ):
            fld.txt = fld.txt.strip()

        if 0 and self.prefix.txt:
            print(self.tree.this, "HAS TAR-PREFIX", self)
        self.name.txt = self.filename
        self.namespace = tree.namespace.ns_find(
            self.filename.split("/"),
            cls = NameSpace,
            separator = '/',
            priv = self,
        )
        self.that = None

    def ns_render(self):
        ''' ... '''
        mode = self.mode.val
        if self.magic.txt != "ustar":
            if self.name.txt[-1] == '/':
                mode |= unix_stat.stat.S_IFDIR
            else:
                mode |= unix_stat.stat.S_IFREG
            return [
                unix_stat.stat.mode_bits(mode),
                "0",
                self.uid.val,
                self.gid.val,
                self.size.val,
                unix_stat.stat.timestamp(self.mtime.val),
            ]

        if self.flag.txt == "0":
            mode |= unix_stat.stat.S_IFREG
        elif self.flag.txt == "5":
            mode |= unix_stat.stat.S_IFDIR
        return [
            unix_stat.stat.mode_bits(mode),
            "0",
            self.uname.txt,
            self.gname.txt,
            self.size.val,
            unix_stat.stat.timestamp(self.mtime.val),
        ]

    def get_that(self):
        ''' ... '''
        trunc = False
        if self.flag.txt not in ('', '0'):
            self.that = None
            return self.hi
        if self.size.val == 0:
            self.that = None
            return self.hi
        if self.hi + self.size.val > len(self.tree.this):
            print(self.this, "TAR truncated", self)
            self.that = ov.This(self.tree, lo=self.hi, hi=len(self.tree.this)).insert()
            self.that.that.add_note("Tarfile:Truncated")
        else:
            self.that = ov.This(self.tree, lo=self.hi, width = self.size.val).insert()
        if self.namespace.ns_this is None:
            self.namespace.ns_set_this(self.that.that)
        else:
            print(self.tree.this, "NS ALREADY", self)
            print("\t", self.that)
            print("\t", self.namespace)
        tail = self.that.hi & 0x1ff
        if tail:
            y = FilePadding(self.tree, self.that.hi, 0x200 - tail).insert()
            return y.hi
        return self.that.hi

class TarFile(ov.OctetView):

    ''' A UNIX tar(1) file '''

    def __init__(self, this):
        if len(this) <= 512:
            return
        if TarFile in [*this.parents][0].by_class:
            return
        super().__init__(this)
        ptr = 0
        self.namespace = NameSpace(name = "", separator = "", root = this)
        try:
            y = TarEntry(self, ptr).insert()
            ptr = y.get_that()
        except End:
            return
        except Invalid as err:
            return
        this.add_type("Tarfile")
        this.add_note("Tarfile")
        while ptr < len(this):
            try:
                y = TarEntry(self, ptr).insert()
                ptr = y.get_that()
                if y.that is False:
                    break
            except End:
                y = EndOfArchive(self, ptr, width = 512).insert()
                ptr = y.hi
                break
            except Invalid as err:
                print(this, "ERR", err)
                #print(this, bytes(this[ptr:ptr+512]).hex())
                y = ov.Dump(self, lo=ptr, hi=ptr + 512).insert()
                ptr = y.hi
                break
        if ptr < len(this):
            ov.Opaque(self, lo=ptr, hi=len(this)).insert()
        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)
        this.taken = True
