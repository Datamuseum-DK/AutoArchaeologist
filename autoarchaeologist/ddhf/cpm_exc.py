'''
   Standardized CP/M Excavation stuff
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


from ..base import type_case
from ..generic import samesame
from ..generic import textfiles
from ..DigitalResearch import cpm

cpm.cpm_filename_typecase.set_slug(0x5f, '_', '_')
cpm.cpm_filename_typecase.set_slug(0x3b, ';', ';')

def std_cpm_excavation(exc):
    ''' Standard CP/M excavation '''

    exc.type_case = type_case.DS2089Cpm()
    exc.add_examiner(cpm.CpmFileSystem)
    exc.add_examiner(textfiles.TextFile)
    exc.add_examiner(samesame.SameSame)
