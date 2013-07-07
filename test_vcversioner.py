# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

from __future__ import unicode_literals

import pytest

import vcversioner


class FakePopen(object):
    def __init__(self, output):
        self.output = output

    def communicate(self):
        return self.output, None

    def __call__(self, *args, **kwargs):
        return self

class RaisingFakePopen(object):
    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        raise OSError('hi!')

empty = FakePopen(b'')
invalid = FakePopen(b'foob')
basic_version = FakePopen(b'1.0-0-gbeef')
dev_version = FakePopen(b'1.0-2-gfeeb')


def test_astounding_success(tmpdir):
    "Successful output from git is cached and returned."
    tmpdir.chdir()
    version = vcversioner.find_version(Popen=basic_version)
    assert version == ('1.0', '0', 'gbeef')
    with tmpdir.join('version.txt').open() as infile:
        assert infile.read() == '1.0-0-gbeef'

def test_no_git(tmpdir):
    "If git fails and there's no version.txt, abort."
    tmpdir.chdir()
    with pytest.raises(SystemExit) as excinfo:
        vcversioner.find_version(Popen=empty)
    assert excinfo.value.args[0] == 2
    assert not tmpdir.join('version.txt').check()

def test_when_Popen_raises(tmpdir):
    "If *spawning* git fails and there's no version.txt, abort."
    tmpdir.chdir()
    with pytest.raises(SystemExit) as excinfo:
        vcversioner.find_version(Popen=RaisingFakePopen())
    assert excinfo.value.args[0] == 2
    assert not tmpdir.join('version.txt').check()

def test_no_git_but_version_file(tmpdir):
    "If git fails but there's a version.txt, that's fine too."
    tmpdir.chdir()
    with tmpdir.join('version.txt').open('w') as outfile:
        outfile.write('1.0-0-gbeef')
    version = vcversioner.find_version(Popen=empty)
    assert version == ('1.0', '0', 'gbeef')

def test_Popen_raises_but_version_file(tmpdir):
    "If spawning git fails but there's a version.txt, that's similarly fine."
    tmpdir.chdir()
    with tmpdir.join('version.txt').open('w') as outfile:
        outfile.write('1.0-0-gbeef')
    version = vcversioner.find_version(Popen=RaisingFakePopen())
    assert version == ('1.0', '0', 'gbeef')

def test_invalid_git(tmpdir):
    "Invalid output from git is a failure too."
    tmpdir.chdir()
    with pytest.raises(SystemExit) as excinfo:
        vcversioner.find_version(Popen=invalid)
    assert excinfo.value.args[0] == 2
    assert not tmpdir.join('version.txt').check()

def test_invalid_version_file(tmpdir):
    "Invalid output in version.txt is similarly a failure."
    tmpdir.chdir()
    with tmpdir.join('version.txt').open('w') as outfile:
        outfile.write('foob')
    with pytest.raises(SystemExit) as excinfo:
        vcversioner.find_version(Popen=empty)
    assert excinfo.value.args[0] == 2

def test_dev_version(tmpdir):
    ".dev version numbers are automatically created."
    tmpdir.chdir()
    version = vcversioner.find_version(Popen=dev_version)
    assert version == ('1.0.dev2', '2', 'gfeeb')
    with tmpdir.join('version.txt').open() as infile:
        assert infile.read() == '1.0-2-gfeeb'

def test_dev_version_disabled(tmpdir):
    ".dev version numbers can also be disabled."
    tmpdir.chdir()
    version = vcversioner.find_version(Popen=dev_version, include_dev_version=False)
    assert version == ('1.0', '2', 'gfeeb')
    with tmpdir.join('version.txt').open() as infile:
        assert infile.read() == '1.0-2-gfeeb'

def test_custom_git_args(tmpdir):
    "The command to execute to get the version can be customized."
    tmpdir.chdir()
    popen = RaisingFakePopen()
    with pytest.raises(SystemExit):
        vcversioner.find_version(Popen=popen, git_args=('foo', 'bar'))
    assert popen.args[0] == ('foo', 'bar')

def test_custom_version_file(tmpdir):
    "The version.txt file can have a unique name."
    tmpdir.chdir()
    version = vcversioner.find_version(Popen=basic_version, version_file='custom.txt')
    assert version == ('1.0', '0', 'gbeef')
    with tmpdir.join('custom.txt').open() as infile:
        assert infile.read() == '1.0-0-gbeef'

def test_custom_version_file_reading(tmpdir):
    "The custom version.txt can be read from as well."
    tmpdir.chdir()
    with tmpdir.join('custom.txt').open('w') as outfile:
        outfile.write('1.0-0-gbeef')
    version = vcversioner.find_version(Popen=empty, version_file='custom.txt')
    assert version == ('1.0', '0', 'gbeef')

def test_version_file_disabled(tmpdir):
    "The version.txt file can be disabled too."
    tmpdir.chdir()
    version = vcversioner.find_version(Popen=basic_version, version_file=None)
    assert version == ('1.0', '0', 'gbeef')
    assert not tmpdir.join('version.txt').check()

def test_version_file_disabled_git_failed(tmpdir):
    "If version.txt is disabled and git fails, nothing can be done."
    tmpdir.chdir()
    with pytest.raises(SystemExit) as excinfo:
        vcversioner.find_version(Popen=empty, version_file=None)
    assert excinfo.value.args[0] == 2
    assert not tmpdir.join('version.txt').check()

def test_version_file_disabled_Popen_raises(tmpdir):
    "If version.txt is disabled and git fails to spawn, abort as well."
    tmpdir.chdir()
    with pytest.raises(SystemExit) as excinfo:
        vcversioner.find_version(Popen=RaisingFakePopen(), version_file=None)
    assert excinfo.value.args[0] == 2
    assert not tmpdir.join('version.txt').check()

def test_namedtuple():
    "The output namedtuple has attribute names too."

    version = vcversioner.find_version(Popen=basic_version, version_file=None)
    assert version.version == '1.0'
    assert version.commits == '0'
    assert version.sha == 'gbeef'

    version = vcversioner.find_version(Popen=dev_version, version_file=None)
    assert version.version == '1.0.dev2'
    assert version.commits == '2'
    assert version.sha == 'gfeeb'

def test_version_module_paths(tmpdir):
    "Version modules can be written out too."
    tmpdir.chdir()
    paths = ['foo.py', 'bar.py']
    vcversioner.find_version(
        Popen=basic_version, version_module_paths=paths)
    for path in paths:
        with open(path) as infile:
            assert infile.read() == """
# This file is automatically generated by setup.py.
__version__ = '1.0'
__sha__ = 'gbeef'
"""

class Struct(object):
    pass

def test_setup_astounding_success():
    "``find_version`` can be called through distutils too."
    dist = Struct()
    dist.metadata = Struct()
    vcversioner.setup(
        dist, 'vcversioner',
        {str('Popen'): basic_version, str('version_file'): None})
    assert dist.version == '1.0'
    assert dist.metadata.version == '1.0'
