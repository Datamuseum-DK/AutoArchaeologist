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

from autoarchaeologist.base import excavation
from autoarchaeologist.container import argv
from autoarchaeologist.collection.datamuseum_dk import FromBitStore

from . import decorated_context

class DDHFExcavation(excavation.Excavation):
    '''
        Excavation decorated for DataMuseum.dk
    '''

    BITSTORE = ()
    MEDIA_TYPES = None

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

        self.decorator = decorated_context.Decorator(self)

    def from_bitstore(self, *args, **kwargs):
        ''' Add artifacts from the Datamuseum.dk Bitstore '''

    def from_argv(self):
        ''' Process extra command line arguments '''
        do_bitstore = len(sys.argv) == 1
        for fn in sys.argv[1:]:
            if fn in ("-h", "--help"):
                self.usage()
            elif fn == "-b":
                do_bitstore = True
            else:
                argv.argv_file(self, fn)
        if do_bitstore:
            FromBitStore(self, self.ddhf_bitstore_cache, *self.BITSTORE, media_types=self.MEDIA_TYPES)

    def usage(self):
        ''' ... '''
        print()
        i = "Datamuseum.DK AutoArchaeologist script (" + self.__class__.__name__ + ")"
        print(i)
        print('-' * len(i))
        print()
        print("Without arguments, relevant artifacts from the bitstore will be processed.")
        print()
        print("When run with file arguments, those files will be processed instead,")
        print("and the same way as the artifacts from the bitstore would have been.")
        print("To process both file arguments and bitstore artifacts use option `-b`")
        print()
        print("Environment variables:")
        print()
        print("   AUTOARCHAEOLOGIST_HTML_DIR")
        print("      Where to write the output files")
        print("      Now:", self.html_dir)
        print()
        print("   AUTOARCHAEOLOGIST_LINK_PREFIX")
        print("      Prefix to use for html links")
        print("      Set this if the output files are moved")
        print("      to a different location/webserver")
        print("      Now:", self.link_prefix)
        print()
        print("   AUTOARCHAEOLOGIST_BITSTORE_CACHE")
        print("      Cache directory for downloaded bitstore artifacts")
        print("      (If deleted, they are downloaded again)")
        print("      Now:", self.ddhf_bitstore_cache)
        print()
        print("Bitstore artifacts;")
        print()
        if self.MEDIA_TYPES is not None:
            print("   Only media types;")
            print()
            for i in self.MEDIA_TYPES:
                print("     ", i.strip())
            print()
        for i in self.BITSTORE:
            print("  ", i.strip())
        print()
        sys.exit(2)

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
    ctx = job(**kwargs)

    ctx.from_argv()

    ctx.start_examination()
    baseurl = ctx.produce_html()

    print("Now point your browser at:")
    print("\t", baseurl)
    return ctx
