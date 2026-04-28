# 🌐 Network transports

OpenDoor supports direct, proxy, OpenVPN, and WireGuard transport modes.

Transport options are useful when you need controlled network routing for authorized scanning workflows.

---

## Supported modes

| Mode | Purpose |
|---|---|
| `direct` | Use the default system network path |
| `proxy` | Route requests through a configured proxy |
| `openvpn` | Bring up an OpenVPN profile for the scan |
| `wireguard` | Bring up a WireGuard profile for the scan |

---

## Direct mode

```shell
opendoor --host https://example.com --transport direct
```

This is the default network path.

---

## Proxy mode

```shell
opendoor \
  --host https://example.com \
  --transport proxy \
  --proxy socks5://127.0.0.1:9050
```

---

## OpenVPN mode

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn
```

---

## WireGuard mode

```shell
opendoor \
  --host https://example.com \
  --transport wireguard \
  --transport-profile ./profile.conf
```

---

## Profile rotation

For batch scans, OpenDoor can rotate transport profiles per target:

```shell
opendoor \
  --hostlist targets.txt \
  --transport openvpn \
  --transport-profiles vpn-profiles.txt \
  --transport-rotate per-target
```

---

## Healthcheck

Use a healthcheck URL to validate transport connectivity:

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./profile.ovpn \
  --transport-healthcheck-url https://ifconfig.me
```

---

## Secret hygiene

Never commit real transport profiles or credentials.

Do not commit:

- WireGuard private keys;
- OpenVPN private keys;
- `auth-user-pass` files;
- production proxy credentials;
- customer-specific routing data.

Use placeholder examples only.
