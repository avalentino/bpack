# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from setup import cfg                                           # noqa: E402


# -- Project information -----------------------------------------------------

project = 'bpack'
copyright = '2020-2021, Antonio Valentino'
author = 'Antonio Valentino'

# The full version, including alpha/beta/rc tags
release = cfg['version']

master_doc = 'index'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
]

try:
    import sphinxcontrib.spelling                               # noqa: F401
except ImportError:
    pass
else:
    extensions.append('sphinxcontrib.spelling')

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# theme configuration
html_theme_options = {
    # 'vcs_pageview_mode': 'blob',
}

# theme context
html_context = {
    # 'github_url': 'https://github.com/avalentino/bpack/',
    'display_github': True,
    'github_user': 'avalentino',
    'github_repo': 'bpack',
    'github_version': 'main',
    'conf_py_path': '/docs/',  # Path in the checkout to the docs root
}

html_last_updated_fmt = ''


# -- Options for LaTeX output ------------------------------------------------
latex_documents = [
    # (startdocname, targetname, title, author, theme, toctree_only)
    (project, project + '.tex', 'Binary data structures (un-)Packing library',
     author, 'manual', False),
]

latex_domain_indices = False

latex_elements = {
    # 'papersize': 'a4paper',
    'pointsize': '12pt',
}

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------
# autoclass_content = 'both'
autodoc_member_order = 'groupwise'
# autodoc_default_options = {}
autodoc_mock_imports = []
for module_name in ['bitarray', 'bitstruct', 'numpy']:
    try:
        __import__(module_name)
    except ImportError:
        autodoc_mock_imports.append(module_name)


# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'https://docs.python.org/3/': None,
    'https://numpy.org/doc/stable/': None,
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
