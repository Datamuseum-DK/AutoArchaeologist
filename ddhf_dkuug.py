'''
DKUUG and EUUG Conference tapes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation, main

from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.unix.tar_file import TarFile
from autoarchaeologist.unix.compress import Compress

class DkuugEuug(DDHF_Excavation):

    '''
    DKUUG and EUUG Conference tapes
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(Compress)
        self.add_examiner(TarFile)
        self.add_examiner(Ascii)
        self.add_examiner(SameSame)

        self.from_bitstore(
            "30001252",
            "30001253",
        )

if __name__ == "__main__":
    main(
        DkuugEuug,
        html_subdir="dkuug",
        ddhf_topic = "DKUUG/EUUG Conference tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/DKUUG',
    )
