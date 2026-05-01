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

from urllib3._collections import HTTPHeaderDict

from .accept import AcceptHeaderProvider
from .cache import CacheControlProvider


class HeaderProvider(AcceptHeaderProvider, CacheControlProvider):
    """ HeaderProvider class"""

    def __init__(self, config):
        """
        Init interface.
        Accept external params
        :param src.lib.browser.config.Config config: browser configurations
        """

        self.__headers = HTTPHeaderDict()

        self.__cfg = config

        AcceptHeaderProvider.__init__(self)
        CacheControlProvider.__init__(self)

    def add_header(self, key, value):
        """
        Add custom header

        :param str key: header name
        :param str value: header value
        :return: HeaderProvider
        """

        self.__headers.update({key.strip(): value.strip()})
        return self

    def _add_default_header(self, key, value):
        """
        Add default header only when it was not provided manually.

        :param str key: header name
        :param str value: header value
        :return: HeaderProvider
        """

        if key not in self.__headers:
            self.add_header(key, value)
        return self

    @staticmethod
    def _is_default_port(scheme, port):
        """
        Check if port is the default port for selected scheme.

        :param str scheme: request scheme
        :param int|str port: request port
        :return: bool
        """

        if port is None:
            return True

        try:
            normalized_port = int(port)
        except (TypeError, ValueError):
            return False

        if str(scheme).lower().startswith('https://'):
            return normalized_port == 443

        return normalized_port == 80

    def _origin_base(self):
        """
        Build origin base without default ports.

        :return: str
        """

        scheme = str(getattr(self.__cfg, 'scheme', 'http://'))
        host = str(getattr(self.__cfg, 'host', ''))
        port = getattr(self.__cfg, 'port', None)

        origin = ''.join([scheme, host])
        if self._is_default_port(scheme, port) is False:
            origin = ':'.join([origin, str(port)])

        return origin

    def _request_method(self):
        """
        Resolve configured request method.

        :return: str
        """

        method = getattr(self.__cfg, 'method', None)
        if method is None:
            method = getattr(self.__cfg, 'requested_method', None)
        if method is None:
            return 'HEAD'
        return str(method).upper()

    @property
    def _headers(self):
        """
        Get Headers
        :return: dict headers
        """

        origin = self._origin_base()
        referer = origin + '/'
        method = self._request_method()

        self._add_default_header('Accept', self._accept) \
            ._add_default_header('Accept-Encoding', self._accept_encoding) \
            ._add_default_header('Accept-Language', self._accept_language) \
            ._add_default_header('Referer', referer) \
            ._add_default_header('Cache-Control', self._cache_control) \
            ._add_default_header('Upgrade-Insecure-Requests', '1') \
            ._add_default_header('Pragma', 'no-cache')

        if method not in ('GET', 'HEAD'):
            self._add_default_header('Origin', origin)

        return self.__headers
