#!/usr/bin/env python

from __future__ import print_function

import argparse
import subprocess
import os

parser = argparse.ArgumentParser(description='Emit docker flags for exposing environments')
parser.add_argument('--without-live',
                    dest='with_live',
                    action='store_false',
                    help='include the live environment')
parser.add_argument('--with-travis',
                    action='store_true',
                    default=(os.environ.get('TRAVIS') == os.environ.get('CI') == 'true'),
                    help='include most of the travis-ci environment')
parser.add_argument('--with-travis-all',
                    action='store_true',
                    help='include all of the travis-ci environment and probably incompatible with many base images')
parser.add_argument('--with-codecov',
                    action='store_true',
                    help='include the codecov environment')
parser.add_argument('--with-aws',
                    action='store_true',
                    help='include the aws environment')
args = parser.parse_args()

flags = []

if args.with_live:
    flags.extend([
        'CACHE_BUCKET',
        'DEPLOYMENT_BUCKET',
        'CI_SECRET_BUCKET',
        'CI_XCODE_KEYCHAIN',
        'CI_XCODE_KEYCHAIN_PASSWORD',
        'APPLE_DEVELOPMENT_TEAM_ID',
        'KEYSTORE',
        'KEYSTORE_PASS',
        'AWS_KMS_KEY_ID',  # not an official name, so it's here
    ])

if args.with_aws:
    flags.extend([
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
    ])

if args.with_travis or args.with_travis_all:
    flags.extend([
        # from https://docs.travis-ci.com/user/environment-variables
        # The following default environment variables are available to all
        # builds. Most are not included by default because they likely break
        # docker environments. Observe --with-travis-all to determine these.
        'CI',
        'TRAVIS',
        'CONTINUOUS_INTEGRATION',
        'DEBIAN_FRONTEND',
        'HAS_JOSH_K_SEAL_OF_APPROVAL',
        # Additionally, Travis CI sets environment variables you can use in your
        # build, e.g. to tag the build, or to run post-build deployments.
        'TRAVIS_BRANCH',
        'TRAVIS_BUILD_DIR',
        'TRAVIS_BUILD_ID',
        'TRAVIS_BUILD_NUMBER',
        'TRAVIS_COMMIT',
        'TRAVIS_COMMIT_RANGE',
        'TRAVIS_EVENT_TYPE',
        'TRAVIS_JOB_ID',
        'TRAVIS_JOB_NUMBER',
        'TRAVIS_OS_NAME',
        'TRAVIS_PULL_REQUEST',
        'TRAVIS_PULL_REQUEST_BRANCH',
        'TRAVIS_PULL_REQUEST_SHA',
        'TRAVIS_REPO_SLUG',
        'TRAVIS_SECURE_ENV_VARS',
        'TRAVIS_SUDO',
        'TRAVIS_TEST_RESULT',
        'TRAVIS_TAG',
        # Language-specific builds expose additional environment variables
        # representing the current version being used to run the build. Whether or
        # not they're set depends on the language you're using.
        'TRAVIS_DART_VERSION',
        'TRAVIS_GO_VERSION',
        'TRAVIS_HAXE_VERSION',
        'TRAVIS_JDK_VERSION',
        'TRAVIS_JULIA_VERSION',
        'TRAVIS_NODE_VERSION',
        'TRAVIS_OTP_RELEASE',
        'TRAVIS_PERL_VERSION',
        'TRAVIS_PHP_VERSION',
        'TRAVIS_PYTHON_VERSION',
        'TRAVIS_R_VERSION',
        'TRAVIS_RUBY_VERSION',
        'TRAVIS_RUST_VERSION',
        'TRAVIS_SCALA_VERSION',
        # Other software specific environment variables are set when the software or
        # service is installed or started, and contain the version number:
        'TRAVIS_MARIADB_VERSION',
        # The following environment variables are available for Objective-C builds.
        'TRAVIS_XCODE_SDK',
        'TRAVIS_XCODE_SCHEME',
        'TRAVIS_XCODE_PROJECT',
        'TRAVIS_XCODE_WORKSPACE',
    ])
    if args.with_travis_all:
        flags.extend([
            # usually disabled because many docker containers don't support
            # other locales to produce more minimal images
            'LC_ALL',
            # disabled because they will almost surely break anything relying on
            # it inside a docker environment
            'USER',
            'HOME',
            'LANG',
            # when using docker environments, the image will probably have a
            # self-contained installation.
            'RAILS_ENV',
            'RACK_ENV',
            'MERB_ENV',
            'JRUBY_OPTS',
            'JAVA_HOME',
        ])

docker_flags = ' -e ' + ' -e '.join(flags)

if args.with_codecov:
    docker_flags += ' ' + subprocess.check_output(
        'bash -c "bash <(curl -s https://codecov.io/env)"', shell=True).decode()

print(docker_flags, end='')
