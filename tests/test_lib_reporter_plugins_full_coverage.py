# -*- coding: utf-8 -*-

import copy
import os
import unittest
from unittest.mock import patch

from src.lib.reporter.plugins.provider.provider import PluginProvider
from src.core.filesystem.exceptions import FileSystemError
from src.lib.reporter.plugins.html import HtmlReportPlugin
from src.lib.reporter.plugins.json import JsonReportPlugin
from src.lib.reporter.plugins.txt import TextReportPlugin



class TestReporterPluginsFullCoverage(unittest.TestCase):
    """Extra branch tests to close html/json/txt reporter plugin coverage."""

    def setUp(self):
        """Prepare common payloads."""

        self.target = 'test.local'
        self.plain_data = {
            'items': {
                'success': ['http://example.com/admin'],
                'failed': ['http://example.com/missing'],
                'indexof': ['http://example.com/public'],
            }
        }
        self.rich_data = {
            'items': {
                'success': ['http://example.com/admin'],
                'failed': ['http://example.com/missing'],
                'indexof': ['http://example.com/public'],
            },
            'report_items': {
                'success': [{'url': 'http://example.com/admin', 'size': '9B', 'code': '200'}],
                'failed': [{'url': 'http://example.com/missing', 'size': '0B', 'code': '404'}],
                'indexof': [{'url': 'http://example.com/public', 'size': '1KB', 'code': '200'}],
            },
        }

    def test_html_process_preserves_existing_report_items_and_does_not_mutate_source(self):
        """HtmlReportPlugin should keep existing report_items and avoid mutating source data."""

        source = copy.deepcopy(self.rich_data)

        with patch('src.lib.reporter.plugins.html.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.html.filesystem.clear'), \
                patch('src.lib.reporter.plugins.html.Json2Html') as json2html_cls:
            json2html_cls.return_value.convert.return_value = '<table>ok</table>'

            plugin = HtmlReportPlugin(self.target, source, directory='/custom/')
            with patch.object(plugin, 'record') as record_mock:
                plugin.process()

        payload = json2html_cls.return_value.convert.call_args.kwargs['json']
        self.assertEqual(payload['report_items'], self.rich_data['report_items'])
        self.assertEqual(source, self.rich_data)
        record_mock.assert_called_once_with('/tmp/reports', self.target, '<table>ok</table>')

    def test_html_process_handles_missing_items_key(self):
        """HtmlReportPlugin should build an empty report_items map when items are missing."""

        data = {'total': {'items': 0}}

        with patch('src.lib.reporter.plugins.html.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.html.filesystem.clear'), \
                patch('src.lib.reporter.plugins.html.Json2Html') as json2html_cls:
            json2html_cls.return_value.convert.return_value = '<table>ok</table>'

            plugin = HtmlReportPlugin(self.target, data, directory='/custom/')
            with patch.object(plugin, 'record'):
                plugin.process()

        payload = json2html_cls.return_value.convert.call_args.kwargs['json']
        self.assertEqual(payload, {'total': {'items': 0}, 'report_items': {}})

    def test_html_process_wraps_record_filesystem_error(self):
        """HtmlReportPlugin should wrap FileSystemError raised during record."""

        with patch('src.lib.reporter.plugins.html.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.html.filesystem.clear'), \
                patch('src.lib.reporter.plugins.html.Json2Html') as json2html_cls:
            json2html_cls.return_value.convert.return_value = '<table>ok</table>'

            plugin = HtmlReportPlugin(self.target, self.plain_data, directory='/custom/')
            with patch.object(plugin, 'record', side_effect=FileSystemError('boom')):
                with self.assertRaises(Exception):
                    plugin.process()

    def test_text_process_skips_when_only_failed_bucket_exists(self):
        """TextReportPlugin should not write reports when only failed items are present."""

        data = {'items': {'failed': ['http://example.com/missing']}}

        with patch('src.lib.reporter.plugins.txt.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.txt.filesystem.clear') as clear_mock:
            plugin = TextReportPlugin(self.target, data, directory='/custom/')
            with patch.object(plugin, 'record') as record_mock:
                plugin.process()

        clear_mock.assert_called_once_with('/tmp/reports', extension='.txt')
        record_mock.assert_not_called()

    def test_text_process_handles_empty_items_bucket(self):
        """TextReportPlugin should not write reports when items are empty."""

        data = {'items': {}}

        with patch('src.lib.reporter.plugins.txt.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.txt.filesystem.clear') as clear_mock:
            plugin = TextReportPlugin(self.target, data, directory='/custom/')
            with patch.object(plugin, 'record') as record_mock:
                plugin.process()

        clear_mock.assert_called_once_with('/tmp/reports', extension='.txt')
        record_mock.assert_not_called()

    def test_text_process_prefers_detailed_report_items(self):
        """TextReportPlugin should use report_items instead of plain item URLs when present."""

        with patch('src.lib.reporter.plugins.txt.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.txt.filesystem.clear'):
            plugin = TextReportPlugin(self.target, self.rich_data, directory='/custom/')
            with patch.object(plugin, 'record') as record_mock:
                plugin.process()

        record_mock.assert_any_call('/tmp/reports', 'success', ['http://example.com/admin - 200 - 9B'], '\n')
        record_mock.assert_any_call('/tmp/reports', 'indexof', ['http://example.com/public - 200 - 1KB'], '\n')

    def test_text_process_wraps_record_exception(self):
        """TextReportPlugin should wrap generic record exceptions."""

        with patch('src.lib.reporter.plugins.txt.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.txt.filesystem.clear'):
            plugin = TextReportPlugin(self.target, self.rich_data, directory='/custom/')
            with patch.object(plugin, 'record', side_effect=Exception('boom')):
                with self.assertRaises(Exception):
                    plugin.process()

    def test_json_init_joins_custom_directory_without_separator(self):
        """JsonReportPlugin should join custom directories without requiring a trailing separator."""

        with patch('src.lib.reporter.plugins.json.filesystem.makedir', return_value='/tmp/reports') as makedir_mock:
            JsonReportPlugin(self.target, self.plain_data, directory='/custom/reports')

        makedir_mock.assert_called_once_with(os.path.join('/custom/reports', self.target))

    def test_json_process_uses_serialized_payload(self):
        """JsonReportPlugin should record the serialized JSON returned by helper.to_json."""

        with patch('src.lib.reporter.plugins.json.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.json.helper.to_json', return_value='{"ok": true}') as to_json_mock, \
                patch('src.lib.reporter.plugins.json.filesystem.clear'):
            plugin = JsonReportPlugin(self.target, self.plain_data, directory='/custom/')
            with patch.object(plugin, 'record') as record_mock:
                plugin.process()

        to_json_mock.assert_called_once_with(self.plain_data)
        record_mock.assert_called_once_with('/tmp/reports', self.target, '{"ok": true}')

    def test_json_process_propagates_to_json_runtime_error(self):
        """JsonReportPlugin should propagate errors raised before entering the filesystem try block."""

        with patch('src.lib.reporter.plugins.json.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.json.helper.to_json', side_effect=RuntimeError('boom')):
            plugin = JsonReportPlugin(self.target, self.plain_data, directory='/custom/')
            with self.assertRaises(RuntimeError):
                plugin.process()

    def test_json_process_wraps_record_filesystem_error(self):
        """JsonReportPlugin should wrap FileSystemError raised during record."""

        with patch('src.lib.reporter.plugins.json.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.json.helper.to_json', return_value='{"ok": true}'), \
                patch('src.lib.reporter.plugins.json.filesystem.clear'):
            plugin = JsonReportPlugin(self.target, self.plain_data, directory='/custom/')
            with patch.object(plugin, 'record', side_effect=FileSystemError('boom')):
                with self.assertRaises(Exception):
                    plugin.process()

    def test_text_process_formats_header_bypass_metadata(self):
        """TextReportPlugin should include header-bypass evidence in bypass report lines."""

        data = {
            'items': {
                'bypass': ['http://example.com/admin'],
            },
            'report_items': {
                'bypass': [
                    {
                        'url': 'http://example.com/admin',
                        'code': '200',
                        'size': '90B',
                        'bypass': 'header',
                        'bypass_header': 'X-Original-URL',
                        'bypass_value': '/admin',
                        'bypass_from_code': '403',
                        'bypass_to_code': '200',
                    }
                ],
            },
        }

        with patch('src.lib.reporter.plugins.txt.filesystem.makedir', return_value='/tmp/reports'), \
                patch('src.lib.reporter.plugins.txt.filesystem.clear'):
            plugin = TextReportPlugin(self.target, data, directory='/custom/')
            with patch.object(plugin, 'record') as record_mock:
                plugin.process()

        record_mock.assert_called_once_with(
            '/tmp/reports',
            'bypass',
            [
                'http://example.com/admin - 200 - 90B | '
                'bypass=header, header=X-Original-URL, value=/admin, 403->200'
            ],
            '\n'
        )

    def test_html_process_preserves_header_bypass_report_items(self):
            """HtmlReportPlugin should preserve header-bypass metadata inside report_items."""

            data = {
                'items': {
                    'bypass': ['http://example.com/admin'],
                },
                'report_items': {
                    'bypass': [
                        {
                            'url': 'http://example.com/admin',
                            'code': '200',
                            'size': '90B',
                            'bypass': 'header',
                            'bypass_header': 'X-Original-URL',
                            'bypass_value': '/admin',
                            'bypass_from_code': '403',
                            'bypass_to_code': '200',
                        }
                    ],
                },
            }

            with patch('src.lib.reporter.plugins.html.filesystem.makedir', return_value='/tmp/reports'), \
                    patch('src.lib.reporter.plugins.html.filesystem.clear'), \
                    patch('src.lib.reporter.plugins.html.Json2Html') as json2html_cls:
                json2html_cls.return_value.convert.return_value = '<table>ok</table>'

                plugin = HtmlReportPlugin(self.target, data, directory='/custom/')
                with patch.object(plugin, 'record'):
                    plugin.process()

            payload = json2html_cls.return_value.convert.call_args.kwargs['json']

            self.assertEqual(payload['report_items']['bypass'][0]['bypass_header'], 'X-Original-URL')
            self.assertEqual(payload['report_items']['bypass'][0]['bypass_from_code'], '403')
            self.assertEqual(payload['report_items']['bypass'][0]['bypass_to_code'], '200')

    def test_json_process_preserves_header_bypass_payload(self):
            """JsonReportPlugin should serialize the original payload with header-bypass metadata."""

            data = {
                'items': {
                    'bypass': ['http://example.com/admin'],
                },
                'report_items': {
                    'bypass': [
                        {
                            'url': 'http://example.com/admin',
                            'code': '200',
                            'size': '90B',
                            'bypass': 'header',
                            'bypass_header': 'X-Original-URL',
                            'bypass_value': '/admin',
                            'bypass_from_code': '403',
                            'bypass_to_code': '200',
                        }
                    ],
                },
            }

            with patch('src.lib.reporter.plugins.json.filesystem.makedir', return_value='/tmp/reports'), \
                    patch('src.lib.reporter.plugins.json.helper.to_json', return_value='{"ok": true}') as to_json_mock, \
                    patch('src.lib.reporter.plugins.json.filesystem.clear'):
                plugin = JsonReportPlugin(self.target, data, directory='/custom/')
                with patch.object(plugin, 'record'):
                    plugin.process()

            to_json_mock.assert_called_once_with(data)

    def test_format_report_item_formats_waf_without_confidence(self):
        """PluginProvider.format_report_item() should format WAF metadata without confidence."""

        actual = PluginProvider.format_report_item({
            'url': 'https://example.com/login',
            'code': '403',
            'size': '25B',
            'waf': 'Cloudflare',
        })

        self.assertEqual(
            actual,
            'https://example.com/login - 403 - 25B - WAF: Cloudflare'
        )

    def test_format_report_item_formats_bypass_without_header_value_and_codes(self):
        """PluginProvider.format_report_item() should format minimal bypass metadata."""

        actual = PluginProvider.format_report_item({
            'url': 'https://example.com/admin',
            'code': '200',
            'size': '90B',
            'bypass': 'header',
        })

        self.assertEqual(
            actual,
            'https://example.com/admin - 200 - 90B | bypass=header'
        )

    def test_format_report_item_formats_bypass_with_only_transition_codes(self):
        """PluginProvider.format_report_item() should format bypass transition without header/value evidence."""

        actual = PluginProvider.format_report_item({
            'url': 'https://example.com/admin',
            'code': '200',
            'size': '90B',
            'bypass': 'header',
            'bypass_from_code': '403',
            'bypass_to_code': '200',
        })

        self.assertEqual(
            actual,
            'https://example.com/admin - 200 - 90B | bypass=header, 403->200'
        )

    def test_format_report_item_formats_bypass_without_transition_codes(self):
        """PluginProvider.format_report_item() should format header/value bypass metadata without transition codes."""

        actual = PluginProvider.format_report_item({
            'url': 'https://example.com/admin',
            'code': '200',
            'size': '90B',
            'bypass': 'header',
            'bypass_header': 'X-Original-URL',
            'bypass_value': '/admin',
        })

        self.assertEqual(
            actual,
            'https://example.com/admin - 200 - 90B | '
            'bypass=header, header=X-Original-URL, value=/admin'
        )

if __name__ == '__main__':
    unittest.main()