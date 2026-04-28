# 🛡️ WAF-safe scans

This page shows cautious scan profiles for authorized targets protected by WAF, CDN, anti-bot, or rate-limiting infrastructure.

---

## Basic WAF detection

```shell
opendoor --host https://example.com --waf-detect
```

---

## Safe mode

```shell
opendoor --host https://example.com --waf-safe-mode
```

Safe mode enables a more cautious scan profile after probable WAF or anti-bot behavior is detected.

---

## WAF-safe low-pressure scan

```shell
opendoor \
  --host https://example.com \
  --waf-safe-mode \
  --method GET \
  --threads 3 \
  --delay 1 \
  --timeout 60 \
  --retries 5 \
  --auto-calibrate \
  --reports json,html
```

---

## WAF-safe scan with filters

```shell
opendoor \
  --host https://example.com \
  --waf-safe-mode \
  --method GET \
  --include-status 200-299,301,302,403 \
  --exclude-status 404,429,500-599 \
  --exclude-size-range 0-256 \
  --reports json,sqlite
```

---

## WAF-safe CI profile

```shell
opendoor \
  --host https://example.com \
  --waf-safe-mode \
  --auto-calibrate \
  --reports json,sqlite \
  --fail-on-bucket success,auth,forbidden
```

---

## Notes

WAF detection is for classification and safer authorized scanning.

Do not treat these examples as bypass guidance for third-party systems.
