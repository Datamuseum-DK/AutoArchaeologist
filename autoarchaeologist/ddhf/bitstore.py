'''
   Pull artifacts directly from Datamuseum.dk's bitstore
   -----------------------------------------------------
'''

import sys
import os
import mmap
import urllib.request

from ..base import artifact
from ..base import excavation
from ..container import simh_tap_file
from ..container import imd_file

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

    def __init__(self, ctx, cache_dir, *args, media_types=None):
        self.ctx = ctx
        self.cache_dir = cache_dir
        self.loaded = set()
        self.blacklist = set()
        if media_types is not None:
            media_types = set(media_types)
        self.media_types = media_types

        if cache_dir:
            try:
                os.mkdir(cache_dir)
            except FileExistsError:
                pass

        for i in args:
            self.process_arg(i)

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

    def cache_fetch(self, key, url):
        ''' Fetch something if not cached '''
        cache_file = self.cache_dir + "/" + key
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
        try:
            body = urllib.request.urlopen(url).read()
        except urllib.error.HTTPError:
            return None
        open(cache_file, "wb").write(body)
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

        if self.media_types and not self.check_media_type(meta):
            return

        handler = BITSTORE_FORMATS.get(meta.BitStore.Format.val)
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
                b = handler(b)
            except AssertionError:
                raise
            except Exception as err:
                print(link_summary)
                print("Handler", handler.__name__, "failed with", [err])
                print(repr(sys.exc_info()))
                return

        try:
            this = self.ctx.add_top_artifact(b, description=link_summary)
        except excavation.DuplicateArtifact as why:
            this = why.that
        except:
            raise

        if handler is not True:
            this.add_type(handler.__name__)
        self.impose_geometry(meta, this)
        self.set_media_type(meta, this)

        symlink = os.path.join(self.ctx.html_dir, arg + ".html")
        try:
            os.remove(symlink)
        except FileNotFoundError:
            pass
        os.symlink(self.ctx.basename_for(this), symlink, )

    def fetch_pattern(self, arg):
        ''' Fetch and parse the keyword page from the wiki '''
        metalist = self.fetch_wiki_source('Bits:Keyword/' + arg)
        lines = metalist.split("\n")
        while lines:
            line1 = lines.pop(0)
            if line1[:10] != '|[[Bits:30':
                continue
            line2 = lines.pop(0)
            line2 = line2[2:].split()[0]
            ident = line2.split("/")[-1]
            if ident in self.blacklist:
                continue
            _line3 = lines.pop(0)	# Excavation
            line4 = lines.pop(0)
            line5 = lines.pop(0)
            j = BITSTORE_FORMATS.get(line4[1:])
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
        ngeom = []
        for geom in i.val.split(','):
            i = { "c": 1, "h": 1, "s": 1, "b": 0 }
            for j in geom.split():
                i[j[-1]] = int(j[:-1])
            ngeom.append(i)

        # The Media.Geometry format is ambigous :-(
        #    1c 1h 10s 128b, 1c 1h 5s 256b
        # does not tell if the disk is single or double sided.
        # This heuristic finds the max #head and assumes that
        # applies to the full media.
        # Maybe this could work better ?
        #    c=0 h=0 10s 128b, c=0 h=1 5s 256b
        maxhead = max(x["h"] for x in ngeom)
        ptr = 0
        ncyl = 0
        nhead = 0
        for i in ngeom:
            if maxhead == 1 and i["c"] == 1 and i["h"] == 1:
                for sect in range(i["s"]):
                    chs = (ncyl, nhead, sect + 1)
                    this.define_rec(
                        artifact.Record(
                            low=ptr,
                            frag=this[ptr:ptr+i["b"]],
                            key=chs,
                        )
                    )
                    ptr += i["b"]
                nhead += 1
                if nhead == maxhead:
                    nhead = 0
                    ncyl += 1
            else:
                for cyl in range(i["c"]):
                    for head in range(i["h"]):
                        for sect in range(i["s"]):
                            chs = (ncyl, head, sect + 1)
                            this.define_rec(
                                artifact.Record(
                                    low=ptr,
                                    frag=this[ptr:ptr+i["b"]],
                                    key=chs,
                                )
                            )
                            ptr += i["b"]
                    ncyl += 1


