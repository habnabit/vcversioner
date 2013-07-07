# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

from __future__ import print_function, unicode_literals

import collections
import os
import subprocess
import sys


Version = collections.namedtuple('Version', 'version commits sha')


_print = print
def print(*a, **kw):
    _print('vcversioner:', *a, **kw)


def find_version(include_dev_version=True, version_file='version.txt',
                 git_args=('git', 'describe', '--tags', '--long'),
                 Popen=subprocess.Popen):

    # try to pull the version from git, or (perhaps) fall back on a
    # previously-saved version.
    try:
        proc = Popen(git_args, stdout=subprocess.PIPE)
    except OSError:
        raw_version = None
    else:
        raw_version = proc.communicate()[0].strip().decode()
        version_source = 'git'

    # git failed if the string is empty
    if not raw_version:
        if version_file is None:
            print('%r failed' % (git_args,))
            sys.exit(2)
        elif not os.path.exists(version_file):
            print("%r failed and %r isn't present." % (git_args, version_file))
            print("are you installing from a github tarball?")
            sys.exit(2)
        print("couldn't determine version from git; using %r" % version_file)
        with open(version_file, 'r') as infile:
            raw_version = infile.read()
        version_source = repr(version_file)


    # try to parse the version into something usable.
    try:
        tag_version, commits, sha = raw_version.rsplit('-', 2)
    except ValueError:
        print("%r (from %s) couldn't be parsed into a version" % (
            raw_version, version_source))
        sys.exit(2)

    if version_file is not None:
        with open(version_file, 'w') as outfile:
            outfile.write(raw_version)

    if commits == '0' or not include_dev_version:
        version = tag_version
    else:
        version = '%s.dev%s' % (tag_version, commits)

    return Version(version, commits, sha)


def setup(dist, attr, value):
    dist.version = find_version(**value)
