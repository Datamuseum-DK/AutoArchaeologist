#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    Datamuseum.dk HTML decorations
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import sys
import os

from autoarchaeologist.base import excavation, decorator
from autoarchaeologist.container import simh_tap_file, plain_file, imd_file
from autoarchaeologist.collection.datamuseum_dk import FromBitStore

class Decorator(decorator.Decorator):

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
        if self.top.ddhf_topic:
            file.write('<h2>\n')
            if self.top.ddhf_topic_link:
                file.write('<a href="' + self.top.ddhf_topic_link + '">')
            file.write(self.top.ddhf_topic + '\n')
            if self.top.ddhf_topic_link:
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
        if self.top.ddhf_topic_link:
            file.write('<p>\n')
            file.write('See our Wiki for more about ')
            file.write('<a href="' + self.top.ddhf_topic_link + '">')
            file.write(self.top.ddhf_topic + '</a>\n')
            file.write('</p>\n')
        file.write('<p>\n')
        file.write('Excavated with: ')
        file.write(' <A href="https://github.com/Datamuseum-DK/AutoArchaeologist">')
        file.write('AutoArchaeologist</A> - Free &amp; Open Source Software.\n')
        file.write('</td>\n')
        file.write('</tr>\n')
        file.write('</table>\n')
        file.write('<hr/>\n')

class DDHF_Excavation(excavation.Excavation):
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

        self.decorator = Decorator(self)

    def from_bitstore(self, *args, **kwargs):
        ''' Add artifacts from the Datamuseum.dk Bitstore '''
        FromBitStore(self, self.ddhf_bitstore_cache, *args, **kwargs)

    def from_argv(self):
        ''' Process extra command line arguments '''
        for fn in sys.argv[1:]:
            ext = os.path.splitext(fn)
            try:
                if ext[1] in (".tap", ".TAP"):
                    s = simh_tap_file.SimhTapContainer(filename = fn)
                    self.add_top_artifact(s, description=fn)
                elif ext[1] in (".imd", ".IMD"):
                    s = imd_file.ImdContainer(filename = fn)
                    self.add_top_artifact(s, description=fn)
                else:
                    s = plain_file.PlainFileArtifact(fn)
                    self.add_top_artifact(s, description=fn)
            except excavation.DuplicateArtifact:
                pass

OK_ENVS = {
    "AUTOARCHAEOLOGIST_HTML_DIR": "html_dir",
    "AUTOARCHAEOLOGIST_LINK_PREFIX": "link_prefix",
    "AUTOARCHAEOLOGIST_BITSTORE_CACHE": "ddhf_bitstore_cache",
}

def parse_arguments(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', default='/tmp/_autoarchaologist')

    args = parser.parse_args(args=argv)
    if args.out == '.':
        args.out = os.path.join(os.getcwd(), "_autoarchaologist")
    return args

def main(job, html_subdir, **kwargs):
    args = parse_arguments()
    kwargs["html_dir"] = args.out

    ''' A standard main routine to reduce boiler-plate '''
    for key in os.environ:
        i = OK_ENVS.get(key)
        if i:
            kwargs[i] = os.environ[key]

    if 'html_dir' not in kwargs:
        raise AttributeError("missing: html_dir")


    kwargs['html_dir'] = os.path.join(kwargs['html_dir'], html_subdir)
    kwargs.setdefault('download_links', True)
    kwargs.setdefault('download_limit', 1 << 20)
    ctx = job(**kwargs)

    ctx.from_argv()

    ctx.start_examination()
    baseurl = ctx.produce_html()

    print("Now point your browser at:")
    print("\t", baseurl)
    return ctx
