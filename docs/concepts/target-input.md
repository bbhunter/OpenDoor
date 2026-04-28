# 🎯 Target input

OpenDoor can scan a single target, a target file, targets from standard input, or a saved session.

This makes it usable both as an interactive scanner and as a batch-oriented CLI tool.

---

## Single target

Use `--host` for one target:

```shell
opendoor --host https://example.com
```

For directory discovery, prefer a full URL:

```shell
opendoor --host https://example.com --scan directories
```

For subdomain discovery, use a domain name:

```shell
opendoor --host example.com --scan subdomains
```

---

## Target list

Use `--hostlist` for multiple targets:

```shell
opendoor --hostlist targets.txt
```

Example `targets.txt`:

```text
https://example.com
https://app.example.com
example.org
```

This mode is useful for larger batches, scheduled checks, and CI/CD workflows.

---

## Standard input

Use `--stdin` when targets are produced by another command:

```shell
cat targets.txt | opendoor --stdin
```

Example pipeline:

```shell
cat targets.txt | grep example | opendoor --stdin --reports json,sqlite
```

This keeps OpenDoor easy to compose with shell tooling.

---

## Session input

Use `--session-load` to resume a previous scan:

```shell
opendoor --session-load scan.session
```

Sessions are created with:

```shell
opendoor --host https://example.com --session-save scan.session
```

Use session input when you need to continue an interrupted scan without rebuilding the scan state manually.

---

## Choosing the right input mode

| Use case | Recommended option |
|---|---|
| One web application | `--host` |
| Many targets from a file | `--hostlist` |
| Pipeline input | `--stdin` |
| Resume interrupted work | `--session-load` |

---

## Practical examples

### Batch scan with reports

```shell
opendoor \
  --hostlist targets.txt \
  --reports json,sqlite \
  --reports-dir ./reports
```

### Pipeline scan

```shell
cat targets.txt | opendoor --stdin --auto-calibrate --reports json
```

### Resume long scan

```shell
opendoor --session-load long-scan.session
```
