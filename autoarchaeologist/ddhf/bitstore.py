'''
   Pull artifacts directly from Datamuseum.dk's bitstore
   -----------------------------------------------------
'''

import urllib.request

SERVERNAME = "datamuseum.dk"

class FromBitStore():

    ''' Pull in top-level artifacts from Datamuseum.dk's bitstore '''

    def __init__(self, ctx, cache_dir, *args):
        self.ctx = ctx
        self.cache_dir = cache_dir

        for i in args:
            self.process_arg(i)

    def process_arg(self, arg):
        ''' Separate arguments into bitstore idents and bitstore keywords '''
        print("ARG", arg)
        try:
            nbr = int(arg, 10)
        except ValueError:
            nbr = None
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
                return open(self.cache_dir + "/" + key, "rb").read()
            except FileNotFoundError:
                pass
        print("fetching " + url)
        body = urllib.request.urlopen(url).read()
        open(self.cache_dir + "/" + key, "wb").write(body)
        return body

    def fetch_wiki_source(self, wikipage):
        ''' Fetch the source of a wiki-page '''
        url = 'https://' + SERVERNAME
        url += "/w/index.php?title=" + wikipage + "&action=edit"
        body = self.cache_fetch(
            wikipage.replace("/", "_") + ".utf8",
            url,
        )
        body = body.decode("UTF-8")
        body = body.split('<textarea')[-1]
        body = body.split('>', 1)[-1]
        body = body.split('</textarea>')[0]
        return body

    def fetch_artifact(self, arg, expected):
        ''' Fetch the actual bits from the bitstore '''
        url = 'https://' + SERVERNAME + "/bits/" + arg
        body = self.cache_fetch(arg + ".bin", url)
        if len(body) != expected:
            print(arg, "Length mismatch (%d/%d)" % (expected, len(body)))
        return body

    def fetch_single(self, arg):
        ''' Fetch and parse the metadata page from the wiki '''
        meta = self.fetch_wiki_source('Bits:' + arg)
        meta = meta.split('= METADATA =')[1]
        metalines = [x.strip() for x in meta.split("\n")]
        i = metalines.index("Media.Summary:")
        if i < 0:
            print(arg, "Ignored, no Media.Summary found")
            return
        media_summary = metalines[i+1]
        i = metalines.index("BitStore.Size:")
        if i < 0:
            print(arg, "Ignored, no Bitstore.Size found (This is BAD!)")
            return
        expected = int(metalines[i+1], 10)
        b = self.fetch_artifact(arg, expected)
        self.ctx.add_top_artifact(b, arg + " " + media_summary)

    def fetch_pattern(self, arg):
        ''' Fetch and parse the keyword page from the wiki '''
        metalist = self.fetch_wiki_source('Bits:Keyword/' + arg)
        lines = metalist.split("\n")
        while lines:
            line1 = lines.pop(0)
            if line1[:10] != '|[[Bits:30':
                continue
            line2 = lines.pop(0)
            line3 = lines.pop(0)
            _line4 = lines.pop(0)
            line5 = lines.pop(0)
            j = {
                "PDF": 0,
                "MP4": 0,
                "ASCII": 1,
                "ASCII-EVEN": 1,
                "ASCII-ODD": 1,
                "ASCII-SET": 1,
                "BINARY": 1,
                "GIERTEXT": 1,
            }.get(line3[1:])
            if j is None:
                print("FORMAT? --", line3, line5)
                continue
            if not j:
                continue
            line2 = line2[2:].split()[0]
            ident = line2.split("/")[-1]
            self.fetch_single(ident)
