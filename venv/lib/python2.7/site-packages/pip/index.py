"""Routines related to PyPI, indexes"""
from __future__ import absolute_import

import logging
import cgi
import sys
import os
import re
import mimetypes
import posixpath
import warnings

from pip._vendor.six.moves.urllib import parse as urllib_parse
from pip._vendor.six.moves.urllib import request as urllib_request

from pip.compat import ipaddress
from pip.utils import (
    Inf, cached_property, normalize_name, splitext, normalize_path)
from pip.utils.deprecation import RemovedInPip7Warning, RemovedInPip8Warning
from pip.utils.logging import indent_log
from pip.exceptions import (
    DistributionNotFound, BestVersionAlreadyInstalled, InvalidWheelFilename,
    UnsupportedWheel,
)
from pip.download import url_to_path, path_to_url
from pip.models import PyPI
from pip.wheel import Wheel, wheel_ext
from pip.pep425tags import supported_tags, supported_tags_noarch, get_platform
from pip.req.req_requirement import InstallationCandidate
from pip._vendor import html5lib, requests, pkg_resources, six
from pip._vendor.packaging.version import parse as parse_version
from pip._vendor.requests.exceptions import SSLError


__all__ = ['PackageFinder']


# Taken from Chrome's list of secure origins (See: http://bit.ly/1qrySKC)
SECURE_ORIGINS = [
    # protocol, hostname, port
    ("https", "*", "*"),
    ("*", "localhost", "*"),
    ("*", "127.0.0.0/8", "*"),
    ("*", "::1/128", "*"),
    ("file", "*", None),
]


logger = logging.getLogger(__name__)


