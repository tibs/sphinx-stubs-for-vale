Vale innards
============

Looking at ``vale/internal/lint/rst.go`` on the ``v2`` branch.

``startRstServer(lib, exe)``

* doesn't do anything if ``rstRunning`` is already true
* finds Python using ``findPython`` based on the shebang string in the file named by ``lib``
* write the ``rstServer`` string to a temporary file
* runs it with (the) Python (it found) using ``exec.Command``, which starts a
  server at ``127.0.0.1`` on port ``7069``
* remembers the process PID and temporary file on the Linter
* sets the global ``rstRunning`` to true

``callRst`` generates the HTML:

  * on Windows (I think) runs ``<python> <rst2html>``
  * otherwise, runs ``<rst2html>`` - i.e., runs the program it found as ``rst2html``
  * gets the HTML that rst2html outputs on stdout, sanitises it, and returns it

It's *maybe* called by ``lintRST``

* ``lintRST`` takes a file ``f``

  * calculates ``rst2html`` <- first it finds of ``rst2html``,
    ``rst2html.py``, ``rst2html-3``, ``rst2html-3.py``

    - for me, ``rst2html`` is ``/opt/homebrew/bin/rst2html``::

        rst2html (Docutils 0.19, Python 3.10.8, on darwin)

    - for me, ``rst2html.py`` is ``<virtual-environment>/bin/rst2html.py`` and
      comes from ``docutils``::

        rst2html.py (Docutils 0.19, Python 3.10.8, on darwin)

      for devportal, it comes from ``sphinx`` and ``docutils`` and::

        rst2html.py (Docutils 0.17.1 [release], Python 3.10.1, on darwin)

    - I'm guessing that the ``-3`` variants are for people using a Python 2
      and Python 3 mixed environment. I don't have them.

  * calculates ``python`` <- first it finds of various plausible names for
    Python

  * Looks at ``l`` to work out what to do next:

    * if ``l.HasDir`` is false, it calls ``callRst(.., rst2html, python)``
    * otherwise, if ``startRstServer`` fails, also calls ``callRst(.., rst2html, python)``
    * otherwise, assuming the server started, POSTs the reST text to the
      server, which is basically what I want to happen, as the server is where
      I can make it load my new roles/directives.

Unfortunately, when I run::

  ; ~/sw/TibsAtWork/vale/bin/vale --output=line test.rst

it does::

    rst2html /opt/homebrew/bin/rst2html
    python /Users/tony.ibbs/Library/Caches/pypoetry/virtualenvs/sphinx-stubs-for-vale-lojeRBOe-py3.10/bin/python
    not l.HasDir - calling callRst
    cmd /opt/homebrew/bin/rst2html --quiet --halt=5 --report=5 --link-stylesheet --no-file-insertion --no-toc-backlinks --no-footnote-backlinks --no-section-numbering

    HTML:

    <div class="document" id="this-is-a-title">
    <h1 class="title">This is a title</h1>

    <p><a class="reference external" href="notawordcapital">An inline link</a>.</p>
    <p>:ref:`reference badreport capital`.</p>
    <p>:ref:`Reference text goodreport &lt;reference badreport capital&gt;`.</p>
    <p>:doc:`doc badreport capital`.</p>
    <p>:doc:`Document text goodreport &lt;doc badreport capital&gt;`.</p>
    </div>

So ``l.HasDir`` is false, and ``callRst`` is used, instead of the server.
Because of that, the ``unknown`` directive gets entirely thrown away - which
is the default behaviour of plain docutils.

One might *assume* that something called ``HasDir`` would be true for a file
on the filesystem...

Let's follow our ``l`` back. It's the context for the things in ``rst.go``,
and its of type ``*Linter``

Looking in ``internal/lint/lint.go`` we see:

.. code:: go

    // A Linter lints a File.
    type Linter struct {
        pids      []int
        temps     []*os.File
        Manager   *check.Manager
        glob      *glob.Glob
        client    *http.Client
        HasDir    bool
        nonGlobal bool
    }

So why is ``l.HasDir`` false, and what is it used for?

