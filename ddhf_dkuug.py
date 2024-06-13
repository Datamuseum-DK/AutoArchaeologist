'''
DKUUG and EUUG Conference tapes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist import ddhf

from autoarchaeologist.base import excavation
from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame
from autoarchaeologist.unix import tar_file
from autoarchaeologist.unix import compress

class DkuugEuug(excavation.Excavation):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(compress.Compress)
        self.add_examiner(tar_file.TarFile)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)

class DDHF_DkuugEuug(ddhf.DDHF_Excavation):

    '''
    DKUUG and EUUG Conference tapes
    '''

    def __init__(self, **kwargs):
        super().__init__(DkuugEuug, **kwargs)

        self.from_bitstore(
            "30001252",
            "30001253",
        )

if __name__ == "__main__":
    ddhf.main(
        DkuugEuug,
        html_subdir="dkuug",
        ddhf_topic = "DKUUG/EUUG Conference tapes",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/DKUUG',
    )
