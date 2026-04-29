# -*- coding: utf-8 -*-

import unittest
from types import SimpleNamespace

from src.lib.browser.header_bypass import HeaderBypassProbe


class TestHeaderBypassProbe(unittest.TestCase):
    """Header injection bypass probe tests."""

    @staticmethod
    def make_config(**kwargs):
        """
        Build lightweight probe config.

        :param dict kwargs: config overrides
        :return: types.SimpleNamespace
        """

        values = {
            'is_header_bypass': True,
            'header_bypass_headers': list(HeaderBypassProbe.DEFAULT_HEADERS),
            'header_bypass_ips': list(HeaderBypassProbe.DEFAULT_IP_VALUES),
            'header_bypass_status': list(HeaderBypassProbe.DEFAULT_STATUS_CODES),
            'header_bypass_limit': 32,
        }
        values.update(kwargs)

        return SimpleNamespace(**values)

    def test_should_probe_only_when_enabled_and_status_matches(self):
        """Probe should run only for configured blocked status codes."""

        enabled_cfg = self.make_config(header_bypass_status=[401, 403])
        disabled_cfg = self.make_config(is_header_bypass=False)
        enabled_probe = HeaderBypassProbe(enabled_cfg)
        disabled_probe = HeaderBypassProbe(disabled_cfg)

        self.assertTrue(enabled_probe.should_probe(('forbidden', 'https://example.com/admin', '10B', '403')))
        self.assertTrue(enabled_probe.should_probe(('auth', 'https://example.com/admin', '10B', '401')))
        self.assertFalse(enabled_probe.should_probe(('ok', 'https://example.com/admin', '90B', '200')))
        self.assertFalse(disabled_probe.should_probe(('forbidden', 'https://example.com/admin', '10B', '403')))

    def test_known_headers_include_user_requested_candidates(self):
        """Known headers should include the stabilized user-provided candidate list."""

        expected_headers = (
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
            'X-Referrer',
            'X-Remote-Addr',
            'X-Remote-IP',
            'X-Rewrite-URL',
            'X-WAP-Profile',
            'X-Real-Ip',
            'X-True-IP',
        )

        for header in expected_headers:
            self.assertIn(header, HeaderBypassProbe.KNOWN_HEADERS)

    def test_probe_builds_deterministic_limited_variants(self):
        """Probe should build deterministic variants and respect the configured limit."""

        cfg = self.make_config(
            header_bypass_headers=['X-Original-URL', 'X-Forwarded-For', 'Forwarded'],
            header_bypass_ips=['127.0.0.1', '10.0.0.1'],
            header_bypass_limit=4,
        )
        probe = HeaderBypassProbe(cfg)

        variants = probe.build_variants('https://example.com/admin?tab=1')

        self.assertEqual(variants, [
            {'header': 'X-Original-URL', 'value': '/admin?tab=1'},
            {'header': 'X-Original-URL', 'value': '/'},
            {'header': 'X-Forwarded-For', 'value': '127.0.0.1'},
            {'header': 'X-Forwarded-For', 'value': '10.0.0.1'},
        ])

    def test_probe_supports_host_origin_referer_and_url_variants(self):
        """Probe should generate context-aware values for host, origin, referer and URL headers."""

        cfg = self.make_config(
            header_bypass_headers=['X-Forwarded-Host', 'Origin', 'Referer', 'Proxy-Url'],
            header_bypass_ips=['127.0.0.1'],
            header_bypass_limit=0,
        )
        probe = HeaderBypassProbe(cfg)

        variants = probe.build_variants('https://example.com/admin?tab=1')

        self.assertIn({'header': 'X-Forwarded-Host', 'value': 'example.com'}, variants)
        self.assertIn({'header': 'X-Forwarded-Host', 'value': 'localhost'}, variants)
        self.assertIn({'header': 'Origin', 'value': 'https://example.com'}, variants)
        self.assertIn({'header': 'Referer', 'value': 'https://example.com/admin?tab=1'}, variants)
        self.assertIn({'header': 'Referer', 'value': 'https://example.com'}, variants)
        self.assertIn({'header': 'Proxy-Url', 'value': 'https://example.com/admin?tab=1'}, variants)
        self.assertIn({'header': 'Proxy-Url', 'value': 'https://example.com'}, variants)

    def test_probe_deduplicates_case_insensitive_header_values(self):
        """Probe should avoid duplicated header/value pairs."""

        cfg = self.make_config(
            header_bypass_headers=['X-Real-IP', 'X-Real-IP'],
            header_bypass_ips=['127.0.0.1', '127.0.0.1'],
            header_bypass_limit=0,
        )
        probe = HeaderBypassProbe(cfg)

        self.assertEqual(probe.build_variants('https://example.com/admin'), [
            {'header': 'X-Real-IP', 'value': '127.0.0.1'},
        ])

    def test_probe_reports_only_promising_transitions(self):
        """Only meaningful status transitions should be treated as bypass candidates."""

        self.assertTrue(HeaderBypassProbe.is_promising(
            ('forbidden', 'https://example.com/admin', '10B', '403'),
            ('success', 'https://example.com/admin', '100B', '200')
        ))
        self.assertTrue(HeaderBypassProbe.is_promising(
            ('auth', 'https://example.com/admin', '10B', '401'),
            ('redirect', 'https://example.com/admin', '0B', '302')
        ))
        self.assertTrue(HeaderBypassProbe.is_promising(
            ('forbidden', 'https://example.com/admin', '10B', '403'),
            ('not_found', 'https://example.com/admin', '40B', '404')
        ))
        self.assertFalse(HeaderBypassProbe.is_promising(
            ('forbidden', 'https://example.com/admin', '10B', '403'),
            ('forbidden', 'https://example.com/admin', '11B', '403')
        ))
        self.assertFalse(HeaderBypassProbe.is_promising(
            ('forbidden', 'https://example.com/admin', '10B', '403'),
            None
        ))

    def test_probe_metadata_contains_report_fields(self):
        """Metadata should contain stable report fields."""

        metadata = HeaderBypassProbe.metadata(
            {'header': 'X-Original-URL', 'value': '/admin'},
            ('forbidden', 'https://example.com/admin', '10B', '403'),
            ('success', 'https://example.com/admin', '100B', '200')
        )

        self.assertEqual(metadata, {
            'bypass': 'header',
            'bypass_header': 'X-Original-URL',
            'bypass_value': '/admin',
            'bypass_from_code': 403,
            'bypass_to_code': 200,
        })

    def test_probe_uses_path_value_for_unknown_custom_header(self):
        """Unknown custom headers should safely fallback to the request path value."""

        cfg = self.make_config(
            header_bypass_headers=['X-Unknown-Bypass-Header'],
            header_bypass_ips=['127.0.0.1'],
            header_bypass_limit=0,
        )
        probe = HeaderBypassProbe(cfg)

        self.assertEqual(probe.build_variants('https://example.com/private/admin?debug=1'), [
            {'header': 'X-Unknown-Bypass-Header', 'value': '/private/admin?debug=1'},
        ])

    def test_probe_rejects_non_blocked_base_non_success_transition(self):
        """Non-success transitions from non-blocked base statuses should not be reported."""

        self.assertFalse(HeaderBypassProbe.is_promising(
            ('server_error', 'https://example.com/admin', '10B', '500'),
            ('not_found', 'https://example.com/admin', '40B', '404')
        ))

    def test_response_code_handles_malformed_response_data(self):
        """Response code resolver should tolerate malformed response tuples."""

        self.assertIsNone(HeaderBypassProbe.response_code(None))
        self.assertIsNone(HeaderBypassProbe.response_code(()))
        self.assertIsNone(HeaderBypassProbe.response_code(('body', 'url', 'size', 'abc')))


if __name__ == '__main__':
    unittest.main()