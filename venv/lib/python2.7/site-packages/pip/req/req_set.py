from __future__ import absolute_import

from collections import defaultdict
import functools
import itertools
import logging
import os

from pip._vendor import pkg_resources
from pip._vendor import requests

from pip.download import (url_to_path, unpack_url)
from pip.exceptions import (InstallationError, BestVersionAlreadyInstalled,
                            DistributionNotFound, PreviousBuildDirError)
from pip.locations import (PIP_DELETE_MARKER_FILENAME, build_prefix)
from pip.req.req_install import InstallRequirement
from pip.utils import (display_path, rmtree, dist_in_usersite, normalize_path)
from pip.utils.logging import indent_log
from pip.vcs import vcs


logger = logging.getLogger(__name__)


class Requirements(object):

    def __init__(self):
        self._keys = []
        self._dict = {}

    def keys(self):
        return self._keys

    def values(self):
        return [self._dict[key] for key in self._keys]

    def __contains__(self, item):
        return item in self._keys

    def __setitem__(self, key, value):
        if key not in self._keys:
            self._keys.append(key)
        self._dict[key] = value

    def __getitem__(self, key):
        return self._dict[key]

    def __repr__(self):
        values = ['%s: %s' % (repr(k), repr(self[k])) for k in self.keys()]
        return 'Requirements({%s})' % ', '.join(values)


class DistAbstraction(object):
    """Abstracts out the wheel vs non-wheel prepare_files logic.

    The requirements for anything installable are as follows:
     - we must be able to determine the requirement name
       (or we can't correctly handle the non-upgrade case).
     - we must be able to generate a list of run-time dependencies
       without installing any additional packages (or we would
       have to either burn time by doing temporary isolated installs
       or alternatively violate pips 'don't start installing unless
       all requirements are available' rule - neither of which are
       desirable).
     - for packages with setup requirements, we must also be able
       to determine their requirements without installing additional
       packages (for the same reason as run-time dependencies)
     - we must be able to create a Distribution object exposing the
       above metadata.
    """

    def __init__(self, req_to_install):
        self.req_to_install = req_to_install

    def dist(self, finder):
        """Return a setuptools Dist object."""
        raise NotImplementedError(self.dist)

    def prep_for_dist(self):
        """Ensure that we can get a Dist for this requirement."""
        raise NotImplementedError(self.dist)


def make_abstract_dist(req_to_install):
    """Factory to make an abstract dist object.

    Preconditions: Either an editable req with a source_dir, or satisfied_by or
    a wheel link, or a non-editable req with a source_dir.

    :return: A concrete DistAbstraction.
    """
    if req_to_install.editable:
        return IsSDist(req_to_install)
    elif req_to_install.link and req_to_install.link.is_wheel:
        return IsWheel(req_to_install)
    else:
        return IsSDist(req_to_install)


class IsWheel(DistAbstraction):

    def dist(self, finder):
        return list(pkg_resources.find_distributions(
            self.req_to_install.source_dir))[0]

    def prep_for_dist(self):
        # FIXME:https://github.com/pypa/pip/issues/1112
        pass


class IsSDist(DistAbstraction):

    def dist(self, finder):
        dist = self.req_to_install.get_dist()
        # FIXME: shouldn't be globally added:
        if dist.has_metadata('dependency_links.txt'):
            finder.add_dependency_links(
                dist.get_metadata_lines('dependency_links.txt')
            )
        return dist

    def prep_for_dist(self):
        self.req_to_install.run_egg_info()
        self.req_to_install.assert_source_matches_version()


class Installed(DistAbstraction):

    def dist(self, finder):
        return self.req_to_install.satisfied_by

    def prep_for_dist(self):
        pass