class PackageFinder(object):
    """This finds packages.

    This is meant to match easy_install's technique for looking for
    packages, by reading pages and looking for appropriate links
    """

    def __init__(self, find_links, index_urls,
                 use_wheel=True, allow_external=(), allow_unverified=(),
                 allow_all_external=False, allow_all_prereleases=False,
                 trusted_hosts=None, process_dependency_links=False,
                 session=None):
        if session is None:
            raise TypeError(
                "PackageFinder() missing 1 required keyword argument: "
                "'session'"
            )

        # Build find_links. If an argument starts with ~, it may be
        # a local file relative to a home directory. So try normalizing
        # it and if it exists, use the normalized version.
        # This is deliberately conservative - it might be fine just to
        # blindly normalize anything starting with a ~...
        self.find_links = []
        for link in find_links:
            if link.startswith('~'):
                new_link = normalize_path(link)
                if os.path.exists(new_link):
                    link = new_link
            self.find_links.append(link)

        self.index_urls = index_urls
        self.dependency_links = []

        # These are boring links that have already been logged somehow:
        self.logged_links = set()

        self.use_wheel = use_wheel

        # Do we allow (safe and verifiable) externally hosted files?
        self.allow_external = set(normalize_name(n) for n in allow_external)

        # Which names are allowed to install insecure and unverifiable files?
        self.allow_unverified = set(
            normalize_name(n) for n in allow_unverified
        )

        # Anything that is allowed unverified is also allowed external
        self.allow_external |= self.allow_unverified

        # Do we allow all (safe and verifiable) externally hosted files?
        self.allow_all_external = allow_all_external

        # Domains that we won't emit warnings for when not using HTTPS
        self.secure_origins = [
            ("*", host, "*")
            for host in (trusted_hosts if trusted_hosts else [])
        ]

        # Stores if we ignored any external links so that we can instruct
        #   end users how to install them if no distributions are available
        self.need_warn_external = False

        # Stores if we ignored any unsafe links so that we can instruct
        #   end users how to install them if no distributions are available
        self.need_warn_unverified = False

        # Do we want to allow _all_ pre-releases?
        self.allow_all_prereleases = allow_all_prereleases

        # Do we process dependency links?
        self.process_dependency_links = process_dependency_links

        # The Session we'll use to make requests
        self.session = session

    def add_dependency_links(self, links):
        # # FIXME: this shouldn't be global list this, it should only
        # # apply to requirements of the package that specifies the
        # # dependency_links value
        # # FIXME: also, we should track comes_from (i.e., use Link)
        if self.process_dependency_links:
            warnings.warn(
                "Dependency Links processing has been deprecated and will be "
                "removed in a future release.",
                RemovedInPip7Warning,
            )
            self.dependency_links.extend(links)

    def _sort_locations(self, locations):
        """
        Sort locations into "files" (archives) and "urls", and return
        a pair of lists (files,urls)
        """
        files = []
        urls = []

        # puts the url for the given file path into the appropriate list
        def sort_path(path):
            url = path_to_url(path)
            if mimetypes.guess_type(url, strict=False)[0] == 'text/html':
                urls.append(url)
            else:
                files.append(url)

        for url in locations:

            is_local_path = os.path.exists(url)
            is_file_url = url.startswith('file:')
            is_find_link = url in self.find_links

            if is_local_path or is_file_url:
                if is_local_path:
                    path = url
                else:
                    path = url_to_path(url)
                if is_find_link and os.path.isdir(path):
                    path = os.path.realpath(path)
                    for item in os.listdir(path):
                        sort_path(os.path.join(path, item))
                elif is_file_url and os.path.isdir(path):
                    urls.append(url)
                elif os.path.isfile(path):
                    sort_path(path)
            else:
                urls.append(url)

        return files, urls

    def _candidate_sort_key(self, candidate):
        """
        Function used to generate link sort key for link tuples.
        The greater the return value, the more preferred it is.
        If not finding wheels, then sorted by version only.
        If finding wheels, then the sort order is by version, then:
          1. existing installs
          2. wheels ordered via Wheel.support_index_min()
          3. source archives
        Note: it was considered to embed this logic into the Link
              comparison operators, but then different sdist links
              with the same version, would have to be considered equal
        """
        if self.use_wheel:
            support_num = len(supported_tags)
            if candidate.location == INSTALLED_VERSION:
                pri = 1
            elif candidate.location.is_wheel:
                # can raise InvalidWheelFilename
                wheel = Wheel(candidate.location.filename)
                if not wheel.supported():
                    raise UnsupportedWheel(
                        "%s is not a supported wheel for this platform. It "
                        "can't be sorted." % wheel.filename
                    )
                pri = -(wheel.support_index_min())
            else:  # sdist
                pri = -(support_num)
            return (candidate.version, pri)
        else:
            return candidate.version

    def _sort_versions(self, applicable_versions):
        """
        Bring the latest version (and wheels) to the front, but maintain the
        existing ordering as secondary. See the docstring for `_link_sort_key`
        for details. This function is isolated for easier unit testing.
        """
        return sorted(
            applicable_versions,
            key=self._candidate_sort_key,
            reverse=True
        )

    def _validate_secure_origin(self, logger, location):
        # Determine if this url used a secure transport mechanism
        parsed = urllib_parse.urlparse(str(location))
        origin = (parsed.scheme, parsed.hostname, parsed.port)

        # Determine if our origin is a secure origin by looking through our
        # hardcoded list of secure origins, as well as any additional ones
        # configured on this PackageFinder instance.
        for secure_origin in (SECURE_ORIGINS + self.secure_origins):
            # Check to see if the protocol matches
            if origin[0] != secure_origin[0] and secure_origin[0] != "*":
                continue

            try:
                # We need to do this decode dance to ensure that we have a
                # unicode object, even on Python 2.x.
                addr = ipaddress.ip_address(
                    origin[1]
                    if (
                        isinstance(origin[1], six.text_type) or
                        origin[1] is None
                    )
                    else origin[1].decode("utf8")
                )
                network = ipaddress.ip_network(
                    secure_origin[1]
                    if isinstance(secure_origin[1], six.text_type)
                    else secure_origin[1].decode("utf8")
                )
            except ValueError:
                # We don't have both a valid address or a valid network, so
                # we'll check this origin against hostnames.
                if origin[1] != secure_origin[1] and secure_origin[1] != "*":
                    continue
            else:
                # We have a valid address and network, so see if the address
                # is contained within the network.
                if addr not in network:
                    continue

            # Check to see if the port patches
            if (origin[2] != secure_origin[2] and
                    secure_origin[2] != "*" and
                    secure_origin[2] is not None):
                continue

            # If we've gotten here, then this origin matches the current
            # secure origin and we should break out of the loop and continue
            # on.
            break
        else:
            # If the loop successfully completed without a break, that means
            # that the origin we are testing is not a secure origin.
            logger.warning(
                "This repository located at %s is not a trusted host, if "
                "this repository is available via HTTPS it is recommend to "
                "use HTTPS instead, otherwise you may silence this warning "
                "with '--trusted-host %s'.",
                parsed.hostname,
                parsed.hostname,
            )

            warnings.warn(
                "Implicitly allowing locations which are not hosted at a "
                "secure origin is deprecated and will require the use of "
                "--trusted-host in the future.",
                RemovedInPip7Warning,
            )

    def _get_index_urls_locations(self, project_name):
        """Returns the locations found via self.index_urls

        Checks the url_name on the main (first in the list) index and
        use this url_name to produce all locations
        """

        def mkurl_pypi_url(url):
            loc = posixpath.join(url, project_url_name)
            # For maximum compatibility with easy_install, ensure the path
            # ends in a trailing slash.  Although this isn't in the spec
            # (and PyPI can handle it without the slash) some other index
            # implementations might break if they relied on easy_install's
            # behavior.
            if not loc.endswith('/'):
                loc = loc + '/'
            return loc

        project_url_name = urllib_parse.quote(project_name.lower())

        if self.index_urls:
            # Check that we have the url_name correctly spelled:

            # Only check main index if index URL is given
            main_index_url = Link(
                mkurl_pypi_url(self.index_urls[0]),
                trusted=True,
            )

            page = self._get_page(main_index_url)
            if page is None and PyPI.netloc not in str(main_index_url):
                warnings.warn(
                    "Failed to find %r at %s. It is suggested to upgrade "
                    "your index to support normalized names as the name in "
                    "/simple/{name}." % (project_name, main_index_url),
                    RemovedInPip8Warning,
                )

                project_url_name = self._find_url_name(
                    Link(self.index_urls[0], trusted=True),
                    project_url_name,
                ) or project_url_name

        if project_url_name is not None:
            return [mkurl_pypi_url(url) for url in self.index_urls]
        return []

    def _find_all_versions(self, project_name):
        """Find all available versions for project_name

        This checks index_urls, find_links and dependency_links
        All versions found are returned

        See _link_package_versions for details on which files are accepted
        """
        index_locations = self._get_index_urls_locations(project_name)
        file_locations, url_locations = self._sort_locations(index_locations)
        fl_file_loc, fl_url_loc = self._sort_locations(self.find_links)
        file_locations.extend(fl_file_loc)
        url_locations.extend(fl_url_loc)

        _flocations, _ulocations = self._sort_locations(self.dependency_links)
        file_locations.extend(_flocations)

        # We trust every url that the user has given us whether it was given
        #   via --index-url or --find-links
        locations = [Link(url, trusted=True) for url in url_locations]

        # We explicitly do not trust links that came from dependency_links
        locations.extend([Link(url) for url in _ulocations])

        logger.debug('%d location(s) to search for versions of %s:',
                     len(locations), project_name)
        for location in locations:
            logger.debug('* %s', location)
            self._validate_secure_origin(logger, location)

        find_links_versions = list(self._package_versions(
            # We trust every directly linked archive in find_links
            (Link(url, '-f', trusted=True) for url in self.find_links),
            project_name.lower()
        ))

        page_versions = []
        for page in self._get_pages(locations, project_name):
            logger.debug('Analyzing links from page %s', page.url)
            with indent_log():
                page_versions.extend(
                    self._package_versions(page.links, project_name.lower())
                )

        dependency_versions = list(self._package_versions(
            (Link(url) for url in self.dependency_links), project_name.lower()
        ))
        if dependency_versions:
            logger.debug(
                'dependency_links found: %s',
                ', '.join([
                    version.location.url for version in dependency_versions
                ])
            )

        file_versions = list(
            self._package_versions(
                (Link(url) for url in file_locations),
                project_name.lower()
            )
        )
        if file_versions:
            file_versions.sort(reverse=True)
            logger.debug(
                'Local files found: %s',
                ', '.join([
                    url_to_path(candidate.location.url)
                    for candidate in file_versions
                ])
            )

        # This is an intentional priority ordering
        return (
            file_versions + find_links_versions + page_versions +
            dependency_versions
        )

    def find_requirement(self, req, upgrade):
        """Try to find an InstallationCandidate for req

        Expects req, an InstallRequirement and upgrade, a boolean
        Returns an InstallationCandidate or None
        May raise DistributionNotFound or BestVersionAlreadyInstalled
        """
        all_versions = self._find_all_versions(req.name)
        # Filter out anything which doesn't match our specifier

        _versions = set(
            req.specifier.filter(
                [x.version for x in all_versions],
                prereleases=(
                    self.allow_all_prereleases
                    if self.allow_all_prereleases else None
                ),
            )
        )
        applicable_versions = [
            x for x in all_versions if x.version in _versions
        ]

        if req.satisfied_by is not None:
            # Finally add our existing versions to the front of our versions.
            applicable_versions.insert(
                0,
                InstallationCandidate(
                    req.name,
                    req.satisfied_by.version,
                    INSTALLED_VERSION,
                )
            )
            existing_applicable = True
        else:
            existing_applicable = False

        applicable_versions = self._sort_versions(applicable_versions)

        if not upgrade and existing_applicable:
            if applicable_versions[0].location is INSTALLED_VERSION:
                logger.debug(
                    'Existing installed version (%s) is most up-to-date and '
                    'satisfies requirement',
                    req.satisfied_by.version,
                )
            else:
                logger.debug(
                    'Existing installed version (%s) satisfies requirement '
                    '(most up-to-date version is %s)',
                    req.satisfied_by.version,
                    applicable_versions[0][2],
                )
            return None

        if not applicable_versions:
            logger.critical(
                'Could not find a version that satisfies the requirement %s '
                '(from versions: %s)',
                req,
                ', '.join(
                    sorted(
                        set(str(i.version) for i in all_versions),
                        key=parse_version,
                    )
                )
            )

            if self.need_warn_external:
                logger.warning(
                    "Some externally hosted files were ignored as access to "
                    "them may be unreliable (use --allow-external %s to "
                    "allow).",
                    req.name,
                )

            if self.need_warn_unverified:
                logger.warning(
                    "Some insecure and unverifiable files were ignored"
                    " (use --allow-unverified %s to allow).",
                    req.name,
                )

            raise DistributionNotFound(
                'No matching distribution found for %s' % req
            )

        if applicable_versions[0].location is INSTALLED_VERSION:
            # We have an existing version, and its the best version
            logger.debug(
                'Installed version (%s) is most up-to-date (past versions: '
                '%s)',
                req.satisfied_by.version,
                ', '.join(str(i.version) for i in applicable_versions[1:]) or
                "none",
            )
            raise BestVersionAlreadyInstalled

        if len(applicable_versions) > 1:
            logger.debug(
                'Using version %s (newest of versions: %s)',
                applicable_versions[0].version,
                ', '.join(str(i.version) for i in applicable_versions)
            )

        selected_version = applicable_versions[0].location

        if (selected_version.verifiable is not None and not
                selected_version.verifiable):
            logger.warning(
                "%s is potentially insecure and unverifiable.", req.name,
            )

        if selected_version._deprecated_regex:
            warnings.warn(
                "%s discovered using a deprecated method of parsing, in the "
                "future it will no longer be discovered." % req.name,
                RemovedInPip7Warning,
            )

        return selected_version

    def _find_url_name(self, index_url, url_name):
        """
        Finds the true URL name of a package, when the given name isn't quite
        correct.
        This is usually used to implement case-insensitivity.
        """
        if not index_url.url.endswith('/'):
            # Vaguely part of the PyPI API... weird but true.
            # FIXME: bad to modify this?
            index_url.url += '/'
        page = self._get_page(index_url)
        if page is None:
            logger.critical('Cannot fetch index base URL %s', index_url)
            return
        norm_name = normalize_name(url_name)
        for link in page.links:
            base = posixpath.basename(link.path.rstrip('/'))
            if norm_name == normalize_name(base):
                logger.debug(
                    'Real name of requirement %s is %s', url_name, base,
                )
                return base
        return None

    def _get_pages(self, locations, project_name):
        """
        Yields (page, page_url) from the given locations, skipping
        locations that have errors, and adding download/homepage links
        """
        all_locations = list(locations)
        seen = set()
        normalized = normalize_name(project_name)

        while all_locations:
            location = all_locations.pop(0)
            if location in seen:
                continue
            seen.add(location)

            page = self._get_page(location)
            if page is None:
                continue

            yield page

            for link in page.rel_links():

                if (normalized not in self.allow_external and not
                        self.allow_all_external):
                    self.need_warn_external = True
                    logger.debug(
                        "Not searching %s for files because external "
                        "urls are disallowed.",
                        link,
                    )
                    continue

                if (link.trusted is not None and not
                        link.trusted and
                        normalized not in self.allow_unverified):
                    logger.debug(
                        "Not searching %s for urls, it is an "
                        "untrusted link and cannot produce safe or "
                        "verifiable files.",
                        link,
                    )
                    self.need_warn_unverified = True
                    continue

                all_locations.append(link)

    _egg_fragment_re = re.compile(r'#egg=([^&]*)')
    _egg_info_re = re.compile(r'([a-z0-9_.]+)-([a-z0-9_.!+-]+)', re.I)
    _py_version_re = re.compile(r'-py([123]\.?[0-9]?)$')

    def _sort_links(self, links):
        """
        Returns elements of links in order, non-egg links first, egg links
        second, while eliminating duplicates
        """
        eggs, no_eggs = [], []
        seen = set()
        for link in links:
            if link not in seen:
                seen.add(link)
                if link.egg_fragment:
                    eggs.append(link)
                else:
                    no_eggs.append(link)
        return no_eggs + eggs

    def _package_versions(self, links, search_name):
        for link in self._sort_links(links):
            v = self._link_package_versions(link, search_name)
            if v is not None:
                yield v

    def _known_extensions(self):
        extensions = ('.tar.gz', '.tar.bz2', '.tar', '.tgz', '.zip')
        if self.use_wheel:
            return extensions + (wheel_ext,)
        return extensions

    def _link_package_versions(self, link, search_name):
        """Return an InstallationCandidate or None"""
        platform = get_platform()

        version = None
        if link.egg_fragment:
            egg_info = link.egg_fragment
        else:
            egg_info, ext = link.splitext()
            if not ext:
                if link not in self.logged_links:
                    logger.debug('Skipping link %s; not a file', link)
                    self.logged_links.add(link)
                return
            if egg_info.endswith('.tar'):
                # Special double-extension case:
                egg_info = egg_info[:-4]
                ext = '.tar' + ext
            if ext not in self._known_extensions():
                if link not in self.logged_links:
                    logger.debug(
                        'Skipping link %s; unknown archive format: %s',
                        link,
                        ext,
                    )
                    self.logged_links.add(link)
                return
            if "macosx10" in link.path and ext == '.zip':
                if link not in self.logged_links:
                    logger.debug('Skipping link %s; macosx10 one', link)
                    self.logged_links.add(link)
                return
            if ext == wheel_ext:
                try:
                    wheel = Wheel(link.filename)
                except InvalidWheelFilename:
                    logger.debug(
                        'Skipping %s because the wheel filename is invalid',
                        link
                    )
                    return
                if (pkg_resources.safe_name(wheel.name).lower() !=
                        pkg_resources.safe_name(search_name).lower()):
                    logger.debug(
                        'Skipping link %s; wrong project name (not %s)',
                        link,
                        search_name,
                    )
                    return
                if not wheel.supported():
                    logger.debug(
                        'Skipping %s because it is not compatible with this '
                        'Python',
                        link,
                    )
                    return
                # This is a dirty hack to prevent installing Binary Wheels from
                # PyPI unless it is a Windows or Mac Binary Wheel. This is
                # paired with a change to PyPI disabling uploads for the
                # same. Once we have a mechanism for enabling support for
                # binary wheels on linux that deals with the inherent problems
                # of binary distribution this can be removed.
                comes_from = getattr(link, "comes_from", None)
                if (
                        (
                            not platform.startswith('win') and not
                            platform.startswith('macosx') and not
                            platform == 'cli'
                        ) and
                        comes_from is not None and
                        urllib_parse.urlparse(
                            comes_from.url
                        ).netloc.endswith(PyPI.netloc)):
                    if not wheel.supported(tags=supported_tags_noarch):
                        logger.debug(
                            "Skipping %s because it is a pypi-hosted binary "
                            "Wheel on an unsupported platform",
                            link,
                        )
                        return
                version = wheel.version

        if not version:
            version = self._egg_info_matches(egg_info, search_name, link)
        if version is None:
            logger.debug(
                'Skipping link %s; wrong project name (not %s)',
                link,
                search_name,
            )
            return

        if (link.internal is not None and not
                link.internal and not
                normalize_name(search_name).lower()
                in self.allow_external and not
                self.allow_all_external):
            # We have a link that we are sure is external, so we should skip
            #   it unless we are allowing externals
            logger.debug("Skipping %s because it is externally hosted.", link)
            self.need_warn_external = True
            return

        if (link.verifiable is not None and not
                link.verifiable and not
                (normalize_name(search_name).lower()
                    in self.allow_unverified)):
            # We have a link that we are sure we cannot verify its integrity,
            #   so we should skip it unless we are allowing unsafe installs
            #   for this requirement.
            logger.debug(
                "Skipping %s because it is an insecure and unverifiable file.",
                link,
            )
            self.need_warn_unverified = True
            return

        match = self._py_version_re.search(version)
        if match:
            version = version[:match.start()]
            py_version = match.group(1)
            if py_version != sys.version[:3]:
                logger.debug(
                    'Skipping %s because Python version is incorrect', link
                )
                return
        logger.debug('Found link %s, version: %s', link, version)

        return InstallationCandidate(search_name, version, link)

    def _egg_info_matches(self, egg_info, search_name, link):
        match = self._egg_info_re.search(egg_info)
        if not match:
            logger.debug('Could not parse version from link: %s', link)
            return None
        name = match.group(0).lower()
        # To match the "safe" name that pkg_resources creates:
        name = name.replace('_', '-')
        # project name and version must be separated by a dash
        look_for = search_name.lower() + "-"
        if name.startswith(look_for):
            return match.group(0)[len(look_for):]
        else:
            return None

    def _get_page(self, link):
        return HTMLPage.get_page(link, session=self.session)


