'''
   Standardized CP/M Excavation stuff
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


from ..base import excavation
from ..base import type_case
from ..generic import samesame
from ..generic import textfiles
from ..DigitalResearch import cpm

cpm.cpm_filename_typecase.set_slug(0x5f, '_', '_')
cpm.cpm_filename_typecase.set_slug(0x3b, ';', ';')

class Cpm(excavation.Excavation):

    ''' Standard CP/M excavation '''

    def __init__(self, **kwargs):
        self.type_case = type_case.DS2089Cpm()
        self.add_examiner(cpm.CpmFileSystem)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)
