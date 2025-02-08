#!/usr/bin/env python3

'''
   ICL Comet Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Comet(ddhf.DDHFExcavation):

    ''' All Comet artifacts '''

    BITSTORE = (
        "COMPANY/ICL/COMET",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ddhf.cpm_exc.std_cpm_excavation(self)

if __name__ == "__main__":
    ddhf.main(
        Comet,
        html_subdir="comet",
        ddhf_topic = 'ICL Comet',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/ICL_Comet'
    )
