#!/usr/bin/env python3

PROTOCOL = "https"
URL = "bitsavers.org/"

IGNORE = (
    ".jpg",
)

import os
import mmap
import urllib.request

from ..base import excavation, decorator
from ..container import imd_file

class FromBitsavers():

    def __init__(self, ctx, *args, media_types=None, cache_dir=None):
        self.ctx = ctx
        if cache_dir is None:
            cache_dir = "/tmp/BS/Cache"
        try:
            os.mkdir(cache_dir)
        except FileExistsError:
            pass
        self.cache_dir = cache_dir
        self.minuslist = set()

        for i in args:
            self.process_arg(i)


    def process_arg(self, arg):
        arg = arg.strip('/')
        if arg[0] == '-':
            self.minuslist.add(arg[1:])
            return
        if arg in self.minuslist:
            return
        # print("ARG", arg)
        if arg[-4:].lower() in IGNORE:
            return
        body = self.cache_fetch(arg)
        if body is None:
            return
        assert len(body) > 0
        if body[:15] == b'<!DOCTYPE HTML ':
            self.process_dir(arg, body)
            return
        if arg[-4:].lower() in (".imd",):
            # print("IMD ARTIFACT", arg)
            artifact = imd_file.ImdContainer(octets = body)
            try:
                this = self.ctx.add_top_artifact(
                    artifact,
                    description="Bitsavers:" + arg
                )
            except excavation.DuplicateArtifact as why:
                this = why.that
            except:
                raise

            return

    def process_dir(self, arg, body):
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
                what = flds[1].decode('utf-8')
                self.process_arg(os.path.join(arg, url))
                break


    def cache_fetch(self, url):
        cache_file = os.path.join(self.cache_dir, url.replace('/', '_'))
        # print("CF", cache_file)
        for turnus in range(2):
            try:
                fi = open(cache_file, "rb")
                return mmap.mmap(
                    fi.fileno(),
                    0,
                    access=mmap.ACCESS_READ,
                )
            except FileNotFoundError:
                pass
            print("fetching " + url)
            url = PROTOCOL + "://" + URL + url
            # print("URL", url)
            body = urllib.request.urlopen(url).read()
            with open(cache_file, "wb") as file:
                file.write(body)
        return None

class Decorator(decorator.Decorator):
    ''' ... '''

    def html_prefix_banner(self, file, _this):
        ''' Emit banner for the excavation '''
        file.write('<H1>AutoArchaelogist excavation of Bitsavers.org artifacts</H1>\n')
        file.write('<p>Bitsavers.org artifacts from <a href="https://bitsavers.org/">Bitsaver.org</a></p>\n')
        file.write('<p>AutoArchaeologist software from <a href="https://github.com/Datamuseum-DK/AutoArchaeologist">DataMuseum.dk\'s github repo</a></p>\n')
        file.write('<p>Contact: Poul-Henning Kamp</p>\n')
        file.write('<hr/>\n')
