'''
Rational R1000/400 Diag Processor Firmware from Datamuseum.dk's BitStore
'''

from autoarchaeologist import ddhf

from autoarchaeologist.rational import r1k_diag

class R1KDIPROC(ddhf.DDHF_Excavation):

    ''' Rational R1000/400 Diag Processor firmware '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(r1k_diag.R1kDiagFirmWare)

        self.from_bitstore(
            "30002517",
            "30003041",
        )

if __name__ == "__main__":
    ddhf.main(
        R1KDIPROC,
        html_subdir="r1k_diproc",
        ddhf_topic = "Rational R1000/400 Diag Processor Firmware",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
