# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Skrypy Documentation'
copyright = '2025, olivier MONTIGON (IRMaGe)'
author = 'olivier MONTIGON (IRMaGe)'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'sphinx_rtd_theme'
html_theme = 'sphinxdoc'
html_static_path = ['_static']

html_context = {
    "display_github": True, # Integrate GitHub
    "github_user": "montigno", # Username
    "github_repo": "MyDoc", # Repo name
    "github_version": "main", # Version
    "conf_py_path": "/doc/", # Path in the checkout to the docs root
}
