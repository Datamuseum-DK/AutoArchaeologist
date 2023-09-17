'''
Commodore CBM-900 Artifacts from Datamuseum.dk's BitStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.unix.cbm900_partition import CBM900_Partition
from autoarchaeologist.unix.v7_filesystem import V7_Filesystem
from autoarchaeologist.unix.cbm900_ar import Ar
from autoarchaeologist.unix.cbm900_l_out import L_Out
from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic.samesame import SameSame

class CBM900(DDHF_Excavation):

    '''
    Two CBM900 hard-disk images, one also contains the four distribution
    floppy images.
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(CBM900_Partition)
        self.add_examiner(V7_Filesystem)
        self.add_examiner(Ar)
        self.add_examiner(L_Out)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(SameSame)

        self.from_bitstore(
            "30001199",
            "30001972",
        )

if __name__ == "__main__":
    main(
        CBM900,
        html_subdir="cbm900",
        ddhf_topic = "Commodore CBM-900",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Commodore/CBM900',
    )
