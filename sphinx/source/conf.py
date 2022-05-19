# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'gräf'
copyright = '2022, studiodb'
author = 'studiodb'

# The full version, including alpha/beta/rc tags
version = '1.0'
release = '1.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    
    'sphinx_copybutton'
    
    ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = 'furo'
# html_logo = 'logo_transparent.gif'
html_theme_options = {
    'dark_logo': 'logo_transparent.gif',
    'light_logo': 'logo_invert.gif',
    'sidebar_hide_name': True,
}

html_favicon = '_static/graf.ico'


html_sidebars = {
    "**": [
        "sidebar/brand.html",
        #"sidebar/version.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
    ]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# sphinx-build -b html sphinx/source/ docs/
# cd C:\Users\owner\Downloads\cmder\graf