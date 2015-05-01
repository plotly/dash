"""
shared options and groups

The principle here is to define options once, but *not* instantiate them
globally. One reason being that options with action='append' can carry state
between parses. pip parse's general options twice internally, and shouldn't
pass on state. To be consistent, all options will follow this design.

"""
from __future__ import absolute_import

import copy
from optparse import OptionGroup, SUPPRESS_HELP, Option
from pip.index import PyPI
from pip.locations import CA_BUNDLE_PATH, USER_CACHE_DIR, src_prefix


def make_option_group(group, parser):
    """
    Return an OptionGroup object
    group  -- assumed to be dict with 'name' and 'options' keys
    parser -- an optparse Parser
    """
    option_group = OptionGroup(parser, group['name'])
    for option in group['options']:
        option_group.add_option(option.make())
    return option_group


class OptionMaker(object):
    """Class that stores the args/kwargs that would be used to make an Option,
    for making them later, and uses deepcopy's to reset state."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def make(self):
        args_copy = copy.deepcopy(self.args)
        kwargs_copy = copy.deepcopy(self.kwargs)
        return Option(*args_copy, **kwargs_copy)

###########
# options #
###########

help_ = OptionMaker(
    '-h', '--help',
    dest='help',
    action='help',
    help='Show help.')

isolated_mode = OptionMaker(
    "--isolated",
    dest="isolated_mode",
    action="store_true",
    default=False,
    help=(
        "Run pip in an isolated mode, ignoring environment variables and user "
        "configuration."
    ),
)

require_virtualenv = OptionMaker(
    # Run only if inside a virtualenv, bail if not.
    '--require-virtualenv', '--require-venv',
    dest='require_venv',
    action='store_true',
    default=False,
    help=SUPPRESS_HELP)

verbose = OptionMaker(
    '-v', '--verbose',
    dest='verbose',
    action='count',
    default=0,
    help='Give more output. Option is additive, and can be used up to 3 times.'
)

version = OptionMaker(
    '-V', '--version',
    dest='version',
    action='store_true',
    help='Show version and exit.')

quiet = OptionMaker(
    '-q', '--quiet',
    dest='quiet',
    action='count',
    default=0,
    help='Give less output.')

log = OptionMaker(
    "--log", "--log-file", "--local-log",
    dest="log",
    metavar="path",
    help="Path to a verbose appending log."
)

log_explicit_levels = OptionMaker(
    # Writes the log levels explicitely to the log'
    '--log-explicit-levels',
    dest='log_explicit_levels',
    action='store_true',
    default=False,
    help=SUPPRESS_HELP)

no_input = OptionMaker(
    # Don't ask for input
    '--no-input',
    dest='no_input',
    action='store_true',
    default=False,
    help=SUPPRESS_HELP)

proxy = OptionMaker(
    '--proxy',
    dest='proxy',
    type='str',
    default='',
    help="Specify a proxy in the form [user:passwd@]proxy.server:port.")

retries = OptionMaker(
    '--retries',
    dest='retries',
    type='int',
    default=5,
    help="Maximum number of retries each connection should attempt "
         "(default %default times).")

timeout = OptionMaker(
    '--timeout', '--default-timeout',
    metavar='sec',
    dest='timeout',
    type='float',
    default=15,
    help='Set the socket timeout (default %default seconds).')

default_vcs = OptionMaker(
    # The default version control system for editables, e.g. 'svn'
    '--default-vcs',
    dest='default_vcs',
    type='str',
    default='',
    help=SUPPRESS_HELP)

skip_requirements_regex = OptionMaker(
    # A regex to be used to skip requirements
    '--skip-requirements-regex',
    dest='skip_requirements_regex',
    type='str',
    default='',
    help=SUPPRESS_HELP)

exists_action = OptionMaker(
    # Option when path already exist
    '--exists-action',
    dest='exists_action',
    type='choice',
    choices=['s', 'i', 'w', 'b'],
    default=[],
    action='append',
    metavar='action',
    help="Default action when a path already exists: "
    "(s)witch, (i)gnore, (w)ipe, (b)ackup.")

cert = OptionMaker(
    '--cert',
    dest='cert',
    type='str',
    default=CA_BUNDLE_PATH,
    metavar='path',
    help="Path to alternate CA bundle.")

client_cert = OptionMaker(
    '--client-cert',
    dest='client_cert',
    type='str',
    default=None,
    metavar='path',
    help="Path to SSL client certificate, a single file containing the "
         "private key and the certificate in PEM format.")

index_url = OptionMaker(
    '-i', '--index-url', '--pypi-url',
    dest='index_url',
    metavar='URL',
    default=PyPI.simple_url,
    help='Base URL of Python Package Index (default %default).')

extra_index_url = OptionMaker(
    '--extra-index-url',
    dest='extra_index_urls',
    metavar='URL',
    action='append',
    default=[],
    help='Extra URLs of package indexes to use in addition to --index-url.')

no_index = OptionMaker(
    '--no-index',
    dest='no_index',
    action='store_true',
    default=False,
    help='Ignore package index (only looking at --find-links URLs instead).')

find_links = OptionMaker(
    '-f', '--find-links',
    dest='find_links',
    action='append',
    default=[],
    metavar='url',
    help="If a url or path to an html file, then parse for links to archives. "
         "If a local path or file:// url that's a directory, then look for "
         "archives in the directory listing.")

# TODO: Remove after 6.0
use_mirrors = OptionMaker(
    '-M', '--use-mirrors',
    dest='use_mirrors',
    action='store_true',
    default=False,
    help=SUPPRESS_HELP)

# TODO: Remove after 6.0
mirrors = OptionMaker(
    '--mirrors',
    dest='mirrors',
    metavar='URL',
    action='append',
    default=[],
    help=SUPPRESS_HELP)

allow_external = OptionMaker(
    "--allow-external",
    dest="allow_external",
    action="append",
    default=[],
    metavar="PACKAGE",
    help="Allow the installation of a package even if it is externally hosted",
)

allow_all_external = OptionMaker(
    "--allow-all-external",
    dest="allow_all_external",
    action="store_true",
    default=False,
    help="Allow the installation of all packages that are externally hosted",
)

trusted_host = OptionMaker(
    "--trusted-host",
    dest="trusted_hosts",
    action="append",
    metavar="HOSTNAME",
    default=[],
    help="Mark this host as trusted, even though it does not have valid or "
         "any HTTPS.",
)

# Remove after 7.0
no_allow_external = OptionMaker(
    "--no-allow-external",
    dest="allow_all_external",
    action="store_false",
    default=False,
    help=SUPPRESS_HELP,
)

# Remove --allow-insecure after 7.0
allow_unsafe = OptionMaker(
    "--allow-unverified", "--allow-insecure",
    dest="allow_unverified",
    action="append",
    default=[],
    metavar="PACKAGE",
    help="Allow the installation of a package even if it is hosted "
    "in an insecure and unverifiable way",
)

# Remove after 7.0
no_allow_unsafe = OptionMaker(
    "--no-allow-insecure",
    dest="allow_all_insecure",
    action="store_false",
    default=False,
    help=SUPPRESS_HELP
)

# Remove after 1.5
process_dependency_links = OptionMaker(
    "--process-dependency-links",
    dest="process_dependency_links",
    action="store_true",
    default=False,
    help="Enable the processing of dependency links.",
)

requirements = OptionMaker(
    '-r', '--requirement',
    dest='requirements',
    action='append',
    default=[],
    metavar='file',
    help='Install from the given requirements file. '
    'This option can be used multiple times.')

editable = OptionMaker(
    '-e', '--editable',
    dest='editables',
    action='append',
    default=[],
    metavar='path/url',
    help=('Install a project in editable mode (i.e. setuptools '
          '"develop mode") from a local project path or a VCS url.'),
)

src = OptionMaker(
    '--src', '--source', '--source-dir', '--source-directory',
    dest='src_dir',
    metavar='dir',
    default=src_prefix,
    help='Directory to check out editable projects into. '
    'The default in a virtualenv is "<venv path>/src". '
    'The default for global installs is "<current dir>/src".'
)

use_wheel = OptionMaker(
    '--use-wheel',
    dest='use_wheel',
    action='store_true',
    help=SUPPRESS_HELP,
)

no_use_wheel = OptionMaker(
    '--no-use-wheel',
    dest='use_wheel',
    action='store_false',
    default=True,
    help=('Do not Find and prefer wheel archives when searching indexes and '
          'find-links locations.'),
)

cache_dir = OptionMaker(
    "--cache-dir",
    dest="cache_dir",
    default=USER_CACHE_DIR,
    metavar="dir",
    help="Store the cache data in <dir>."
)

no_cache = OptionMaker(
    "--no-cache-dir",
    dest="cache_dir",
    action="store_false",
    help="Disable the cache.",
)

download_cache = OptionMaker(
    '--download-cache',
    dest='download_cache',
    default=None,
    help=SUPPRESS_HELP)

no_deps = OptionMaker(
    '--no-deps', '--no-dependencies',
    dest='ignore_dependencies',
    action='store_true',
    default=False,
    help="Don't install package dependencies.")

build_dir = OptionMaker(
    '-b', '--build', '--build-dir', '--build-directory',
    dest='build_dir',
    metavar='dir',
    help='Directory to unpack packages into and build in.'
)

install_options = OptionMaker(
    '--install-option',
    dest='install_options',
    action='append',
    metavar='options',
    help="Extra arguments to be supplied to the setup.py install "
         "command (use like --install-option=\"--install-scripts=/usr/local/"
         "bin\"). Use multiple --install-option options to pass multiple "
         "options to setup.py install. If you are using an option with a "
         "directory path, be sure to use absolute path.")

global_options = OptionMaker(
    '--global-option',
    dest='global_options',
    action='append',
    metavar='options',
    help="Extra global options to be supplied to the setup.py "
         "call before the install command.")

no_clean = OptionMaker(
    '--no-clean',
    action='store_true',
    default=False,
    help="Don't clean up build directories.")

disable_pip_version_check = OptionMaker(
    "--disable-pip-version-check",
    dest="disable_pip_version_check",
    action="store_true",
    default=False,
    help="Don't periodically check PyPI to determine whether a new version "
         "of pip is available for download. Implied with --no-index.")

##########
# groups #
##########

general_group = {
    'name': 'General Options',
    'options': [
        help_,
        isolated_mode,
        require_virtualenv,
        verbose,
        version,
        quiet,
        log,
        log_explicit_levels,
        no_input,
        proxy,
        retries,
        timeout,
        default_vcs,
        skip_requirements_regex,
        exists_action,
        trusted_host,
        cert,
        client_cert,
        cache_dir,
        no_cache,
        disable_pip_version_check,
    ]
}

index_group = {
    'name': 'Package Index Options',
    'options': [
        index_url,
        extra_index_url,
        no_index,
        find_links,
        use_mirrors,
        mirrors,
        allow_external,
        allow_all_external,
        no_allow_external,
        allow_unsafe,
        no_allow_unsafe,
        process_dependency_links,
    ]
}
