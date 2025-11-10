
Ohio Scientific ("OSI") Examiners
=================================

Ohio Scientific several different computers using several
different CPUs running several different OSs.

So far there is support for 8" floppies with "OS65U" with
support for the filesystme and the BASIC programs.

The input format is compatible with the ``.65U`` files
used by the various OSI emulators, which is just a
concatenation of the async data in each of the 77 tracks,
without the parity bits, padded to 0xf00 bytes per track.

The BASIC is a Microsoft BASIC, the token list has been
extracted from the boot-code in the first six tracks.

More information about Ohio Scientific Inc computers at:

	https://osi.marks-lab.com/index.php

.. toctree::
   :maxdepth: 1
