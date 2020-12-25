'''
Commordore CBM-900 Artifacts from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.unix.cbm900_partition import CBM900_Partition
from autoarchaeologist.unix.v7_filesystem import V7_Filesystem
from autoarchaeologist.unix.cbm900_ar import Ar
from autoarchaeologist.unix.cbm900_l_out import L_Out
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.samesame import SameSame

def cbm900_job(**kwargs):

    '''
    Two CBM900 hard-disk images, one also contains the four distribution
    floppy images.
    '''

    ctx = DDHF_Excavation(
        ddhf_topic = "Commodore CBM-900",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Commodore/CBM900',
        hexdump_limit=1<<10,
        **kwargs,
    )

    ctx.add_examiner(CBM900_Partition)
    ctx.add_examiner(V7_Filesystem)
    ctx.add_examiner(Ar)
    ctx.add_examiner(L_Out)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30001199",
        "30001972",
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(cbm900_job, subdir="cbm900")
