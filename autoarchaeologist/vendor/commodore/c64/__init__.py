
from . import c64_basic
from . import c64_unicomal
from . import c64_disk

print("IMPORTED")

EXAMINERS = (
    c64_disk.C64Disk,
    c64_basic.C64Basic,
    c64_unicomal.C64Unicomal,
)
