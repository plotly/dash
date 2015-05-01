from __future__ import absolute_import

import os
import re

from pip._vendor.six.moves.urllib import parse as urllib_parse

from pip.download import get_file_content
from pip.req.req_install import InstallRequirement
from pip.utils import normalize_name

_scheme_re = re.compile(r'^(http|https|file):', re.I)


def _remove_prefixes(line, short_prefix, long_prefix):
    if line.startswith(short_prefix):
        return line[len(short_prefix):].lstrip()
    else:
        return _remove_prefix(line, long_prefix)


def _remove_prefix(line, prefix):
    """Remove the prefix and eventually one '=' or spaces"""
    return re.sub(r'\s*=?\s*', '', line[len(prefix):])


def parse_requirements(filename, finder=None, comes_from=None, options=None,
                       session=None):
    if session is None:
        raise TypeError(
            "parse_requirements() missing 1 required keyword argument: "
            "'session'"
        )

    skip_match = None
    skip_regex = options.skip_requirements_regex if options else None
    if skip_regex:
        skip_match = re.compile(skip_regex)
    reqs_file_dir = os.path.dirname(os.path.abspath(filename))
    filename, content = get_file_content(
        filename,
        comes_from=comes_from,
        session=session,
    )
    for line_number, line in enumerate(content.splitlines(), 1):
        line = line.strip()

        # Remove comments from file and all spaces before it
        line = re.sub(r"(^|\s)+#.*$", "", line)

        if not line:
            continue
        if skip_match and skip_match.search(line):
            continue
        if line.startswith(('-r', '--requirement')):
            req_url = _remove_prefixes(line, '-r', '--requirement')
            if _scheme_re.search(filename):
                # Relative to a URL
                req_url = urllib_parse.urljoin(filename, req_url)
            elif not _scheme_re.search(req_url):
                req_url = os.path.join(os.path.dirname(filename), req_url)
            for item in parse_requirements(
                    req_url, finder,
                    comes_from=filename,
                    options=options,
                    session=session):
                yield item
        elif line.startswith(('-Z', '--always-unzip')):
            # No longer used, but previously these were used in
            # requirement files, so we'll ignore.
            pass
        elif line.startswith(('-f', '--find-links')):
            find_links = _remove_prefixes(line, '-f', '--find-links')
            # FIXME: it would be nice to keep track of the source of
            # the find_links:
            # support a find-links local path relative to a requirements file
            relative_to_reqs_file = os.path.join(reqs_file_dir, find_links)
            if os.path.exists(relative_to_reqs_file):
                find_links = relative_to_reqs_file
            if finder:
                finder.find_links.append(find_links)
        elif line.startswith(('-i', '--index-url')):
            index_url = _remove_prefixes(line, '-i', '--index-url')
            if finder:
                finder.index_urls = [index_url]
        elif line.startswith('--extra-index-url'):
            line = _remove_prefix(line, '--extra-index-url')
            if finder:
                finder.index_urls.append(line)
        elif line.startswith('--use-wheel'):
            # Default in 1.5
            pass
        elif line.startswith('--no-use-wheel'):
            if finder:
                finder.use_wheel = False
        elif line.startswith('--no-index'):
            if finder:
                finder.index_urls = []
        elif line.startswith("--allow-external"):
            line = _remove_prefix(line, '--allow-external')
            if finder:
                finder.allow_external |= set([normalize_name(line).lower()])
        elif line.startswith("--allow-all-external"):
            if finder:
                finder.allow_all_external = True
        # Remove in 7.0
        elif line.startswith("--no-allow-external"):
            pass
        # Remove in 7.0
        elif line.startswith("--no-allow-insecure"):
            pass
        # Remove after 7.0
        elif line.startswith("--allow-insecure"):
            line = _remove_prefix(line, '--allow-insecure')
            if finder:
                finder.allow_unverified |= set([normalize_name(line).lower()])
        elif line.startswith("--allow-unverified"):
            line = _remove_prefix(line, '--allow-unverified')
            if finder:
                finder.allow_unverified |= set([normalize_name(line).lower()])
        else:
            comes_from = '-r %s (line %s)' % (filename, line_number)
            if line.startswith(('-e', '--editable')):
                editable = _remove_prefixes(line, '-e', '--editable')
                req = InstallRequirement.from_editable(
                    editable,
                    comes_from=comes_from,
                    default_vcs=options.default_vcs if options else None,
                    isolated=options.isolated_mode if options else False,
                )
            else:
                req = InstallRequirement.from_line(
                    line,
                    comes_from,
                    isolated=options.isolated_mode if options else False,
                )
            yield req
