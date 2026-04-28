# 🧪 CI/CD examples

OpenDoor can be used in CI/CD pipelines as an exposure check or regression gate.

---

## Basic CI command

```shell
opendoor \
  --host https://example.com \
  --reports json,sqlite
```

---

## Fail on selected buckets

```shell
opendoor \
  --host https://example.com \
  --fail-on-bucket success,auth,forbidden
```

OpenDoor completes the scan and exits with code `1` if selected result buckets are found.

---

## Low-noise CI gate

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --auto-calibrate \
  --include-status 200-299,301,302,403 \
  --exclude-status 404,429,500-599 \
  --reports json,sqlite \
  --fail-on-bucket success,auth,forbidden
```

---

## Batch CI gate

```shell
opendoor \
  --hostlist targets.txt \
  --auto-calibrate \
  --reports json,sqlite \
  --fail-on-bucket success,auth,forbidden
```

---

## GitHub Actions example

```yaml
name: OpenDoor exposure check

on:
  workflow_dispatch:
  schedule:
    - cron: "0 3 * * *"

jobs:
  opendoor:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install OpenDoor
        run: |
          python3 -m pip install --user pipx
          python3 -m pipx ensurepath
          pipx install opendoor

      - name: Run OpenDoor
        run: |
          opendoor \
            --host https://example.com \
            --method GET \
            --auto-calibrate \
            --reports json,sqlite \
            --reports-dir ./reports \
            --fail-on-bucket success,auth,forbidden

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: opendoor-reports
          path: reports/
```

---

## GitLab CI example

```yaml
opendoor:
  image: python:3.13
  script:
    - python -m pip install --upgrade pip pipx
    - python -m pipx ensurepath
    - pipx install opendoor
    - |
      opendoor \
        --host https://example.com \
        --method GET \
        --auto-calibrate \
        --reports json,sqlite \
        --reports-dir ./reports \
        --fail-on-bucket success,auth,forbidden
  artifacts:
    when: always
    paths:
      - reports/
```

---

## CI safety notes

Do not put secrets directly in repository workflows.

Use CI secret stores for:

- tokens;
- cookies;
- authenticated raw requests;
- proxy credentials;
- VPN credentials.

Do not upload public artifacts containing sensitive findings.
