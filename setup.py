# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

import vcversioner

# not this again
from setuptools import setup

setup(
    name='vcversioner',
    version=vcversioner.find_version().version,
    py_modules=['vcversioner'],
    entry_points={
        'distutils.setup_keywords': ['vcversioner = vcversioner:setup'],
    },
)
