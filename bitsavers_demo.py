'''
   This is a small demo to show excavation of IMD files
   from bitsavers.org.

   There is NO way the world can ever thank Al Kossow enough for bitsavers.
'''


from autoarchaeologist import Excavation
from autoarchaeologist.bitsavers import bitsavers
from autoarchaeologist.vendor.ibm import midrange

class BitSaversIbm34(Excavation):
    '''
       Excavate the non-fe IBM/S34 floppies
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.decorator = bitsavers.Decorator(self)

        midrange.midrange_excavation(self)

        bitsavers.FromBitsavers(
            self,
            "-bits/IBM/System_34/S34_diag_set2",
            "-bits/IBM/System_34/S34_diags",
            "bits/IBM/System_34/",
        )

def main():
    ''' main functions '''
    ctx = BitSaversIbm34(
        download_links = True,
    )
    ctx.start_examination()
    ctx.produce_html()
    print("Now point your browser at", ctx.filename_for(ctx).link)

if __name__ == "__main__":
    main()
