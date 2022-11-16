#!/usr/bin/env python

"""This is broadly what Vale does - without bothering with making it a service.
"""

import sys

try:
    import locale

    locale.setlocale(locale.LC_ALL, "")
except:
    pass

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import docutils

print(f"Docutils from {docutils.__file__}\n")

from docutils import nodes
from docutils.core import publish_parts
from docutils.parsers.rst.states import Body

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG,
)

# Setup our own special magic
try:
    import sphinx_stubs_for_vale
except ImportError:
    logging.error('Unable to impirt sphinx stubs')

GITHUB_DISPLAY = True


def unknown_directive(self, type_name):
    lineno = self.state_machine.abs_line_number()
    (
        indented,
        indent,
        offset,
        blank_finish,
    ) = self.state_machine.get_first_known_indented(0, strip_indent=False)
    text = "\n".join(indented)
    if GITHUB_DISPLAY:
        cls = ["unknown_directive"]
        result = [nodes.literal_block(text, text, classes=cls)]
        return result, blank_finish
    else:
        return [nodes.comment(text, text)], blank_finish


def do_stuff(data):
    """"""
    Body.unknown_directive = unknown_directive
    overrides = {
        "leave-comments": True,
        "file_insertion_enabled": False,
        "footnote_backlinks": False,
        "toc_backlinks": False,
        "sectnum_xform": False,
        "report_level": 5,
        "halt_level": 5,
    }
    html = publish_parts(data, settings_overrides=overrides, writer_name="html")[
        "html_body"
    ]
    return html
    # return html.encode("utf-8")


TEST_DATA = """\
This is a title
===============

Vanilla text
------------
This is some text.

`An inline link <some-url>`_.

.. image:: some-url
   :alt: Some text

Spinx text
----------
:ref:`text-reference`.

:ref:`Text <text-reference>`.

:doc:`/some/location`.

:doc:`Text </some/location>`.

.. unknown:: something
   :more: something else
"""


if __name__ == "__main__":
    html = do_stuff(TEST_DATA)
    print(html)
