
import os

from autoarchaeologist import Excavation

from autoarchaeologist.ddhf.bitstore import FromBitStore

from autoarchaeologist.generic.samesame import SameSame
from autoarchaeologist.generic.ascii import Ascii
from autoarchaeologist.unix.v7_filesystem import V7_Filesystem
from autoarchaeologist.unix.cbm900_ar import Ar
from autoarchaeologist.unix.cbm900_l_out import L_Out

def main():

    ctx = Excavation()

    ctx.add_examiner(V7_Filesystem)
    ctx.add_examiner(Ar)
    ctx.add_examiner(L_Out)
    ctx.add_examiner(Ascii)
    ctx.add_examiner(SameSame)

    FromBitStore(
        ctx,
        "_ddhf_bitstore_cache",
        "30001199",
    )

    # You could instead:
    # ctx.add_file_artifact("/some/v7pdpdisk.img")

    ctx.start_examination()

    try:
        os.mkdir("/tmp/_aa_cbm900")
    except FileExistsError:
        pass

    ctx.produce_html(
       html_dir="/tmp/_aa_cbm900",
       hexdump_limit=1<<10,
       # link_prefix="http://phk.freebsd.dk/misc/gier/",
       download_links=True,
    )

    print("Now point your browser at", ctx.link_prefix + '/' + ctx.filename_for(ctx))

if __name__ == "__main__":
    main()
