'''
   CR80 Wang WCS floppy disks
   ~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf

from autoarchaeologist.base import excavation
from autoarchaeologist.generic import samesame
from autoarchaeologist.Wang import wang_wps
from autoarchaeologist.Wang import wang_text

class Cr80Wang(excavation.Excavation):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(wang_wps.WangWps)
        self.add_examiner(wang_text.WangText)
        self.add_examiner(samesame.SameSame)

class DDHF_Cr80Wang(ddhf.DDHF_Excavation):
    def __init__(self, **kwargs):
        super().__init__(Wang, **kwargs)

        self.from_bitstore(
            "CR/CR80/DOCS",
        )

if __name__ == "__main__":
    ddhf.main(
        DDHF_Cr80Wang,
        html_subdir="cr80_wang",
        ddhf_topic = "CR80 Wang WCS documentation floppies",
        ddhf_topic_link = 'https://datamuseum.dk/wiki',
    )
