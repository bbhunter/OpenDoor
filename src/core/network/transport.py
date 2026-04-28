# -*- coding: utf-8 -*-

"""
    Network transport manager.
"""

import os

from .exceptions import NetworkTransportError
from .process import ProcessRunner
from .adapters.direct import DirectTransport
from .adapters.proxy import ProxyTransport
from .adapters.openvpn import OpenVpnTransport
from .adapters.wireguard import WireGuardTransport


class NetworkTransportManager(object):

    """Network transport manager."""

    ADAPTERS = {
        'direct': DirectTransport,
        'proxy': ProxyTransport,
        'openvpn': OpenVpnTransport,
        'wireguard': WireGuardTransport,
    }

    def __init__(self, params, runner=None):
        """
        Constructor.

        :param dict params:
        :param ProcessRunner|None runner:
        """

        self.params = dict(params or {})
        self.runner = runner or ProcessRunner()
        self.transport = self.params.get('transport') or 'direct'
        self.rotate_mode = self.params.get('transport_rotate') or 'none'
        self.profiles = self.__load_profiles()
        self.profile_index = -1
        self.adapter = self.__build_adapter(self.params.get('transport_profile'))

    @property
    def is_vpn(self):
        """
        If selected transport is VPN.

        :return: bool
        """

        return self.transport in ['openvpn', 'wireguard']

    @property
    def current_profile_name(self):
        """
        Return safe current profile name.

        :return: str
        """

        return self.adapter.profile_name

    def start(self):
        """
        Start active transport.

        :return:
        """

        if self.rotate_mode == 'per-target' and self.profile_index < 0:
            self.rotate()

        return self.adapter.start()

    def stop(self):
        """
        Stop active transport.

        :return:
        """

        return self.adapter.stop()

    def rotate(self):
        """
        Rotate transport profile for per-target mode.

        :raise NetworkTransportError:
        :return: BaseTransport
        """

        if self.rotate_mode != 'per-target':
            return self.adapter

        if len(self.profiles) <= 0:
            raise NetworkTransportError('--transport-profiles contains no usable profiles')

        self.profile_index = (self.profile_index + 1) % len(self.profiles)
        self.adapter = self.__build_adapter(self.profiles[self.profile_index])
        return self.adapter

    def __build_adapter(self, profile):
        """
        Build selected transport adapter.

        :param str|None profile:
        :raise NetworkTransportError:
        :return: BaseTransport
        """

        if self.transport not in self.ADAPTERS:
            raise NetworkTransportError('Unsupported network transport: {0}'.format(self.transport))

        params = dict(self.params)
        params['transport_profile'] = profile

        return self.ADAPTERS[self.transport](params, runner=self.runner)

    def __load_profiles(self):
        """
        Load transport profiles list.

        :raise NetworkTransportError:
        :return: list[str]
        """

        profiles_path = self.params.get('transport_profiles')
        if profiles_path is None:
            return []

        if os.path.isfile(profiles_path) is False:
            raise NetworkTransportError('Transport profiles file does not exist: {0}'.format(profiles_path))

        profiles = []
        profiles_dir = os.path.dirname(os.path.abspath(profiles_path))

        with open(profiles_path, 'r', encoding='utf-8') as file:
            for line in file:
                value = line.strip()
                if not value or value.startswith('#'):
                    continue

                if os.path.isabs(value):
                    profile_path = value
                else:
                    profile_path = os.path.abspath(os.path.join(profiles_dir, value))

                self.__validate_profile_path(profile_path)
                profiles.append(profile_path)

        return profiles

    def __validate_profile_path(self, profile_path):
        """
        Validate profile path from transport profiles list.

        :param str profile_path:
        :raise NetworkTransportError:
        :return: None
        """

        if self.transport == 'openvpn' and str(profile_path).lower().endswith('.ovpn') is False:
            raise NetworkTransportError('OpenVPN transport profiles list must contain only *.ovpn files')

        if self.transport == 'wireguard' and str(profile_path).lower().endswith('.conf') is False:
            raise NetworkTransportError('WireGuard transport profiles list must contain only *.conf files')

        if self.transport in ['openvpn', 'wireguard'] and os.path.isfile(profile_path) is False:
            raise NetworkTransportError('Transport profile does not exist: {0}'.format(profile_path))