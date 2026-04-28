# -*- coding: utf-8 -*-

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.lib.browser.calibration import Calibration


class TestCalibration(unittest.TestCase):
    """TestCalibration class."""

    def make_response(self, status=404, body='', headers=None):
        """Create a response-like object."""

        return SimpleNamespace(
            status=status,
            data=body.encode('utf-8'),
            headers=headers or {'Content-Type': 'text/html', 'Server': 'nginx'}
        )

    def test_calibration_should_build_signature_from_response(self):
        """Calibration.build_signature() should build a stable response signature."""

        response = self.make_response(
            body='<html><head><title>Not Found</title></head><body>Missing 123456</body></html>',
            headers={'Content-Type': 'text/html', 'Server': 'nginx'}
        )

        actual = Calibration.build_signature(
            response,
            ('success', 'http://example.com/missing', '75B', '404')
        )

        self.assertEqual(actual['bucket'], 'success')
        self.assertEqual(actual['code'], 404)
        self.assertEqual(actual['title'], 'not found')
        self.assertEqual(actual['header_fingerprint']['server'], 'nginx')
        self.assertIn('normalized_body_hash', actual)
        self.assertIn('body_skeleton_hash', actual)

    def test_calibration_should_match_dynamic_soft_404_response(self):
        """Calibration.match() should match dynamic soft-404 pages after normalization."""

        baseline_response = self.make_response(
            status=200,
            body='<html><head><title>Not Found</title></head><body>Missing id 123456</body></html>'
        )
        candidate_response = self.make_response(
            status=200,
            body='<html><head><title>Not Found</title></head><body>Missing id 987654</body></html>'
        )

        baseline = Calibration(
            signatures=[
                Calibration.build_signature(
                    baseline_response,
                    ('success', 'http://example.com/random-a', '75B', '200')
                )
            ],
            threshold=0.92
        )

        actual = baseline.match(
            candidate_response,
            ('success', 'http://example.com/admin', '75B', '200')
        )

        self.assertIsNotNone(actual)
        self.assertGreaterEqual(actual['calibration_score'], 0.92)

    def test_calibration_should_not_match_real_page_with_different_structure(self):
        """Calibration.match() should not match useful pages with different structure."""

        baseline_response = self.make_response(
            status=200,
            body='<html><head><title>Not Found</title></head><body>Missing id 123456</body></html>'
        )
        candidate_response = self.make_response(
            status=200,
            body='<html><head><title>Admin</title></head><body><form><input name="login"></form></body></html>'
        )

        baseline = Calibration(
            signatures=[
                Calibration.build_signature(
                    baseline_response,
                    ('success', 'http://example.com/random-a', '75B', '200')
                )
            ],
            threshold=0.92
        )

        actual = baseline.match(
            candidate_response,
            ('success', 'http://example.com/admin', '90B', '200')
        )

        self.assertIsNone(actual)

    def test_calibration_should_match_redirect_wildcard(self):
        """Calibration.match() should match wildcard redirects by location."""

        baseline_response = self.make_response(
            status=302,
            body='',
            headers={'Location': '/not-found', 'Server': 'nginx'}
        )
        candidate_response = self.make_response(
            status=302,
            body='',
            headers={'Location': '/not-found', 'Server': 'nginx'}
        )

        baseline = Calibration(
            signatures=[
                Calibration.build_signature(
                    baseline_response,
                    ('redirect', 'http://example.com/random-a', '0B', '302')
                )
            ],
            threshold=0.92
        )

        actual = baseline.match(
            candidate_response,
            ('redirect', 'http://example.com/admin', '0B', '302')
        )

        self.assertIsNotNone(actual)

    def test_calibration_should_export_and_restore_state(self):
        """Calibration should export and restore baseline state."""

        baseline = Calibration(signatures=[{'code': 404}], threshold=0.95)

        restored = Calibration.from_dict(baseline.to_dict())

        self.assertIsNotNone(restored)
        self.assertEqual(restored.threshold, 0.95)
        self.assertEqual(restored.signatures, [{'code': 404}])

    def test_calibration_should_return_none_when_baseline_is_empty(self):
        """Calibration.match() should return None when baseline has no signatures."""

        calibration = Calibration(signatures=[], threshold=0.92)

        actual = calibration.match(
            self.make_response(status=404, body='not found'),
            ('success', 'http://example.com/admin', '9B', '404')
        )

        self.assertIsNone(actual)
        self.assertFalse(calibration.is_enabled)

    def test_calibration_should_not_match_different_status_code(self):
        """Calibration.match() should not match responses with different status codes."""

        baseline_response = self.make_response(status=404, body='not found')
        candidate_response = self.make_response(status=200, body='not found')

        calibration = Calibration(
            signatures=[
                Calibration.build_signature(
                    baseline_response,
                    ('success', 'http://example.com/random', '9B', '404')
                )
            ],
            threshold=0.92
        )

        actual = calibration.match(
            candidate_response,
            ('success', 'http://example.com/admin', '9B', '200')
        )

        self.assertIsNone(actual)

    def test_calibration_should_match_empty_soft_404_exact_shape(self):
        """Calibration.match() should match empty/minimal soft-404 responses by exact shape."""

        baseline_response = self.make_response(
            status=404,
            body='',
            headers={'Content-Type': 'text/html', 'Server': 'nginx'}
        )
        candidate_response = self.make_response(
            status=404,
            body='',
            headers={'Content-Type': 'text/html', 'Server': 'nginx'}
        )

        calibration = Calibration(
            signatures=[
                Calibration.build_signature(
                    baseline_response,
                    ('success', 'http://example.com/random', '0B', '404')
                )
            ],
            threshold=0.92
        )

        actual = calibration.match(
            candidate_response,
            ('success', 'http://example.com/admin', '0B', '404')
        )

        self.assertIsNotNone(actual)
        self.assertIn('exact-shape', actual['calibration_reason'])

    def test_calibration_should_restore_none_from_invalid_payload(self):
        """Calibration.from_dict() should reject invalid serialized payloads."""

        self.assertIsNone(Calibration.from_dict(None))
        self.assertIsNone(Calibration.from_dict([]))
        self.assertIsNone(Calibration.from_dict({'signatures': 'bad'}))

    def test_calibration_helpers_should_handle_missing_or_invalid_response_fields(self):
        """Calibration helpers should gracefully handle missing body, headers and invalid status."""

        response = SimpleNamespace(status='bad')

        signature = Calibration.build_signature(
            response,
            ('success', 'http://example.com/missing', '0B', '-')
        )

        self.assertIsNone(signature['code'])
        self.assertEqual(signature['size'], 0)
        self.assertEqual(signature['word_count'], 0)
        self.assertEqual(signature['line_count'], 0)
        self.assertEqual(signature['title'], '')
        self.assertEqual(signature['redirect_location'], '')
        self.assertEqual(signature['header_fingerprint'], {})

    def test_calibration_should_read_headers_case_insensitively(self):
        """Calibration should read stable headers and redirect location case-insensitively."""

        response = self.make_response(
            status=302,
            body='',
            headers={
                'LOCATION': '/Not-Found',
                'SERVER': 'Nginx',
                'CONTENT-TYPE': 'text/html',
                'X-Powered-By': 'Python',
            }
        )

        signature = Calibration.build_signature(
            response,
            ('redirect', 'http://example.com/random', '0B', '302')
        )

        self.assertEqual(signature['redirect_location'], '/not-found')
        self.assertEqual(signature['header_fingerprint']['server'], 'nginx')
        self.assertEqual(signature['header_fingerprint']['content-type'], 'text/html')
        self.assertEqual(signature['header_fingerprint']['x-powered-by'], 'python')

    def test_calibration_similarity_helpers_should_cover_edge_cases(self):
        """Calibration similarity helpers should cover invalid numeric values and empty headers."""

        self.assertEqual(Calibration._numeric_similarity('bad', 1), 0.0)
        self.assertEqual(Calibration._numeric_similarity(10, 10), 1.0)
        self.assertEqual(Calibration._header_similarity({}, {}), 1.0)
        self.assertEqual(
            Calibration._header_similarity({'server': 'nginx'}, {'server': 'apache'}),
            0.0
        )

    def test_calibration_should_not_add_title_score_when_title_differs(self):
        """Calibration._score() should not add title reason when titles differ."""

        baseline = {
            'code': 200,
            'bucket': 'success',
            'normalized_body_hash': 'body-a',
            'body_skeleton_hash': 'skeleton-a',
            'title': 'not found',
            'redirect_location': '',
            'size': 100,
            'word_count': 10,
            'line_count': 2,
            'header_fingerprint': {'server': 'nginx'},
        }
        candidate = dict(baseline)
        candidate['title'] = 'admin'

        score, reasons = Calibration._score(baseline, candidate)

        self.assertGreater(score, 0)
        self.assertNotIn('title', reasons)

    def test_calibration_should_not_add_redirect_score_when_redirect_differs(self):
        """Calibration._score() should not add redirect reason when redirect locations differ."""

        baseline = {
            'code': 302,
            'bucket': 'redirect',
            'normalized_body_hash': 'body-a',
            'body_skeleton_hash': 'skeleton-a',
            'title': '',
            'redirect_location': '/not-found',
            'size': 0,
            'word_count': 0,
            'line_count': 0,
            'header_fingerprint': {'server': 'nginx'},
        }
        candidate = dict(baseline)
        candidate['redirect_location'] = '/login'

        score, reasons = Calibration._score(baseline, candidate)

        self.assertGreater(score, 0)
        self.assertNotIn('redirect', reasons)

    def test_calibration_should_not_add_numeric_reasons_when_similarity_is_low(self):
        """Calibration._score() should skip size, word and line reasons for low numeric similarity."""

        baseline = {
            'code': 200,
            'bucket': 'success',
            'normalized_body_hash': 'body-a',
            'body_skeleton_hash': 'skeleton-a',
            'title': '',
            'redirect_location': '',
            'size': 100,
            'word_count': 100,
            'line_count': 100,
            'header_fingerprint': {'server': 'nginx'},
        }
        candidate = dict(baseline)
        candidate['size'] = 1
        candidate['word_count'] = 1
        candidate['line_count'] = 1

        score, reasons = Calibration._score(baseline, candidate)

        self.assertGreater(score, 0)
        self.assertNotIn('size', reasons)
        self.assertNotIn('words', reasons)
        self.assertNotIn('lines', reasons)

    def test_calibration_should_not_add_header_reason_when_header_similarity_is_low(self):
        """Calibration._score() should skip headers reason when stable headers differ."""

        baseline = {
            'code': 200,
            'bucket': 'success',
            'normalized_body_hash': 'body-a',
            'body_skeleton_hash': 'skeleton-a',
            'title': '',
            'redirect_location': '',
            'size': 100,
            'word_count': 10,
            'line_count': 2,
            'header_fingerprint': {'server': 'nginx', 'content-type': 'text/html'},
        }
        candidate = dict(baseline)
        candidate['header_fingerprint'] = {'server': 'apache', 'content-type': 'application/json'}

        score, reasons = Calibration._score(baseline, candidate)

        self.assertGreater(score, 0)
        self.assertNotIn('headers', reasons)

    def test_calibration_body_should_return_empty_string_when_decode_fails(self):
        """Calibration._body() should return an empty string when helper decode fails."""

        response = SimpleNamespace(data=b'\xff')

        with patch('src.lib.browser.calibration.helper.decode', side_effect=UnicodeError('bad encoding')):
            actual = Calibration._body(response)

        self.assertEqual(actual, '')

    def test_calibration_response_size_should_fallback_when_content_length_is_invalid(self):
        """Calibration._response_size() should fallback to body length when Content-Length is invalid."""

        response = SimpleNamespace(
            headers={'Content-Length': 'bad'},
            data=b'abcdef'
        )

        actual = Calibration._response_size(response)

        self.assertEqual(actual, 6)

    def test_calibration_response_size_should_return_zero_without_body(self):
        """Calibration._response_size() should return zero when response has no body."""

        actual = Calibration._response_size(SimpleNamespace(headers={}))

        self.assertEqual(actual, 0)

    def test_calibration_response_code_should_fallback_to_response_data_code(self):
        """Calibration._response_code() should fallback to response_data code when response status is invalid."""

        response = SimpleNamespace(status='bad')

        actual = Calibration._response_code(response, ('success', 'url', '1B', '404'))

        self.assertEqual(actual, 404)

    def test_calibration_response_code_should_return_none_when_all_codes_are_invalid(self):
        """Calibration._response_code() should return None when status and response_data code are invalid."""

        response = SimpleNamespace(status='bad')

        actual = Calibration._response_code(response, ('success', 'url', '1B', '-'))

        self.assertIsNone(actual)

    def test_calibration_header_should_return_none_when_headers_object_has_no_mapping_api(self):
        """Calibration._header() should return None when headers object has no get/items API."""

        response = SimpleNamespace(headers=object())

        actual = Calibration._header(response, 'server')

        self.assertIsNone(actual)

    def test_calibration_header_should_resolve_value_from_items_fallback(self):
        """Calibration._header() should resolve header value from items fallback."""

        class HeadersWithoutGet(object):
            def items(self):
                return [('SERVER', 'nginx')]

        response = SimpleNamespace(headers=HeadersWithoutGet())

        actual = Calibration._header(response, 'server')

        self.assertEqual(actual, 'nginx')

    def test_calibration_header_similarity_should_partially_match_headers(self):
        """Calibration._header_similarity() should return partial score for partially matching headers."""

        actual = Calibration._header_similarity(
            {'server': 'nginx', 'content-type': 'text/html'},
            {'server': 'nginx', 'content-type': 'application/json'}
        )

        self.assertEqual(actual, 0.5)

    def test_calibration_exact_shape_should_return_false_for_different_shape(self):
        """Calibration._is_exact_shape_match() should return False when normalized shape differs."""

        baseline = {
            'normalized_body_hash': 'body-a',
            'body_skeleton_hash': 'skeleton-a',
            'size': 10,
            'word_count': 2,
            'line_count': 1,
        }
        candidate = dict(baseline)
        candidate['size'] = 11

        self.assertFalse(Calibration._is_exact_shape_match(baseline, candidate))

if __name__ == '__main__':
    unittest.main()