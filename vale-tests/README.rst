Testing how Vale works
======================

Checking for where spellcheck and substitution check is done, in Sphinx
entities.

It's probably enough just to check spelling reporting, really.

``test.rst`` looks like:

.. I can't use the ``include`` directive for a GitHub document, as they
   don't support it (it is technically a possible security issue). So
   I'm going to repdroduce the file by copying it, and trying to remember
   to update the copy when I change the file (!)

.. code:: reStructuredText
    :number-lines:

    This is a title
    ===============

    `An inline link <notaword capital>`_.

    :ref:`reference badreport capital`.

    :ref:`Reference text goodreport <reference badreport capital>`.

    :doc:`doc badreport capital`.

    :doc:`Document text goodreport <doc badreport capital>`.

    .. unknown:: something notaword
       :more: something capital

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
