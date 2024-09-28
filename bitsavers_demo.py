'''
   This is a small demo to show excavation of IMD files
   from bitsavers.org.

   There is NO way the world can ever thank Al Kossow enough for bitsavers.
'''

from autoarchaeologist.base import type_case
from autoarchaeologist.bitsavers import bitsavers

from autoarchaeologist.generic import textfiles

from autoarchaeologist.vendor.ibm import midrange

class BitSaversIbm34(bitsavers.Excavation):
    '''
       Excavate the non-fe IBM/S34 floppies
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.type_case = type_case.WellKnown("cp037")

        self.add_examiner(*midrange.examiners)
        #self.add_examiner(textfiles.TextFile)

        bitsavers.FromBitsavers(
            self,
            "-bits/IBM/System_34/S34_diag_set2",
            "-bits/IBM/System_34/S34_diags",
            "bits/IBM/System_34/",
        )

if __name__ == "__main__":
    ctx = BitSaversIbm34(
        download_links = True,
        # link_prefix = "https://phk.freebsd.dk/misc/aabs",
    )
    ctx.start_examination()
    ctx.produce_html()
    print("Now point your browser at", ctx.filename_for(ctx).link)
