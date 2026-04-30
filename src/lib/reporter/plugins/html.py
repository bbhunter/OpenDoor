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

import os
from xml.sax.saxutils import escape as xml_escape

from .provider import PluginProvider
from src.core import CoreConfig
from src.core import filesystem, FileSystemError


class HtmlReportPlugin(PluginProvider):
    """ HtmlReportPlugin class"""

    PLUGIN_NAME = 'HtmlReport'
    EXTENSION_SET = '.html'

    def __init__(self, target, data, directory=None):
        """
        PluginProvider constructor
        :param str target: target host
        :param dict data: result set
        :param str directory: custom directory
        """

        PluginProvider.__init__(self, target, data)

        try:

            if None is directory:
                directory = CoreConfig.get('data').get('reports')
            self.__target_dir = filesystem.makedir(os.path.join(directory, self._target))
        except FileSystemError as error:
            raise Exception(error)

    def process(self):
        """
        Process data
        :return: str
        """

        try:
            filesystem.clear(self.__target_dir, extension=self.EXTENSION_SET)
            report_data = dict(self._data)
            report_data['report_items'] = {
                status: self.get_report_items(status)
                for status in self._data.get('items', {}).keys()
            }
            resultset = render_html_report(self._target, report_data)
            self.record(self.__target_dir, self._target, resultset)
        except FileSystemError as error:
            raise Exception(error)


def render_html_report(target, report_data):
    """
    Render OpenDoor report data as a standalone HTML document.

    :param str target: target host
    :param dict report_data: report payload
    :return: HTML document
    :rtype: str
    """

    target = _escape(target)
    totals = report_data.get('total', {})
    report_items = report_data.get('report_items', {})
    metadata = _get_metadata(report_data)

    return ''.join([
        '<!doctype html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>OpenDoor Report - {0}</title>'.format(target),
        '<style>',
        _get_report_css(),
        '</style>',
        '</head>',
        '<body>',
        '<main class="page">',
        '<section class="hero">',
        '<div>',
        '<p class="eyebrow">OpenDoor Report</p>',
        '<h1>{0}</h1>'.format(target),
        '<p class="subtitle">Authorized web reconnaissance and directory discovery results.</p>',
        '</div>',
        '<div class="hero-badge">HTML</div>',
        '</section>',
        _render_totals(totals),
        _render_report_items(report_items),
        _render_metadata(metadata),
        '</main>',
        '</body>',
        '</html>',
    ])


def _get_report_css():
    """
    Return embedded report stylesheet.

    :return: CSS stylesheet
    :rtype: str
    """

    return """
:root {
  color-scheme: light;
  --bg: #f6f8fb;
  --panel: #ffffff;
  --panel-soft: #f9fafb;
  --text: #111827;
  --muted: #6b7280;
  --border: #e5e7eb;
  --border-strong: #d1d5db;
  --accent: #2563eb;
  --accent-soft: #eff6ff;
  --success: #047857;
  --success-soft: #ecfdf5;
  --warning: #b45309;
  --warning-soft: #fffbeb;
  --danger: #b91c1c;
  --danger-soft: #fef2f2;
  --shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}

.page {
  width: min(1180px, calc(100% - 32px));
  margin: 32px auto;
}

.hero,
.section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow);
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 30px;
  line-height: 1.15;
}

h2 {
  margin: 0;
  font-size: 18px;
}

h3 {
  margin: 0;
  font-size: 15px;
}

.subtitle {
  margin: 8px 0 0;
  color: var(--muted);
}

.hero-badge {
  flex: 0 0 auto;
  padding: 8px 14px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 700;
}

.section {
  margin-top: 18px;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--panel-soft);
}

.section-description {
  margin: 4px 0 0;
  color: var(--muted);
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  padding: 18px 20px 20px;
}

.card {
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: #fff;
}

.card-label {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-value {
  margin: 0;
  font-size: 24px;
  font-weight: 750;
}

.status-block {
  padding: 18px 20px 20px;
  border-top: 1px solid var(--border);
}

.status-block:first-child {
  border-top: 0;
}

.status-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 14px;
}

table {
  width: 100%;
  min-width: 720px;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
}

th,
td {
  padding: 11px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  text-align: left;
}

th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f3f4f6;
  color: #374151;
  font-size: 12px;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

tr:last-child td {
  border-bottom: 0;
}

tbody tr:hover td {
  background: #f9fafb;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}

.break {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.badge {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.badge-success {
  background: var(--success-soft);
  color: var(--success);
}

.badge-warning {
  background: var(--warning-soft);
  color: var(--warning);
}

.badge-danger {
  background: var(--danger-soft);
  color: var(--danger);
}

.empty {
  margin: 0;
  padding: 18px 20px;
  color: var(--muted);
}

.value-list {
  margin: 0;
  padding-left: 18px;
}

.value-list li {
  margin: 3px 0;
}

.nested {
  margin: 0;
  padding: 10px;
  border-radius: 10px;
  background: #f9fafb;
  border: 1px solid var(--border);
  white-space: pre-wrap;
}

@media print {
  body {
    background: #fff;
  }

  .page {
    width: 100%;
    margin: 0;
  }

  .hero,
  .section {
    box-shadow: none;
  }

  th {
    position: static;
  }
}
"""


