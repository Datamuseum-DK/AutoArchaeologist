#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   List of colors for coloring categories.

   The first 8 colors are from:

   Colorblind barrier-free color palette
  
   From Okabe & Ito (2002):
      Color Universal Design (CUD)
      - How to make figures and presentations that are friendly to Colorblind people
  
   https://jfly.uni-koeln.de/html/color_blind/
  
   Which I found via:

   https://betterfigures.org/2015/06/23/picking-a-colour-scale-for-scientific-graphics/

'''

COLORS = [
   [ 255* 0//100, 255* 0//100, 255* 0//100],   # Black
   [ 255*90//100, 255*60//100, 255* 0//100],   # Orange
   [ 255*35//100, 255*70//100, 255*90//100],   # Sky blue
   [ 255* 0//100, 255*60//100, 255*50//100],   # Bluish green
   [ 255*95//100, 255*90//100, 255*25//100],   # Yellow
   [ 255* 0//100, 255*45//100, 255*70//100],   # Blue
   [ 255*80//100, 255*40//100, 255* 0//100],   # Vermillion
   [ 255*80//100, 255*60//100, 255*70//100],   # Reddish purple

   # These additional colors are not colorblind safe, but contrast decently

   [ 0xa6, 0xce, 0xe3],                        # Light blue
   [ 0xb2, 0xdf, 0x8a],                        # Light green
   [ 0xe3, 0x1a, 0x1c],                        # Red
   [ 0x6a, 0x3d, 0x9a],                        # Purple
   [ 0xff, 0xff, 0xb3],                        # Light yellow
   [ 0xfc, 0xcd, 0xe5],                        # Light Pink
   [ 0xd9, 0xd9, 0xd9],                        # Light Grey
   [ 0x8c, 0x51, 0x0a],                        # Brown
]
