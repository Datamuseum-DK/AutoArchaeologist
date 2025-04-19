#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Download artifacts from bitsavers.org
'''

import os

import urllib.request

from ..base import excavation, decorator
from ..container import imd_file

PROTOCOL = "https"
URL = "bitsavers.org/"

IGNORE = (
    ".jpg",
    ".txt",
    ".zip",
)

class FromBitsavers():
    ''' Pull in artifacts from bitsavers.org '''

    def __init__(self, top, *args, media_types=None, cache_dir=None):
        self.top = top
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = self.top.get_cache_subdir("Bitsavers.org")

        self.minuslist = set()

        if top.decorator is None:
            top.decorator = Decorator(top)

        for i in args:
            self.process_arg(i)

    def cache_filename(self, key):
        ''' return the cache file name for a given key '''
        cache_file = os.path.join(self.cache_dir, key)
        return cache_file

    def resolve(self, arg):
        ''' Resolve an argument (recursively) '''

        for i in IGNORE:
            if arg[-len(i):].lower() == i:
                return

        if arg.rstrip('/') in self.minuslist:
            return

        cf = self.cache_filename(arg)
        if os.path.isfile(cf):
            yield cf
            return

        dcf = self.cache_filename(os.path.join(arg, "_.dir"))
        if os.path.isdir(cf) and os.path.isfile(dcf):
            yield from self.parse_dir(arg, dcf)
            return

        assert os.path.isdir(cf) or not os.path.exists(cf)

        tcf = self.cache_filename(arg + ".tmp")
        os.makedirs(os.path.dirname(tcf), exist_ok=True)
        url = PROTOCOL + "://" + URL + arg
        print("fetching", url)
        with urllib.request.urlopen(url) as file:
            body = file.read()
        print("fetched", arg, len(body))
        with open(tcf, "wb") as file:
            file.write(body)

        if body[:9] != b'<!DOCTYPE':
            os.makedirs(os.path.dirname(cf), exist_ok=True)
            os.rename(tcf, cf)
            yield cf
            return
        os.makedirs(os.path.dirname(dcf), exist_ok=True)
        os.rename(tcf, dcf)
        yield from self.parse_dir(arg, dcf)

    def parse_dir(self, arg, dcf):
        ''' Parse a directory's HTML (crudely) '''
        with open(dcf, "rb") as file:
            body = file.read()
        for ptr in range(len(body) - 16):
            if body[ptr:ptr+16] != b'\n<tr><td><a href':
                continue
            for ptr2 in range(ptr, len(body)):
                if body[ptr2:ptr2+10] != b'</td></tr>':
                    continue
                flds = bytes(body[ptr:ptr2]).split(b'<')
                for i in [b'\n', b'tr>', b'td>']:
                    assert flds[0] == i
                    flds.pop(0)
                assert flds[1] == b'/a>'

                flds = flds[0].split(b'"')
                assert flds[0] == b'a href='
                flds.pop(0)
                assert flds[1][0] == b'>'[0]
                flds[1] = flds[1][1:]
                if flds[1] == b'Parent Directory':
                    continue

                url = flds[0].decode('utf-8')
                yield from self.resolve(os.path.join(arg, url))
                break

    def process_arg(self, arg):
        ''' Process an argument '''
        if arg[0] == '-':
            self.minuslist.add(arg[1:].rstrip('/'))
            return
        for fn in self.resolve(arg):
            if fn[-4:].lower() in (".imd",):
                # print("IMD ARTIFACT", arg)
                artifact = imd_file.ImdContainer(self.top, filename = fn)
                try:
                    self.top.add_top_artifact(
                        artifact,
                        description="Bitsavers:" + fn[len(self.cache_dir):]
                    )
                except excavation.DuplicateArtifact:
                    pass

class Decorator(decorator.Decorator):
    ''' ... '''

    def html_prefix_banner(self, file, _this):
        ''' Emit banner for the excavation '''
        file.write('''
<H1>
<a href="https://github.com/Datamuseum-DK/AutoArchaeologist">AutoArchaeologist</a>
AutoArchaelogist
excavation of
<a href="https://bitsavers.org/">Bitsaver.org</a>
artifacts
</H1>
<hr/>
''')
