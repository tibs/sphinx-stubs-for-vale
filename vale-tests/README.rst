Testing how Vale works
======================

Checking for where spellcheck and substitution check is done, in Sphinx
entities.

It's probably enough just to check spelling reporting, really.

``test.rst`` looks like:

.. include:: test.rst
   :code: reStructuredText
   :number-lines:

::
    ; vale --version
    vale version 2.21.0

We want to see the reports for ``goodreport``.

We don't want to see the reports for ``badreport`` or ``capital``::

    ; vale --output=line test.rst
    test.rst:6:17:Test.spelling:'badreport' does not seem to be a recognised word
    test.rst:6:27:Test.substitutions:Use 'Capital' instead of 'capital'.
    test.rst:8:22:Test.spelling:'goodreport' does not seem to be a recognised word
    test.rst:8:44:Test.spelling:'badreport' does not seem to be a recognised word
    test.rst:8:54:Test.substitutions:Use 'Capital' instead of 'capital'.
    test.rst:10:11:Test.spelling:'badreport' does not seem to be a recognised word
    test.rst:10:21:Test.substitutions:Use 'Capital' instead of 'capital'.
    test.rst:12:21:Test.spelling:'goodreport' does not seem to be a recognised word
    test.rst:12:37:Test.spelling:'badreport' does not seem to be a recognised word
    test.rst:12:47:Test.substitutions:Use 'Capital' instead of 'capital'.
