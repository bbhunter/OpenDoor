# -*- coding: utf-8 -*-

"""
    Smart auto-calibration for soft-404 / wildcard / catch-all responses.
"""

import hashlib
import html
import re

from src.core import helper


class Calibration(object):

    """Calibration baseline matcher."""

    DEFAULT_THRESHOLD = 0.92
    STABLE_HEADERS = ('content-type', 'server', 'x-powered-by')
    DYNAMIC_PATTERNS = (
        r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
        r'\b[0-9a-f]{24,}\b',
        r'\b\d{4}-\d{2}-\d{2}(?:[t\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?\b',
        r'\b\d{2}:\d{2}:\d{2}\b',
        r'\b\d{5,}\b',
        r'csrf[_-]?token=["\'][^"\']+["\']',
        r'nonce=["\'][^"\']+["\']',
        r'([?&][a-z0-9_-]+)=([^&#\s"\']+)',
    )

    def __init__(self, signatures=None, threshold=None):
        """
        Constructor.

        :param list[dict]|None signatures:
        :param float|None threshold:
        """

        self.signatures = signatures or []
        self.threshold = self.DEFAULT_THRESHOLD if threshold is None else float(threshold)

    @property
    def is_enabled(self):
        """Return True when baseline has at least one usable signature."""

        return len(self.signatures) > 0

    def to_dict(self):
        """
        Export calibration state.

        :return: dict
        """

        return {
            'threshold': self.threshold,
            'signatures': list(self.signatures),
        }

    @classmethod
    def from_dict(cls, payload):
        """
        Restore calibration state.

        :param dict|None payload:
        :return: Calibration|None
        """

        if not isinstance(payload, dict):
            return None

        signatures = payload.get('signatures') or []
        threshold = payload.get('threshold', cls.DEFAULT_THRESHOLD)

        if not isinstance(signatures, list):
            return None

        return cls(signatures=signatures, threshold=threshold)

    @classmethod
    def build_signature(cls, response, response_data):
        """
        Build a response signature.

        :param object response:
        :param tuple response_data:
        :return: dict
        """

        body = cls._body(response)
        normalized_body = cls._normalize_body(body)
        skeleton = cls._body_skeleton(body)

        return {
            'bucket': str(response_data[0]),
            'url': str(response_data[1]),
            'size': cls._response_size(response),
            'code': cls._response_code(response, response_data),
            'word_count': cls._word_count(body),
            'line_count': cls._line_count(body),
            'title': cls._title(body),
            'redirect_location': cls._redirect_location(response),
            'normalized_body_hash': cls._hash(normalized_body),
            'body_skeleton_hash': cls._hash(skeleton),
            'header_fingerprint': cls._header_fingerprint(response),
        }

    def match(self, response, response_data):
        """
        Match a response against calibration baseline.

        :param object response:
        :param tuple response_data:
        :return: dict|None
        """

        if self.is_enabled is not True:
            return None

        candidate = self.build_signature(response, response_data)
        best_score = 0.0
        best_reasons = []

        for baseline in self.signatures:
            score, reasons = self._score(baseline, candidate)
            if score > best_score:
                best_score = score
                best_reasons = reasons

        if best_score >= self.threshold:
            return {
                'calibration_score': round(best_score, 4),
                'calibration_reason': ','.join(best_reasons),
            }

        return None

    @classmethod
    def _score(cls, baseline, candidate):
        """
        Score candidate against one baseline signature.

        :param dict baseline:
        :param dict candidate:
        :return: tuple[float, list[str]]
        """

        reasons = []

        if baseline.get('code') != candidate.get('code'):
            return 0.0, reasons

        score = 0.18
        reasons.append('code')

        if baseline.get('bucket') == candidate.get('bucket'):
            score += 0.08
            reasons.append('bucket')

        if baseline.get('normalized_body_hash') == candidate.get('normalized_body_hash'):
            score += 0.24
            reasons.append('body-hash')

        if baseline.get('body_skeleton_hash') == candidate.get('body_skeleton_hash'):
            score += 0.15
            reasons.append('skeleton-hash')

        if baseline.get('title') and baseline.get('title') == candidate.get('title'):
            score += 0.06
            reasons.append('title')

        if baseline.get('redirect_location') and baseline.get('redirect_location') == candidate.get('redirect_location'):
            score += 0.08
            reasons.append('redirect')

        size_score = cls._numeric_similarity(baseline.get('size'), candidate.get('size'))
        if size_score >= 0.90:
            score += 0.10 * size_score
            reasons.append('size')

        word_score = cls._numeric_similarity(baseline.get('word_count'), candidate.get('word_count'))
        if word_score >= 0.90:
            score += 0.05 * word_score
            reasons.append('words')

        line_score = cls._numeric_similarity(baseline.get('line_count'), candidate.get('line_count'))
        if line_score >= 0.90:
            score += 0.03 * line_score
            reasons.append('lines')

        if cls._is_exact_shape_match(baseline, candidate) is True:
            score += 0.08
            reasons.append('exact-shape')

        header_score = cls._header_similarity(
            baseline.get('header_fingerprint') or {},
            candidate.get('header_fingerprint') or {}
        )
        if header_score >= 0.80:
            score += 0.03 * header_score
            reasons.append('headers')

        return min(score, 1.0), reasons

    @staticmethod
    def _hash(value):
        """
        Build a stable sha256 hash.

        :param str value:
        :return: str
        """

        return hashlib.sha256(str(value).encode('utf-8')).hexdigest()

    @staticmethod
    def _body(response):
        """
        Decode response body.

        :param object response:
        :return: str
        """

        try:
            return helper.decode(response.data)
        except (AttributeError, TypeError, UnicodeError):
            return ''

    @classmethod
    def _normalize_body(cls, body):
        """
        Normalize dynamic body fragments.

        :param str body:
        :return: str
        """

        value = html.unescape(str(body or '')).lower()
        value = re.sub(r'<!--.*?-->', ' ', value, flags=re.DOTALL)
        value = re.sub(r'<script\b[^>]*>.*?</script>', ' ', value, flags=re.DOTALL | re.IGNORECASE)
        value = re.sub(r'<style\b[^>]*>.*?</style>', ' ', value, flags=re.DOTALL | re.IGNORECASE)

        for pattern in cls.DYNAMIC_PATTERNS:
            value = re.sub(pattern, '<dynamic>', value, flags=re.IGNORECASE)

        value = re.sub(r'\s+', ' ', value)
        return value.strip()

    @staticmethod
    def _body_skeleton(body):
        """
        Build a lightweight HTML structure signature.

        :param str body:
        :return: str
        """

        tags = re.findall(r'<\s*/?\s*([a-z0-9:-]+)', str(body or ''), flags=re.IGNORECASE)

        if len(tags) > 0:
            return ' '.join([tag.lower() for tag in tags])

        text = re.sub(r'\w+', 'w', str(body or '').lower())
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def _title(body):
        """
        Extract HTML title.

        :param str body:
        :return: str
        """

        match = re.search(r'<title[^>]*>(.*?)</title>', str(body or ''), flags=re.IGNORECASE | re.DOTALL)
        if match is None:
            return ''

        value = re.sub(r'\s+', ' ', html.unescape(match.group(1)))
        return value.strip().lower()

    @staticmethod
    def _word_count(body):
        """
        Count text words.

        :param str body:
        :return: int
        """

        text = re.sub(r'<[^>]+>', ' ', str(body or ''))
        return len(re.findall(r'\S+', text))

    @staticmethod
    def _line_count(body):
        """
        Count non-empty lines.

        :param str body:
        :return: int
        """

        return len([line for line in str(body or '').splitlines() if line.strip()])

    @staticmethod
    def _response_size(response):
        """
        Resolve response size.

        :param object response:
        :return: int
        """

        try:
            content_length = response.headers.get('Content-Length')
            if content_length is not None:
                return int(content_length)
        except (AttributeError, TypeError, ValueError):
            pass

        try:
            return len(response.data)
        except (AttributeError, TypeError):
            return 0

    @staticmethod
    def _response_code(response, response_data):
        """
        Resolve HTTP status code.

        :param object response:
        :param tuple response_data:
        :return: int|None
        """

        try:
            return int(response.status)
        except (AttributeError, TypeError, ValueError):
            pass

        try:
            return int(response_data[3])
        except (IndexError, TypeError, ValueError):
            return None

    @classmethod
    def _redirect_location(cls, response):
        """
        Resolve normalized redirect target.

        :param object response:
        :return: str
        """

        location = cls._header(response, 'location')

        if location is None:
            return ''

        return str(location).strip().lower()

    @classmethod
    def _header_fingerprint(cls, response):
        """
        Build stable header fingerprint.

        :param object response:
        :return: dict
        """

        fingerprint = {}

        for header_name in cls.STABLE_HEADERS:
            value = cls._header(response, header_name)
            if value is not None:
                fingerprint[header_name] = str(value).strip().lower()

        return fingerprint

    @staticmethod
    def _header(response, header_name):
        """
        Read response header case-insensitively.

        :param object response:
        :param str header_name:
        :return: str|None
        """

        try:
            headers = response.headers
        except AttributeError:
            return None

        try:
            value = headers.get(header_name)
            if value is not None:
                return value
        except AttributeError:
            pass

        expected = str(header_name).lower()

        try:
            value = headers.get(expected)
            if value is not None:
                return value
        except AttributeError:
            pass

        try:
            for key, value in headers.items():
                if str(key).lower() == expected:
                    return value
        except AttributeError:
            return None

        return None

    @staticmethod
    def _is_exact_shape_match(baseline, candidate):
        """
        Detect exact normalized response shape match.

        :param dict baseline:
        :param dict candidate:
        :return: bool
        """

        return all([
            baseline.get('normalized_body_hash') == candidate.get('normalized_body_hash'),
            baseline.get('body_skeleton_hash') == candidate.get('body_skeleton_hash'),
            baseline.get('size') == candidate.get('size'),
            baseline.get('word_count') == candidate.get('word_count'),
            baseline.get('line_count') == candidate.get('line_count'),
        ])

    @staticmethod
    def _numeric_similarity(left, right):
        """
        Return numeric similarity in range 0..1.

        :param int|None left:
        :param int|None right:
        :return: float
        """

        try:
            left = int(left)
            right = int(right)
        except (TypeError, ValueError):
            return 0.0

        maximum = max(abs(left), abs(right), 1)
        return max(0.0, 1.0 - (abs(left - right) / float(maximum)))

    @staticmethod
    def _header_similarity(left, right):
        """
        Compare stable header fingerprints.

        :param dict left:
        :param dict right:
        :return: float
        """

        if not left and not right:
            return 1.0

        keys = set(left.keys()) | set(right.keys())
        if len(keys) <= 0:
            return 1.0

        matched = 0
        for key in keys:
            if left.get(key) == right.get(key):
                matched += 1

        return matched / float(len(keys))