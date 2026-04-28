# -*- coding: utf-8 -*-

"""
    Base network transport adapter.
"""

import os

from src.core.network.exceptions import NetworkTransportError
from src.core.network.process import ProcessRunner


class BaseTransport(object):

    """Base network transport adapter."""

    name = 'base'
    profile_extension = None

    def __init__(self, params, runner=None):
        """
        Constructor.

        :param dict params:
        :param ProcessRunner|None runner:
        """

        self.params = params
        self.runner = runner or ProcessRunner()
        self.profile = params.get('transport_profile')
        self.timeout = 30 if params.get('transport_timeout') is None else int(params.get('transport_timeout'))
        self.process = None

    @property
    def profile_name(self):
        """
        Safe profile basename for logs.

        :return: str
        """

        if self.profile is None:
            return '-'

        return os.path.basename(str(self.profile))

    def validate_profile(self):
        """
        Validate selected transport profile.

        :raise NetworkTransportError:
        :return: None
        """

        if self.profile_extension is None:
            return

        if self.profile is None:
            raise NetworkTransportError('{0} transport requires a profile'.format(self.name))

        if str(self.profile).lower().endswith(self.profile_extension) is False:
            raise NetworkTransportError('{0} transport requires *{1} profile'.format(
                self.name,
                self.profile_extension
            ))

        if os.path.isfile(self.profile) is False:
            raise NetworkTransportError('{0} profile does not exist: {1}'.format(
                self.name,
                self.profile
            ))

    def start(self):
        """
        Start transport.

        :return: None
        """

        return None

    def stop(self):
        """
        Stop transport.

        :return: None
        """

        return None