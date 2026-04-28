# 🧵 WireGuard transport

WireGuard transport brings up a WireGuard profile for the duration of a scan.

Use it only for authorized workflows and local profiles you control.

---

## Basic usage

```shell
opendoor \
  --host https://example.com \
  --transport wireguard \
  --transport-profile ./profile.conf
```

---

## Transport timeout

```shell
opendoor \
  --host https://example.com \
  --transport wireguard \
  --transport-profile ./profile.conf \
  --transport-timeout 60
```

---

## Healthcheck

```shell
opendoor \
  --host https://example.com \
  --transport wireguard \
  --transport-profile ./profile.conf \
  --transport-healthcheck-url https://ifconfig.me
```

---

## Multiple WireGuard profiles

Create `wireguard-profiles.txt`:

```text
./vpn/wg-1.conf
./vpn/wg-2.conf
./vpn/wg-3.conf
```

Run:

```shell
opendoor \
  --hostlist targets.txt \
  --transport wireguard \
  --transport-profiles wireguard-profiles.txt \
  --transport-rotate per-target
```

---

## Example profile

Use placeholder examples only.

```text
data/wireguard-profiles/example.conf
```

Never commit real WireGuard private keys or production profiles.

---

## Secret hygiene

A WireGuard profile can contain:

- private keys;
- peer endpoints;
- internal network details;
- DNS settings;
- routing rules.

Treat it as sensitive runtime configuration.
