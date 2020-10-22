'''
	Commordore CBM-900 Artifacts from Datamuseum.dk's BitStore
'''

import os

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.unix.v7_filesystem import V7_Filesystem
from autoarchaeologist.unix.cbm900_ar import Ar
from autoarchaeologist.unix.cbm900_l_out import L_Out

def CBM900_job(html_dir, **kwargs):

    ctx = DDHF_Excavation(
        ddhf_topic = "Commodore CBM-900",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Commodore/CBM900',
    )

    ctx.add_examiner(V7_Filesystem)
    ctx.add_examiner(Ar)
    ctx.add_examiner(L_Out)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30001199",
    )

    ctx.start_examination()

    try:
        os.mkdir(html_dir)
    except FileExistsError:
        pass

    ctx.produce_html(
       html_dir=html_dir,
       hexdump_limit=1<<10,
       **kwargs,
    )

    return ctx

if __name__ == "__main__":

    i = CBM900_job(html_dir="/tmp/_aa_cbm900")

    print("Now point your browser at:")
    print("\t", i.link_prefix + '/' + i.filename_for(i))
