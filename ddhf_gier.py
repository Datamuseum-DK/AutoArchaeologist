'''
GIER Artifacts from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.regnecentralen.gier_text import GIER_Text
from autoarchaeologist.generic.samesame import SameSame

def gier_job(**kwargs):

    ''' All GIER artifacts '''

    ctx = DDHF_Excavation(
        ddhf_topic = "RegneCentralen GIER Computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/GIER',
        hexdump_limit=1<<10,
        **kwargs,
    )

    ctx.add_examiner(GIER_Text)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "GIER/ALGOL_4",
        "GIER/ALGOL_II",
        "GIER/ALGOL_III",
        "GIER/ASTRONOMY",
        "GIER/CHEMISTRY",
        "GIER/DEMO",
        "GIER/GAMES",
        "GIER/HELP",
        "GIER/HELP3",
        "GIER/MATHEMATICS",
        "GIER/MISC",
        "GIER/MUSIC",
        "GIER/OTHER_SCIENCE",
        "GIER/TEST",
        "GIER/UTIL",
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(gier_job, subdir="gier")
