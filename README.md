# OpenDoor — OWASP Web Directory Scanner

![OpenDoor](https://raw.githubusercontent.com/stanislav-web/OpenDoor/master/logo.png)

**OpenDoor** is an open-source CLI scanner for authorized web reconnaissance, directory discovery, subdomain enumeration, fingerprint detection, WAF detection, response filtering, reporting, and transport-based scanning workflows.

It helps security researchers, penetration testers, bug bounty hunters, DevSecOps engineers, and developers identify exposed paths, login panels, directory listings, restricted resources, backup files, web shells, subdomains, and other potentially sensitive web assets.

> Use OpenDoor only on systems you own or have explicit permission to test.

---

## ✅ CI status

| Python | Linux | macOS | Windows |
|---|---|---|---|
| 3.12 | [![CI Linux Python 3.12](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-linux-py312.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-linux-py312.yml) | [![CI macOS Python 3.12](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-macos-py312.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-macos-py312.yml) | [![CI Windows Python 3.12](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-windows-py312.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-windows-py312.yml) |
| 3.13 | [![CI Linux Python 3.13](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-linux-py313.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-linux-py313.yml) | [![CI macOS Python 3.13](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-macos-py313.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-macos-py313.yml) | [![CI Windows Python 3.13](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-windows-py313.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-windows-py313.yml) |
| 3.14 | [![CI Linux Python 3.14](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-linux-py314.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-linux-py314.yml) | [![CI macOS Python 3.14](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-macos-py314.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-macos-py314.yml) | [![CI Windows Python 3.14](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-windows-py314.yml/badge.svg?branch=master)](https://github.com/stanislav-web/OpenDoor/actions/workflows/ci-windows-py314.yml) |

[![Documentation Status](https://app.readthedocs.org/projects/opendoor/badge/?version=latest)](https://opendoor.readthedocs.io/en/latest/)
[![PyPI - Version](https://img.shields.io/pypi/v/opendoor)](https://pypi.org/project/opendoor/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-green.svg)](https://www.python.org/)
[![codecov](https://codecov.io/github/stanislav-web/OpenDoor/graph/badge.svg?token=dyBxutYBso)](https://codecov.io/github/stanislav-web/OpenDoor)
[![Codacy Security Scan](https://github.com/stanislav-web/OpenDoor/actions/workflows/codacy.yml/badge.svg)](https://github.com/stanislav-web/OpenDoor/actions/workflows/codacy.yml)
[![Dependency Review](https://github.com/stanislav-web/OpenDoor/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/stanislav-web/OpenDoor/actions/workflows/dependency-review.yml)
[![CodeQL](https://github.com/stanislav-web/OpenDoor/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/stanislav-web/OpenDoor/actions/workflows/github-code-scanning/codeql)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## 🚀 Quick links

- [Documentation](https://opendoor.readthedocs.io/)
- [Quickstart](https://opendoor.readthedocs.io/en/latest/quickstart/)
- [Installation and update](https://opendoor.readthedocs.io/en/latest/Installation-and-update/)
- [Usage guide](https://opendoor.readthedocs.io/en/latest/Usage/)
- [Practical examples](https://opendoor.readthedocs.io/en/latest/examples/basic-scans/)
- [Changelog](CHANGELOG.md)
- [PyPI package](https://pypi.org/project/opendoor/)
- [Issues](https://github.com/stanislav-web/OpenDoor/issues)

---

## ✨ Features

- directory discovery;
- recursive directory discovery;
- subdomain enumeration;
- single target, target file, and stdin input modes;
- custom wordlists, prefixes, and extension filters;
- custom request headers, cookies, and raw HTTP request templates;
- response filters by status, size, text, regex, and body length;
- smart auto-calibration for soft-404, wildcard, and catch-all responses;
- technology fingerprint detection;
- passive WAF detection and WAF-safe scan mode;
- resumable scan sessions with checkpoint autosave;
- CI/CD fail-on result bucket rules;
- reports in terminal, text, JSON, HTML, and SQLite formats;
- proxy, OpenVPN, and WireGuard transport profiles;
- sequential per-target transport rotation for batch workflows;
- configuration wizard for repeatable scan profiles.

---

## 📦 Installation

### pipx

Recommended for most CLI users:

```bash
pipx install opendoor
```

### pip

```bash
python3 -m pip install --upgrade opendoor
```

### Homebrew

When the Homebrew formula is available:

```bash
brew install opendoor
```

### From source

```bash
git clone https://github.com/stanislav-web/OpenDoor.git
cd OpenDoor

python3 -m pip install -r requirements.txt
python3 opendoor.py --help
```

See the full [installation guide](https://opendoor.readthedocs.io/en/latest/Installation-and-update/).

---

## 🚀 Quick usage

### Basic directory scan

```bash
opendoor --host https://example.com
```

### Subdomain scan

```bash
opendoor --host example.com --scan subdomains
```

### Target list

```bash
opendoor --hostlist targets.txt
```

### Standard input

```bash
cat targets.txt | opendoor --stdin
```

### Low-noise scan

```bash
opendoor \
  --host https://example.com \
  --method GET \
  --auto-calibrate \
  --include-status 200-299,301,302,403 \
  --exclude-status 404,429,500-599 \
  --exclude-size-range 0-256 \
  --sniff skipempty,collation,indexof,file \
  --reports std,json
```

### Authenticated scan from raw request

```bash
opendoor \
  --raw-request request.txt \
  --scheme https \
  --method GET \
  --auto-calibrate \
  --reports json,html
```

### WAF-safe scan

```bash
opendoor \
  --host https://example.com \
  --waf-safe-mode \
  --timeout 60 \
  --retries 5 \
  --delay 0.5
```

### OpenVPN transport

```bash
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn
```

### WireGuard transport

```bash
opendoor \
  --host https://example.com \
  --transport wireguard \
  --transport-profile ./profile.conf
```

More examples:

- [Basic scans](https://opendoor.readthedocs.io/en/latest/examples/basic-scans/)
- [Batch scans](https://opendoor.readthedocs.io/en/latest/examples/batch-scans/)
- [Authenticated scans](https://opendoor.readthedocs.io/en/latest/examples/authenticated-scans/)
- [WAF-safe scans](https://opendoor.readthedocs.io/en/latest/examples/waf-safe-scans/)
- [VPN transport scans](https://opendoor.readthedocs.io/en/latest/examples/vpn-transport-scans/)
- [CI/CD examples](https://opendoor.readthedocs.io/en/latest/examples/ci-cd/)

---

## 📚 Documentation

The full documentation is available on ReadTheDocs:

- [Home](https://opendoor.readthedocs.io/)
- [Quickstart](https://opendoor.readthedocs.io/en/latest/quickstart/)
- [Installation and update](https://opendoor.readthedocs.io/en/latest/Installation-and-update/)
- [Usage guide](https://opendoor.readthedocs.io/en/latest/Usage/)
- [Target input](https://opendoor.readthedocs.io/en/latest/concepts/target-input/)
- [Reports](https://opendoor.readthedocs.io/en/latest/concepts/reports/)
- [Fingerprinting](https://opendoor.readthedocs.io/en/latest/detection/fingerprinting/)
- [WAF detection and safe mode](https://opendoor.readthedocs.io/en/latest/detection/waf-detection/)
- [Auto-calibration](https://opendoor.readthedocs.io/en/latest/detection/auto-calibration/)
- [Network transports](https://opendoor.readthedocs.io/en/latest/transports/overview/)
- [OpenVPN transport](https://opendoor.readthedocs.io/en/latest/transports/openvpn/)
- [WireGuard transport](https://opendoor.readthedocs.io/en/latest/transports/wireguard/)
- [Practical examples](https://opendoor.readthedocs.io/en/latest/examples/basic-scans/)
- [Testing](https://opendoor.readthedocs.io/en/latest/Testing/)
- [Contribution](https://opendoor.readthedocs.io/en/latest/Contribution/)

---

## 🧪 Development

Install development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

Run tests:

```bash
python -m unittest
```

Run coverage:

```bash
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report -m
```

Build documentation:

```bash
python3 -m venv .docs-venv
source .docs-venv/bin/activate
python -m pip install -r docs/requirements.txt
python -m mkdocs build --strict
```

Build package artifacts:

```bash
python -m build
```

See the full [testing guide](https://opendoor.readthedocs.io/en/latest/Testing/) and [contribution guide](https://opendoor.readthedocs.io/en/latest/Contribution/).

---

## 🔐 Security and secret hygiene

Do not commit real secrets or private transport profiles.

Never publish:

- real OpenVPN profiles;
- WireGuard private keys;
- auth-user-pass files;
- cookies;
- bearer tokens;
- customer target lists;
- private scan reports;
- sensitive CI artifacts.

Use placeholder examples only.

---

## ⚖️ Responsible use

OpenDoor is a security testing tool.

Use it only against systems you own or have explicit permission to test.

The project does not grant permission to scan third-party systems, organizations, commercial services, or public infrastructure without authorization.

---

## 🧾 Changelog

See [CHANGELOG.md](CHANGELOG.md) and [GitHub Releases](https://github.com/stanislav-web/OpenDoor/releases).

---

## 🤝 Contributing

Pull requests are welcome.

Before contributing, read the [contribution guide](https://opendoor.readthedocs.io/en/latest/Contribution/) and run the relevant tests.

---

## 📄 License

OpenDoor is released under the GNU General Public License v3.0 only.

See [LICENSE](LICENSE).

---

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/stanislav-web/OpenDoor)
