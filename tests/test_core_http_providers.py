# -*- coding: utf-8 -*-

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.core.http.providers.accept import AcceptHeaderProvider
from src.core.http.providers.cache import CacheControlProvider
from src.core.http.providers.connection import ConnectionHeaderProvider
from src.core.http.providers.cookies import CookiesProvider
from src.core.http.providers.header import HeaderProvider
from src.core.http.providers.user_agent import UserAgentHeaderProvider
from src.core.http.providers.request import RequestProvider
from src.core.http.providers.debug import DebugProvider
from src.core.http.exceptions import SocketError, ProxyRequestError, HttpRequestError, HttpsRequestError, ResponseError


class TestHttpProviders(unittest.TestCase):
    """TestHttpProviders class."""

    def test_accept_cache_and_connection_headers(self):
        """Header providers should expose stable browser-like defaults."""

        accept = AcceptHeaderProvider()
        with patch('src.core.http.providers.accept.random.randrange', return_value=0):
            self.assertEqual(
                accept._accept,
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
            )
            self.assertEqual(accept._accept_encoding, 'gzip, deflate')
            self.assertEqual(accept._accept_language, 'en-US,en;q=0.9')

        self.assertEqual(CacheControlProvider()._cache_control, 'max-age=0')
        self.assertEqual(ConnectionHeaderProvider(SimpleNamespace())._keep_alive, 'keep-alive')

    def test_cookies_provider_flow(self):
        """CookiesProvider should fetch and push request-safe cookie pairs."""

        provider = CookiesProvider()
        self.assertFalse(provider._is_cookie_fetched)

        provider._fetch_cookies({'set-cookie': ' token=value; Path=/; HttpOnly; SameSite=Lax '})
        self.assertTrue(provider._is_cookie_fetched)
        self.assertEqual(provider._push_cookies(), 'token=value')

    def test_cookies_provider_should_collect_multiple_set_cookie_values(self):
        """CookiesProvider should join multiple Set-Cookie headers as Cookie header pairs."""

        class Headers(object):
            def getlist(self, name):
                if name == 'set-cookie':
                    return [
                        'sid=abc; Path=/; HttpOnly',
                        'locale=en; Path=/; SameSite=Lax',
                    ]
                return []

        provider = CookiesProvider()
        provider._fetch_cookies(Headers())

        self.assertEqual(provider._push_cookies(), 'sid=abc; locale=en')

    def test_header_provider_builds_default_headers(self):
        """HeaderProvider should build a default browser-like header set."""

        cfg = SimpleNamespace(scheme='http://', host='example.com', port=80, method='GET')
        provider = HeaderProvider(cfg)

        provider.add_header('X-Test', ' value ')
        headers = provider._headers

        self.assertEqual(headers['X-Test'], 'value')
        self.assertNotIn('Origin', headers)
        self.assertEqual(headers['Referer'], 'http://example.com/')
        self.assertEqual(headers['Cache-Control'], 'max-age=0')
        self.assertEqual(headers['Accept-Encoding'], 'gzip, deflate')

    def test_header_provider_should_set_origin_for_body_methods(self):
        """HeaderProvider should add Origin for body-like methods and keep non-default ports."""

        cfg = SimpleNamespace(scheme='https://', host='example.com', port=8443, method='POST')
        provider = HeaderProvider(cfg)
        headers = provider._headers

        self.assertEqual(headers['Origin'], 'https://example.com:8443')
        self.assertEqual(headers['Referer'], 'https://example.com:8443/')

    def test_header_provider_should_not_override_custom_headers(self):
        """HeaderProvider defaults should not overwrite custom/raw headers."""

        cfg = SimpleNamespace(scheme='https://', host='example.com', port=443, method='POST')
        provider = HeaderProvider(cfg)
        provider.add_header('Accept', 'application/json')
        provider.add_header('Accept-Encoding', 'identity')
        provider.add_header('Accept-Language', 'uk-UA')
        provider.add_header('Origin', 'https://custom-origin.test')
        provider.add_header('Referer', 'https://custom-referer.test/path')
        provider.add_header('Cache-Control', 'no-store')
        provider.add_header('Pragma', 'no-cache-custom')
        provider.add_header('Upgrade-Insecure-Requests', '0')

        headers = provider._headers

        self.assertEqual(headers['Accept'], 'application/json')
        self.assertEqual(headers['Accept-Encoding'], 'identity')
        self.assertEqual(headers['Accept-Language'], 'uk-UA')
        self.assertEqual(headers['Origin'], 'https://custom-origin.test')
        self.assertEqual(headers['Referer'], 'https://custom-referer.test/path')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['Pragma'], 'no-cache-custom')
        self.assertEqual(headers['Upgrade-Insecure-Requests'], '0')

    def test_user_agent_provider_uses_random_or_default(self):
        """UserAgentHeaderProvider should return either the configured UA or a random one."""

        cfg = SimpleNamespace(is_random_user_agent=False, user_agent='UA')
        provider = UserAgentHeaderProvider(cfg, ['A', 'B'])
        self.assertEqual(provider._user_agent, 'UA')

        random_cfg = SimpleNamespace(is_random_user_agent=True, user_agent='UA')
        provider = UserAgentHeaderProvider(random_cfg, ['A\n', 'B\n'])
        with patch('src.core.http.providers.user_agent.random.randrange', return_value=1):
            self.assertEqual(provider._user_agent, 'B')

    def test_request_provider_cookies_middleware(self):
        """RequestProvider.cookies_middleware() should propagate cookies only when enabled."""

        cfg = SimpleNamespace(
            scheme='http://',
            host='example.com',
            port=80,
            method='GET',
            is_random_user_agent=False,
            user_agent='UA',
        )
        provider = RequestProvider(cfg, ['UA'])
        response = SimpleNamespace(headers={'set-cookie': ' token=value; Path=/; HttpOnly '})

        provider.cookies_middleware(True, response)
        self.assertEqual(provider._headers['Cookie'], 'token=value')

        provider = RequestProvider(cfg, ['UA'])
        provider.cookies_middleware(False, response)
        self.assertNotIn('Cookie', provider._headers)

    def test_debug_provider_base_contract(self):
        """DebugProvider base methods should remain no-op."""

        provider = DebugProvider()
        self.assertIsNone(provider.level)
        self.assertIsNone(provider.debug_user_agents())
        self.assertIsNone(provider.debug_connection_pool('k', object(), 'http'))
        self.assertIsNone(provider.debug_proxy_pool())
        self.assertIsNone(provider.debug_list(1))
        self.assertIsNone(provider.debug_request({}, 'http://example.com', 'HEAD'))
        self.assertIsNone(provider.debug_response({}))
        self.assertIsNone(provider.debug_request_uri('success', 'http://example.com'))
        self.assertIsNone(provider.debug_load_sniffer_plugin('desc'))

    def test_http_exceptions_preserve_message(self):
        """HTTP exception classes should preserve the provided message."""

        for exc in [SocketError('a'), ProxyRequestError('b'), HttpRequestError('c'), HttpsRequestError('d'), ResponseError('e')]:
            self.assertTrue(str(exc))

    def test_request_provider_should_apply_header_fallback_and_skip_invalid_entries(self):
        """RequestProvider should use config.header fallback and ignore malformed custom header values."""

        cfg = SimpleNamespace(
            scheme='http://',
            host='example.com',
            port=80,
            method='GET',
            is_random_user_agent=False,
            user_agent='UA',
            headers=None,
            header=['Broken', 'X-Test: 1', ': empty', 'X-Ok: yes'],
            cookies=None,
            cookie=None,
            request_body=None,
        )

        provider = RequestProvider(cfg, ['UA'])
        headers = provider._headers

        self.assertEqual(headers['X-Test'], '1')
        self.assertEqual(headers['X-Ok'], 'yes')
        self.assertNotIn('Broken', headers)

    def test_request_provider_should_apply_cookie_fallback_and_skip_empty_values(self):
        """RequestProvider should use config.cookie fallback and skip blank cookie values."""

        cfg = SimpleNamespace(
            scheme='http://',
            host='example.com',
            port=80,
            method='GET',
            is_random_user_agent=False,
            user_agent='UA',
            headers=None,
            header=None,
            cookies=None,
            cookie=[' sid=abc ', '   ', 'locale=en'],
            request_body=None,
        )

        provider = RequestProvider(cfg, ['UA'])

        self.assertEqual(provider._headers['Cookie'], 'sid=abc; locale=en')

    def test_request_provider_should_not_override_custom_browser_headers(self):
        """RequestProvider should keep custom/raw browser headers over defaults."""

        cfg = SimpleNamespace(
            scheme='https://',
            host='example.com',
            port=443,
            method='GET',
            is_random_user_agent=False,
            user_agent='UA',
            headers=[
                'Accept: application/json',
                'Accept-Language: uk-UA',
                'Referer: https://previous.example/path',
            ],
            header=None,
            cookies=None,
            cookie=None,
            request_body=None,
        )

        provider = RequestProvider(cfg, ['UA'])
        headers = provider._headers

        self.assertEqual(headers['Accept'], 'application/json')
        self.assertEqual(headers['Accept-Language'], 'uk-UA')
        self.assertEqual(headers['Referer'], 'https://previous.example/path')
        self.assertNotIn('Origin', headers)

    def test_request_provider_cookie_middleware_should_skip_non_accepted_or_headerless_responses(self):
        """RequestProvider.cookies_middleware() should not fetch cookies when preconditions are not met."""

        cfg = SimpleNamespace(
            scheme='http://',
            host='example.com',
            port=80,
            method='GET',
            is_random_user_agent=False,
            user_agent='UA',
            headers=None,
            header=None,
            cookies=None,
            cookie=None,
            request_body=None,
        )
        provider = RequestProvider(cfg, ['UA'])

        with patch.object(provider, '_fetch_cookies') as fetch_mock:
            provider.cookies_middleware(False, SimpleNamespace(headers={'set-cookie': 'a=b'}))
            fetch_mock.assert_not_called()

        with patch.object(provider, '_fetch_cookies') as fetch_mock:
            provider.cookies_middleware(True, SimpleNamespace())
            fetch_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
