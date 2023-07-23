'''
Regnecentralen RC3600/RC7000 Artifacts from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.regnecentralen.domus_fs import Domus_Filesystem
from autoarchaeologist.regnecentralen.rc3600_fdtape import RC3600_FD_Tape
from autoarchaeologist.regnecentralen.rc7000_comal import ComalSaveFile
from autoarchaeologist.generic.bigdigits import BigDigits
from autoarchaeologist.data_general.absbin import AbsBin
from autoarchaeologist.data_general.relbin import RelBin
from autoarchaeologist.data_general.papertapechecksum import DGC_PaperTapeCheckSum
from autoarchaeologist.regnecentralen.rcsl import RCSL
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.samesame import SameSame

from autoarchaeologist.type_case import DS2089

def rc3600_job(**kwargs):

    ''' All RC3600 artifacts '''

    ctx = DDHF_Excavation(
        ddhf_topic = "RegneCentralen RC3600/RC7000",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC/RC7000',
        hexdump_limit=1<<10,
        **kwargs,
    )

    ctx.type_case = DS2089()

    ctx.add_examiner(Domus_Filesystem)
    ctx.add_examiner(RC3600_FD_Tape)
    ctx.add_examiner(ComalSaveFile)
    ctx.add_examiner(AbsBin)
    ctx.add_examiner(RelBin)
    ctx.add_examiner(BigDigits)
    ctx.add_examiner(DGC_PaperTapeCheckSum)
    ctx.add_examiner(RCSL)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "RC/RC3600/COMAL",
        "RC/RC3600/DE2",
        "RC/RC3600/DISK",
        "RC/RC3600/DOMUS",
        "RC/RC3600/HW",
        "RC/RC3600/LOADER",
        "RC/RC3600/MUSIL",
        "RC/RC3600/PAPERTAPE",
        "RC/RC3600/SW",
        "RC/RC3600/TEST",
        "RC/RC3600/UTIL",
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(rc3600_job, subdir="rc3600", download_links=True)
