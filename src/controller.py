# -*- coding: utf-8 -*-

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Development: Stanislav WEB
"""

from src.core.decorators import execution_time
from src.lib import ArgumentsError
from src.lib import BrowserError
from src.lib import PackageError
from src.lib import ReporterError
from src.lib import TplError
from src.lib import args
from src.lib import browser
from src.lib import events
from src.lib import package
from src.lib import reporter
from src.lib import tpl
from src.lib.browser.session import SessionManager, SessionError
from src.core.network import NetworkTransportManager, NetworkTransportError
from .exceptions import SrcError


class Controller(object):

    """Controller class"""

    def __init__(self):
        """
        Init constructor
        :raise SrcError
        """

        events.terminate()

        try:
            interpreter = package.check_interpreter()

            if interpreter is not True:
                raise SrcError(
                    tpl.error(
                        key='unsupported',
                        actual=interpreter.get('actual'),
                        expected=interpreter.get('expected')
                    )
                )
            else:
                self.ioargs = args().get_arguments()
        except ArgumentsError as error:
            raise SrcError(tpl.error(error))

    @execution_time(log=tpl)
    def run(self):
        """
        Bootstrap action
        :raise SrcError
        :return: int
        """

        try:
            tpl.message(package.banner())

            if 'host' in self.ioargs or 'targets' in self.ioargs or 'wizard' in self.ioargs or 'session_load' in self.ioargs:
                return getattr(self, 'scan_action')(self.ioargs) or 0

            for action in self.ioargs.keys():
                if hasattr(self, '{0}_action'.format(action)) \
                        and args().is_arg_callable(getattr(self, '{0}_action'.format(action))):
                    getattr(self, '{func}_action'.format(func=action))()
                    return 0

            return 0

        except (SrcError, PackageError, BrowserError, AttributeError) as error:
            raise SrcError(tpl.error(error))

    @staticmethod
    def examples_action():
        """
        Show examples action
        :return: None
        """

        tpl.message(package.examples())

    @staticmethod
    def update_action():
        """
        App update action
        :raise SrcError
        :return: None
        """

        try:
            tpl.message(package.update())
        except (AttributeError, PackageError) as error:
            raise SrcError(error)

    @staticmethod
    def docs_action():
        """
        Displays the user guide for the app.

        :raises SrcError: If there is an error with the package or attribute.
        :return: None
        """

        try:
            package.docs()
        except (AttributeError, PackageError) as error:
            raise SrcError(error)

    @staticmethod
    def version_action():
        """
        Show app version action

        :raise SrcError
        :return: None
        """

        try:
            tpl.message(package.version())
        except (AttributeError, PackageError) as error:
            raise SrcError(error)

    @staticmethod
    def local_version():
        """
        Returns the local version of the app.

        :raises SrcError: If there is an error retrieving the local version.
        :return: None
        """

        try:
            tpl.message(package.local_version())
        except (AttributeError, PackageError) as error:
            raise SrcError(error)

    @classmethod
    def scan_action(cls, params):
        """
        URL scan action
        :param dict params: console input args
        :raise SrcError
        :return: int
        """

        try:
            cli_fail_on_bucket = params.get('fail_on_bucket')
            cli_auto_calibrate = params.get('auto_calibrate')
            cli_calibration_samples = params.get('calibration_samples')
            cli_calibration_threshold = params.get('calibration_threshold')
            cli_transport_overrides = cls._collect_transport_cli_overrides(params)

            if 'wizard' in params:
                tpl.info(key='load_wizard', config=params['wizard'])
                params = package.wizard(params['wizard'])

                if cli_fail_on_bucket is not None:
                    params['fail_on_bucket'] = cli_fail_on_bucket

                if cli_auto_calibrate is not None:
                    params['auto_calibrate'] = cli_auto_calibrate

                if cli_calibration_samples is not None:
                    params['calibration_samples'] = cli_calibration_samples

                if cli_calibration_threshold is not None:
                    params['calibration_threshold'] = cli_calibration_threshold

                params.update(cli_transport_overrides)

            if params.get('session_load'):
                snapshot = SessionManager.load(params.get('session_load'))
                restored = dict(snapshot.get('params') or {})
                restored['session_snapshot'] = snapshot
                restored['session_save'] = params.get('session_load')

                if params.get('session_autosave_sec') is not None:
                    restored['session_autosave_sec'] = params.get('session_autosave_sec')

                if params.get('session_autosave_items') is not None:
                    restored['session_autosave_items'] = params.get('session_autosave_items')

                if cli_fail_on_bucket is not None:
                    restored['fail_on_bucket'] = cli_fail_on_bucket

                if cli_auto_calibrate is not None:
                    restored['auto_calibrate'] = cli_auto_calibrate

                if cli_calibration_samples is not None:
                    restored['calibration_samples'] = cli_calibration_samples

                if cli_calibration_threshold is not None:
                    restored['calibration_threshold'] = cli_calibration_threshold

                restored.update(cli_transport_overrides)

                params = restored
                tpl.info(msg='Loaded session checkpoint from {0}'.format(
                    snapshot.get('_loaded_from', restored['session_save'])))

            targets = cls._resolve_scan_targets(params)

            if params.get('session_save') and len(targets) > 1:
                raise BrowserError(Exception('Persistent sessions currently support one target per run'))

            fail_on_buckets = params.get('fail_on_bucket') or []
            ci_mode_enabled = len(fail_on_buckets) > 0
            fail_on_matches = []

            if ci_mode_enabled is True:
                tpl.info(msg='CI/CD mode enabled: fail-on-bucket={0}'.format(','.join(fail_on_buckets)))

            if reporter.default == params.get('reports'):
                tpl.info(key='use_reports')

            transport = NetworkTransportManager(params)

            if transport.rotate_mode == 'per-target':
                for target in targets:
                    target_params = dict(params)
                    target_params.update(target)

                    transport.rotate()
                    cls._log_transport_start(transport)

                    transport_started = False
                    try:
                        transport.start()
                        transport_started = True

                        scan_result = cls._scan_target(target_params)

                        if ci_mode_enabled is True:
                            fail_on_matches.extend(
                                cls._match_fail_on_buckets(
                                    target_params.get('host'),
                                    scan_result,
                                    fail_on_buckets
                                )
                            )
                    finally:
                        if transport_started is True:
                            transport.stop()
                            cls._log_transport_stop(transport)

            else:
                cls._log_transport_start(transport)

                transport_started = False
                try:
                    transport.start()
                    transport_started = True

                    for target in targets:
                        target_params = dict(params)
                        target_params.update(target)

                        scan_result = cls._scan_target(target_params)

                        if ci_mode_enabled is True:
                            fail_on_matches.extend(
                                cls._match_fail_on_buckets(
                                    target_params.get('host'),
                                    scan_result,
                                    fail_on_buckets
                                )
                            )
                finally:
                    if transport_started is True:
                        transport.stop()
                        cls._log_transport_stop(transport)

            if ci_mode_enabled is True:
                if len(fail_on_matches) > 0:
                    tpl.warning(
                        msg='CI/CD fail-on matched: {0}. Exit code: 1'.format(
                            cls._format_fail_on_matches(fail_on_matches)
                        )
                    )
                    return 1

                tpl.info(msg='CI/CD fail-on passed: no matched buckets. Exit code: 0')

            return 0

        except (AttributeError, BrowserError, ReporterError, TplError, SessionError, NetworkTransportError) as error:
            raise SrcError(error)
        except (KeyboardInterrupt, SystemExit):
            tpl.cancel(key='abort')
            return 0

    @classmethod
    def _scan_target(cls, target_params):
        """
        Run scan flow for one resolved target.

        :param dict target_params:
        :raise BrowserError:
        :return: dict
        """

        brows = browser(target_params)

        if True is reporter.is_reported(target_params.get('host')):
            try:
                tpl.prompt(key='logged')
            except KeyboardInterrupt:
                tpl.cancel(key='abort')

        brows.ping()

        if target_params.get('fingerprint') is True:
            brows.fingerprint()

        if target_params.get('auto_calibrate') is True:
            brows.calibrate()

        brows.scan()
        brows.done()

        return brows.result

    @staticmethod
    def _collect_transport_cli_overrides(params):
        """
        Collect explicit transport options that should override wizard/session params.

        Defaults inserted by option filtering must not accidentally override
        transport settings restored from wizard or session configuration.

        :param dict params:
        :return: dict
        """

        overrides = {}

        transport = params.get('transport')
        if transport in ['proxy', 'openvpn', 'wireguard']:
            overrides['transport'] = transport

        if params.get('transport_profile') is not None:
            overrides['transport_profile'] = params.get('transport_profile')

        if params.get('transport_profiles') is not None:
            overrides['transport_profiles'] = params.get('transport_profiles')

        if params.get('transport_timeout') is not None:
            overrides['transport_timeout'] = params.get('transport_timeout')

        if params.get('transport_healthcheck_url') is not None:
            overrides['transport_healthcheck_url'] = params.get('transport_healthcheck_url')

        if params.get('openvpn_auth') is not None:
            overrides['openvpn_auth'] = params.get('openvpn_auth')

        if params.get('transport_rotate') is not None:
            if params.get('transport_rotate') != 'none' \
                    or overrides.get('transport') in ['proxy', 'openvpn', 'wireguard'] \
                    or overrides.get('transport_profiles') is not None:
                overrides['transport_rotate'] = params.get('transport_rotate')

        return overrides

    @staticmethod
    def _match_fail_on_buckets(host, result, buckets):
        """
        Match CI/CD fail-on buckets against a scan result.

        :param str host:
        :param dict result:
        :param list[str] buckets:
        :return: list[dict]
        """

        if not isinstance(result, dict):
            return []

        totals = result.get('total') or {}
        matches = []

        for bucket in buckets:
            try:
                count = int(totals.get(bucket, 0))
            except (TypeError, ValueError):
                count = 0

            if count > 0:
                matches.append({
                    'host': host,
                    'bucket': bucket,
                    'count': count,
                })

        return matches

    @staticmethod
    def _format_fail_on_matches(matches):
        """
        Format CI/CD fail-on matches for terminal output.

        :param list[dict] matches:
        :return: str
        """

        return '; '.join([
            '{0} {1}={2}'.format(
                item.get('host') or '-',
                item.get('bucket'),
                item.get('count')
            )
            for item in matches
        ])

    @staticmethod
    def _resolve_scan_targets(params):
        """
        Build the list of scan targets from filtered params.

        :param dict params:
        :return: list[dict]
        """

        targets = params.get('targets')
        if targets:
            return targets

        if params.get('host'):
            target = {'host': params.get('host')}

            if params.get('scheme') is not None:
                target['scheme'] = params.get('scheme')

            if params.get('ssl') is not None:
                target['ssl'] = params.get('ssl')

            if params.get('port') is not None:
                target['port'] = params.get('port')

            return [target]

        return []

    @staticmethod
    def _is_transport_loggable(transport):
        """
        Check if transport should be shown in terminal logs.

        :param NetworkTransportManager transport:
        :return: bool
        """

        return getattr(transport, 'transport', 'direct') != 'direct'

    @classmethod
    def _log_transport_start(cls, transport):
        """
        Print transport startup message.

        :param NetworkTransportManager transport:
        :return: None
        """

        if cls._is_transport_loggable(transport) is not True:
            return

        tpl.info(msg='Network transport enabled: {0} profile={1}'.format(
            transport.transport,
            transport.current_profile_name
        ))

    @classmethod
    def _log_transport_stop(cls, transport):
        """
        Print transport stop message.

        :param NetworkTransportManager transport:
        :return: None
        """

        if cls._is_transport_loggable(transport) is not True:
            return

        tpl.info(msg='Network transport stopped: {0} profile={1}'.format(
            transport.transport,
            transport.current_profile_name
        ))