# 🧾 Authenticated scans

OpenDoor can scan authenticated areas when you provide the required headers, cookies, or raw HTTP request.

Use authenticated scans only on systems you own or have explicit permission to test.

---

## Cookie-based scan

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --cookie "sid=abc123" \
  --auto-calibrate \
  --reports json,html
```

Do not commit real cookies.

---

## Header-based scan

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --header "Authorization: Bearer TOKEN" \
  --reports json,html
```

Do not commit real bearer tokens.

---

## Multiple headers

```shell
opendoor \
  --host https://example.com \
  --method GET \
  --header "Authorization: Bearer TOKEN" \
  --header "X-Tenant: demo" \
  --header "X-Test: 1"
```

---

## Raw HTTP request

Save a request as `request.txt`:

```http
GET /admin HTTP/1.1
Host: example.com
User-Agent: OpenDoor
Cookie: sid=abc123
```

Run:

```shell
opendoor --raw-request request.txt --scheme https
```

---

## Raw request with filters

```shell
opendoor \
  --raw-request request.txt \
  --scheme https \
  --method GET \
  --auto-calibrate \
  --match-regex "admin|dashboard|profile" \
  --reports json,html
```

---

## Safe handling

Authenticated scans can expose sensitive results.

Do not commit:

- raw request files;
- session cookies;
- bearer tokens;
- private headers;
- generated reports with sensitive findings.

Use local ignored files or CI secrets where appropriate.
