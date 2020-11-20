'''
   A standard main routine to remove some of the tedium
'''

import os

def main(job, subdir, **kwargs):
    if os.path.isdir("/critter/aa"):
        i = job(html_dir="/critter/aa/" + subdir, **kwargs)
    else:
        i = job(html_dir="/tmp/aa/" + subdir, **kwargs)
    print("Now point your browser at:")
    print("\t", i.filename_for(i).link)
