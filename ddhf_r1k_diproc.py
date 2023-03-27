'''
Rational R1000/400 Diag Artifacts from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.rational.r1k_diag import R1kDiagFirmWare

def r1k_diproc_job(**kwargs):

    ''' Rational R1000/400 Diag processor firmware '''

    ctx = DDHF_Excavation(
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
        hexdump_limit=1<<10,
        **kwargs,
    )

    ctx.add_examiner(R1kDiagFirmWare)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30002517",
        "30003041",
    )

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(r1k_diproc_job, subdir="r1k_diproc", downloads=True)
