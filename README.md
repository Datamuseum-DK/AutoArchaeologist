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

http://datamuseum.dk/aa/cbm900//5c/5caa31010.html

# Second Example: RegneCentralen GIER computer

The paper-tapes from this computer, like many other of 1950-1960
vintage, are not in ASCII but in a per-model, and in some cases,
per-installation character set.  The one on GIER isnt too bad
(https://datamuseum.dk/wiki/GIER/Flexowriter) but did cause a bit
of headache before we got a good HTML representation of overprinting
underlines and the "10" glyph.

GIER is of course the computer Peter Naur of Backus-Naur-Notatation
fame worked on, and his demonstration program is a good example of the output:

http://datamuseum.dk/aa/gier/9cb418c94.html

# Third Example: Regnecentralen RC3600/RC7000

RC7000 was a Data General Nova with a "RC7000" sticker, RC3600 was
Regnecentralens own reimplementation, and they were as a sort of swiss
army-knife computer doing everything from industrial control and monitoring,
to teaching programming in high-schools.

We have a rich software archive for these computers, and making sense
of them requires quite a number of "examiners".

Here is a saved COMAL program (https://datamuseum.dk/wiki/COMAL) to
solve second degree equations, written by a high-school student in 1981:

http://datamuseum.dk/aa/rc3600/7b/7b059e3b3.html

/phk
