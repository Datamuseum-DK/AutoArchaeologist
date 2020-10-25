'''
	Regnecentralen RC3600/RC7000 Artifacts from Datamuseum.dk's BitStore
'''

import os

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.generic.bigdigits import BigDigits
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic.ascii import Ascii

from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.relbin import RelBin

from autoarchaeologist.regnecentralen.papertapechecksum import RC_PaperTapeCheckSum
from autoarchaeologist.regnecentralen.gier_text import GIER_Text
from autoarchaeologist.regnecentralen.domus_fs import Domus_Filesystem
from autoarchaeologist.regnecentralen.rcsl import RCSL
from autoarchaeologist.regnecentralen.rc3600_fdtape import RC3600_FD_Tape

from autoarchaeologist.ddhf.bitstore import FromBitStore

def RC3600_job(html_dir, **kwargs):

    ctx = DDHF_Excavation(
        ddhf_topic = "RegneCentralen RC3600/RC7000",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC/RC7000',
    )

    ctx.add_examiner(Domus_Filesystem)
    ctx.add_examiner(RC3600_FD_Tape)
    ctx.add_examiner(AbsBin)
    ctx.add_examiner(RelBin)
    ctx.add_examiner(GIER_Text)
    ctx.add_examiner(BigDigits)
    ctx.add_examiner(DGC_PaperTapeCheckSum)
    ctx.add_examiner(RC_PaperTapeCheckSum)
    ctx.add_examiner(RCSL)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "RC3600/COMAL",
        "RC3600/DE2",
        "RC3600/DISK",
        "RC3600/DOMUS",
        "RC3600/HW",
        "RC3600/LOADER",
        "RC3600/MUSIL",
        "RC3600/PAPERTAPE",
        "RC3600/SW",
        "RC3600/TEST",
        "RC3600/UTIL",
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

    i = RC3600_job("/tmp/_aa_rc3600")

    print("Now point your browser at:")
    print("\t", i.link_prefix + '/' + i.filename_for(i))
