#!/usr/bin/env python3

'''
    Datamuseum.dk HTML decorations
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

import os
import autoarchaeologist
from autoarchaeologist.ddhf.bitstore import FromBitStore

class DDHF_Excavation(autoarchaeologist.Excavation):
    '''
        Excavation decorated for DataMuseum.dk
    '''

    def __init__(
        self,
        ddhf_topic=None,
        ddhf_topic_link=None,
        ddhf_bitstore_cache=None,
        **kwargs
    ):
        self.ddhf_topic = ddhf_topic
        self.ddhf_topic_link = ddhf_topic_link
        if ddhf_bitstore_cache is None:
            ddhf_bitstore_cache = "/tmp/_bitstore_cache"
        self.ddhf_bitstore_cache = ddhf_bitstore_cache
        super().__init__(**kwargs)

    def html_prefix_banner(self, file, _this):
        ''' Emit the banner for this excavation '''
        file.write('<table>\n')
        file.write('<tr>\n')

        file.write('<td style="vertical-align: middle;">\n')
        file.write('<img src="/logo/ddhf_logo.svg"/>\n')
        file.write('</td>\n')

        file.write('<td style="vertical-align: top;')
        file.write(' padding-left: 40px; padding-right: 40px;">\n')
        file.write('<h1><a href="https://datamuseum.dk/wiki">DataMuseum.dk</a></h1>\n')
        file.write('<p>Presents historical artifacts from the history of:</p>\n')
        if self.ddhf_topic:
            file.write('<h2>\n')
            if self.ddhf_topic_link:
                file.write('<a href="' + self.ddhf_topic_link + '">')
            file.write(self.ddhf_topic + '\n')
            if self.ddhf_topic_link:
                file.write('</a>')
            file.write('</h2>\n')
        file.write('</td>\n')
        file.write('<td style="vertical-align: top; padding: 10px;">\n')
        file.write('<P>\n')
        file.write('This is an automatic "excavation" of a thematic subset of\n')
        file.write('<br>\n')
        file.write('artifacts from\n')
        file.write('<A href="https://datamuseum.dk/wiki">Datamuseum.dk</A>\'s')
        file.write(' <A href="https://datamuseum.dk/wiki/Bits:Keyword">BitArchive</A>.\n')
        if self.ddhf_topic_link:
            file.write('<p>\n')
            file.write('See our Wiki for more about ')
            file.write('<a href="' + self.ddhf_topic_link + '">')
            file.write(self.ddhf_topic + '</a>\n')
            file.write('</p>\n')
        file.write('<p>\n')
        file.write('Excavated with: ')
        file.write(' <A href="https://github.com/Datamuseum-DK/AutoArchaeologist">')
        file.write('AutoArchaeologist</A> - Free &amp; Open Source Software.\n')
        file.write('</td>\n')
        file.write('</tr>\n')
        file.write('</table>\n')
        file.write('<hr/>\n')

    def from_bitstore(self, *args):
        ''' Add artifacts from the Datamuseum.dk Bitstore '''
        FromBitStore(self, self.ddhf_bitstore_cache, *args)

OK_ENVS = {
    "AUTOARCHAEOLOGIST_HTML_DIR": "html_dir",
    "AUTOARCHAEOLOGIST_LINK_PREFIX": "link_prefix",
    "AUTOARCHAEOLOGIST_BITSTORE_CACHE": "ddhf_bitstore_cache",
}

def main(job, html_subdir="tmp", **kwargs):
    ''' A standard main routine to reduce boiler-plate '''
    for key in os.environ:
        i = OK_ENVS.get(key)
        if i:
            kwargs[i] = os.environ[key]

    kwargs['html_dir'] = os.path.join(kwargs['html_dir'], html_subdir)
    kwargs.setdefault('download_links', True)
    kwargs.setdefault('download_limit', 1 << 20)
    kwargs.setdefault('hexdump_limit', 1 << 24)
    ctx = job(**kwargs)

    ctx.start_examination()
    baseurl = ctx.produce_html()

    print("Now point your browser at:")
    print("\t", baseurl)
    return ctx
