'''
DKUUG and EUUG Conference tapes
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.unix.tar_file import TarFile
from autoarchaeologist.unix.compress import Compress

def dkuug_job(**kwargs):

    '''
    DKUUG and EUUG Conference tapes
    '''

    ctx = DDHF_Excavation(
        ddhf_topic = "DKUUG/EUUG Conference tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/DKUUG',
        hexdump_limit=1<<10,
        **kwargs,
    )

    ctx.add_examiner(Compress)
    ctx.add_examiner(TarFile)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30001252",
        "30001253",
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(dkuug_job, subdir="dkuug", downloads=True, download_links=True)
