'''
   Pull artifacts directly from Datamuseum.dk's bitstore
   -----------------------------------------------------
'''

import os
import mmap
import urllib.request

from ..base import excavation
import ddhf_bitstore_metadata


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
    "TAR": True,
    "SIMH-TAP": True,
    "ASCII": True,
    "ASCII_EVEN": True,
    "ASCII_ODD": True,
    "ASCII_SET": True,
    "BINARY": True,
    "GIERTEXT": True,
}

class FromBitStore():

    ''' Pull in top-level artifacts from Datamuseum.dk's bitstore '''

    def __init__(self, ctx, cache_dir, *args):
        self.ctx = ctx
        self.cache_dir = cache_dir
        self.loaded = set()
        self.blacklist = set()

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
        if self.cache_dir:
            try:
                fi = open(self.cache_dir + "/" + key, "rb")
                return mmap.mmap(
                    fi.fileno(),
                    0,
                    access=mmap.ACCESS_READ,
                )
            except FileNotFoundError:
                pass
        print("fetching " + url)
        body = urllib.request.urlopen(url).read()
        open(self.cache_dir + "/" + key, "wb").write(body)
        return body

    def fetch_meta(self, ident):
        ''' Fetch the metadata from the bitstore '''
        url = PROTOCOL + '://' + SERVERNAME
        url += "/bits/%s.meta" % ident
        body = self.cache_fetch(
            "%s.meta.utf8" % ident,
            url,
        )
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

        meta = ddhf_bitstore_metadata.internals.metadata.MetadataBase(metatxt)

        j = BITSTORE_FORMATS.get(meta.BitStore.Format.val)
        if j is None:
            print(arg, "Ignored, unknown format", meta.BitStore.Format.val)
            return
        if not j:
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
        try:
            this = self.ctx.add_top_artifact(b, description=link_summary)
        except excavation.DuplicateArtifact as why:
            print(why)
            print(why.that)
            this = why.that
        except:
            raise

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
