# AutoArchaeologist

A Python Toolchest to dissect historic data media. 

The fundamental problem is how to explore the data from ancient and rare
computers, in a convenient and user-friendly way.

The AutoArchaeologist is a framework where plugins can be written to take
apart and present old data media, in a browser-friendly fashion.

# First Example: Commodore CBM900 Harddisk

Our first historic use of the AutoArchaeologist is now online:

	https://datamuseum.dk/aa/cbm900

This is the harddisk from datamuseum.dk's rare and running Commodore CBM-900
UNIX computer (https://datamuseum.dk/wiki/Commodore/CBM900)

In this case, the code in `unix/v7_filesystem.py` recognizes this as a little
endian Version 7 unix filesystem, and creates artifacts for the individual
files in the filesystem.

The `generic/ascii.py` code spots which files are text files, and thus we can
see how few fortunes, the CBM-900 came with, back in 1984:

	http://datamuseum.dk/aa/cbm900//5caa.html

More examples comming soon...
