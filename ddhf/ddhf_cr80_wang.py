'''
   CR80 Wang WCS floppy disks
   ~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf

from autoarchaeologist.generic import samesame
from autoarchaeologist.Wang import wang_wps
from autoarchaeologist.Wang import wang_text

class Wang(ddhf.DDHF_Excavation):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(wang_wps.WangWps)
        self.add_examiner(wang_text.WangText)
        self.add_examiner(samesame.SameSame)

        self.from_bitstore(
            "CR/CR80/DOCS",
        )

if __name__ == "__main__":
    ddhf.main(
        Wang,
        html_subdir="cr80_wang",
        ddhf_topic = "CR80 Wang WCS documentation floppies",
        ddhf_topic_link = 'https://datamuseum.dk/wiki',
    )
