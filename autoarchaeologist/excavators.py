import importlib.util
import os
import sys

# XXX: importing excavations this way is a kludge to avoid multiple rounds
#      of file splitting churn that would pollute diffs.. important as the
#      the most critical thing (for now) is avoiding changes to behaviour
def _import_name(import_name):
    import_path = f"{import_name}.py"
    spec = importlib.util.spec_from_file_location(import_name, import_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

from .ddhf.cpm_excavator import Cpm as cpm
cbm900 = _import_name("ddhf_cbm900").Cbm900
cr80 = _import_name("ddhf_cr80").Cr80Floppy
cr80_wang = _import_name("ddhf_cr80_wang").Cr80Wang
dask = _import_name("ddhf_dask").Dask
gier = _import_name("ddhf_gier").Gier
intel_isis = _import_name("ddhf_intel_isis").IntelISIS
r1k = _import_name("ddhf_r1k_tapes").R1k
r1k_backup = _import_name("ddhf_r1k_backup").R1kBackup
r1k_dfs = _import_name("ddhf_r1k_dfs").R1kDFS
rc3600 = _import_name("ddhf_rc3600").Rc3600
uug = _import_name("ddhf_dkuug").DkuugEuug
zilog_mcz = _import_name("ddhf_zilog_mcz").ZilogMCZ

# from .gier import configure_excavation as gier
# from .intel_isis import configure_excavation as intel_isis
# from .r1kdfs import configure_excavation as r1kdfs
# from .uug import configure_excavation as uug

__all__ = [
    "cbm900",
    "cpm",
    "cr80",
    "cr80_wang",
    "dask",
    "gier",
    "intel_isis",
    "r1k",
    "r1k_backup",
    "r1k_dfs",
    "rc3600",
    "uug",
    "zilog_mcz",
]

EXCAVATORS = {name:getattr(sys.modules[__name__], name) for name in __all__}

def excavator_by_name(excavator_name):
    if excavator_name not in EXCAVATORS:
        raise LookupError(f'no extractor named "{excavator_name}"')
    return EXCAVATORS[excavator_name]
