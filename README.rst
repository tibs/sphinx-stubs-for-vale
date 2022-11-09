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

The problem
-----------

Vale (which is wonderful) doesn't understand reStructuredText directly (it's
written in Go and there's no good library for it to use). So it starts a
docutils service and sends files to that, converting the reStructuredText to
HTML, which it does understand.

.. note:: And it does some serious magic that I don't (yet) understand so that
          it can refer back to the original lines in the reStructuredText, not
          to the line numbers in the HTML.

This works very well for "plain" reStructuredText, but less well for
documentation managed with Sphinx, because Sphinx provides extra roles and
directives which the standard docutils library doesn't understand.

For instance, we use the `:ref:` and `:doc:` roles in the Aiven developer
documentation. Naturally, docutils itself doesn' undertand these extra
constructs. And for reasons that I'll explain another time, it's not practical
for Vale to run Sphinx itself over the documentation (short form: Sphinx does
not support looking at indvidual files without looking over the entire
document tree - that's part of its design).

Sphinx runs a docutils server with code something like:

.. code:: python

    try:
        from http.server import BaseHTTPRequestHandler, HTTPServer
    except ImportError:
        from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

    import docutils

    from docutils import nodes
    from docutils.core import publish_parts
    from docutils.parsers.rst.states import Body


    def unknown_directive(self, type_name):
        lineno = self.state_machine.abs_line_number()
        (
            indented,
            indent,
            offset,
            blank_finish,
        ) = self.state_machine.get_first_known_indented(0, strip_indent=False)
        text = "\n".join(indented)
        cls = ["unknown_directive"]
        result = [nodes.literal_block(text, text, classes=cls)]
        return result, blank_finish


    def do_stuff(data):
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
        return html   # it actuall does ``return html.encode("utf-8")``

And if I give it the following data:

.. code:: reStructuredText

    This is a title
    ===============

    This is some text.

    `An inline link <some-url>`_.

    :ref:`text-reference`.

    :ref:`Text <text-reference>`.

    :doc:`/some/location`.

    :doc:`Text </some/location>`.

    .. unknown:: something
       :more: something else

then it produces the following HTML:

.. code:: html

    <div class="document" id="this-is-a-title">
    <h1 class="title">This is a title</h1>
    <p>This is some text.</p>
    <p><a class="reference external" href="some-url">An inline link</a>.</p>
    <p>:ref:`text-reference`.</p>
    <p>:ref:`Text &lt;text-reference&gt;`.</p>
    <p>:doc:`/some/location`.</p>
    <p>:doc:`Text &lt;/some/location&gt;`.</p>
    <pre class="unknown_directive literal-block">
    .. unknown:: something
    :more: something else
    </pre>
    </div>

For the roles, Vale should not be given ``text-reference`` or
``/some/location`` to check, nor should it be given the same wrapped in
``&lt;`` and ``&gt;`` - we don't want to be checking filenames or URLs.

For the directive, Vale gets to see the actual reStructuredText, and it's
quite possible that it shouldn't be show some of the included text - that
depends on the directive.


.. note:: If I take out the ``unknown_directive`` support, the HTML is
   instead:

   .. code:: html

        <div class="document" id="this-is-a-title">
        <h1 class="title">This is a title</h1>
        <p>This is some text.</p>
        <p><a class="reference external" href="some-url">An inline link</a>.</p>
        <p>:ref:`text-reference`.</p>
        <p>:ref:`Text &lt;text-reference&gt;`.</p>
        <p>:doc:`/some/location`.</p>
        <p>:doc:`Text &lt;/some/location&gt;`.</p>
        </div>

    and the unrecognised directive just disappears. Which is arguably worse.

Acknowledgements
----------------

Package setup done using advice from
https://mathspp.com/blog/how-to-create-a-python-package-in-2022
(since I use poetry anyway).

License
-------

Docutils itself is licensed under a Public Doman license, and Vale under an
MIT license. Since I don't believe I can actually release software to the
Public Domain from any of the countries in the UK, this package is released
under an MIT license.
