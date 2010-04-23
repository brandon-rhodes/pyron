
``pyron`` -- The DRY Python package builder
===========================================

Pyron is a simple tool that lets you develop and distribute Python
packages while avoiding the complexity of writing and maintaining a
"setup.py" file.  With Pyron, each package you are developing needs only
a small ``pyron.ini`` file, whose format is designed to help you avoid
repeating yourself.

Developing with Pyron
---------------------

To see Pyron in action, install Ian Bicking's virtualenv_ tool and
create a virtual environment to serve as your development environment.
Install the Pyron package there. ::

    $ virtualenv dev
    $ cd dev
    $ source bin/activate
    (dev)$ ls
    bin/  include/  lib/
    (dev)$ pip install pyron
    ...
    Successfully installed argparse pyron

Two packages that are currently developed using Pyron, and that we can
use here as samples, are the ``cursive`` tools that you might have seen
on the `Python Package Index`_.  You can check out their development
trees very simply, using Mercurial::

    (dev)$ hg clone http://bitbucket.org/brandon/cursivepymag
    (dev)$ hg clone http://bitbucket.org/brandon/cursivetools
    (dev)$ ls
    bin/  cursivepymag/  cursivetools/  include/  lib/

You can always identify a Pyron-powered development package because it
will have a ``pyron.ini`` file at the top level. ::

    (dev)$ ls cursivetools
    README.txt  __init__.py  cursive.py  entry_points.ini  pyron.ini  wc.py

The ``pyron.ini`` file contains all of the essential metadata about a
project that cannot be easily introspected from its contents::

    (dev)$ cat cursivetools/pyron.ini
    [package]
    name = cursive.tools
    author = Brandon Craig Rhodes <brandon@rhodesmill.org>
    url = http://bitbucket.org/brandon/cursivetools/
    requires = docutils

The version, however, is taken directly from the ``__version__`` symbol
in the package's ``__init__.py`` file, to avoid having to maintain the
same version number in two different places. ::

    (dev)$ grep __version__ cursivetools/__init__.py
    __version__ = '0.3'

The description that is placed on the Python Package Index for this
package will be copied verbatim from ``README.txt``, which should start
with a title that can be used for the short summary description on the
Package Index::

    (dev)$ head -6 cursivetools/README.txt
    
    Tools for authoring restructured text files
    ===========================================
    
    This package provides a ``cursive`` command that is intended to become
    the core of a whole set of tools for working with `reStructured Text`_

By pulling version information from the package's code and documentation
from its ``README.txt``, Pyron not only enforces good Python community
customs, but it avoids either making the developer repeat the same
information in several different places, or else write complicated
``setup.py`` code to pull the information in from elsewhere.

Activating Development Packages
-------------------------------

When developing a package, you not only need its files on your hard
drive, but you need for Python itself to be able to see the package.
This involves three things:

* Python should be able to import the package.
* The package's entry points should be available.
* Any console scripts the package declares should be installed.

None of these three things are true yet of the development packages in
our example, because Python cannot yet see them. ::

    (dev)$ python -c 'import cursive.tools'
    Traceback (most recent call last):
      ...
    ImportError: No module named cursive.tools

To make the development copy of this package "appear" in our virtual
environment, we have to use the Pyron command-line tool to activate it.
You can use the Pyron "status" (abbreviated "st") command to see which
development packages are currently active in the virtual environment,
and the "add" command to activate further projects::

    (dev)$ pyron status
    No packages are under development in this environment.
    (dev)$ pyron add cursivetools 
    (dev)$ pyron status
    /home/brandon/dev/cursivetools
        Package: cursive.tools
        Console-script: cursive (cursive.tools.cursive:console_script_cursive)

As you can see from the "status" command, the ``cursive.tools`` package
is now under active development.  This means that Python will now be
able to import it!  You can verify that Python is now loading the
package directly from its development directory::

    (dev)$ python
    >>> import cursive.tools
    >>> cursive.tools.__file__
    '/home/brandon/dev/cursivetools/__init__.py'
    >>> exit()

