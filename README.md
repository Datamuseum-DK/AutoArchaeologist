# AutoArchaeologist

A Python Toolchest to excavate data media into static HTML pages.

Old, rare and often historically important computers uses weird character sets,
data formats and data media, which makes it hard to study and appreciate what
those historic artifacts teach us.

This project is a toolbox for presenting datamedia as static HTML files which
can be browsed with any browser either locally or from a webserver.

Here are two examples to show what we are talking about:

# First Example: Commodore CBM900 Harddisk

This excavation contains harddisk images from Commodore CBM900 machines.
This was a prototype UNIX computer which Commodore abandoned after building
a few hundred prototypes of which only a dozen or so has survived.
(More info: https://datamuseum.dk/wiki/Commodore/CBM900)

Start with this deep link, which shows you the contents of the "fortune"
file, and use the various links to navigate the full excavation:

https://datamuseum.dk/aa/cbm900//5c/5caa31010.html

# Second Example: RegneCentralen GIER computer

The GIER was the second computer designed and built in Denmark,
and like most computers built in the 1950-1960 timeframe, it had
it's own character set, data formats and used paper-tape as
datamedia.

GIER is of course also the computer Peter Naur, of Backus-Naur-Notatation
fame worked on, and his demonstration program is a good example of the output:

https://datamuseum.dk/aa/gier/9c/9cb418c94.html

You can find a full list of the excavations maintained by datamuseum.dk here:

https://datamuseum.dk/aa

# Try it out

If you want to try for yourself, you can run this example::

	python3 bitsavers_demo.py

This will fetch some IBM S/34 floppies from bitsavers.org and excavate them
into your /tmp directory, this probably takes some minutes, and then tell
you to point your browser at the excavation.

# Read more

I have started a proper documentation project, but there is not much
in it yet, I plan to flesh it out as I saunter through the source code
in the future:

https://datamuseum.dk/aa/docs/

# Quo Vadis ?

The development in this project is very much driven by the needs
of datamuseum.dk's data preservation activities, but we are trying
very hard to move in the direction of generality and usability.

Right now you probably need at least basic python skills to use
this, but you can probably get far by playing with and modifying
the scripts in the ddhf subdirectory.

(Yes, I'm working on a command line interface)

/phk
