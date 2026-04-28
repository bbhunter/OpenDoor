# OpenDoor

**OpenDoor** is an open-source CLI scanner for authorized web reconnaissance, directory discovery, and exposure assessment.

It helps security researchers, penetration testers, bug bounty hunters, and developers identify exposed paths, login panels, directory listings, restricted resources, backup files, web shells, subdomains, and other potentially sensitive web assets.

OpenDoor supports single-target and batch scanning, custom wordlists, response filtering, recursive discovery, fingerprint detection, passive WAF detection, smart auto-calibration, resumable sessions, CI/CD fail-on rules, multiple report formats, and optional network transport profiles for proxy, OpenVPN, and WireGuard workflows.

> OpenDoor must be used only on systems you own or have explicit permission to test.

![OpenDoor](img/open-door.png)

---

Supported Python versions:

| Python | Status |
|---|---|
| 3.12 | Supported |
| 3.13 | Supported |
| 3.14 | Supported |

---

## Key capabilities

### Target input

OpenDoor can scan a single target, a target file, or targets from standard input.

```shell
opendoor --host https://example.com
opendoor --hostlist targets.txt
cat targets.txt | opendoor --stdin
```

### Directory and subdomain discovery

```shell
opendoor --host https://example.com --scan directories
opendoor --host example.com --scan subdomains
```

### Custom wordlists and extensions

```shell
opendoor --host https://example.com --wordlist ./paths.txt
opendoor --host https://example.com --extensions php,json,txt
opendoor --host https://example.com --ignore-extensions aspx,jsp
```

### Response filtering

```shell
opendoor --host https://example.com --include-status 200-299,301,302,403
opendoor --host https://example.com --exclude-status 404,429,500-599
opendoor --host https://example.com --exclude-size-range 0-256,1024-2048
opendoor --host https://example.com --match-regex "admin|login|dashboard"
```

### Smart auto-calibration

Auto-calibration helps reduce noise from soft-404, wildcard, and catch-all responses.

```shell
opendoor --host https://example.com --auto-calibrate
opendoor --host https://example.com --auto-calibrate --calibration-samples 8 --calibration-threshold 0.85
```

### Fingerprint detection

```shell
opendoor --host https://example.com --fingerprint
```

OpenDoor can identify probable application stacks, CMS platforms, frameworks, site builders, static-site tooling, and infrastructure providers.

### WAF detection and safe mode

```shell
opendoor --host https://example.com --waf-detect
opendoor --host https://example.com --waf-safe-mode
```

Safe mode enables a more cautious runtime profile after probable WAF or anti-bot behavior is detected.

### Resumable sessions

```shell
opendoor --host https://example.com --session-save scan.session
opendoor --session-load scan.session
```

Sessions allow long scans to be resumed after interruption.

### Network transport profiles

```shell
opendoor --host https://example.com --transport direct
opendoor --host https://example.com --transport proxy --proxy socks5://127.0.0.1:9050
opendoor --host https://example.com --transport openvpn --transport-profile ./profile.ovpn
opendoor --host https://example.com --transport wireguard --transport-profile ./profile.conf
```

OpenDoor supports direct, proxy, OpenVPN, and WireGuard transport modes.

### Reports

```shell
opendoor --host https://example.com --reports std,json,html
opendoor --host https://example.com --reports json,sqlite --reports-dir ./reports
```

Supported report formats include:

| Format | Purpose |
|---|---|
| `std` | Terminal output |
| `txt` | Plain text output |
| `json` | Machine-readable output |
| `csv` | Spreadsheet-friendly output |
| `html` | Human-readable report |
| `sqlite` | Structured local database for post-processing |

### CI/CD fail-on rules

```shell
opendoor --host https://example.com --fail-on-bucket success,auth,forbidden
```

This allows OpenDoor to return exit code `1` only when selected result buckets are found.

---

## Recommended reading

Start here:

1. [Quickstart](quickstart.md)
2. [Installation and update](Installation-and-update.md)
3. [Usage](Usage.md)
4. [Sniffers](Sniffers.md)
5. [Wizard](Wizard.md)

---

## Responsible use

OpenDoor is a security testing tool. Use it only against systems where you have authorization.

Do not use OpenDoor to scan third-party infrastructure, commercial systems, public services, or organizations without explicit permission.
