# 🧠 Auto-calibration

Auto-calibration helps reduce false positives from soft-404, wildcard, and catch-all responses.

Enable it with:

```shell
opendoor --host https://example.com --auto-calibrate
```

---

## Why auto-calibration exists

Many modern applications return successful-looking responses for invalid paths.

Examples:

- a custom 404 page with status `200`;
- a single-page app fallback;
- wildcard routing;
- CDN fallback pages;
- repeated login redirects;
- catch-all framework routes.

Without calibration, these responses can look like valid findings.

---

## Basic usage

```shell
opendoor --host https://example.com --auto-calibrate
```

For body-based classification, use `GET`:

```shell
opendoor --host https://example.com --method GET --auto-calibrate
```

---

## Calibration samples

```shell
opendoor --host https://example.com --auto-calibrate --calibration-samples 8
```

More samples can improve baseline quality on noisy targets, but may add startup time.

---

## Calibration threshold

```shell
opendoor --host https://example.com --auto-calibrate --calibration-threshold 0.85
```

The threshold accepts values from `0.01` to `1.0`.

Higher values make matching stricter. Lower values make matching more tolerant.

---

## Recommended workflow

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --auto-calibrate \
  --calibration-samples 8 \
  --calibration-threshold 0.85 \
  --include-status 200-299,301,302,403 \
  --exclude-status 404,429,500-599
```

---

## Auto-calibration and sessions

For long scans, combine auto-calibration with sessions:

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --auto-calibrate \
  --session-save scan.session
```

Resume:

```shell
opendoor --session-load scan.session
```

---

## Auto-calibration vs sniffers

| Feature | Purpose |
|---|---|
| Auto-calibration | Baseline-based detection of soft-404/wildcard/catch-all responses |
| Sniffers | Built-in heuristics for known response patterns |
| Response filters | Explicit user-defined rules |

A practical low-noise scan can use all three:

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --auto-calibrate \
  --sniff skipempty,collation,indexof,file \
  --exclude-size-range 0-256
```

## Semantic response diffing

OpenDoor 5.14.3 extends auto-calibration with lightweight semantic response-diff signals.

When `--auto-calibrate` is enabled, calibration signatures include:

- normalized visible text;
- known soft-404 phrases;
- stable semantic terms;
- bounded DOM-tag tokens;
- content kind (`html`, `json`, `text`, or `empty`);
- visible-text density;
- existing status, bucket, size, title, redirect, body hash, skeleton hash, word count, line count, and stable headers.

This helps detect dynamic soft-404 templates where the HTML wrapper changes but the response has the same meaning, such as “page not found”, “requested resource does not exist”, changing trace IDs, CSRF-like values, timestamps, or path echoes.

The feature is part of the existing `--auto-calibrate` flow. It does not run unless auto-calibration is explicitly enabled.

## DNS wildcard calibration

OpenDoor 5.14.4 extends auto-calibration for subdomain scans.

```shell
opendoor --host example.com --scan subdomains --auto-calibrate
```

When this mode is enabled, OpenDoor generates random impossible subdomains under the target domain and resolves them before the scan. If at least two random subdomains resolve, their addresses become the DNS wildcard baseline.

During subdomain scanning, candidates that resolve only to those wildcard baseline addresses are classified into the `calibrated` bucket before HTTP probing. Candidates that resolve to different addresses are scanned normally.

This remains opt-in and only runs when both options are present:

- `--scan subdomains`
- `--auto-calibrate`

