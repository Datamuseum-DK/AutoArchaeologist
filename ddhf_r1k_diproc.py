'''
Rational R1000/400 Diag Processor Firmware from Datamuseum.dk's BitStore
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.rational.r1k_diag import R1kDiagFirmWare

class R1KDIPROC(DDHF_Excavation):

    ''' Rational R1000/400 Diag Processor firmware '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(R1kDiagFirmWare)

        self.from_bitstore(
            "30002517",
            "30003041",
        )

if __name__ == "__main__":
    main(
        R1KDIPROC,
        html_subdir="r1k_diproc",
        ddhf_topic = "Rational R1000/400 Diag Processor Firmware",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
