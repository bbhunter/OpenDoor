# 🧬 Fingerprinting

Fingerprinting attempts to identify probable technologies before or during a scan.

Enable it with:

```shell
opendoor --host https://example.com --fingerprint
```

---

## What fingerprinting helps with

Fingerprinting can help identify probable:

- CMS platforms;
- frameworks;
- static-site tooling;
- application stacks;
- hosting platforms;
- infrastructure providers;
- CDN or edge infrastructure signals.

This helps you choose better wordlists, filters, and scan strategy.

---

## Basic example

```shell
opendoor --host https://example.com --fingerprint
```

Combine with directory discovery:

```shell
opendoor \
  --host https://example.com \
  --fingerprint \
  --scan directories
```

---

## Fingerprinting with reports

```shell
opendoor \
  --host https://example.com \
  --fingerprint \
  --reports json,html
```

Use machine-readable reports when you want to process detected technologies later.

---

## Fingerprinting and scan strategy

A detected technology can influence:

| Signal | Possible scan adjustment |
|---|---|
| CMS | Use CMS-specific wordlists |
| Static hosting | Focus on exposed files and deployment artifacts |
| CDN or edge provider | Enable WAF detection and safer request settings |
| Framework | Scan common framework routes and asset paths |
| Admin panel signal | Focus on auth and restricted resources |

---

## Recommended workflow

```shell
opendoor \
  --host https://example.com \
  --fingerprint \
  --auto-calibrate \
  --reports std,json
```

This gives a better initial view of the target before deeper scans.

---

## Notes

Fingerprinting is heuristic. Treat results as probable signals, not as guaranteed facts.

Always verify important findings manually.
