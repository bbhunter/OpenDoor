# 🛡️ WAF detection and safe mode

OpenDoor can passively detect probable WAF, CDN, and anti-bot behavior.

Enable detection:

```shell
opendoor --host https://example.com --waf-detect
```

Enable safe mode:

```shell
opendoor --host https://example.com --waf-safe-mode
```

---

## What WAF detection does

WAF detection looks for signals that indicate protective infrastructure, such as:

- blocking responses;
- WAF-specific headers;
- CDN or edge infrastructure markers;
- suspicious response patterns;
- anti-bot behavior.

It is intended for safer scan classification and better operator awareness.

---

## Safe mode

Safe mode enables a more cautious runtime profile after WAF or anti-bot behavior is detected.

```shell
opendoor --host https://example.com --waf-safe-mode
```

Use safe mode when scanning authorized targets protected by:

- WAF;
- CDN;
- anti-bot middleware;
- rate limiting;
- managed edge security.

---

## Recommended WAF-safe scan

```shell
opendoor \
  --host https://example.com \
  --waf-safe-mode \
  --auto-calibrate \
  --timeout 60 \
  --retries 5 \
  --delay 0.5 \
  --reports json,html
```

---

## WAF detection with CI/CD

```shell
opendoor \
  --host https://example.com \
  --waf-detect \
  --reports json,sqlite
```

This can help track whether protective infrastructure behavior changed between releases.

---

## Responsible use

This feature is for detection and cautious scanning of authorized targets.

Do not use OpenDoor documentation or examples as a bypass guide for third-party systems.

---

## Troubleshooting

### Many blocked responses

Reduce scan pressure:

```shell
opendoor \
  --host https://example.com \
  --waf-safe-mode \
  --threads 3 \
  --delay 1 \
  --timeout 60
```

### Too much noise

Combine WAF detection with auto-calibration and response filters:

```shell
opendoor \
  --host https://example.com \
  --waf-safe-mode \
  --auto-calibrate \
  --exclude-status 404,429,500-599
```
