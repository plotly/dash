from __future__ import absolute_import

import logging
import operator
import os
import tempfile
import shutil
import warnings

from pip.req import InstallRequirement, RequirementSet, parse_requirements
from pip.locations import build_prefix, virtualenv_no_global, distutils_scheme
from pip.basecommand import Command
from pip.index import PackageFinder
from pip.exceptions import (
    InstallationError, CommandError, PreviousBuildDirError,
)
from pip import cmdoptions
from pip.utils.build import BuildDirectory
from pip.utils.deprecation import RemovedInPip7Warning, RemovedInPip8Warning


logger = logging.getLogger(__name__)


class InstallCommand(Command):
    """
    Install packages from:

    - PyPI (and other indexes) using requirement specifiers.
    - VCS project urls.
    - Local project directories.
    - Local or remote source archives.

    pip also supports installing from "requirements files", which provide
    an easy way to specify a whole environment to be installed.
    """
    name = 'install'

    usage = """
      %prog [options] <requirement specifier> [package-index-options] ...
      %prog [options] -r <requirements file> [package-index-options] ...
      %prog [options] [-e] <vcs project url> ...
      %prog [options] [-e] <local project path> ...
      %prog [options] <archive url/path> ..."""

    summary = 'Install packages.'

    def __init__(self, *args, **kw):
        super(InstallCommand, self).__init__(*args, **kw)

        cmd_opts = self.cmd_opts

        cmd_opts.add_option(cmdoptions.editable.make())
        cmd_opts.add_option(cmdoptions.requirements.make())
        cmd_opts.add_option(cmdoptions.build_dir.make())

        cmd_opts.add_option(
            '-t', '--target',
            dest='target_dir',
            metavar='dir',
            default=None,
            help='Install packages into <dir>. '
                 'By default this will not replace existing files/folders in '
                 '<dir>. Use --upgrade to replace existing packages in <dir> '
                 'with new versions.'
        )

        cmd_opts.add_option(
            '-d', '--download', '--download-dir', '--download-directory',
            dest='download_dir',
            metavar='dir',
            default=None,
            help=("Download packages into <dir> instead of installing them, "
                  "regardless of what's already installed."),
        )

        cmd_opts.add_option(cmdoptions.download_cache.make())
        cmd_opts.add_option(cmdoptions.src.make())

        cmd_opts.add_option(
            '-U', '--upgrade',
            dest='upgrade',
            action='store_true',
            help='Upgrade all specified packages to the newest available '
                 'version. This process is recursive regardless of whether '
                 'a dependency is already satisfied.'
        )

        cmd_opts.add_option(
            '--force-reinstall',
            dest='force_reinstall',
            action='store_true',
            help='When upgrading, reinstall all packages even if they are '
                 'already up-to-date.')

        cmd_opts.add_option(
            '-I', '--ignore-installed',
            dest='ignore_installed',
            action='store_true',
            help='Ignore the installed packages (reinstalling instead).')

        cmd_opts.add_option(cmdoptions.no_deps.make())

        cmd_opts.add_option(
            '--no-install',
            dest='no_install',
            action='store_true',
            help="DEPRECATED. Download and unpack all packages, but don't "
                 "actually install them."
        )

        cmd_opts.add_option(
            '--no-download',
            dest='no_download',
            action="store_true",
            help="DEPRECATED. Don't download any packages, just install the "
                 "ones already downloaded (completes an install run with "
                 "--no-install).")

        cmd_opts.add_option(cmdoptions.install_options.make())
        cmd_opts.add_option(cmdoptions.global_options.make())

        cmd_opts.add_option(
            '--user',
            dest='use_user_site',
            action='store_true',
            help="Install to the Python user install directory for your "
                 "platform. Typically ~/.local/, or %APPDATA%\Python on "
                 "Windows. (See the Python documentation for site.USER_BASE "
                 "for full details.)")

        cmd_opts.add_option(
            '--egg',
            dest='as_egg',
            action='store_true',
            help="Install packages as eggs, not 'flat', like pip normally "
                 "does. This option is not about installing *from* eggs. "
                 "(WARNING: Because this option overrides pip's normal install"
                 " logic, requirements files may not behave as expected.)")

        cmd_opts.add_option(
            '--root',
            dest='root_path',
            metavar='dir',
            default=None,
            help="Install everything relative to this alternate root "
                 "directory.")

        cmd_opts.add_option(
            "--compile",
            action="store_true",
            dest="compile",
            default=True,
            help="Compile py files to pyc",
        )

        cmd_opts.add_option(
            "--no-compile",
            action="store_false",
            dest="compile",
            help="Do not compile py files to pyc",
        )

        cmd_opts.add_option(cmdoptions.use_wheel.make())
        cmd_opts.add_option(cmdoptions.no_use_wheel.make())

        cmd_opts.add_option(
            '--pre',
            action='store_true',
            default=False,
            help="Include pre-release and development versions. By default, "
                 "pip only finds stable versions.")

        cmd_opts.add_option(cmdoptions.no_clean.make())

        index_opts = cmdoptions.make_option_group(
            cmdoptions.index_group,
            self.parser,
        )

        self.parser.insert_option_group(0, index_opts)
        self.parser.insert_option_group(0, cmd_opts)

    def _build_package_finder(self, options, index_urls, session):
        """
        Create a package finder appropriate to this install command.
        This method is meant to be overridden by subclasses, not
        called directly.
        """
        return PackageFinder(
            find_links=options.find_links,
            index_urls=index_urls,
            use_wheel=options.use_wheel,
            allow_external=options.allow_external,
            allow_unverified=options.allow_unverified,
            allow_all_external=options.allow_all_external,
            trusted_hosts=options.trusted_hosts,
            allow_all_prereleases=options.pre,
            process_dependency_links=options.process_dependency_links,
            session=session,
        )

    def run(self, options, args):

        if (
            options.no_install or
            options.no_download
        ):
            warnings.warn(
                "--no-install and --no-download are deprecated. "
                "See https://github.com/pypa/pip/issues/906.",
                RemovedInPip7Warning,
            )

        # If we have --no-install or --no-download and no --build we use the
        # legacy static build dir
        if (options.build_dir is None and
                (options.no_install or options.no_download)):
            options.build_dir = build_prefix

        if options.download_dir:
            options.no_install = True
            options.ignore_installed = True

        if options.build_dir:
            options.build_dir = os.path.abspath(options.build_dir)

        options.src_dir = os.path.abspath(options.src_dir)
        install_options = options.install_options or []
        if options.use_user_site:
            if virtualenv_no_global():
                raise InstallationError(
                    "Can not perform a '--user' install. User site-packages "
                    "are not visible in this virtualenv."
                )
            install_options.append('--user')

        temp_target_dir = None
        if options.target_dir:
            options.ignore_installed = True
            temp_target_dir = tempfile.mkdtemp()
            options.target_dir = os.path.abspath(options.target_dir)
            if (os.path.exists(options.target_dir) and not
                    os.path.isdir(options.target_dir)):
                raise CommandError(
                    "Target path exists but is not a directory, will not "
                    "continue."
                )
            install_options.append('--home=' + temp_target_dir)

        global_options = options.global_options or []
        index_urls = [options.index_url] + options.extra_index_urls
        if options.no_index:
            logger.info('Ignoring indexes: %s', ','.join(index_urls))
            index_urls = []

        if options.use_mirrors:
            warnings.warn(
                "--use-mirrors has been deprecated and will be removed in the "
                "future. Explicit uses of --index-url and/or --extra-index-url"
                " is suggested.",
                RemovedInPip7Warning,
            )

        if options.mirrors:
            warnings.warn(
                "--mirrors has been deprecated and will be removed in the "
                "future. Explicit uses of --index-url and/or --extra-index-url"
                " is suggested.",
                RemovedInPip7Warning,
            )
            index_urls += options.mirrors

        if options.download_cache:
            warnings.warn(
                "--download-cache has been deprecated and will be removed in "
                "the future. Pip now automatically uses and configures its "
                "cache.",
                RemovedInPip8Warning,
            )

        with self._build_session(options) as session:

            finder = self._build_package_finder(options, index_urls, session)

            build_delete = (not (options.no_clean or options.build_dir))
            with BuildDirectory(options.build_dir,
                                delete=build_delete) as build_dir:
                requirement_set = RequirementSet(
                    build_dir=build_dir,
                    src_dir=options.src_dir,
                    download_dir=options.download_dir,
                    upgrade=options.upgrade,
                    as_egg=options.as_egg,
                    ignore_installed=options.ignore_installed,
                    ignore_dependencies=options.ignore_dependencies,
                    force_reinstall=options.force_reinstall,
                    use_user_site=options.use_user_site,
                    target_dir=temp_target_dir,
                    session=session,
                    pycompile=options.compile,
                    isolated=options.isolated_mode,
                )

                for name in args:
                    requirement_set.add_requirement(
                        InstallRequirement.from_line(
                            name, None, isolated=options.isolated_mode,
                        )
                    )

                for name in options.editables:
                    requirement_set.add_requirement(
                        InstallRequirement.from_editable(
                            name,
                            default_vcs=options.default_vcs,
                            isolated=options.isolated_mode,
                        )
                    )

                for filename in options.requirements:
                    for req in parse_requirements(
                            filename,
                            finder=finder, options=options, session=session):
                        requirement_set.add_requirement(req)

                if not requirement_set.has_requirements:
                    opts = {'name': self.name}
                    if options.find_links:
                        msg = ('You must give at least one requirement to '
                               '%(name)s (maybe you meant "pip %(name)s '
                               '%(links)s"?)' %
                               dict(opts, links=' '.join(options.find_links)))
                    else:
                        msg = ('You must give at least one requirement '
                               'to %(name)s (see "pip help %(name)s")' % opts)
                    logger.warning(msg)
                    return

                try:
                    if not options.no_download:
                        requirement_set.prepare_files(finder)
                    else:
                        # This is the only call site of locate_files. Nuke with
                        # fire.
                        requirement_set.locate_files()

                    if not options.no_install:
                        requirement_set.install(
                            install_options,
                            global_options,
                            root=options.root_path,
                        )
                        reqs = sorted(
                            requirement_set.successfully_installed,
                            key=operator.attrgetter('name'))
                        items = []
                        for req in reqs:
                            item = req.name
                            try:
                                if hasattr(req, 'installed_version'):
                                    if req.installed_version:
                                        item += '-' + req.installed_version
                            except Exception:
                                pass
                            items.append(item)
                        installed = ' '.join(items)
                        if installed:
                            logger.info('Successfully installed %s', installed)
                    else:
                        downloaded = ' '.join([
                            req.name
                            for req in requirement_set.successfully_downloaded
                        ])
                        if downloaded:
                            logger.info(
                                'Successfully downloaded %s', downloaded
                            )
                except PreviousBuildDirError:
                    options.no_clean = True
                    raise
                finally:
                    # Clean up
                    if ((not options.no_clean) and
                            ((not options.no_install) or
                                options.download_dir)):
                        requirement_set.cleanup_files()

        if options.target_dir:
            if not os.path.exists(options.target_dir):
                os.makedirs(options.target_dir)

            lib_dir = distutils_scheme('', home=temp_target_dir)['purelib']

            for item in os.listdir(lib_dir):
                target_item_dir = os.path.join(options.target_dir, item)
                if os.path.exists(target_item_dir):
                    if not options.upgrade:
                        logger.warning(
                            'Target directory %s already exists. Specify '
                            '--upgrade to force replacement.',
                            target_item_dir
                        )
                        continue
                    if os.path.islink(target_item_dir):
                        logger.warning(
                            'Target directory %s already exists and is '
                            'a link. Pip will not automatically replace '
                            'links, please remove if replacement is '
                            'desired.',
                            target_item_dir
                        )
                        continue
                    if os.path.isdir(target_item_dir):
                        shutil.rmtree(target_item_dir)
                    else:
                        os.remove(target_item_dir)

                shutil.move(
                    os.path.join(lib_dir, item),
                    target_item_dir
                )
            shutil.rmtree(temp_target_dir)
        return requirement_set