class HTMLPage(object):
    """Represents one page, along with its URL"""

    # FIXME: these regexes are horrible hacks:
    _homepage_re = re.compile(b'<th>\\s*home\\s*page', re.I)
    _download_re = re.compile(b'<th>\\s*download\\s+url', re.I)
    _href_re = re.compile(
        b'href=(?:"([^"]*)"|\'([^\']*)\'|([^>\\s\\n]*))',
        re.I | re.S
    )

    def __init__(self, content, url, headers=None, trusted=None):
        # Determine if we have any encoding information in our headers
        encoding = None
        if headers and "Content-Type" in headers:
            content_type, params = cgi.parse_header(headers["Content-Type"])

            if "charset" in params:
                encoding = params['charset']

        self.content = content
        self.parsed = html5lib.parse(
            self.content,
            encoding=encoding,
            namespaceHTMLElements=False,
        )
        self.url = url
        self.headers = headers
        self.trusted = trusted

    def __str__(self):
        return self.url

    @classmethod
    def get_page(cls, link, skip_archives=True, session=None):
        if session is None:
            raise TypeError(
                "get_page() missing 1 required keyword argument: 'session'"
            )

        url = link.url
        url = url.split('#', 1)[0]

        # Check for VCS schemes that do not support lookup as web pages.
        from pip.vcs import VcsSupport
        for scheme in VcsSupport.schemes:
            if url.lower().startswith(scheme) and url[len(scheme)] in '+:':
                logger.debug('Cannot look at %s URL %s', scheme, link)
                return None

        try:
            if skip_archives:
                filename = link.filename
                for bad_ext in ['.tar', '.tar.gz', '.tar.bz2', '.tgz', '.zip']:
                    if filename.endswith(bad_ext):
                        content_type = cls._get_content_type(
                            url, session=session,
                        )
                        if content_type.lower().startswith('text/html'):
                            break
                        else:
                            logger.debug(
                                'Skipping page %s because of Content-Type: %s',
                                link,
                                content_type,
                            )
                            return

            logger.debug('Getting page %s', url)

            # Tack index.html onto file:// URLs that point to directories
            (scheme, netloc, path, params, query, fragment) = \
                urllib_parse.urlparse(url)
            if (scheme == 'file' and
                    os.path.isdir(urllib_request.url2pathname(path))):
                # add trailing slash if not present so urljoin doesn't trim
                # final segment
                if not url.endswith('/'):
                    url += '/'
                url = urllib_parse.urljoin(url, 'index.html')
                logger.debug(' file: URL is directory, getting %s', url)

            resp = session.get(
                url,
                headers={
                    "Accept": "text/html",
                    "Cache-Control": "max-age=600",
                },
            )
            resp.raise_for_status()

            # The check for archives above only works if the url ends with
            #   something that looks like an archive. However that is not a
            #   requirement of an url. Unless we issue a HEAD request on every
            #   url we cannot know ahead of time for sure if something is HTML
            #   or not. However we can check after we've downloaded it.
            content_type = resp.headers.get('Content-Type', 'unknown')
            if not content_type.lower().startswith("text/html"):
                logger.debug(
                    'Skipping page %s because of Content-Type: %s',
                    link,
                    content_type,
                )
                return

            inst = cls(
                resp.content, resp.url, resp.headers,
                trusted=link.trusted,
            )
        except requests.HTTPError as exc:
            level = 2 if exc.response.status_code == 404 else 1
            cls._handle_fail(link, exc, url, level=level)
        except requests.ConnectionError as exc:
            cls._handle_fail(link, "connection error: %s" % exc, url)
        except requests.Timeout:
            cls._handle_fail(link, "timed out", url)
        except SSLError as exc:
            reason = ("There was a problem confirming the ssl certificate: "
                      "%s" % exc)
            cls._handle_fail(link, reason, url, level=2, meth=logger.info)
        else:
            return inst

    @staticmethod
    def _handle_fail(link, reason, url, level=1, meth=None):
        if meth is None:
            meth = logger.debug

        meth("Could not fetch URL %s: %s - skipping", link, reason)

    @staticmethod
    def _get_content_type(url, session):
        """Get the Content-Type of the given url, using a HEAD request"""
        scheme, netloc, path, query, fragment = urllib_parse.urlsplit(url)
        if scheme not in ('http', 'https'):
            # FIXME: some warning or something?
            # assertion error?
            return ''

        resp = session.head(url, allow_redirects=True)
        resp.raise_for_status()

        return resp.headers.get("Content-Type", "")

    @cached_property
    def api_version(self):
        metas = [
            x for x in self.parsed.findall(".//meta")
            if x.get("name", "").lower() == "api-version"
        ]
        if metas:
            try:
                return int(metas[0].get("value", None))
            except (TypeError, ValueError):
                pass

        return None

    @cached_property
    def base_url(self):
        bases = [
            x for x in self.parsed.findall(".//base")
            if x.get("href") is not None
        ]
        if bases and bases[0].get("href"):
            return bases[0].get("href")
        else:
            return self.url

    @property
    def links(self):
        """Yields all links in the page"""
        for anchor in self.parsed.findall(".//a"):
            if anchor.get("href"):
                href = anchor.get("href")
                url = self.clean_link(
                    urllib_parse.urljoin(self.base_url, href)
                )

                # Determine if this link is internal. If that distinction
                #   doesn't make sense in this context, then we don't make
                #   any distinction.
                internal = None
                if self.api_version and self.api_version >= 2:
                    # Only api_versions >= 2 have a distinction between
                    #   external and internal links
                    internal = bool(
                        anchor.get("rel") and
                        "internal" in anchor.get("rel").split()
                    )

                yield Link(url, self, internal=internal)

    def rel_links(self):
        for url in self.explicit_rel_links():
            yield url
        for url in self.scraped_rel_links():
            yield url

    def explicit_rel_links(self, rels=('homepage', 'download')):
        """Yields all links with the given relations"""
        rels = set(rels)

        for anchor in self.parsed.findall(".//a"):
            if anchor.get("rel") and anchor.get("href"):
                found_rels = set(anchor.get("rel").split())
                # Determine the intersection between what rels were found and
                #   what rels were being looked for
                if found_rels & rels:
                    href = anchor.get("href")
                    url = self.clean_link(
                        urllib_parse.urljoin(self.base_url, href)
                    )
                    yield Link(url, self, trusted=False)

    def scraped_rel_links(self):
        # Can we get rid of this horrible horrible method?
        for regex in (self._homepage_re, self._download_re):
            match = regex.search(self.content)
            if not match:
                continue
            href_match = self._href_re.search(self.content, pos=match.end())
            if not href_match:
                continue
            url = (
                href_match.group(1) or
                href_match.group(2) or
                href_match.group(3)
            )
            if not url:
                continue
            try:
                url = url.decode("ascii")
            except UnicodeDecodeError:
                continue
            url = self.clean_link(urllib_parse.urljoin(self.base_url, url))
            yield Link(url, self, trusted=False, _deprecated_regex=True)

    _clean_re = re.compile(r'[^a-z0-9$&+,/:;=?@.#%_\\|-]', re.I)

    def clean_link(self, url):
        """Makes sure a link is fully encoded.  That is, if a ' ' shows up in
        the link, it will be rewritten to %20 (while not over-quoting
        % or other characters)."""
        return self._clean_re.sub(
            lambda match: '%%%2x' % ord(match.group(0)), url)


