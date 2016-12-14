#!/usr/bin/env python

import argparse
import subprocess
import os
import shlex

from contextlib import contextmanager


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

parser = argparse.ArgumentParser(description='prepare needy libraries for nightly builds')
parser.add_argument('--needy',
                    required=True,
                    help='needy binary location')
parser.add_argument('--needy-args',
                    help='needy arguments')
parser.add_argument('--branch',
                    default='develop',
                    help='branch to set for libraries')
parser.add_argument('library',
                    nargs='+',
                    help='library to prepare')
args = parser.parse_args()

subprocess.check_call([args.needy, 'init'] + shlex.split(args.needy_args) + args.library)

for lib in args.library:
    subprocess.check_call([args.needy, 'dev', 'enable', lib])
    with cd(subprocess.check_output([args.needy, 'sourcedir', lib])):
        subprocess.check_call(['git', 'checkout', args.branch])
        subprocess.check_call(['git', 'submodule', 'update', '--init', '--recursive'])
