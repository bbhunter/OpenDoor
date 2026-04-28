# -*- coding: utf-8 -*-

"""
    WireGuard network transport.
"""

from .base import BaseTransport


class WireGuardTransport(BaseTransport):

    """WireGuard transport adapter."""

    name = 'wireguard'
    profile_extension = '.conf'

    def build_up_command(self):
        """
        Build WireGuard up command.

        :return: list[str]
        """

        self.validate_profile()
        return ['wg-quick', 'up', self.profile]

    def build_down_command(self):
        """
        Build WireGuard down command.

        :return: list[str]
        """

        self.validate_profile()
        return ['wg-quick', 'down', self.profile]

    def start(self):
        """
        Start WireGuard transport.

        :return:
        """

        return self.runner.run(self.build_up_command(), timeout=self.timeout)

    def stop(self):
        """
        Stop WireGuard transport.

        :return:
        """

        return self.runner.run(self.build_down_command(), timeout=self.timeout)