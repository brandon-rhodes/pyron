
``pyron`` -- The DRY Python package builder
===========================================

NOTE: the ``pyron`` command is still under development, and, in
particular, does not yet support projects with dependencies.

The ``pyron`` command is designed to eliminate the vast reptition that
characterizes the ``setup.py`` file of typical Python packages.  Instead
of needing a setup file, ``pyron`` simply inspects your package to
gather all of the information it needs to build, test, and distribute.
And thanks to the fact that ``pyron`` uses the ``distutils`` for source
distributions and the ``setuptools`` for building eggs, the results
should be compatible with everything else in Python.

Your project, at minimum, needs to consist of a directory with a
``README.txt`` and an ``__init__.py`` sitting next to each other inside
of it.  Here is where ``pyron`` looks for the information found in a
typical ``setup.py`` file:

**packages**

    Your project's ``README.txt`` file should be formatted as
    Restructured Text, and should look something like this::

        ``my.package`` -- Does exactly the things I need
        ------------------------------------------------

        There is, of course, no point in having a Python package
        around, taking up disk space, unless it does just what...

    Your package's name is assumed to be the string inside of the double
    back-quotes in your ``README.txt`` title.  It can have as many dots
    in it as you like; all of the packages except the last will be
    assumed to be namespace packages, and built as such.

**name**

    The source packages and eggs that you distribute will be given the
    same name as your Python package, per Python best practices.

**description**

    This is the string that takes up the rest of the first line of your
    ``README.txt`` file.

**long_description**

    The long description is built from the rest of your ``README.txt``
    file, with the first two non-blank lines (the title and underline)
    removed.

**namespace_packages**

    If your package name contains dots, then any parent packages are
    assumed to be namespace packages automatically.  If your package is
    named ``web.utils.url``, then ``web`` and ``web.utils`` will both be
    made namespace packages.

**version**

    The project version is taken from the ``__version__`` symbol inside
    of your package's ``__init__.py`` file.

As long as you make this information available using the above
techniques — which are merely a codification of already existing Python
best practices — then ``pyron`` will build both your ``setup.py`` and
your project for you without requiring any further intervention.

Using the ``pyron`` command
---------------------------

The ``pyron`` command-line tool is how you build and distribute packages
that follow the conventions outlined above.  A typical session might
look like::

    $ cd web.utils.url
    $ ls
    README.txt
    __init___.py
    rfc1738.py
    urlobj.py
    $ pyron sdist
    $ pyron bdist_egg
    $ ls
    README.txt
    __init___.py
    rfc1738.py
    urlobj.py
    web.utils.url-1.4-py2.5.egg
    web.utils.url-1.4.tar.gz
    $ pyron python
    >>>> import web.utils.url
    >>>> web.utils.url.__version__
    '0.4'
    >>>> ^D

If you peek under the hood, you will see that ``pyron`` does its work in
a hidden directory under your project directory named ``.pyron``, where
you can always look if you want to double-check the ``setup.py`` that
``pyrun`` is generating and using.