And the console script declared by ``cursive.tools`` is now available in
the virtual environment as well. ::

    (dev)$ bin/cursive
    Usage: cursive [options] <command> [options]
    ...
    Available Commands:

     wc - Word count

The above output shows both that the ``cursive.tools`` package is fully
up and running, and also that its one built-in entry point, that defines
the "wc" sub-command, is active as well.  To add another entry point, we
can activate the ``cursive.pymag`` package that we downloaded earlier as
well::

    (dev)$ pyron add cursivepymag
    (dev)$ pyron st
    /home/brandon/dev/cursivetools
        Package: cursive.tools
            Console-script: cursive (cursive.tools.cursive:console_script_cursive)

    /home/brandon/dev/cursivepymag
        Package: cursive.pymag

    (dev)$ bin/cursive
    Usage: cursive [options] <command> [options]
    ...
    Available Commands:

     pymag - Convert an RST document to Python Magazine Ceres markup
     wc    - Word count

You can see that a second sub-command, "pymag", is available because the
``cursive.pymag`` package declares an entry point for it.  Activating a
development project with Pyron has all of the old advantages of running
a ``setup.py`` with the ``develop`` sub-command, but has the additional
features that metadata is always pulled live from the ``pyron.ini`` file
(rather than being copied into an ``egg-info`` directory and growing
stale), and that you can easily turn packages back off.  You can turn
them off with the "remove" or "rm" sub-command by either naming their
directory, or using the package name itself::

    (dev)$ pyron rm ./cursivepymag
    (dev)$ pyron rm cursive.tools
    (dev)$ pyron st
    No packages are under development in this environment.
    (dev)$ python -c 'import cursive.tools'
    Traceback (most recent call last):
      ...
    ImportError: No module named cursive.tools
    (dev)$ bin/cursive
    zsh: no such file or directory: bin/cursive

This makes it easy to quickly adjust the mix of active development
packages as you write and test your code.

Deploying Packages
------------------

Sharing a Python package with other people typically has two steps: you
need to first *register* the package on the `Python Package Index`_ so
that its name, description, and other metadata shows up, and then you
need to provide a ``.tar.gz`` file that other people can download and
install using ``pip`` or ``easy_install``.  These two steps are quite
easy to accomplish using Pyron::

    (dev)$ pyron register cursivetools
    (dev)$ pyron upload cursivetools

With both of these sub-commands, and in fact with most Pyron commands,
you should follow the command with the names of one or more directories
where a Pyron-powered development package lives.  If you provide no
directory name, then the current directory is searched, so the two
commands above could also have been written::

    (dev)$ cd cursivetools
    (dev)$ pyron register
    (dev)$ pyron upload
    (dev)$ cd ..

If you want the source distribution written to a local file without
being made available yet for the entire world, use the "sdist"
sub-command.  It prints out the name of the file it creates. ::

    (dev)$ pyron sdist cursivetools
    ./cursive.tools-0.3.tar.gz

Note that when Pyron builds a ``.tar.gz`` distribution, it includes
most of the files in the development package, except that Pyron:

* Ignores hidden files that begin with a period.
* Ignores files whose names end with ``.pyc`` and ``.pyo``.
* Does not include the ``pyron.ini`` file.
* Does not include the ``entry_points.ini`` file (if any).

Before you run the "sdist" or "upload" sub-command, therefore, you
should make sure that no temporary data or other unnecessary files are
sitting inside of the development package's directory, or those files
will be included in the archive.

Note that Pyron has *no* provision for building, or distributing,
C-language extensions or shared libraries or other binary code that has
to be compiled.  If your package needs to be compiled to operate, then
you should use the normal ``setup.py`` mechanism; that's what it's good
for: situations that are already complicated, where you need lots of
control over a difficult build process.  Pyron, by constrast, is
intended only for distributing pure-Python packages.


.. _virtualenv: http://pypi.python.org/pypi/virtualenv/
.. _Python Package Index: http://pypi.python.org/pypi/