def _render_totals(totals):
    """
    Render total statistics block.

    :param dict totals: total counters
    :return: HTML fragment
    :rtype: str
    """

    if not isinstance(totals, dict) or not totals:
        return ''

    cards = []

    for key in sorted(totals.keys()):
        cards.append(
            '<article class="card">'
            '<p class="card-label">{0}</p>'
            '<p class="card-value">{1}</p>'
            '</article>'.format(
                _escape(key),
                _escape(totals.get(key)),
            )
        )

    return (
        '<section class="section">'
        '<div class="section-header">'
        '<div>'
        '<h2>Summary</h2>'
        '<p class="section-description">Aggregated scan counters.</p>'
        '</div>'
        '</div>'
        '<div class="cards">{0}</div>'
        '</section>'
    ).format(''.join(cards))


def _render_report_items(report_items):
    """
    Render discovered report items grouped by status.

    :param dict report_items: status-to-items map
    :return: HTML fragment
    :rtype: str
    """

    if not isinstance(report_items, dict) or not report_items:
        return (
            '<section class="section">'
            '<div class="section-header">'
            '<div>'
            '<h2>Findings</h2>'
            '<p class="section-description">No report items were generated.</p>'
            '</div>'
            '</div>'
            '<p class="empty">No findings.</p>'
            '</section>'
        )

    sections = []

    for status in sorted(report_items.keys()):
        items = report_items.get(status) or []
        sections.append(_render_status_items(status, items))

    return (
        '<section class="section">'
        '<div class="section-header">'
        '<div>'
        '<h2>Findings</h2>'
        '<p class="section-description">Discovered resources grouped by OpenDoor status.</p>'
        '</div>'
        '</div>'
        '{0}'
        '</section>'
    ).format(''.join(sections))


def _render_status_items(status, items):
    """
    Render one status group.

    :param str status: item status
    :param list items: status items
    :return: HTML fragment
    :rtype: str
    """

    count = len(items) if isinstance(items, list) else 0

    if not items:
        table = '<p class="empty">No items in this bucket.</p>'
    elif all(isinstance(item, dict) for item in items):
        table = _render_list_of_dicts(items)
    else:
        table = _render_plain_list(items)

    return (
        '<div class="status-block">'
        '<div class="status-title">'
        '<h3>{0}</h3>'
        '<span class="{1}">{2}</span>'
        '</div>'
        '{3}'
        '</div>'
    ).format(
        _escape(status),
        _get_status_badge_class(status),
        _escape(count),
        table,
    )


def _render_list_of_dicts(items):
    """
    Render a list of dictionaries as a table.

    :param list items: list of dict items
    :return: HTML table
    :rtype: str
    """

    columns = _get_columns(items)

    head = ''.join(
        '<th>{0}</th>'.format(_escape(column))
        for column in columns
    )

    rows = []

    for item in items:
        cells = ''.join(
            '<td>{0}</td>'.format(_render_cell(column, item.get(column)))
            for column in columns
        )
        rows.append('<tr>{0}</tr>'.format(cells))

    return (
        '<div class="table-wrap">'
        '<table class="report-table">'
        '<thead><tr>{0}</tr></thead>'
        '<tbody>{1}</tbody>'
        '</table>'
        '</div>'
    ).format(head, ''.join(rows))


def _render_plain_list(items):
    """
    Render plain list values as a table.

    :param list items: list values
    :return: HTML table
    :rtype: str
    """

    rows = []

    for index, item in enumerate(items, start=1):
        rows.append(
            '<tr>'
            '<td><span class="badge">{0}</span></td>'
            '<td>{1}</td>'
            '</tr>'.format(index, _render_value(item))
        )

    return (
        '<div class="table-wrap">'
        '<table class="report-table">'
        '<thead><tr><th>#</th><th>value</th></tr></thead>'
        '<tbody>{0}</tbody>'
        '</table>'
        '</div>'
    ).format(''.join(rows))


def _render_metadata(metadata):
    """
    Render additional report metadata.

    :param dict metadata: report metadata
    :return: HTML fragment
    :rtype: str
    """

    if not metadata:
        return ''

    rows = []

    for key in sorted(metadata.keys()):
        rows.append(
            '<tr>'
            '<th>{0}</th>'
            '<td>{1}</td>'
            '</tr>'.format(
                _escape(key),
                _render_value(metadata.get(key)),
            )
        )

    return (
        '<section class="section">'
        '<div class="section-header">'
        '<div>'
        '<h2>Metadata</h2>'
        '<p class="section-description">Additional scan context.</p>'
        '</div>'
        '</div>'
        '<div class="table-wrap">'
        '<table class="report-table">'
        '<tbody>{0}</tbody>'
        '</table>'
        '</div>'
        '</section>'
    ).format(''.join(rows))


