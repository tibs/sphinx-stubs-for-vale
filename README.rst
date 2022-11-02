Stubs for Sphinx doles and directives, for use with Vale
========================================================

When using plain docutils, the roles and directives added by Sphinx are not
available. This can sometimes be a problem. This package aims to provide
very simple stubs that produce something "enough like" the expected results.

The initial aim is to make it easier to perform checks using Vale on documents
created with Sphinx.

Specifically, I want to be able to specify "this role/directive turns into
(the equivalent of) this normal reStructuredText", with preservation of
anything that a documentation linter like Vale might reasonably check (hint:
that means I don't particularly care about turning partial URLs into full
URLs, as in ``:doc:`` or ``:ref:``).


-----

Package setup done using advice from
https://mathspp.com/blog/how-to-create-a-python-package-in-2022
(since I use poetry anyway).

License
-------

Docutils itself is licensed under a Public Doman license, and Vale under an
MIT license. Since I don't believe I can actually release software to the
Public Domain from any of the countries in the UK, this package is released
under an MIT license.