::

    ; rg HasDir
    cmd/vale/main.go
    57:             l.HasDir = status == 0

    internal/lint/rst.go
    192:    if !l.HasDir {
    193:        fmt.Println("not l.HasDir - calling callRst")

    internal/lint/lint.go
    25:     HasDir    bool

    internal/lint/fragment.go
    55:     l.HasDir = true

    internal/lint/adoc.go
    91:     if !l.HasDir {

It's set to true in ``internal/lint/fragment.go``:

.. code:: go

    func (l *Linter) lintFragments(f *core.File) error {
            var err error

            // We want to set up our processing servers as if we were dealing with
            // a directory since we likely have many fragments to convert.
            l.HasDir = true

``lintFragments`` is (maybe) called in ``internal/lint/lint.go`` - but if the
thing to be linted is a file with a known format, then the appropriate linting
function is called, so for an RST file, ``lintRST`` would be called. I assume
``lintFragments`` is used when a fragment of text is passed on the command
line (but that's a guess).

  Ah - looking at ``testdata/fixtures/fragments/``, I think it's used for
  fragments of text in source code - so for docstrings in Python, and so on.
  So that makes sense.

Looking at ``cmd/vale/main.go``, in the function ``doLint``, we see:

.. code:: go

    length := len(args)
    if length == 1 && looksLikeStdin(args[0]) == 1 {
        // Case 1:
        //
        // $ vale "some text in a string"
        linted, err = l.LintString(args[0])
    } else if length > 0 {
        // Case 2:
        //
        // $ vale file1 dir1 file2
        input := []string{}
        for _, file := range args {
            status := looksLikeStdin(file)
            if status == 1 {
                return linted, core.NewE100(
                    "doLint",
                    fmt.Errorf("argument '%s' does not exist", file),
                )
            }
            l.HasDir = status == 0
            input = append(input, file)
        }
        linted, err = l.Lint(input, glob)
    } else {
        // Case 3:
        //
        // $ cat file.md | vale
        stdin, err := io.ReadAll(os.Stdin)
        if err != nil {
            return linted, core.NewE100("doLint", err)
        }
        linted, err = l.LintString(string(stdin))
        if err != nil {
            return linted, core.NewE100("doLint", err)
        }
    }

So I'd expect that we'd hit the second case, and none of the command line
arguments would look like ``stdin``.

But *actually* when we get to the ``l.HasDir = status == 0``, it appears that
``status`` is ``-1``. Specifically, ``looksLikeStdin`` is returning -1 when
given ``test.rst``

In the same file:

.. code:: go

    func looksLikeStdin(s string) int {
        isDir := core.IsDir(s)
        if !(core.FileExists(s) || isDir) && s != "" {
            return 1
        } else if isDir {
            return 0
        }
        return -1
    }

and ``looksLikeStdin`` is *only* called from ``doLint``

The first branch of the ``if`` is when there's only one argument, and is
*meant* to "pretend" that a string arguemnt is sort-of stdin.

The second branch is meant to be detecting files or directories. And I think
that usage is what's broken - the function returns 1 if the argument is not a
file or a directory, and is not the empty string (fair enough), and 0 if it is
a directory.

So the check in Case 2 of ``doLint`` presumably *should* be:

.. code:: go

            l.HasDir = status != 1

because both files *and* directories exist "on the filesystem", i.e., have a
directory (and thus can be handed to a service).

And in fact, since the code in the loop would have returned if it found a
status value of 1, we can just do:

.. code:: go

            l.HasDir = true

So let's try experimentally making that change...

(actually, the *proper* change would be for ``looksLikeStdin`` not to worry
about what the thing is if it's not stdin-like, but let's not go there for now...)

...and now I've got the service running, because the HTML output looks like:

.. code:: html

    <div class="document" id="this-is-a-title">
    <h1 class="title">This is a title</h1>
    <p><a class="reference external" href="notawordcapital">An inline link</a>.</p>
    <p>:ref:`reference badreport capital`.</p>
    <p>:ref:`Reference text goodreport &lt;reference badreport capital&gt;`.</p>
    <p>:doc:`doc badreport capital`.</p>
    <p>:doc:`Document text goodreport &lt;doc badreport capital&gt;`.</p>
    <pre class="unknown_directive literal-block">
    .. unknown:: something notaword
       :more: something capital
    </pre>
    </div>

that is, it's doing the "I don't recognise this directive" thing.

...and now I've (finally!) got my logging working, which tells me::

  2022-11-16 17:19:13,297 INFO Could not import sphinx_stubs_for_vale: ModuleNotFoundError("No module named 'sphinx_stubs_for_vale'")

which is honestly not that surprising, as actually I haven't yet installed it.

So to cheat, I add the directory above this (which contains the
``sphinx_stubs_for_vale`` directory) to ``sys.path`` in the Python server code
(ick!), rebuild ``vale`` and then the log says that my import worked.

But the HTML returned is still:

.. code:: html

    <div class="document" id="this-is-a-title">
    <h1 class="title">This is a title</h1>
    <p><a class="reference external" href="notawordcapital">An inline link</a>.</p>
    <p><a class="reference external" href="reference badreport capital"></a>.</p>
    <p><a class="reference external" href="Reference text goodreport &lt;reference badreport capital&gt;"></a>.</p>
    <p><a class="reference external" href="doc badreport capital"></a>.</p>
    <p><a class="reference external" href="Document text goodreport &lt;doc badreport capital&gt;"></a>.</p>
    <pre class="unknown_directive literal-block">
    .. unknown:: something notaword
       :more: something capital
    </pre>
    </div>

so I haven't *quite* got things working yet - but at least it's a problem at
the Python end.

Aha! I'd managed to get some extra random characters into the regular
expression I was using to recognise the parts of the `:ref:` or `:doc:`.
With that mended, I get the following HTML:

.. code:: html

    <div class="document" id="this-is-a-title">
    <h1 class="title">This is a title</h1>
    <p><a class="reference external" href="notawordcapital">An inline link</a>.</p>
    <p><a class="reference external" href="reference badreport capital"></a>.</p>
    <p><a class="reference external" href="reference badreport capital">Reference text goodreport</a>.</p>
    <p><a class="reference external" href="doc badreport capital"></a>.</p>
    <p><a class="reference external" href="doc badreport capital">Document text goodreport</a>.</p>
    <pre class="unknown_directive literal-block">
    .. unknown:: something notaword
       :more: something capital
    </pre>
    </div>

and the actual output of my vale command becomes::

    test.rst:8:22:Test.spelling:'goodreport' does not seem to be a recognised word
    test.rst:12:21:Test.spelling:'goodreport' does not seem to be a recognised word

which means that I have my proof of concept (and also probably a bug in vale).

----------

How vale currently copes with such things
=========================================

See (closed) issue `Support Sphinx :doc: and :ref: by replacement`_

.. _`Support Sphinx :doc: and :ref: by replacement`: https://github.com/errata-ai/vale/issues/470

``rst2html`` (and ``rst2html.py``) put a ``problematic`` class onto the HTML
generated for roles they don't recognise. Vale then (in
``vale/inernal/lint/ast.go``) ignores text in such a class.

**Except** it doesn' always seem to work for me, on my work computer, for
reasons I've still to work out. I can see ``rst2html`` and ``rst2html.py``
both producing the ``problematic`` class, as indicated, but still get errors
from substitution rules.

Is that ``problematic`` class a docutils thing, or an ``rst2html`` thing?
...no, it should be OK, as it's a docutils thing, at least in docutils 0.19.

Of course, our Sphinx is using docutils 0.17.1

...It doesn't seem to matter whether I'm using docutils 0.17 or 0.19

My locally built vale seems to be showing the HTML produced as:

.. code:: html

   <tt class="docutils literal">kcat</tt> is a tool to explore data in Apache Kafka topics, check the :doc:`dedicate documentation &lt;/docs/products/kafka/howto/kcat&gt;` to understand how to use it with Aiven for Apache Kafka</li>
<li><dl class="first docutils">

where I'd expect (as produced by ``rst2html``):

.. code:: html

   <p class="first"><tt class="docutils literal">kcat</tt> is a tool to explore data in Apache Kafka topics, check the <a href="#system-message-5"><span class="problematic" id="problematic-5">:doc:`dedicate documentation &lt;/docs/products/kafka/howto/kcat&gt;`</span></a> to understand how to use it with Aiven for Apache Kafka</p>
   <div class="system-message" id="system-message-5">
   <p class="system-message-title">System Message: ERROR/3 (<tt class="docutils">/Users/tony.ibbs/work/devportal/docs/community/challenge/the-rolling-challenge.rst</tt>, line 99); <em><a href="#problematic-5">backlink</a></em></p>
   <p>Unknown interpreted text role &quot;doc&quot;.</p>

I've still not worked out what is weird on my system.

A quick look at docutils 0.17.1 versus 0.19 doesn't seem to show any obvious
differences that would cause this, and anyway I'm fairly sure I've shown this
using docutils 0.19.
