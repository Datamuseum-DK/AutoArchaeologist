#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Pull artifacts directly from Datamuseum.dk's bitstore
   -----------------------------------------------------
'''

import sys
import os
import mmap
import urllib.request

import ddhf_bitstore_metadata
import ddhf_bitstore_metadata.sections.media as media

from ..base import artifact
from ..base import excavation
from ..container import simh_tap_file
from ..container import imd_file

PRIVATE_ACCESS = False

SERVERNAME = os.environ.get("AUTOARCHAEOLOGIST_BITSTORE_HOSTNAME")
if SERVERNAME is None:
    SERVERNAME = "datamuseum.dk"

PROTOCOL = os.environ.get("AUTOARCHAEOLOGIST_BITSTORE_PROTOCOL")
if PROTOCOL is None:
    PROTOCOL = "http"

BS_HOME = os.environ.get("AUTOARCHAEOLOGIST_BITSTORE_HOME")
if BS_HOME is None:
    BS_HOME = "http://datamuseum.dk"

BITSTORE_FORMATS = {
    "PDF": False,
    "MP4": False,
    "BAGIT": False,
    "TAR": True,
    "SIMH-TAP": simh_tap_file.SimhTapContainer,
    "ASCII": True,
    "ASCII_EVEN": True,
    "ASCII_ODD": True,
    "ASCII_SET": True,
    "BINARY": True,
    "GIERTEXT": True,
    "IMAGEDISK": imd_file.ImdContainer,
}

class FromBitStore():

    ''' Pull in top-level artifacts from Datamuseum.dk's bitstore '''

    FORMATS = BITSTORE_FORMATS

    def __init__(self, top, *args, media_types=None, cache_dir=None):
        self.top = top
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = self.top.get_cache_subdir("Datamuseum.dk")
        self.loaded = set()
        self.blacklist = set()
        if media_types is not None:
            media_types = set(media_types)
        self.media_types = media_types

        for i in args:
            try:
                self.process_arg(i)
            except urllib.error.URLError as err:
                print("Network down?", err)
                break

    def process_arg(self, arg):
        ''' Separate arguments into bitstore idents and bitstore keywords '''
        try:
            nbr = int(arg, 10)
        except ValueError:
            nbr = None
        if nbr and -30000000 >= nbr >= -39999999:
            self.blacklist.add("%d" % -nbr)
            return
        if nbr and not 30000000 <= nbr <= 39999999:
            nbr = None
        if nbr is not None:
            self.fetch_single(arg)
        else:
            self.fetch_pattern(arg)

    def cache_fetch_file(self, key, url):
        ''' Fetch something if not cached '''
        cache_file = os.path.join(self.cache_dir, key)
        try:
            fi = open(cache_file, "rb")
            return cache_file
        except FileNotFoundError:
            pass
        print("fetching " + url)
        try:
            body = urllib.request.urlopen(url).read()
        except urllib.error.HTTPError:
            return None
        with open(cache_file, "wb") as file:
            file.write(body)
        return cache_file

    def cache_fetch(self, key, url):
        ''' Fetch something if not cached '''
        cache_file = self.cache_fetch_file(key, url)
        if not cache_file:
            return cache_file
        fi = open(cache_file, "rb")
        return mmap.mmap(
            fi.fileno(),
            0,
            access=mmap.ACCESS_READ,
        )

    def fetch_meta(self, ident):
        ''' Fetch the metadata from the bitstore '''
        url = PROTOCOL + '://' + SERVERNAME
        url += "/bits/%s.meta" % ident
        body = self.cache_fetch(
            "%s.meta.utf8" % ident,
            url,
        )
        if body is None:
            return body
        return bytes(body).decode("UTF-8")

    def fetch_wiki_source(self, wikipage):
        ''' Fetch the source of a wiki-page '''
        url = PROTOCOL + '://' + SERVERNAME
        url += "/w/index.php?title=" + wikipage + "&action=edit"
        body = self.cache_fetch(
            wikipage.replace("/", "_") + ".utf8",
            url,
        )
        body = bytes(body).decode("UTF-8")
        body = body.rsplit('<textarea',maxsplit=1)[-1]
        body = body.split('>', maxsplit=1)[-1]
        body = body.split('</textarea>')[0]
        return body

    def fetch_artifact_file(self, arg):
        ''' Fetch the actual bits from the bitstore '''
        url = PROTOCOL + '://' + SERVERNAME + "/bits/" + arg
        filename = self.cache_fetch_file(arg + ".bin", url)
        return filename

    def fetch_artifact(self, arg, expected):
        ''' Fetch the actual bits from the bitstore '''
        url = PROTOCOL + '://' + SERVERNAME + "/bits/" + arg
        body = self.cache_fetch(arg + ".bin", url)
        if len(body) != expected:
            print(arg, "Length mismatch (%d/%d)" % (expected, len(body)))
        return body

    def find_summary(self, meta):
        ''' Find a one line summary of this artifact '''

        try:
            summary = meta.Media.Summary.val
            return summary
        except AttributeError:
            pass

        try:
            summary = meta.Document.Title.val
            return summary
        except AttributeError:
            pass

        return None

    def fetch_single(self, arg):
        ''' Fetch and parse the metadata page from the wiki '''
        if arg in self.loaded or arg in self.blacklist:
            return
        metatxt = self.fetch_meta(arg)
        if metatxt is None:
            print("Could not fetch", arg)
            return

        meta = ddhf_bitstore_metadata.internals.metadata.MetadataBase(metatxt)
        if meta is None:
            return

        if self.media_types and not self.check_media_type(meta):
            return

        handler = self.FORMATS.get(meta.BitStore.Format.val)
        if handler is None:
            print(arg, "Ignored, unknown format", meta.BitStore.Format.val)
            return
        if handler is False:
            return

        summary = self.find_summary(meta)
        if not summary:
            print(arg, "Ignored, no Summary found")
            return

        link_summary = '<A href="' + BS_HOME + '/wiki/Bits:' + arg + '">'
        link_summary += "Bits:" + arg + '</a>&nbsp'
        link_summary += summary

        expected = int(meta.BitStore.Size.val)

        b = self.fetch_artifact(arg, expected)

        self.loaded.add(arg)

        if handler is not True:
            try:
                b = handler(self.top, b)
            except AssertionError:
                raise
            except Exception as err:
                print(link_summary)
                print("Handler", handler.__name__, "failed with", [err])
                print(repr(sys.exc_info()))
                return

        try:
            this = self.top.add_top_artifact(b, description=link_summary)
        except excavation.DuplicateArtifact as why:
            this = why.that
        except:
            raise

        if handler is not True:
            this.add_type(handler.__name__)
        self.impose_geometry(meta, this)
        self.set_media_type(meta, this)

        symlink = os.path.join(self.top.html_dir, arg + ".html")
        try:
            os.remove(symlink)
        except FileNotFoundError:
            pass
        os.symlink(self.top.basename_for(this), symlink, )

    def fetch_pattern(self, arg):
        ''' Fetch and parse the keyword page from the wiki '''
        metalist = self.fetch_wiki_source('Bits:Keyword/' + arg)
        lines = metalist.split("\n")
        while lines:
            line1 = lines.pop(0)
            if line1[:9] == '|[[Bits:3':
                pass
            elif PRIVATE_ACCESS and line1[:10] == '|([[Bits:3':
                pass
            else:
                continue

            line2 = lines.pop(0)
            if '<s>' in line2:
                continue
            if not PRIVATE_ACCESS and '(' in line2:
                continue

            ident = line1.split("Bits:")[1][:8]
            if ident in self.blacklist:
                continue
            _line3 = lines.pop(0)	# Excavation
            line4 = lines.pop(0)
            line5 = lines.pop(0)
            j = self.FORMATS.get(line4[1:])
            if j is None:
                print("FORMAT? --", line4, line5)
                continue
            if not j:
                continue
            self.fetch_single(ident)

    def check_media_type(self, meta):
        ''' Check Media.Type against filter '''

        i = getattr(meta, "Media", None)
        if i is None:
            return False
        i = getattr(i, "Type", None)
        if i is None or i.val is None:
            return False
        return i.val in self.media_types

    def set_media_type(self, meta, this):
        ''' Set Media.Type on artifact '''

        i = getattr(meta, "Media", None)
        if i is None:
            return
        i = getattr(i, "Type", None)
        if i is None or i.val is None:
            return
        this.add_type(i.val)

    # XXX: On Wang floppies sectors count from zero
    def impose_geometry(self, meta, this):
        ''' Impose Media.Geometry as records '''
        if this._keys:
            # Probably an aliased artifact
            return
        i = getattr(meta, "Media", None)
        if i is None:
            return
        i = getattr(i, "Geometry", None)
        if i is None or i.val is None:
            return
        impose_bitstore_geometry(this, i.val)


def impose_bitstore_geometry(this, gspec):

    geom = media.ParseGeometry(gspec, tolerant=True)
    try:
        off = 0
        for chs, sector_size in geom:
            this.define_rec(
                artifact.Record(
                    low=off,
                    frag=this[off:off+sector_size],
                    key=chs,
                )
            )
            off += sector_size
    except:
        print(this, "Geometry Trouble", geom)