class Link(object):

    def __init__(self, url, comes_from=None, internal=None, trusted=None,
                 _deprecated_regex=False):

        # url can be a UNC windows share
        if url != Inf and url.startswith('\\\\'):
            url = path_to_url(url)

        self.url = url
        self.comes_from = comes_from
        self.internal = internal
        self.trusted = trusted
        self._deprecated_regex = _deprecated_regex

    def __str__(self):
        if self.comes_from:
            return '%s (from %s)' % (self.url, self.comes_from)
        else:
            return str(self.url)

    def __repr__(self):
        return '<Link %s>' % self

    def __eq__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url == other.url

    def __ne__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url != other.url

    def __lt__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url < other.url

    def __le__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url <= other.url

    def __gt__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url > other.url

    def __ge__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.url >= other.url

    def __hash__(self):
        return hash(self.url)

    @property
    def filename(self):
        _, netloc, path, _, _ = urllib_parse.urlsplit(self.url)
        name = posixpath.basename(path.rstrip('/')) or netloc
        name = urllib_parse.unquote(name)
        assert name, ('URL %r produced no filename' % self.url)
        return name

    @property
    def scheme(self):
        return urllib_parse.urlsplit(self.url)[0]

    @property
    def netloc(self):
        return urllib_parse.urlsplit(self.url)[1]

    @property
    def path(self):
        return urllib_parse.unquote(urllib_parse.urlsplit(self.url)[2])

    def splitext(self):
        return splitext(posixpath.basename(self.path.rstrip('/')))

    @property
    def ext(self):
        return self.splitext()[1]

    @property
    def url_without_fragment(self):
        scheme, netloc, path, query, fragment = urllib_parse.urlsplit(self.url)
        return urllib_parse.urlunsplit((scheme, netloc, path, query, None))

    _egg_fragment_re = re.compile(r'#egg=([^&]*)')

    @property
    def egg_fragment(self):
        match = self._egg_fragment_re.search(self.url)
        if not match:
            return None
        return match.group(1)

    _hash_re = re.compile(
        r'(sha1|sha224|sha384|sha256|sha512|md5)=([a-f0-9]+)'
    )

    @property
    def hash(self):
        match = self._hash_re.search(self.url)
        if match:
            return match.group(2)
        return None

    @property
    def hash_name(self):
        match = self._hash_re.search(self.url)
        if match:
            return match.group(1)
        return None

    @property
    def show_url(self):
        return posixpath.basename(self.url.split('#', 1)[0].split('?', 1)[0])

    @property
    def verifiable(self):
        """
        Returns True if this link can be verified after download, False if it
        cannot, and None if we cannot determine.
        """
        trusted = self.trusted or getattr(self.comes_from, "trusted", None)
        if trusted is not None and trusted:
            # This link came from a trusted source. It *may* be verifiable but
            #   first we need to see if this page is operating under the new
            #   API version.
            try:
                api_version = getattr(self.comes_from, "api_version", None)
                api_version = int(api_version)
            except (ValueError, TypeError):
                api_version = None

            if api_version is None or api_version <= 1:
                # This link is either trusted, or it came from a trusted,
                #   however it is not operating under the API version 2 so
                #   we can't make any claims about if it's safe or not
                return

            if self.hash:
                # This link came from a trusted source and it has a hash, so we
                #   can consider it safe.
                return True
            else:
                # This link came from a trusted source, using the new API
                #   version, and it does not have a hash. It is NOT verifiable
                return False
        elif trusted is not None:
            # This link came from an untrusted source and we cannot trust it
            return False

    @property
    def is_wheel(self):
        return self.ext == wheel_ext


# An object to represent the "link" for the installed version of a requirement.
# Using Inf as the url makes it sort higher.
INSTALLED_VERSION = Link(Inf)
