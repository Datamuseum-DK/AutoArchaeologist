#!/usr/bin/env python3

'''
    Datamuseum.dk HTML decorations

'''
import autoarchaeologist

class DDHF_Excavation(autoarchaeologist.Excavation):
    '''
        Excavation decorated for DataMuseum.dk
        --------------------------------------
    '''

    def __init__(self, ddhf_topic=None, ddhf_topic_link=None, **kwargs):
        self.ddhf_topic = ddhf_topic
        self.ddhf_topic_link = ddhf_topic_link
        super().__init__(**kwargs)

    def html_prefix_banner(self, fo, _this):
        fo.write('<table>\n')
        fo.write('<tr>\n')

        fo.write('<td style="vertical-align: middle;">\n')
        fo.write('<img src="https://datamuseum.dk/w/images/ddhf.png"/>\n')
        fo.write('</td>\n')

        fo.write('<td style="vertical-align: top;')
        fo.write(' padding-left: 40px; padding-right: 40px;">\n')
        fo.write('<h1>\n')
        fo.write('<html a="https://datamuseum.dk/"/>DataMuseum.dk</a>\n')
        fo.write('</h1>\n')
        if self.ddhf_topic:
            fo.write('<h2>\n')
            fo.write(self.ddhf_topic + '\n')
            fo.write('</h2>\n')
        fo.write('</td>\n')
        fo.write('<td style="vertical-align: top; padding: 10px;">\n')
        fo.write('<P>\n')
        fo.write('An automatic "excavation" of a thematic subset of\n')
        fo.write('<br>\n')
        fo.write('artifacts from\n')
        fo.write('<A href="https://datamuseum.dk/">Datamuseum.dk</A>\'s')
        fo.write(' <A href="https://datamuseum.dk/wiki/Bits:Keyword">BitArchive</A>.\n')
        fo.write('<p>\n')
        fo.write('See our Wiki for more about ')
        fo.write('<a href="' + self.ddhf_topic_link + '">')
        fo.write(self.ddhf_topic + '</a>\n')
        fo.write('<p>\n')
        fo.write('Produced by: ')
        fo.write(' <A href="https://github.com/Datamuseum-DK/AutoArchaeologist">')
        fo.write('AutoArchaeologist</A> - Free &amp; Open Source Software.\n')
        fo.write('</td>\n')
        fo.write('</tr>\n')
        fo.write('</table>\n')
        fo.write('<hr/>\n')
