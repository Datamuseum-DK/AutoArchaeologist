'''
   A standard main routine to remove some of the tedium
'''

import os

OK_ENVS = {
    "AUTOARCHAEOLOGIST_HTML_DIR": "html_dir",
    "AUTOARCHAEOLOGIST_LINK_PREFIX": "link_prefix",
}

def main(job, **kwargs):

    for key in os.environ:
        i = OK_ENVS.get(key)
        if i:
            kwargs[i] = os.environ[key]

    ctx = job(**kwargs)

    ctx.start_examination()
    baseurl = ctx.produce_html()

    print("Now point your browser at:")
    print("\t", baseurl)
    return ctx
