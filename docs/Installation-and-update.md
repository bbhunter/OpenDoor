# 📦 Installation and update

OpenDoor is distributed as a Python CLI application. It can be installed with Homebrew, pipx, pip, or run directly from a source checkout.

For most users, the recommended installation methods are:

| Environment | Recommended method |
|---|---|
| macOS | Homebrew |
| General CLI usage | pipx |
| Existing Python environment | pip |
| Development | editable source install |
| Package verification | source build |

---

## 🍺 Homebrew

Homebrew is the recommended installation method for macOS users when the formula is available.

```shell
brew install opendoor
```

Verify the installation:

```shell
opendoor --version
opendoor --help
```

Update OpenDoor with Homebrew:

```shell
brew update
brew upgrade opendoor
```

If you maintain or use a custom tap, installation may look like this:

```shell
brew install stanislav-web/opendoor/opendoor
```

---

## 🧰 pipx

`pipx` installs Python CLI applications into isolated environments and exposes their commands globally. This is the recommended method for most non-Homebrew CLI users.

### Linux and macOS

```shell
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install opendoor
```

Verify:

```shell
opendoor --version
```

Update:

```shell
pipx upgrade opendoor
```

Uninstall:

```shell
pipx uninstall opendoor
```

### Windows PowerShell

Install Python first if it is not already available:

```powershell
winget install Python.Python.3
```

Install pipx:

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
```

Reopen PowerShell, then install OpenDoor:

```powershell
pipx install opendoor
opendoor --version
```

Update:

```powershell
pipx upgrade opendoor
```

---

## 🐍 pip

Use `pip` when you intentionally want OpenDoor installed into the current Python environment.

### Linux and macOS

```shell
python3 -m pip install --upgrade opendoor
opendoor --version
```

Update:

```shell
python3 -m pip install --upgrade opendoor
```

Uninstall:

```shell
python3 -m pip uninstall opendoor
```

### Windows PowerShell

```powershell
py -m pip install --upgrade pip
py -m pip install --upgrade opendoor
opendoor --version
```

Update:

```powershell
py -m pip install --upgrade opendoor
```

---

## 🧾 Run from source

Use this mode if you want to run OpenDoor directly from a source checkout without installing it as a package.

### Linux and macOS

```shell
git clone https://github.com/stanislav-web/OpenDoor.git
cd OpenDoor

python3 -m pip install -r requirements.txt
python3 opendoor.py --version
python3 opendoor.py --host https://example.com
```

### Windows PowerShell

```powershell
git clone https://github.com/stanislav-web/OpenDoor.git
cd OpenDoor

py -m pip install -r requirements.txt
py opendoor.py --version
py opendoor.py --host https://example.com
```

---

## 🛠️ Development installation

Use an editable installation when contributing to OpenDoor, running tests, or validating changes locally.

### Linux and macOS

```shell
git clone https://github.com/stanislav-web/OpenDoor.git
cd OpenDoor

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-dev.txt
python -m pip install -e .

opendoor --version
opendoor --help
```

### Windows PowerShell

```powershell
git clone https://github.com/stanislav-web/OpenDoor.git
cd OpenDoor

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-dev.txt
python -m pip install -e .

opendoor --version
opendoor --help
```

---

## 🏗️ Build from source

This flow is useful for maintainers, package builders, and release verification.

```shell
python3 -m pip install --upgrade build
python3 -m build
```

Generated artifacts are written to:

```text
dist/
```

Install a locally built wheel:

```shell
python3 -m pip install dist/opendoor-*.whl
```

Install a locally built source archive:

```shell
python3 -m pip install dist/opendoor-*.tar.gz
```

Do not hardcode old wheel filenames in scripts or documentation. Use the generated artifact names from `dist/`.

---

## 🧪 Verify runtime assets

A packaged OpenDoor installation should include the built-in configuration and dictionaries.

Useful verification commands:

```shell
opendoor --version
opendoor --help
```

For package maintainers, also verify that the installed package includes runtime assets such as:

```text
opendoor.conf
data/directories.dat
data/subdomains.dat
data/useragents.dat
data/proxies.dat
data/ignored.dat
```

Transport profile examples are examples only. Never distribute real OpenVPN or WireGuard credentials, private keys, or production profiles.

---

## 🔄 Update strategy

Use the same package manager that installed OpenDoor.

| Installed with | Update command |
|---|---|
| Homebrew | `brew update && brew upgrade opendoor` |
| pipx | `pipx upgrade opendoor` |
| pip | `python3 -m pip install --upgrade opendoor` |
| Source checkout | `git pull` and reinstall dependencies if needed |

---

## 🧯 Common issues

### `mkdocs: command not found`

This is relevant only when building documentation locally. Install documentation dependencies in a virtual environment:

```shell
python3 -m venv .docs-venv
source .docs-venv/bin/activate
python -m pip install -r docs/requirements.txt
python -m mkdocs build --strict
```

### `externally-managed-environment`

Some Python distributions, including Homebrew Python, prevent global `pip install` into the system environment.

Use a virtual environment, pipx, or Homebrew instead of forcing installation into the system Python.

Do not use `--break-system-packages` unless you fully understand the risk.

### Command not found after installation

Check that your package manager's binary directory is in `PATH`.

For pipx:

```shell
python3 -m pipx ensurepath
```

Then reopen the terminal.
