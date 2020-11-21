'''
   A standard main routine to remove some of the tedium
'''

import os

OK_ENVS = {
    "AUTOARCHAEOLOGIST_HTML_DIR": "html_dir",
    "AUTOARCHAEOLOGIST_LINK_PREFIX": "link_prefix",
}

def main(job, subdir, **kwargs):
    if os.path.isdir("/critter/aa"):
        kwargs['html_dir'] = "/critter/aa/" + subdir
    else:
        kwargs['html_dir'] = "/critter/aa/" + subdir

    for key in os.environ:
        i = OK_ENVS.get(key)
        if i:
            kwargs[i] = os.environ[key]

    i = job(**kwargs)
    print("Now point your browser at:")
    print("\t", i.filename_for(i).link)
