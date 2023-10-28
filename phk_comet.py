'''
Comet tapes
'''

import os
import sys

from autoarchaeologist.ddhf.decorated_context import DDHF_Excavation
from autoarchaeologist.type_case import DS2089

from autoarchaeologist.generic.tap_file import TAPfile
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.generic.textfiles import TextFiles
from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.icl.comet import CometTape

def comet_tapes(**kwargs):

    ''' Rational R1000/400 Backup tape '''

    ctx = DDHF_Excavation(
        ddhf_topic = "Rational R1000/400",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
        **kwargs,
    )
    ctx.type_case = DS2089()

    ctx.add_examiner(TAPfile)
    ctx.add_examiner(CometTape)

    ctx.add_examiner(Ascii)
    ctx.add_examiner(TextFiles)
    ctx.add_examiner(SameSame)

    for fn in sorted(sys.argv[1:]):
        print("FN", fn)
        if os.path.getsize(fn):
            try:
                ctx.add_file_artifact(fn)
            except Exception as e:
                print(fn, e)

    return ctx

if __name__ == "__main__":
    import subr_main
    subr_main.main(comet_tapes, subdir="comet", download_links=True)
