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
import os
import sys
# import pydata_sphinx_theme

# import sys
# print(sys.version)
# import pkg_resources
# installed_packages = pkg_resources.working_set
# installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
#    for i in installed_packages])
# print(installed_packages_list)
# autodoc_mock_imports = ['osmnx']

sys.path.insert(0, os.path.abspath('../'))

# BUILDDIR      = docs

# -- Project information -----------------------------------------------------

project = 'Transit-routing'
copyright = '2023, Prateek Agarwal, Tarun Rambha'
author = 'Prateek Agarwal, Tarun Rambha'

# The full version, including alpha/beta/rc tags
release = 'Pending'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
	'sphinx.ext.autodoc', 
	'sphinx.ext.coverage', 
	'sphinx.ext.autosummary',
	'sphinx.ext.mathjax',
	'sphinx.ext.ifconfig',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
	'sphinx.ext.githubpages',
	# 'pydata_sphinx_theme',
	'sphinx.ext.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to SOURCE directory, that match files and
# directories to ignore when looking for SOURCE files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

todo_include_todos = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinxdoc'

html_theme_options = {
}
html_theme_path = ['']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']