class RequirementSet(object):

    def __init__(self, build_dir, src_dir, download_dir, upgrade=False,
                 ignore_installed=False, as_egg=False, target_dir=None,
                 ignore_dependencies=False, force_reinstall=False,
                 use_user_site=False, session=None, pycompile=True,
                 isolated=False, wheel_download_dir=None):
        if session is None:
            raise TypeError(
                "RequirementSet() missing 1 required keyword argument: "
                "'session'"
            )

        self.build_dir = build_dir
        self.src_dir = src_dir
        # XXX: download_dir and wheel_download_dir overlap semantically and may
        # be combinable.
        self.download_dir = download_dir
        self.upgrade = upgrade
        self.ignore_installed = ignore_installed
        self.force_reinstall = force_reinstall
        self.requirements = Requirements()
        # Mapping of alias: real_name
        self.requirement_aliases = {}
        self.unnamed_requirements = []
        self.ignore_dependencies = ignore_dependencies
        self.successfully_downloaded = []
        self.successfully_installed = []
        self.reqs_to_cleanup = []
        self.as_egg = as_egg
        self.use_user_site = use_user_site
        self.target_dir = target_dir  # set from --target option
        self.session = session
        self.pycompile = pycompile
        self.isolated = isolated
        if wheel_download_dir:
            wheel_download_dir = normalize_path(wheel_download_dir)
        self.wheel_download_dir = wheel_download_dir
        # Maps from install_req -> dependencies_of_install_req
        self._dependencies = defaultdict(list)

    def __str__(self):
        reqs = [req for req in self.requirements.values()
                if not req.comes_from]
        reqs.sort(key=lambda req: req.name.lower())
        return ' '.join([str(req.req) for req in reqs])

    def __repr__(self):
        reqs = [req for req in self.requirements.values()]
        reqs.sort(key=lambda req: req.name.lower())
        reqs_str = ', '.join([str(req.req) for req in reqs])
        return ('<%s object; %d requirement(s): %s>'
                % (self.__class__.__name__, len(reqs), reqs_str))

    def add_requirement(self, install_req, parent_req_name=None):
        """Add install_req as a requirement to install.

        :param parent_req_name: The name of the requirement that needed this
            added. The name is used because when multiple unnamed requirements
            resolve to the same name, we could otherwise end up with dependency
            links that point outside the Requirements set. parent_req must
            already be added. Note that None implies that this is a user
            supplied requirement, vs an inferred one.
        :return: Additional requirements to scan. That is either [] if
            the requirement is not applicable, or [install_req] if the
            requirement is applicable and has just been added.
        """
        name = install_req.name
        if ((not name or not self.has_requirement(name)) and not
                install_req.match_markers()):
            # Only log if we haven't already got install_req from somewhere.
            logger.debug("Ignore %s: markers %r don't match",
                         install_req.name, install_req.markers)
            return []

        install_req.as_egg = self.as_egg
        install_req.use_user_site = self.use_user_site
        install_req.target_dir = self.target_dir
        install_req.pycompile = self.pycompile
        if not name:
            # url or path requirement w/o an egg fragment
            self.unnamed_requirements.append(install_req)
            return [install_req]
        else:
            if parent_req_name is None and self.has_requirement(name):
                raise InstallationError(
                    'Double requirement given: %s (already in %s, name=%r)'
                    % (install_req, self.get_requirement(name), name))
            if not self.has_requirement(name):
                # Add requirement
                self.requirements[name] = install_req
                # FIXME: what about other normalizations?  E.g., _ vs. -?
                if name.lower() != name:
                    self.requirement_aliases[name.lower()] = name
                result = [install_req]
            else:
                # Canonicalise to the already-added object
                install_req = self.get_requirement(name)
                # No need to scan, this is a duplicate requirement.
                result = []
            if parent_req_name:
                parent_req = self.get_requirement(parent_req_name)
                self._dependencies[parent_req].append(install_req)
            return result

    def has_requirement(self, project_name):
        for name in project_name, project_name.lower():
            if name in self.requirements or name in self.requirement_aliases:
                return True
        return False

    @property
    def has_requirements(self):
        return list(self.requirements.values()) or self.unnamed_requirements

    @property
    def is_download(self):
        if self.download_dir:
            self.download_dir = os.path.expanduser(self.download_dir)
            if os.path.exists(self.download_dir):
                return True
            else:
                logger.critical('Could not find download directory')
                raise InstallationError(
                    "Could not find or access download directory '%s'"
                    % display_path(self.download_dir))
        return False

    def get_requirement(self, project_name):
        for name in project_name, project_name.lower():
            if name in self.requirements:
                return self.requirements[name]
            if name in self.requirement_aliases:
                return self.requirements[self.requirement_aliases[name]]
        raise KeyError("No project with the name %r" % project_name)

    def uninstall(self, auto_confirm=False):
        for req in self.requirements.values():
            req.uninstall(auto_confirm=auto_confirm)
            req.commit_uninstall()

    def _walk_req_to_install(self, handler):
        """Call handler for all pending reqs.

        :param handler: Handle a single requirement. Should take a requirement
            to install. Can optionally return an iterable of additional
            InstallRequirements to cover.
        """
        # The list() here is to avoid potential mutate-while-iterating bugs.
        discovered_reqs = []
        reqs = itertools.chain(
            list(self.unnamed_requirements), list(self.requirements.values()),
            discovered_reqs)
        for req_to_install in reqs:
            more_reqs = handler(req_to_install)
            if more_reqs:
                discovered_reqs.extend(more_reqs)

    def locate_files(self):
        """Remove in 7.0: used by --no-download"""
        self._walk_req_to_install(self._locate_file)

    def _locate_file(self, req_to_install):
        install_needed = True
        if not self.ignore_installed and not req_to_install.editable:
            req_to_install.check_if_exists()
            if req_to_install.satisfied_by:
                if self.upgrade:
                    # don't uninstall conflict if user install and
                    # conflict is not user install
                    if not (self.use_user_site and
                            not dist_in_usersite(
                                req_to_install.satisfied_by
                            )):
                        req_to_install.conflicts_with = \
                            req_to_install.satisfied_by
                    req_to_install.satisfied_by = None
                else:
                    install_needed = False
                    logger.info(
                        'Requirement already satisfied (use --upgrade to '
                        'upgrade): %s',
                        req_to_install,
                    )

        if req_to_install.editable:
            if req_to_install.source_dir is None:
                req_to_install.source_dir = req_to_install.build_location(
                    self.src_dir
                )
        elif install_needed:
            req_to_install.source_dir = req_to_install.build_location(
                self.build_dir,
            )

        if (req_to_install.source_dir is not None and not
                os.path.isdir(req_to_install.source_dir)):
            raise InstallationError(
                'Could not install requirement %s because source folder %s'
                ' does not exist (perhaps --no-download was used without '
                'first running an equivalent install with --no-install?)' %
                (req_to_install, req_to_install.source_dir)
            )

    def prepare_files(self, finder):
        """
        Prepare process. Create temp directories, download and/or unpack files.
        """
        self._walk_req_to_install(
            functools.partial(self._prepare_file, finder))

    def _check_skip_installed(self, req_to_install, finder):
        """Check if req_to_install should be skipped.

        This will check if the req is installed, and whether we should upgrade
        or reinstall it, taking into account all the relevant user options.

        After calling this req_to_install will only have satisfied_by set to
        None if the req_to_install is to be upgraded/reinstalled etc. Any
        other value will be a dist recording the current thing installed that
        satisfies the requirement.

        Note that for vcs urls and the like we can't assess skipping in this
        routine - we simply identify that we need to pull the thing down,
        then later on it is pulled down and introspected to assess upgrade/
        reinstalls etc.

        :return: A text reason for why it was skipped, or None.
        """
        # Check whether to upgrade/reinstall this req or not.
        req_to_install.check_if_exists()
        if req_to_install.satisfied_by:
            skip_reason = 'satisfied (use --upgrade to upgrade)'
            if self.upgrade:
                best_installed = False
                # For link based requirements we have to pull the
                # tree down and inspect to assess the version #, so
                # its handled way down.
                if not (self.force_reinstall or req_to_install.link):
                    try:
                        finder.find_requirement(req_to_install, self.upgrade)
                    except BestVersionAlreadyInstalled:
                        skip_reason = 'up-to-date'
                        best_installed = True
                    except DistributionNotFound:
                        # No distribution found, so we squash the
                        # error - it will be raised later when we
                        # re-try later to do the install.
                        # Why don't we just raise here?
                        pass

                if not best_installed:
                    # don't uninstall conflict if user install and
                    # conflict is not user install
                    if not (self.use_user_site and not
                            dist_in_usersite(req_to_install.satisfied_by)):
                        req_to_install.conflicts_with = \
                            req_to_install.satisfied_by
                    req_to_install.satisfied_by = None
            return skip_reason
        else:
            return None

    def _prepare_file(self, finder, req_to_install):
        """Prepare a single requirements files.

        :return: A list of addition InstallRequirements to also install.
        """
        # Tell user what we are doing for this requirement:
        # obtain (editable), skipping, processing (local url), collecting
        # (remote url or package name)
        if req_to_install.editable:
            logger.info('Obtaining %s', req_to_install)
        else:
            # satisfied_by is only evaluated by calling _check_skip_installed,
            # so it must be None here.
            assert req_to_install.satisfied_by is None
            if not self.ignore_installed:
                skip_reason = self._check_skip_installed(
                    req_to_install, finder)

            if req_to_install.satisfied_by:
                assert skip_reason is not None, (
                    '_check_skip_installed returned None but '
                    'req_to_install.satisfied_by is set to %r'
                    % (req_to_install.satisfied_by,))
                logger.info(
                    'Requirement already %s: %s', skip_reason,
                    req_to_install)
            else:
                if (req_to_install.link and
                        req_to_install.link.scheme == 'file'):
                    path = url_to_path(req_to_install.link.url)
                    logger.info('Processing %s', display_path(path))
                else:
                    logger.info('Collecting %s', req_to_install)

        with indent_log():
            # ################################ #
            # # vcs update or unpack archive # #
            # ################################ #
            if req_to_install.editable:
                req_to_install.ensure_has_source_dir(self.src_dir)
                req_to_install.update_editable(not self.is_download)
                abstract_dist = make_abstract_dist(req_to_install)
                abstract_dist.prep_for_dist()
                if self.is_download:
                    req_to_install.archive(self.download_dir)
            elif req_to_install.satisfied_by:
                abstract_dist = Installed(req_to_install)
            else:
                # @@ if filesystem packages are not marked
                # editable in a req, a non deterministic error
                # occurs when the script attempts to unpack the
                # build directory
                req_to_install.ensure_has_source_dir(self.build_dir)
                # If a checkout exists, it's unwise to keep going.  version
                # inconsistencies are logged later, but do not fail the
                # installation.
                # FIXME: this won't upgrade when there's an existing
                # package unpacked in `req_to_install.source_dir`
                if os.path.exists(
                        os.path.join(req_to_install.source_dir, 'setup.py')):
                    raise PreviousBuildDirError(
                        "pip can't proceed with requirements '%s' due to a"
                        " pre-existing build directory (%s). This is "
                        "likely due to a previous installation that failed"
                        ". pip is being responsible and not assuming it "
                        "can delete this. Please delete it and try again."
                        % (req_to_install, req_to_install.source_dir)
                    )
                req_to_install.populate_link(finder, self.upgrade)
                # We can't hit this spot and have populate_link return None.
                # req_to_install.satisfied_by is None here (because we're
                # guarded) and upgrade has no impact except when satisfied_by
                # is not None.
                # Then inside find_requirement existing_applicable -> False
                # If no new versions are found, DistributionNotFound is raised,
                # otherwise a result is guaranteed.
                assert req_to_install.link
                try:
                    if req_to_install.link.is_wheel and \
                            self.wheel_download_dir:
                        # when doing 'pip wheel`
                        download_dir = self.wheel_download_dir
                        do_download = True
                    else:
                        download_dir = self.download_dir
                        do_download = self.is_download
                    unpack_url(
                        req_to_install.link, req_to_install.source_dir,
                        download_dir, do_download, session=self.session,
                    )
                except requests.HTTPError as exc:
                    logger.critical(
                        'Could not install requirement %s because '
                        'of error %s',
                        req_to_install,
                        exc,
                    )
                    raise InstallationError(
                        'Could not install requirement %s because '
                        'of HTTP error %s for URL %s' %
                        (req_to_install, exc, req_to_install.link)
                    )
                abstract_dist = make_abstract_dist(req_to_install)
                abstract_dist.prep_for_dist()
                if self.is_download:
                    # Make a .zip of the source_dir we already created.
                    if req_to_install.link.scheme in vcs.all_schemes:
                        req_to_install.archive(self.download_dir)
                # req_to_install.req is only avail after unpack for URL
                # pkgs repeat check_if_exists to uninstall-on-upgrade
                # (#14)
                if not self.ignore_installed:
                    req_to_install.check_if_exists()
                if req_to_install.satisfied_by:
                    if self.upgrade or self.ignore_installed:
                        # don't uninstall conflict if user install and
                        # conflict is not user install
                        if not (self.use_user_site and not
                                dist_in_usersite(
                                    req_to_install.satisfied_by)):
                            req_to_install.conflicts_with = \
                                req_to_install.satisfied_by
                        req_to_install.satisfied_by = None
                    else:
                        logger.info(
                            'Requirement already satisfied (use '
                            '--upgrade to upgrade): %s',
                            req_to_install,
                        )

            # ###################### #
            # # parse dependencies # #
            # ###################### #
            dist = abstract_dist.dist(finder)
            more_reqs = []

            def add_req(subreq):
                sub_install_req = InstallRequirement(
                    str(subreq),
                    req_to_install,
                    isolated=self.isolated,
                )
                more_reqs.extend(self.add_requirement(
                    sub_install_req, req_to_install.name))

            # We add req_to_install before its dependencies, so that we
            # can refer to it when adding dependencies.
            if not self.has_requirement(req_to_install.name):
                # 'unnamed' requirements will get added here
                self.add_requirement(req_to_install, None)

            if not self.ignore_dependencies:
                if (req_to_install.extras):
                    logger.debug(
                        "Installing extra requirements: %r",
                        ','.join(req_to_install.extras),
                    )
                missing_requested = sorted(
                    set(req_to_install.extras) - set(dist.extras)
                )
                for missing in missing_requested:
                    logger.warning(
                        '%s does not provide the extra \'%s\'',
                        dist, missing
                    )

                available_requested = sorted(
                    set(dist.extras) & set(req_to_install.extras)
                )
                for subreq in dist.requires(available_requested):
                    add_req(subreq)

            # cleanup tmp src
            self.reqs_to_cleanup.append(req_to_install)

            if not req_to_install.editable and not req_to_install.satisfied_by:
                # XXX: --no-install leads this to report 'Successfully
                # downloaded' for only non-editable reqs, even though we took
                # action on them.
                self.successfully_downloaded.append(req_to_install)

        return more_reqs

    def cleanup_files(self):
        """Clean up files, remove builds."""
        logger.debug('Cleaning up...')
        with indent_log():
            for req in self.reqs_to_cleanup:
                req.remove_temporary_source()

            if self._pip_has_created_build_dir():
                logger.debug('Removing temporary dir %s...', self.build_dir)
                rmtree(self.build_dir)

    def _pip_has_created_build_dir(self):
        return (
            self.build_dir == build_prefix and
            os.path.exists(
                os.path.join(self.build_dir, PIP_DELETE_MARKER_FILENAME)
            )
        )

    def _to_install(self):
        """Create the installation order.

        The installation order is topological - requirements are installed
        before the requiring thing. We break cycles at an arbitrary point,
        and make no other guarantees.
        """
        # The current implementation, which we may change at any point
        # installs the user specified things in the order given, except when
        # dependencies must come earlier to achieve topological order.
        order = []
        ordered_reqs = set()

        def schedule(req):
            if req.satisfied_by or req in ordered_reqs:
                return
            ordered_reqs.add(req)
            for dep in self._dependencies[req]:
                schedule(dep)
            order.append(req)
        for install_req in self.requirements.values():
            schedule(install_req)
        return order

    def install(self, install_options, global_options=(), *args, **kwargs):
        """
        Install everything in this set (after having downloaded and unpacked
        the packages)
        """
        to_install = self._to_install()

        # DISTRIBUTE TO SETUPTOOLS UPGRADE HACK (1 of 3 parts)
        # move the distribute-0.7.X wrapper to the end because it does not
        # install a setuptools package. by moving it to the end, we ensure it's
        # setuptools dependency is handled first, which will provide the
        # setuptools package
        # TODO: take this out later
        distribute_req = pkg_resources.Requirement.parse("distribute>=0.7")
        for req in to_install:
            if (req.name == 'distribute' and
                    req.installed_version is not None and
                    req.installed_version in distribute_req):
                to_install.remove(req)
                to_install.append(req)

        if to_install:
            logger.info(
                'Installing collected packages: %s',
                ', '.join([req.name for req in to_install]),
            )

        with indent_log():
            for requirement in to_install:

                # DISTRIBUTE TO SETUPTOOLS UPGRADE HACK (1 of 3 parts)
                # when upgrading from distribute-0.6.X to the new merged
                # setuptools in py2, we need to force setuptools to uninstall
                # distribute. In py3, which is always using distribute, this
                # conversion is already happening in distribute's
                # pkg_resources. It's ok *not* to check if setuptools>=0.7
                # because if someone were actually trying to ugrade from
                # distribute to setuptools 0.6.X, then all this could do is
                # actually help, although that upgade path was certainly never
                # "supported"
                # TODO: remove this later
                if requirement.name == 'setuptools':
                    try:
                        # only uninstall distribute<0.7. For >=0.7, setuptools
                        # will also be present, and that's what we need to
                        # uninstall
                        distribute_requirement = \
                            pkg_resources.Requirement.parse("distribute<0.7")
                        existing_distribute = \
                            pkg_resources.get_distribution("distribute")
                        if existing_distribute in distribute_requirement:
                            requirement.conflicts_with = existing_distribute
                    except pkg_resources.DistributionNotFound:
                        # distribute wasn't installed, so nothing to do
                        pass

                if requirement.conflicts_with:
                    logger.info(
                        'Found existing installation: %s',
                        requirement.conflicts_with,
                    )
                    with indent_log():
                        requirement.uninstall(auto_confirm=True)
                try:
                    requirement.install(
                        install_options,
                        global_options,
                        *args,
                        **kwargs
                    )
                except:
                    # if install did not succeed, rollback previous uninstall
                    if (requirement.conflicts_with and not
                            requirement.install_succeeded):
                        requirement.rollback_uninstall()
                    raise
                else:
                    if (requirement.conflicts_with and
                            requirement.install_succeeded):
                        requirement.commit_uninstall()
                requirement.remove_temporary_source()

        self.successfully_installed = to_install
