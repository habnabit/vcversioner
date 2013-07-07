.. image:: https://travis-ci.org/habnabit/vcversioner.png

===========
vcversioner
===========

In-depth documentation:
https://docs.readthedocs.org/en/latest/getting_started.html

To quote myself:

    It's much more convenient to be able to use your version control system's
    tagging mechanism to derive a version number than to have to duplicate that
    information all over the place.

I ended up copy-pasting the same code into a couple different ``setup.py``
files just to avoid duplicating version information. But, copy-pasting is dumb
and unit testing ``setup.py`` files is hard. Thus: vcversioner.

Basic use
=========

vcversioner installs itself as a distutils hook, which makes its use
exceedingly simple::

  from setuptools import setup

  setup(
      # [...]
      setup_requires=['vcversioner'],
      vcversioner={},
  )

The presence of a ``vcversioner`` argument automagically activates vcversioner
and updates the project's version. In most cases, the following line should
also be added to ``MANIFEST.in``::

  include version.txt
