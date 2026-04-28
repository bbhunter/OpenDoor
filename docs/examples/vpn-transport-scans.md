# 🌐 VPN transport scans

OpenDoor supports proxy, OpenVPN, and WireGuard transport modes.

Use transport profiles only for authorized workflows.

---

## Proxy transport

```shell
opendoor \
  --host https://example.com \
  --transport proxy \
  --proxy socks5://127.0.0.1:9050
```

---

## OpenVPN transport

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./vpn/profile.ovpn
```

With `auth-user-pass`:

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./vpn/profile.ovpn \
  --openvpn-auth ./vpn/auth.txt
```

---

## WireGuard transport

```shell
opendoor \
  --host https://example.com \
  --transport wireguard \
  --transport-profile ./vpn/profile.conf
```

---

## Healthcheck

```shell
opendoor \
  --host https://example.com \
  --transport openvpn \
  --transport-profile ./vpn/profile.ovpn \
  --transport-healthcheck-url https://ifconfig.me
```

---

## Per-target rotation

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

## Secret hygiene

Never commit:

- real OpenVPN profiles;
- WireGuard private keys;
- VPN auth files;
- production proxy credentials;
- customer-specific transport routes.

Use placeholder examples only.
