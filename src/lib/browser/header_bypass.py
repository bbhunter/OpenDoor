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

    Development Team: Brain Storm Team
"""

from urllib.parse import urlparse


class HeaderBypassProbe(object):
    """Build and score controlled header-injection bypass probes."""

    KNOWN_HEADERS = (
        'CF-Connecting-IP',
        'CF-Connecting_IP',
        'Client-IP',
        'Forwarded',
        'Host',
        'Origin',
        'Proxy',
        'Proxy-Host',
        'Proxy-Url',
        'Real-Ip',
        'Referer',
        'Referrer',
        'Request-Uri',
        'True-Client-IP',
        'X-Client-IP',
        'X-Custom-IP-Authorization',
        'X-Forwarded',
        'X-Forwarded-For',
        'X-Forwarded-Host',
        'X-Forwarded-Proto',
        'X-Forwarded-Server',
        'X-Host',
        'X-HTTP-DestinationURL',
        'X-HTTP-Host-Override',
        'X-Original-Remote-Addr',
        'X-Original-URL',
        'X-Originating-IP',
        'X-Proxy-Url',
        'X-Real-IP',
        'X-Real-Ip',
        'X-Referrer',
        'X-Remote-Addr',
        'X-Remote-IP',
        'X-Rewrite-URL',
        'X-True-IP',
        'X-WAP-Profile',
    )

    DEFAULT_HEADERS = (
        'X-Original-URL',
        'X-Rewrite-URL',
        'Request-Uri',
        'X-Custom-IP-Authorization',
        'X-Forwarded-For',
        'X-Forwarded-Host',
        'X-Forwarded-Proto',
        'X-Host',
        'X-HTTP-Host-Override',
        'X-Originating-IP',
        'X-Real-IP',
        'X-Remote-Addr',
        'X-Remote-IP',
        'X-Client-IP',
        'X-True-IP',
        'True-Client-IP',
        'Client-IP',
        'CF-Connecting-IP',
        'Real-Ip',
        'Forwarded',
        'Referer',
        'Referrer',
        'Origin',
    )

    PATH_HEADERS = (
        'X-Original-URL',
        'X-Rewrite-URL',
        'X-HTTP-DestinationURL',
        'Request-Uri',
    )

    HOST_HEADERS = (
        'Host',
        'X-Forwarded-Host',
        'X-Forwarded-Server',
        'X-Host',
        'X-HTTP-Host-Override',
        'Forwarded',
        'Origin',
        'Referer',
        'Referrer',
        'X-Referrer',
    )

    TRUSTED_IP_HEADERS = (
        'CF-Connecting-IP',
        'CF-Connecting_IP',
        'Client-IP',
        'Real-Ip',
        'True-Client-IP',
        'X-Client-IP',
        'X-Custom-IP-Authorization',
        'X-Forwarded',
        'X-Forwarded-For',
        'X-Original-Remote-Addr',
        'X-Originating-IP',
        'X-Real-IP',
        'X-Real-Ip',
        'X-Remote-Addr',
        'X-Remote-IP',
        'X-True-IP',
    )

    URL_HEADERS = (
        'Proxy',
        'Proxy-Host',
        'Proxy-Url',
        'X-Proxy-Url',
        'X-HTTP-DestinationURL',
        'X-WAP-Profile',
    )

    DEFAULT_IP_VALUES = (
        '127.0.0.1',
        'localhost',
        '10.0.0.1',
        '192.168.1.1',
    )

    DEFAULT_STATUS_CODES = (401, 403)

    def __init__(self, config):
        """
        HeaderBypassProbe constructor.

        :param object config: browser configuration
        """

        self.__config = config

    @staticmethod
    def response_code(response_data):
        """
        Resolve HTTP status code from handled response data.

        :param tuple response_data: handled response data
        :return: int | None
        """

        try:
            return int(response_data[3])
        except (IndexError, TypeError, ValueError):
            return None

    def should_probe(self, response_data):
        """
        Decide whether header bypass probes should run for the response.

        :param tuple response_data: handled response data
        :return: bool
        """

        if True is not getattr(self.__config, 'is_header_bypass', False):
            return False

        return self.response_code(response_data) in self.__config.header_bypass_status

    def build_variants(self, url):
        """
        Build deterministic header variants for one blocked URL.

        :param str url: blocked target URL
        :return: list[dict]
        """

        variants = []
        seen = set()
        parsed = urlparse(url)
        path = parsed.path or '/'

        if parsed.query:
            path += '?' + parsed.query

        origin = '{0}://{1}'.format(parsed.scheme, parsed.netloc)
        full_url = parsed.geturl()
        headers = self.__config.header_bypass_headers
        ip_values = self.__config.header_bypass_ips

        def add(name, value):
            """
            Add unique header variant.

            :param str name: header name
            :param str value: header value
            :return: None
            """

            key = (str(name).lower(), str(value))
            if key in seen:
                return

            seen.add(key)
            variants.append({'header': str(name), 'value': str(value)})

        for header in headers:
            if header in self.PATH_HEADERS:
                add(header, path)
                add(header, '/')
                continue

            if header == 'Forwarded':
                for ip in ip_values:
                    add(header, 'for={0};host={1};proto={2}'.format(ip, parsed.netloc, parsed.scheme))
                continue

            if header in self.TRUSTED_IP_HEADERS:
                for ip in ip_values:
                    add(header, ip)
                continue

            if header in ('Origin',):
                add(header, origin)
                continue

            if header in ('Referer', 'Referrer', 'X-Referrer'):
                add(header, full_url)
                add(header, origin)
                continue

            if header in self.HOST_HEADERS:
                add(header, parsed.netloc)
                add(header, 'localhost')
                continue

            if header in self.URL_HEADERS:
                add(header, full_url)
                add(header, origin)
                continue

            add(header, path)

        limit = self.__config.header_bypass_limit
        if limit > 0:
            return variants[:limit]

        return variants

    @staticmethod
    def is_promising(base_response_data, probe_response_data):
        """
        Check if a probe response is worth reporting.

        :param tuple base_response_data: original blocked response data
        :param tuple probe_response_data: probe response data
        :return: bool
        """

        base_code = HeaderBypassProbe.response_code(base_response_data)
        probe_code = HeaderBypassProbe.response_code(probe_response_data)

        if probe_code is None or probe_code == base_code:
            return False

        if 200 <= probe_code <= 399:
            return True

        if base_code in HeaderBypassProbe.DEFAULT_STATUS_CODES and probe_code not in HeaderBypassProbe.DEFAULT_STATUS_CODES:
            return True

        return False

    @staticmethod
    def metadata(variant, base_response_data, probe_response_data):
        """
        Build report metadata for a bypass probe.

        :param dict variant: header variant
        :param tuple base_response_data: original response data
        :param tuple probe_response_data: probe response data
        :return: dict
        """

        return {
            'bypass': 'header',
            'bypass_header': variant.get('header'),
            'bypass_value': variant.get('value'),
            'bypass_from_code': HeaderBypassProbe.response_code(base_response_data),
            'bypass_to_code': HeaderBypassProbe.response_code(probe_response_data),
        }