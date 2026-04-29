# 🧩 Header-bypass scans

This page contains practical Header Injection Bypass examples for authorized testing.

Header Injection Bypass is opt-in and probes blocked resources with temporary per-request headers.

---

## Basic header-bypass scan

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --header-bypass
```

By default, OpenDoor probes `401` and `403` responses.

---

## WAF-aware header-bypass scan

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --waf-detect \
  --waf-safe-mode \
  --header-bypass \
  --header-bypass-limit 32 \
  --reports std,json,csv,sqlite
```

Use this profile when testing authorized WAF-protected targets.

---

## Custom statuses and headers

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --header-bypass \
  --header-bypass-status 401,403 \
  --header-bypass-headers X-Original-URL,X-Rewrite-URL,X-Forwarded-For,X-Real-IP \
  --header-bypass-limit 32 \
  --reports json,html,sqlite
```

---

## Custom trusted IP values

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --header-bypass \
  --header-bypass-ips 127.0.0.1,10.0.0.1,192.168.1.1 \
  --reports json,csv
```

---

## CI/CD header-bypass gate

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --header-bypass \
  --reports json,sqlite,csv \
  --fail-on-bucket success,auth,forbidden,bypass
```

The `bypass` bucket can fail the pipeline when candidates are found.

---

## Recommended report formats

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --header-bypass \
  --reports std,json,csv,sqlite
```

Use:

- `std` for operator summary;
- `json` for full machine-readable metadata;
- `csv` for stable bypass columns;
- `sqlite` for structured local analysis.

---

## Notes

- Header-bypass probes are disabled by default.
- Probe headers are temporary per-request headers.
- Normal scan headers are not mutated.
- Use `--header-bypass-limit` to keep probe volume controlled.
- Use this only on systems you are authorized to test.
