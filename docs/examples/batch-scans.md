# 🎯 Batch scans

Batch scans are useful when you need to scan multiple targets from a file or pipeline.

---

## Target file

Create `targets.txt`:

```text
https://example.com
https://app.example.com
https://admin.example.com
example.org
```

Run:

```shell
opendoor --hostlist targets.txt
```

---

## Batch scan with reports

```shell
opendoor \
  --hostlist targets.txt \
  --reports json,sqlite \
  --reports-dir ./reports
```

Use `json` and `sqlite` for batch processing and later analysis.

---

## Batch scan with auto-calibration

```shell
opendoor \
  --hostlist targets.txt \
  --method GET \
  --auto-calibrate \
  --reports json,sqlite
```

Use this when targets are likely to return soft-404 or catch-all pages.

---

## Batch scan from stdin

```shell
cat targets.txt | opendoor --stdin
```

Pipeline example:

```shell
cat targets.txt | grep example.com | opendoor --stdin --reports json
```

---

## Batch scan with CI fail-on

```shell
opendoor \
  --hostlist targets.txt \
  --auto-calibrate \
  --reports json,sqlite \
  --fail-on-bucket success,auth,forbidden
```

OpenDoor completes the scan and exits with code `1` if selected buckets are found.

---

## Batch scan with sessions

```shell
opendoor \
  --hostlist targets.txt \
  --session-save batch.session \
  --session-autosave-sec 30 \
  --reports json,sqlite
```

Resume later:

```shell
opendoor --session-load batch.session
```

---

## Batch scan with transport rotation

```shell
opendoor \
  --hostlist targets.txt \
  --transport openvpn \
  --transport-profiles vpn-profiles.txt \
  --transport-rotate per-target
```

Use this only for authorized workflows where transport routing is expected.
