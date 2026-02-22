# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AutoArchaeologist'
copyright = '2024, Poul-Henning Kamp'
author = 'Poul-Henning Kamp'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_logo = "../logo/aa_logo.svg"

html_sidebars = {
    '**': [
        'navigation.html',
    ],
}

import sys
from pathlib import Path
sys.path.insert(0, str(Path('..', 'autoarchaeologist').resolve()))

