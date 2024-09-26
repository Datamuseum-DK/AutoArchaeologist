
BigText - Human readable text on paper-tape
===========================================

It was quite common to punch human readable information on the first part
of paper tapes like this:

.. code-block:: none

   ────────────────────────────────────
      ●●   ●●●    ●●          ●●   ●●●●
     ●  ●     ●  ●  ●        ●  ●    ● 
     ●  ●     ●  ●  ●        ●  ●   ●  
   ◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦◦
     ●  ●    ●    ●●   ●●●   ●  ●  ●●● 
     ●  ●   ●    ●  ●        ●  ●     ●
     ●  ●  ●     ●  ●        ●  ●     ●
     ●  ●  ●     ●  ●        ●  ●     ●
      ●●   ●●●●   ●●          ●●   ●●● 
   ────────────────────────────────────

This examiner tries to spot such sequences, and creates them
as child artifacts, but gives up if nothing is found in the
first kilobyte.

Currently the examiner recognizes the glyphs ``0123456789-*`` as
Data General punched them.
Adding more glyphs is easy, check the bottom of the source file.
