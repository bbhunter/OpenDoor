# 🔐 OpenVPN transport

OpenVPN transport brings up an OpenVPN profile for the duration of a scan.

Use it only for authorized workflows and local profiles you control.

---

## Basic usage

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn
```

---

## Username/password auth

For OpenVPN profiles that require `auth-user-pass`, provide an auth file:

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn \
  --openvpn-auth ./auth.txt
```

Example `auth.txt` format:

```text
username
password
```

Do not commit `auth.txt`.

---

## Transport timeout

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn \
  --transport-timeout 60
```

---

## Healthcheck

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn \
  --transport-healthcheck-url https://ifconfig.me
```

---

## Multiple OpenVPN profiles

Create `vpn-profiles.txt`:

```text
./vpn/profile-1.ovpn
./vpn/profile-2.ovpn
./vpn/profile-3.ovpn
```

Run:

```shell
opendoor \
  --hostlist targets.txt \
  --transport openvpn \
  --transport-profiles vpn-profiles.txt \
  --transport-rotate per-target
```

---

## Example profile

Use placeholder examples only.

```text
data/openvpn-profiles/example.ovpn
```

Never commit real OpenVPN profiles, private keys, or auth files.
