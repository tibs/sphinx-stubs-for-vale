"""Role and directive stubs to help Vale check Sphinx documents.
"""

from docutils import nodes
from docutils.parsers.rst.roles import normalized_role_options
from docutils.parsers.rst import roles

import re

__version__ = "0.1.0"


# XXX DEBUG XXX
import logging
logging.debug("Importing %r", __file__)


# If the text is not closely conforming to what we want, just pass it through
role_text_and_link_re = re.compile(
    r"""
    ^               # Start of string
    (?P<text>.*)    # Any text
    \s              # Some whitespace
    <(?P<link>.*)>  # < followed by any text followed by >
    $               # End of string
    """,
    re.VERBOSE | re.DOTALL,
)


def ref_role_fn(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Support Sphinx ``:ref:`` and ``:doc:`` roles

    Either::

      :ref:`reference`

    or::

      :ref:`some text <reference>`

    (or the same with ``:doc:``).

    For ``:ref:``, Sphinx will use the ``reference`` to find a reStructuredText
    label of the same name, anywhere in the Sphinx document tree.

    For ``:doc:`` it looks for a document.

    IF ``some text`` is not given, it will deduce what text to use for the link
    text from the labelled text or referenced document.

    For the purposes of Vale, it seems sensible to turn this into a reference,
    using the ``reference`` part as the "URL" (even though we don't work out
    what URL that would be), and ``some text`` as the link text.

    If ``some text`` isn't given, we don't know what text Sphinx would assign,
    so for the moment we'll just use an empty string there.
    """
    logging.debug("role name=%r rawtext=%r text=%r lineno=%r", name, rawtext, text, lineno)
    matches = role_text_and_link_re.fullmatch(text)
    if matches:
        # If the user gave us "some text" we can ask Vale to check it
        text = matches["text"]
        link = matches["link"]
        logging.debug("matches > text %r link %r", text, link)
    else:
        # If the user just gave us the reference, Sphinx would generate
        # the text from the target, so the best thing we can do is use ""
        #
        # Since Vale won't be able to tell this apart from any other reference
        # (that is, ``<a href=LINK></a>``) we have to hope there isn't a Vale
        # rule to check for an empty reference text.
        #
        # However, it's also hard to think of a "dummy" text that we could use,
        # that Vale won't complain about - especially given the language might
        # not be english.
        link = text
        text = ""
        logging.debug("NO match > text %r link %r", text, link)

    options = normalized_role_options(options)

    node = nodes.reference(
        rawtext,
        text,
        refuri=link,
        **options,
    )
    return [node], []


# While :ref: and :doc: are different to Sphinx, we can treat them as
# more-or-less the same thing
roles.register_canonical_role("ref", ref_role_fn)
roles.register_canonical_role("doc", ref_role_fn)
