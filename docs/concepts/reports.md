# 📊 Reports

OpenDoor can write scan results in several formats.

Reports are configured with:

```shell
opendoor --host https://example.com --reports std,json,html
```

Use a custom output directory:

```shell
opendoor --host https://example.com --reports json,sqlite --reports-dir ./reports
```

---

## Supported formats

| Format | Purpose |
|---|---|
| `std` | Terminal output |
| `txt` | Plain text output |
| `json` | Machine-readable output |
| `html` | Human-readable report |
| `sqlite` | Structured local database for post-processing |

Use the exact formats shown by:

```shell
opendoor --help
```

because available report plugins can vary by build.

---

## Terminal output

```shell
opendoor --host https://example.com --reports std
```

Use `std` for interactive work.

---

## JSON

```shell
opendoor --host https://example.com --reports json
```

Use JSON for automation, pipelines, post-processing, and CI/CD artifact uploads.

---

## HTML

```shell
opendoor --host https://example.com --reports html
```

Use HTML for a readable standalone report.

---

## SQLite

```shell
opendoor --host https://example.com --reports sqlite
```

Use SQLite when you want structured local analysis, later filtering, or integration with other tools.

SQLite is useful for:

- large scans;
- batch scans;
- CI artifacts;
- recurring exposure checks;
- historical comparison.

---

## Multiple reports

```shell
opendoor \
  --host https://example.com \
  --reports std,json,html,sqlite \
  --reports-dir ./reports
```

This is useful when one scan needs both human-readable and machine-readable output.

---

## CI/CD reports

```shell
opendoor \
  --host https://example.com \
  --reports json,sqlite \
  --fail-on-bucket success,auth,forbidden
```

In CI/CD, prefer machine-readable formats such as `json` and `sqlite`.

---

## Report hygiene

Reports may contain sensitive findings.

Do not commit scan reports that include:

- private target URLs;
- internal paths;
- authentication-related endpoints;
- customer systems;
- cookies;
- tokens;
- private infrastructure details.

Store reports as CI artifacts or local evidence, not as public repository files.
