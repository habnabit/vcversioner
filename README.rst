.. image:: https://travis-ci.org/habnabit/vcversioner.png

===========
vcversioner
===========

`Elevator pitch`_: you can write a ``setup.py`` with no version information
specified, and vcversioner will find a recent, properly-formatted git tag and
extract a version from it.

It's much more convenient to be able to use your version control system's
tagging mechanism to derive a version number than to have to duplicate that
information all over the place. I eventually ended up copy-pasting the same
code into a couple different ``setup.py`` files just to avoid duplicating
version information. But, copy-pasting is dumb and unit testing ``setup.py``
files is hard. This code got factored out into vcversioner.


Basic usage
-----------

vcversioner installs itself as a setuptools hook, which makes its use
exceedingly simple::

  from setuptools import setup

  setup(
      # [...]
      setup_requires=['vcversioner'],
      vcversioner={},
  )

The presence of a ``vcversioner`` argument automagically activates vcversioner
and updates the project's version. The parameter to the ``vcversioner``
argument can also be a dict of keyword arguments which |find_version|
will be called with.

To allow tarballs to be distributed without requiring a ``.git`` directory,
vcversioner will also write out a file named (by default) ``version.txt``.
Then, if there is no git or git is unable to find any version information,
vcversioner will read version information from the ``version.txt`` file.
However, this file needs to be included in a distributed tarball, so the
following line should be added to ``MANIFEST.in``::

  include version.txt

This isn't necessary if ``setup.py`` will always be run from a git checkout,
but otherwise is essential for vcversioner to know what version to use.

The name ``version.txt`` also can be changed by specifying the ``version_file``
parameter. For example::

  from setuptools import setup

  setup(
      # [...]
      setup_requires=['vcversioner'],
      vcversioner={
          'version_file': 'custom_version.txt',
      },
  )


Non-hook usage
--------------

It's not necessary to depend on vcversioner; while `pip`_ will take care of
dependencies automatically, sometimes having a self-contained project is
simpler. vcversioner is a single file which is easy to add to a project. Simply
copy the entire ``vcversioner.py`` file adjacent to the existing ``setup.py``
file and update the usage slightly::

  from setuptools import setup
  import vcversioner

  setup(
      # [...]
      version=vcversioner.find_version().version,
  )

This is necessary because the ``vcversioner`` distutils hook won't be
available.


Version modules
---------------

``setup.py`` isn't the only place that version information gets duplicated. By
generating a version module, the ``__init__.py`` file of a package can import
version information. For example, with a package named ``spam``::

  from setuptools import setup

  setup(
      # [...]
      setup_requires=['vcversioner'],
      vcversioner={
          'version_module_paths': ['spam/_version.py'],
      },
  )

This will generate a ``spam/_version.py`` file that defines ``__version__`` and
``__sha__``. Then, in ``spam/__init__.py``::

  from spam._version import __version__, __sha__

Since this acts like (and *is*) a regular python module, changing
``MANIFEST.in`` is not required.


Customizing git commands
------------------------

vcversioner by default executes ``git describe --tags --long`` to get version
information. This command will output a string that describes the current
commit, using all tags (as opposed to just unannotated tags), and always output
the long format (``1.0-0-gdeadbeef`` instead of just ``1.0`` if the current
commit is tagged).

However, sometimes this isn't sufficient. If someone wanted to only use
annotated tags, the git command could be amended like so::

  from setuptools import setup

  setup(
      # [...]
      setup_requires=['vcversioner'],
      vcversioner={
          'git_args': ['git', 'describe', '--long'],
      },
  )

The ``git_args`` parameter must always be a list of strings, which will not be
interpreted by the shell. This is the same as what ``subprocess.Popen``
expects.


Development versions
--------------------

vcversioner can also automatically make a version that corresponds to a commit
that isn't itself tagged. Following `PEP 386`_, this is done by adding a
``.dev`` suffix to the version specified by a tag on an earlier commit. For
example, if the current commit is three revisions past the ``1.0`` tag, the
computed version will be ``1.0.dev3``.

This behavior can be disabled by setting the ``include_dev_version`` parameter
to ``False``. In that case, the aforementioned untagged commit's version would
be just ``1.0``.


Sphinx documentation
--------------------

`Sphinx`_ documentation is yet another place where version numbers get
duplicated. Fortunately, since sphinx configuration is python code, vcversioner
can be used there too. Assuming vcversioner is installed system-wide, this is
quite easy. Simply change your ``conf.py`` to include::

  import vcversioner
  version = release = vcversioner.find_version().version

If your current working directory while building documentation is not your
project root, this will make a duplicate ``version.txt`` file in the
documentation directory. In this case, it might be preferable to call
|find_version| with ``version_file=None`` or ``version_file='../version.txt'``.

If vcversioner is bundled with your project instead of relying on it being
installed, you might have to add the following to your ``conf.py`` before
``import vcversioner``::

  import sys, os
  sys.path.insert(0, os.path.abspath('..'))

This line, or something with the same effect, is sometimes already present when
using the sphinx ``autodoc`` extension.


Read the Docs
~~~~~~~~~~~~~

Using vcversioner is even possible when building documentation on `Read the
Docs`_. If vcversioner is bundled with your project, nothing further needs to
be done. Otherwise, you need to tell Read the Docs to install vcversioner
before it builds the documentation. This means using a ``requirements.txt``
file.

If your project is already set up to install dependencies with a
``requirements.txt`` file, add ``vcversioner`` to it. Otherwise, create a
``requirements.txt`` file. Assuming your documentation is in a ``docs``
subdirectory of the main project directory, create ``docs/requirements.txt``
containing a ``vcversioner`` line.

Then, make the following changes to your project's configuration: (Project
configuration is edited at e.g.
https://readthedocs.org/dashboard/vcversioner/edit/)

- Check the checkbox under **Use virtualenv**.
- If there was no ``requirements.txt`` previously, set the **Requirements
  file** to the newly-created one, e.g. ``docs/requirements.txt``.


.. _Elevator pitch: http://en.wikipedia.org/wiki/Elevator_pitch
.. _pip: https://pypi.python.org/pypi/pip
.. _PEP 386: http://www.python.org/dev/peps/pep-0386/
.. _Sphinx: http://sphinx-doc.org
.. _Read the Docs: https://readthedocs.org/

.. |find_version| replace:: ``find_version``