def _render_cell(column, value):
    """
    Render a table cell value.

    :param str column: column name
    :param value: cell value
    :return: HTML fragment
    :rtype: str
    """

    if column == 'url' and _is_http_url(value):
        url = _escape(value)

        return (
            '<a class="mono break" href="{0}" target="_blank" rel="noopener noreferrer">'
            '{0}'
            '</a>'
        ).format(url)

    if column == 'code':
        return _render_status_code(value)

    if isinstance(value, bool):
        return _render_bool(value)

    if value is None:
        return '<span class="badge">-</span>'

    if isinstance(value, (dict, list, tuple)):
        return '<pre class="nested">{0}</pre>'.format(_escape(value))

    return '<span class="{0}">{1}</span>'.format(
        _get_value_class(column),
        _escape(value),
    )


def _render_value(value):
    """
    Render a generic value.

    :param value: value to render
    :return: HTML fragment
    :rtype: str
    """

    if isinstance(value, bool):
        return _render_bool(value)

    if value is None:
        return '<span class="badge">-</span>'

    if isinstance(value, dict):
        return _render_dict_value(value)

    if isinstance(value, (list, tuple)):
        return _render_list_value(value)

    return '<span class="break">{0}</span>'.format(_escape(value))


def _render_dict_value(value):
    """
    Render dictionary value as a compact nested table.

    :param dict value: dictionary value
    :return: HTML fragment
    :rtype: str
    """

    if not value:
        return '<span class="badge">empty</span>'

    rows = []

    for key in sorted(value.keys()):
        rows.append(
            '<tr>'
            '<th>{0}</th>'
            '<td>{1}</td>'
            '</tr>'.format(
                _escape(key),
                _render_value(value.get(key)),
            )
        )

    return (
        '<div class="table-wrap">'
        '<table class="report-table">'
        '<tbody>{0}</tbody>'
        '</table>'
        '</div>'
    ).format(''.join(rows))


def _render_list_value(value):
    """
    Render list-like value.

    :param list|tuple value: list-like value
    :return: HTML fragment
    :rtype: str
    """

    if not value:
        return '<span class="badge">empty</span>'

    items = [
        '<li>{0}</li>'.format(_render_value(item))
        for item in value
    ]

    return '<ul class="value-list">{0}</ul>'.format(''.join(items))


def _render_status_code(value):
    """
    Render HTTP status code with visual severity.

    :param value: HTTP status code
    :return: HTML fragment
    :rtype: str
    """

    code = str(value)

    if code.startswith('2') or code.startswith('3'):
        badge_class = 'badge badge-success'
    elif code.startswith('4'):
        badge_class = 'badge badge-warning'
    elif code.startswith('5'):
        badge_class = 'badge badge-danger'
    else:
        badge_class = 'badge'

    return '<span class="{0}">{1}</span>'.format(badge_class, _escape(value))


def _render_bool(value):
    """
    Render boolean value as a badge.

    :param bool value: boolean value
    :return: HTML fragment
    :rtype: str
    """

    if value:
        return '<span class="badge badge-success">true</span>'

    return '<span class="badge">false</span>'


def _get_columns(items):
    """
    Return stable table columns for report item dictionaries.

    :param list items: report item dictionaries
    :return: ordered column names
    :rtype: list
    """

    preferred = [
        'url',
        'code',
        'size',
        'title',
        'redirect',
        'content_type',
        'waf',
        'waf_confidence',
        'bypass',
        'bypass_header',
        'bypass_value',
        'bypass_from_code',
        'bypass_to_code',
    ]

    existing = []

    for item in items:
        for key in item.keys():
            if key not in existing:
                existing.append(key)

    columns = [
        key
        for key in preferred
        if key in existing
    ]

    columns.extend([
        key
        for key in existing
        if key not in columns
    ])

    return columns


def _get_metadata(report_data):
    """
    Return report metadata excluding noisy item buckets.

    :param dict report_data: report payload
    :return: metadata map
    :rtype: dict
    """

    excluded = set(['items', 'report_items', 'total'])

    return {
        key: value
        for key, value in report_data.items()
        if key not in excluded
    }


def _get_status_badge_class(status):
    """
    Return badge CSS class for a finding status.

    :param str status: finding status
    :return: CSS class
    :rtype: str
    """

    status = str(status).lower()

    if status in ('success', 'index', 'indexof'):
        return 'badge badge-success'

    if status in ('failed', 'error', 'blocked'):
        return 'badge badge-danger'

    if status in ('warning', 'redirect'):
        return 'badge badge-warning'

    return 'badge'


def _get_value_class(column):
    """
    Return CSS class for a regular cell value.

    :param str column: column name
    :return: CSS class
    :rtype: str
    """

    if column in ('url', 'redirect', 'content_type', 'bypass_header', 'bypass_value'):
        return 'mono break'

    return 'break'


def _is_http_url(value):
    """
    Check whether value is a safe HTTP(S) URL for link rendering.

    :param value: candidate value
    :return: check result
    :rtype: bool
    """

    if not isinstance(value, str):
        return False

    return value.startswith('http://') or value.startswith('https://')


def _escape(value):
    """
    Escape value for safe HTML rendering.

    :param value: value to escape
    :return: escaped string
    :rtype: str
    """

    if value is None:
        return ''

    return xml_escape(str(value), {
        '"': '&quot;',
        "'": '&#x27;',
    })