#!/usr/bin/env python

import argparse
import os
import sys
import tarfile
import shutil
import glob
import fnmatch

parser = argparse.ArgumentParser(description='Produce distribution from input paths')
parser.add_argument('--output-directory',
                    default='deploy',
                    required=True,
                    help='directory to place deployment path')
parser.add_argument('input',
                    nargs='+',
                    help='input patterns to include')
parser.add_argument('--suffix',
                    help='path suffix')
parser.add_argument('--exclude',
                    default=[],
                    nargs='*',
                    help='file patterns to exclude')
args = parser.parse_args()


def destination_path():
    if 'TRAVIS_BRANCH' not in os.environ:
        print('TRAVIS_BRANCH not defined')
        sys.exit(1)

    if 'TRAVIS_REPO_SLUG' not in os.environ:
        print('TRAVIS_REPO_SLUG not defined')
        sys.exit(1)

    if 'TRAVIS_COMMIT' not in os.environ and 'TRAVIS_TAG' not in os.environ:
        print('TRAVIS_COMMIT or TRAVIS_TAG must be defined')
        sys.exit(1)

    tag_or_commit = os.environ.get('TRAVIS_TAG') or os.environ.get('TRAVIS_COMMIT')
    destination = os.path.join(os.environ['TRAVIS_REPO_SLUG'], tag_or_commit)

    if args.suffix:
        destination = os.path.join(destination, args.suffix)

    return destination


def tarfile_excludes(tarinfo):
    for exclude_pattern in args.exclude:
        if fnmatch.fnmatch(tarinfo.name, exclude_pattern):
            return None
    print('+ {}'.format(tarinfo.name))
    return tarinfo

destination_dir = os.path.join(args.output_directory, destination_path())
destination_file = os.path.join(destination_dir, 'dist.tar.gz')
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)
if os.path.exists(destination_file):
    os.remove(destination_file)

with tarfile.open(destination_file, 'w:gz') as tar:
    for input_pattern in args.input:
        for path in glob.iglob(input_pattern):
            tar.add(path, arcname=os.path.basename(path), filter=tarfile_excludes)
