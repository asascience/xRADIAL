# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAPIBUILD= sphinx-apidoc
APIDOCOPTS    = -f -o
APIEXCLUDES   = ../*setup*
APIDOCROOT    = ..
SOURCEDIR     = source
BUILDDIR      = build
HTMLBUILDDIR  = $(BUILDDIR)/html

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Make the .rst source files using sphinx-apidoc, which traverses the modules
# and transforms the docstrings into reStructuredText format (.rst). These source
# .rst files are then used to make the HTML pages.
rst-src:
	$(SPHINXAPIBUILD) $(APIDOCOPTS) $(SOURCEDIR) $(APIDOCROOT) $(APIEXCLUDES)

# Create the HTML pages of the documentation
html:
	$(SPHINXBUILD) -b html -d $(BUILDDIR)/doctrees $(SOURCEDIR) $(HTMLBUILDDIR)
	@echo
	@echo "Build finished. The html pages are in $(HTMLBUILDDIR)."
