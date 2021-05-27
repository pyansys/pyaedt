# Configuration file for the Sphinx_PyAEDT documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
import sys
import os
import pathlib
import warnings

import pyvista
import numpy as np
from sphinx_gallery.sorting import FileNameSortKey


local_path = os.path.dirname(os.path.realpath(__file__))
module_path = pathlib.Path(local_path)
root_path = module_path.parent.parent
sys.path.append(os.path.abspath(os.path.join(local_path)))
sys.path.append(os.path.join(root_path))

sys.path.append(os.path.join(root_path))
project = 'PyAEDT'
copyright = 'Copyright(c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited.'
author = 'Ansys Inc.'
documentation_dir = os.path.join(root_path, "Documentation")
if not os.path.exists(documentation_dir):
    os.mkdir(documentation_dir)
with open(os.path.join(root_path, "pyaedt", "version.txt"), "r") as f:
    version = f.readline()
# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx_PyAEDT extension module names here, as strings. They can be
# extensions coming with Sphinx_PyAEDT (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              "sphinx.ext.viewcode",
              "sphinx.ext.autosummary",
              "nbsphinx",
              "sphinx.ext.intersphinx",
              'sphinx.ext.napoleon',
              'sphinx.ext.coverage',
              "sphinx_copybutton",
              'recommonmark',
              'sphinx.ext.graphviz',
              'nbsphinx',
              'sphinx.ext.mathjax',
              'sphinx.ext.inheritance_diagram']


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx_PyAEDT. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'Python'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', "sphinx_boogergreen_theme_1", 'Thumbs.db', '.DS_Store', '*.txt']

inheritance_graph_attrs = dict(rankdir="RL", size='"8.0, 10.0"',
                               fontsize=14, ratio='compress')
inheritance_node_attrs = dict(shape='ellipse', fontsize=14, height=0.75,
                              color='dodgerblue1', style='filled')


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}



# The master toctree document.
master_doc = 'index'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# Manage errors
pyvista.set_error_output_file('errors.txt')

# Ensure that offscreen rendering is used for docs generation
pyvista.OFF_SCREEN = True

# Preferred plotting style for documentation
# pyvista.set_plot_theme('document')

# must be less than or equal to the XVFB window size
pyvista.rcParams['window_size'] = np.array([1024, 768])  # * 2

# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath('./images/'), 'auto-generated/')
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

# necessary when building the sphinx gallery

if os.name != 'posix':
    extensions.append('sphinx_gallery.gen_gallery')

    pyvista.BUILDING_GALLERY = True

    # suppress annoying matplotlib bug
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message='Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.',
    )

    sphinx_gallery_conf = {
        # convert rst to md for ipynb
        'pypandoc': True,
        # path to your examples scripts
        "examples_dirs": ["../../examples/"],
        # path where to save gallery generated examples
        "gallery_dirs": ["examples"],
        # Patter to search for examples files
        "filename_pattern": r"\.py",
        # Remove the "Download all examples" button from the top level gallery
        "download_all_examples": False,
        # Sort gallery examples by file name instead of number of lines (default)
        "within_subsection_order": FileNameSortKey,
        # directory where function granular galleries are stored
        "backreferences_dir": None,
        # Modules for which function level galleries are created.  In
        "doc_module": "ansys-mapdl-core",
        "image_scrapers": ('pyvista', 'matplotlib'),
        'ignore_pattern': 'flycheck*',
        "thumbnail_size": (350, 350),
        # 'first_notebook_cell': ("%matplotlib inline\n"
        #                         "from pyvista import set_plot_theme\n"
        #                         "set_plot_theme('document')"),
    }


# -- Options for HTML output -------------------------------------------------
html_show_sourcelink = True
html_theme = 'pyansys_sphinx_theme'
html_logo = "./Resources/logo-ansys.png"

html_theme_options = {
    "github_url": "https://github.com/pyansys/PyAEDT",
}

html_static_path = ['_static']

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'pyaedtdoc'
