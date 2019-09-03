### Documentation

If you want to build the source code documentation HTML pages, you'll need to install the `requirements-docs.txt`. This project uses [Sphinx](www.sphinx-doc.org). A Makefile has been provided to make the process a bit easier.

To update the documentation:

```bash
$ make clean   # remove old files from build directory
$ make rst-src # generate the reStructuredText source files
$ make html    # build the HTML pages from .rst
```
