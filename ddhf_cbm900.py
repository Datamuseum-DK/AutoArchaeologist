'''
Commodore CBM-900 Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf
from autoarchaeologist.base import excavation

from autoarchaeologist.unix import cbm900_partition
from autoarchaeologist.unix import v7_filesystem
from autoarchaeologist.unix import cbm900_ar
from autoarchaeologist.unix import cbm900_l_out
from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame

class Cbm900(excavation.Excavation):

    '''
    Two CBM900 hard-disk images, one also contains the four distribution
    floppy images.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(cbm900_partition.CBM900_Partition)
        self.add_examiner(v7_filesystem.V7_Filesystem)
        self.add_examiner(cbm900_ar.Ar)
        self.add_examiner(cbm900_l_out.L_Out)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)

class DDHF_Cbm900(ddhf.DDHF_Excavation):
    def __init__(self, **kwargs):
        super().__init__(Cbm900, **kwargs)

        self.from_bitstore(
            "30001199",
            "30001972",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Cbm900,
        html_subdir="cbm900",
        ddhf_topic = "Commodore CBM-900",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Commodore/CBM900',
    )
