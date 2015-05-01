"""Base Command class, and related routines"""
from __future__ import absolute_import

import logging
import os
import sys
import traceback
import optparse
import warnings

from pip._vendor.six import StringIO

from pip import cmdoptions
from pip.locations import running_under_virtualenv
from pip.download import PipSession
from pip.exceptions import (BadCommand, InstallationError, UninstallationError,
                            CommandError, PreviousBuildDirError)
from pip.compat import logging_dictConfig
from pip.baseparser import ConfigOptionParser, UpdatingDefaultsHelpFormatter
from pip.status_codes import (
    SUCCESS, ERROR, UNKNOWN_ERROR, VIRTUALENV_NOT_FOUND,
    PREVIOUS_BUILD_DIR_ERROR,
)
from pip.utils import appdirs, get_prog, normalize_path
from pip.utils.deprecation import RemovedInPip8Warning
from pip.utils.filesystem import check_path_owner
from pip.utils.logging import IndentingFormatter
from pip.utils.outdated import pip_version_check


__all__ = ['Command']


logger = logging.getLogger(__name__)


class Command(object):
    name = None
    usage = None
    hidden = False
    log_streams = ("ext://sys.stdout", "ext://sys.stderr")

    def __init__(self, isolated=False):
        parser_kw = {
            'usage': self.usage,
            'prog': '%s %s' % (get_prog(), self.name),
            'formatter': UpdatingDefaultsHelpFormatter(),
            'add_help_option': False,
            'name': self.name,
            'description': self.__doc__,
            'isolated': isolated,
        }

        self.parser = ConfigOptionParser(**parser_kw)

        # Commands should add options to this option group
        optgroup_name = '%s Options' % self.name.capitalize()
        self.cmd_opts = optparse.OptionGroup(self.parser, optgroup_name)

        # Add the general options
        gen_opts = cmdoptions.make_option_group(
            cmdoptions.general_group,
            self.parser,
        )
        self.parser.add_option_group(gen_opts)

    def _build_session(self, options, retries=None, timeout=None):
        session = PipSession(
            cache=(
                normalize_path(os.path.join(options.cache_dir, "http"))
                if options.cache_dir else None
            ),
            retries=retries if retries is not None else options.retries,
            insecure_hosts=options.trusted_hosts,
        )

        # Handle custom ca-bundles from the user
        if options.cert:
            session.verify = options.cert

        # Handle SSL client certificate
        if options.client_cert:
            session.cert = options.client_cert

        # Handle timeouts
        if options.timeout or timeout:
            session.timeout = (
                timeout if timeout is not None else options.timeout
            )

        # Handle configured proxies
        if options.proxy:
            session.proxies = {
                "http": options.proxy,
                "https": options.proxy,
            }

        # Determine if we can prompt the user for authentication or not
        session.auth.prompting = not options.no_input

        return session

    def parse_args(self, args):
        # factored out for testability
        return self.parser.parse_args(args)

    def main(self, args):
        options, args = self.parse_args(args)

        if options.quiet:
            level = "WARNING"
        elif options.verbose:
            level = "DEBUG"
        else:
            level = "INFO"

        # Compute the path for our debug log.
        debug_log_path = os.path.join(appdirs.user_log_dir("pip"), "debug.log")

        # Ensure that the path for our debug log is owned by the current user
        # and if it is not, disable the debug log.
        write_debug_log = check_path_owner(debug_log_path)

        logging_dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "exclude_warnings": {
                    "()": "pip.utils.logging.MaxLevelFilter",
                    "level": logging.WARNING,
                },
            },
            "formatters": {
                "indent": {
                    "()": IndentingFormatter,
                    "format": (
                        "%(message)s"
                        if not options.log_explicit_levels
                        else "[%(levelname)s] %(message)s"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "level": level,
                    "class": "pip.utils.logging.ColorizedStreamHandler",
                    "stream": self.log_streams[0],
                    "filters": ["exclude_warnings"],
                    "formatter": "indent",
                },
                "console_errors": {
                    "level": "WARNING",
                    "class": "pip.utils.logging.ColorizedStreamHandler",
                    "stream": self.log_streams[1],
                    "formatter": "indent",
                },
                "debug_log": {
                    "level": "DEBUG",
                    "class": "pip.utils.logging.BetterRotatingFileHandler",
                    "filename": debug_log_path,
                    "maxBytes": 10 * 1000 * 1000,  # 10 MB
                    "backupCount": 1,
                    "delay": True,
                    "formatter": "indent",
                },
                "user_log": {
                    "level": "DEBUG",
                    "class": "pip.utils.logging.BetterRotatingFileHandler",
                    "filename": options.log or "/dev/null",
                    "delay": True,
                    "formatter": "indent",
                },
            },
            "root": {
                "level": level,
                "handlers": list(filter(None, [
                    "console",
                    "console_errors",
                    "debug_log" if write_debug_log else None,
                    "user_log" if options.log else None,
                ])),
            },
            # Disable any logging besides WARNING unless we have DEBUG level
            # logging enabled. These use both pip._vendor and the bare names
            # for the case where someone unbundles our libraries.
            "loggers": dict(
                (
                    name,
                    {
                        "level": (
                            "WARNING"
                            if level in ["INFO", "ERROR"]
                            else "DEBUG"
                        ),
                    },
                )
                for name in ["pip._vendor", "distlib", "requests", "urllib3"]
            ),
        })

        # We add this warning here instead of up above, because the logger
        # hasn't been configured until just now.
        if not write_debug_log:
            logger.warning(
                "The directory '%s' or its parent directory is not owned by "
                "the current user and the debug log has been disabled. Please "
                "check the permissions and owner of that directory. If "
                "executing pip with sudo, you may want sudo's -H flag.",
                os.path.dirname(debug_log_path),
            )

        if options.log_explicit_levels:
            warnings.warn(
                "--log-explicit-levels has been deprecated and will be removed"
                " in a future version.",
                RemovedInPip8Warning,
            )

        # TODO: try to get these passing down from the command?
        #      without resorting to os.environ to hold these.

        if options.no_input:
            os.environ['PIP_NO_INPUT'] = '1'

        if options.exists_action:
            os.environ['PIP_EXISTS_ACTION'] = ' '.join(options.exists_action)

        if options.require_venv:
            # If a venv is required check if it can really be found
            if not running_under_virtualenv():
                logger.critical(
                    'Could not find an activated virtualenv (required).'
                )
                sys.exit(VIRTUALENV_NOT_FOUND)

        # Check if we're using the latest version of pip available
        if (not options.disable_pip_version_check and not
                getattr(options, "no_index", False)):
            with self._build_session(
                    options,
                    retries=0,
                    timeout=min(5, options.timeout)) as session:
                pip_version_check(session)

        try:
            status = self.run(options, args)
            # FIXME: all commands should return an exit status
            # and when it is done, isinstance is not needed anymore
            if isinstance(status, int):
                return status
        except PreviousBuildDirError as exc:
            logger.critical(str(exc))
            logger.debug('Exception information:\n%s', format_exc())

            return PREVIOUS_BUILD_DIR_ERROR
        except (InstallationError, UninstallationError, BadCommand) as exc:
            logger.critical(str(exc))
            logger.debug('Exception information:\n%s', format_exc())

            return ERROR
        except CommandError as exc:
            logger.critical('ERROR: %s', exc)
            logger.debug('Exception information:\n%s', format_exc())

            return ERROR
        except KeyboardInterrupt:
            logger.critical('Operation cancelled by user')
            logger.debug('Exception information:\n%s', format_exc())

            return ERROR
        except:
            logger.critical('Exception:\n%s', format_exc())

            return UNKNOWN_ERROR

        return SUCCESS


def format_exc(exc_info=None):
    if exc_info is None:
        exc_info = sys.exc_info()
    out = StringIO()
    traceback.print_exception(*exc_info, **dict(file=out))
    return out.getvalue()
