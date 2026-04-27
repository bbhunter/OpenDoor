# -*- coding: utf-8 -*-

import unittest
from types import SimpleNamespace

from urllib3._collections import HTTPHeaderDict

from src.core.http.providers.cookies import CookiesProvider
from src.core.http.providers.header import HeaderProvider
from src.core.http.providers.request import RequestProvider


class TestBrowserLikeRequestHeaders(unittest.TestCase):
    """Browser-like HTTP provider regression tests."""

    def test_default_headers_do_not_overwrite_custom_values(self):
        """Explicit CLI/raw headers should win over generated default headers."""

        cfg = SimpleNamespace(scheme='https://', host='example.com', port=443, method='POST')
        provider = HeaderProvider(cfg)
        provider.add_header('Accept', 'application/json')
        provider.add_header('Accept-Encoding', 'identity')
        provider.add_header('Accept-Language', 'uk-UA')
        provider.add_header('Origin', 'https://origin.example')
        provider.add_header('Referer', 'https://referer.example/page')
        provider.add_header('Cache-Control', 'no-store')
        provider.add_header('Pragma', 'no-cache')
        provider.add_header('Upgrade-Insecure-Requests', '0')

        headers = provider._headers

        self.assertEqual(headers['Accept'], 'application/json')
        self.assertEqual(headers['Accept-Encoding'], 'identity')
        self.assertEqual(headers['Accept-Language'], 'uk-UA')
        self.assertEqual(headers['Origin'], 'https://origin.example')
        self.assertEqual(headers['Referer'], 'https://referer.example/page')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['Pragma'], 'no-cache')
        self.assertEqual(headers['Upgrade-Insecure-Requests'], '0')

    def test_origin_and_referer_are_browser_like(self):
        """Origin should be skipped for GET/HEAD and ports should be normalized."""

        get_cfg = SimpleNamespace(scheme='https://', host='example.com', port=443, method='GET')
        get_headers = HeaderProvider(get_cfg)._headers

        self.assertNotIn('Origin', get_headers)
        self.assertEqual(get_headers['Referer'], 'https://example.com/')

        post_cfg = SimpleNamespace(scheme='https://', host='example.com', port=8443, method='POST')
        post_headers = HeaderProvider(post_cfg)._headers

        self.assertEqual(post_headers['Origin'], 'https://example.com:8443')
        self.assertEqual(post_headers['Referer'], 'https://example.com:8443/')

    def test_set_cookie_is_routed_as_cookie_pairs_only(self):
        """Set-Cookie metadata should not leak into the next Cookie header."""

        provider = CookiesProvider()
        headers = HTTPHeaderDict()
        headers.add('Set-Cookie', 'sid=abc; Path=/; HttpOnly; SameSite=Lax')
        headers.add('Set-Cookie', 'theme=dark; Expires=Wed, 21 Oct 2030 07:28:00 GMT; Path=/')

        provider._fetch_cookies(headers)

        self.assertEqual(provider._push_cookies(), 'sid=abc; theme=dark')

    def test_cookie_middleware_uses_sanitized_cookie_header(self):
        """RequestProvider should propagate only sanitized Cookie pairs."""

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
        response = SimpleNamespace(headers={'set-cookie': ' token=value; Path=/; HttpOnly '})

        provider.cookies_middleware(True, response)

        self.assertEqual(provider._headers['Cookie'], 'token=value')


if __name__ == '__main__':
    unittest.main()
