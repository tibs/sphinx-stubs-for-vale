"""Role and directive stubs to help Vale check Sphinx documents.
"""

from docutils import nodes
from docutils.parsers.rst import roles

__version__ = "0.1.0"


# XXX DEBUG XXX
print(f"Importing {__file__}")


def ref_role_fn(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Support Sphinx ``:ref:`` roles

    Either::

      :ref:`reference`

    or::

      :ref:`some text <reference>`

    Sphinx will use the ``reference`` to find a reStructuredText label
    of the same name, anywhere in the Sphinx document tree.
    In the first form, it will deduce what text to use for the link text
    from the labelled text.
    """
    print(f"role {name!r} with {rawtext!r} -> {text!r} at line {lineno}")

    if False:
        msg = inliner.reporter.error(
            f"This is a system message for role {name} text {rawtext!r}",
            line=lineno,
        )
        problem_text = inliner.problematic(rawtext, rawtext, msg)
        return [problem_text], [msg]
    else:
        if not options:
            options = {}
        node = nodes.reference(
            rawtext,
            f"REF:{text}",
            refuri=f"URL:{text}",
            **options,
        )
        return [node], []


roles.register_canonical_role('ref', ref_role_fn)
