
'''
   CR80 Executable

   See: 30004610
'''

from ..generic import octetview as ov

from .cr80_util import *

class ProgDesc(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=True,
            magic_=ov.Be16,
            size_=ov.Be16,
            name_=Text6,
            xversion_=ov.Be16,
            xpgtype_=ov.Be16,
            xstart_=ov.Be16,
            xmicro_=ov.Be16,
            f08_=ov.Be16,
            xpgmem_=ov.Be16,
            f11_=ov.Be16,
            f12_=ov.Be16,
            f13_=ov.Be16,
            f14_=ov.Be16,
            f15_=ov.Be16,
            f16_=ov.Be16,
            f17_=ov.Be16,
            f18_=ov.Be16,
            f19_=ov.Be16,
            f20_=ov.Be16,
            f21_=ov.Be16,
            f22_=ov.Be16,
            f23_=ov.Be16,
            f24_=ov.Be16,
            f25_=ov.Be16,
            f26_=ov.Be16,
            f27_=ov.Be16,
            f28_=ov.Be16,
            f29_=ov.Be16,
            f30_=ov.Be16,
            f31_=ov.Be16,
        )

class ProcDesc(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=True,
            magic_=ov.Be16,
            ptr_=ov.Be16,
            name_=Text6,
            saccess_=ov.Be16,
            slogpcb_=ov.Be16,
            sparent_=ov.Be16,
            schild_=ov.Be16,
            snext_=ov.Be16,
            sfwlnk_=ov.Be16,
            srvlnk_=ov.Be16,
            sstate_=ov.Be16,
            sawait_=ov.Be16,
            serror_=ov.Be16,
            f14_=ov.Be16,
            scpu_=ov.Be16,
            srdyq_=ov.Be16,
            sprio_=ov.Be16,
            sprogr_=ov.Be16,
            smicro_=ov.Be16,
            sbase_=ov.Be16,
            sabase_=ov.Be16,
            ssect_=ov.Be16,
            ssize_=ov.Be16,
            sexect_=ov.Be16,
            f25_=ov.Be16,
            f26_=ov.Be16,
            screat_=ov.Be16,
            f28_=ov.Be16,
            f29_=ov.Be16,
            rlink_=ov.Be16,
            ssignal_=ov.Be16,
            swork_=ov.Be16,
            smsglim_=ov.Be16,
            smsgusd_=ov.Be16,
            smsgqh_=ov.Be16,
            f36_=ov.Be16,
            sansqh_=ov.Be16,
            f38_=ov.Be16,
            ssymqh_=ov.Be16,
            f40_=ov.Be16,
        )

class DataDesc(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=True,
            magic_=ov.Be16,
            size_=ov.Be16,
            xprocessnamename_=Text6,
            xcpuname_=Text6,
            xpriority_=ov.Be16,
            xcapabilities_=ov.Be16,
            mem_clain_=ov.Be16,
            exec_size_=ov.Be16,
            xfds_=ov.Be16,
            xibs_=ov.Be16,
            xsts_=ov.Be16,
            xxfs_=ov.Be16,
            xmsgs_=ov.Be16,
            zero17_=ov.Be16,
            xprmem_=ov.Be16,
            iopart_=ov.Be16,
            xuserid0_=ov.Be16,
            xuserid1_=ov.Be16,
            zero22_=ov.Be16,
            zero23_=ov.Be16,
            xprlevel_=ov.Be16,
            bound_=ov.Be16,
            reg26_=ov.Be16,
            reg27_=ov.Be16,
            reg28_=ov.Be16,
            reg29_=ov.Be16,
            reg30_=ov.Be16,
            reg31_=ov.Be16,
            reg32_=ov.Be16,
            reg33_=ov.Be16,
            reg34_=ov.Be16,
            reg35_=ov.Be16,
            reg36_=ov.Be16,
            reg37_=ov.Be16,
            timer_=ov.Be16,
            psw_=ov.Be16,
            zero40_=ov.Be16,
            f41_=ov.Be16,
            f42_=ov.Be16,
            f43_=ov.Be16,
            f44_=ov.Be16,
            f45_=ov.Be16,
            f46_=ov.Be16,
            f47_=ov.Be16,
            f48_=ov.Be16,
            f49_=ov.Be16,
            f50_=ov.Be16,
            f51_=ov.Be16,
            f52_=ov.Be16,
            f53_=ov.Be16,
            f54_=ov.Be16,
            f55_=ov.Be16,
            f56_=ov.Be16,
            f57_=ov.Be16,
            f58_=ov.Be16,
            f59_=ov.Be16,
            zero60_=ov.Be16,
        )

class AmosExec(ov.OctetView):

    def __init__(self, this):
        if not this.has_type("CR80FILE"):
            return
        super().__init__(this)
        y0 = ov.Be16(self, 0)
        if y0.val != 1:
            return
        y1 = ov.Be16(self, 2)
        if y1.val < 0x20 or y1.val * 2 >= len(this) - 2:
            return
        y2 = ov.Be16(self, y1.val * 2)
        if y2.val != 2:
            return
        self.prog = ProgDesc(self, 0).insert()

        self.data = DataDesc(self, self.prog.size.val << 1).insert()

        this.add_type("CR80_EXEC")
        self.render()

