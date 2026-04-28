# 🚀 Quickstart

This page shows the fastest way to install OpenDoor and run common scans.

---

## 📦 Install

Recommended installation for most CLI users:

```shell
pipx install opendoor
```

Alternative installation with pip:

```shell
python3 -m pip install --upgrade opendoor
```

On macOS, OpenDoor can also be installed with Homebrew when the formula is available:

```shell
brew install opendoor
```

Verify the installation:

```shell
opendoor --version
opendoor --help
```

---

## 🔎 Run a basic directory scan

```shell
opendoor --host https://example.com
```

By default, OpenDoor runs a directory discovery scan using the built-in directory dictionary.

---

## 🌍 Scan subdomains

```shell
opendoor --host example.com --scan subdomains
```

Use a domain name for subdomain discovery.

---

## 📚 Use a custom wordlist

```shell
opendoor --host https://example.com --wordlist ./wordlist.txt
```

---

## 🎯 Scan multiple targets from a file

Create `targets.txt`:

```text
https://example.com
https://app.example.com
example.org
```

Run:

```shell
opendoor --hostlist targets.txt
```

---

## 🔗 Read targets from stdin

```shell
cat targets.txt | opendoor --stdin
```

This is useful for pipelines and automation.

---

## 📊 Save reports

```shell
opendoor --host https://example.com --reports std,json,html --reports-dir ./reports
```

Common report formats:

| Format | Usage |
|---|---|
| `std` | Terminal output |
| `json` | Automation and processing |
| `html` | Human-readable report |
| `sqlite` | Structured local analysis |

---

## 🧹 Reduce false positives

Use response filters:

```shell
opendoor --host https://example.com --exclude-status 404,429,500-599
opendoor --host https://example.com --exclude-size-range 0-256
```

Use auto-calibration:

```shell
opendoor --host https://example.com --auto-calibrate
```

Auto-calibration helps classify soft-404, wildcard, and catch-all responses.

---

## 🧬 Detect technologies

```shell
opendoor --host https://example.com --fingerprint
```

Fingerprinting attempts to identify probable CMS, frameworks, application stacks, and infrastructure providers.

---

## 🛡️ Detect WAF behavior

```shell
opendoor --host https://example.com --waf-detect
```

Use safe mode for a cautious scan profile:

```shell
opendoor --host https://example.com --waf-safe-mode
```

Safe mode is designed to reduce aggressive behavior after WAF or anti-bot signals are detected.

---

## 🔁 Resume interrupted scans

Save progress:

```shell
opendoor --host https://example.com --session-save scan.session
```

Resume later:

```shell
opendoor --session-load scan.session
```

---

## 🌐 Use a proxy

```shell
opendoor --host https://example.com --proxy socks5://127.0.0.1:9050
```

Or explicitly select proxy transport:

```shell
opendoor --host https://example.com --transport proxy --proxy socks5://127.0.0.1:9050
```

---

## 🔐 Use OpenVPN transport

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn
```

For username/password based OpenVPN profiles:

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn \
  --openvpn-auth ./auth.txt
```

---

## 🧵 Use WireGuard transport

```shell
opendoor \
  --host https://example.com \
  --transport wireguard \
  --transport-profile ./profile.conf
```

Never commit real VPN private keys or credentials to the repository.

---

## 🧪 CI/CD example

```shell
opendoor \
  --host https://example.com \
  --fail-on-bucket success,auth,forbidden \
  --reports json,sqlite
```

OpenDoor will complete the scan and return exit code `1` only if selected result buckets are found.

---

## ➡️ Next steps

Read the full [Usage](Usage.md) page for all CLI options.
