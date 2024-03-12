'''
   (C)CP/M Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.ddhf.cpm_excavator import Cpm

class Cpm(ddhf.DDHF_Excavation):

    ''' All Cpm artifacts '''

    def __init__(self, **kwargs):
        super().__init__(Cpm, **kwargs)

        self.from_bitstore(
            "-30002875", # PASCAL
            "-30003268", # Ligner CP/M men med COMAL-80 navne semantik
            "-30003296", # Ikke CP/M format
            "RC/RC700",
            "RC/RC750",
            "RC/RC759",
            "RC/RC850/CPM",
            "RC/RC890",
            "CR/CR7",
            "CR/CR8",
            "CR/CR16",
            "JET80",
            "COMPANY/ICL/COMET",
            "COMPANY/BOGIKA",
            media_types = (
                '5¼" Floppy Disk',
                '8" Floppy Disk',
            )
        )

if __name__ == "__main__":
    ddhf.main(
        Cpm,
        html_subdir="cpm",
        ddhf_topic = 'CP/M',
        ddhf_topic_link = 'https://datamuseum.dk/wiki'
    )
