#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   ZIP files
'''

import zipfile

from ..base import namespace

class FileLike():
    def __init__(self, this):
        self.this = this
        self.pos = 0
        print("FL", len(this), this)

    def seekable(self):
        return True

    def seek(self, pos, whence=0):
        if whence == 0:
            self.pos = pos
        elif whence == 1:
            self.pos += pos
        elif whence == 2:
            self.pos = len(self.this) + pos
        return self.pos

    def tell(self):
        return self.pos

    def read(self, howmuch=None):
        if howmuch is None:
            howmuch = len(self.this) - self.pos
        i = bytes(self.this[self.pos:self.pos+howmuch])
        self.pos += howmuch
        return i

class ZipNameSpace(namespace.NameSpace):
    ''' ... '''

    def ns_render(self):
        return [
            zipfile.compressor_names[self.ns_priv.compress_type],
            hex(self.ns_priv.external_attr),
            self.ns_priv.file_size,
            self.ns_priv.compress_size,
            self.ns_priv.comment,
        ] + super().ns_render()

class ZipFile():
    ''' General ZIP file '''

    def __init__(self, this):
        if bytes(this[:2]) != b'PK':
            return
        try:
            z = zipfile.ZipFile(FileLike(this))
        except zipfile.BadZipFile:
            return
        print(z)
        this.add_note("ZIP-file")
        self.namespace = ZipNameSpace(
            name = "",
            root = this,
        )
        this.add_interpretation(self, self.namespace.ns_html_plain)
        for zi in z.infolist():
            ns = ZipNameSpace(zi.filename, parent=self.namespace, priv=zi)
            try:
                b = z.open(zi).read()
                if len(b) > 0:
                    that = this.create(bits=b)
                    ns.ns_set_this(that)
                    print("THAT", that)
            except NotImplementedError as err:
                print("  ZI", err, zi)
            except zipfile.BadZipFile as err:
                print("  ZI", err, zi)
    
