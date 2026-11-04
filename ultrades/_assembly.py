"""NuGet assembly download and per-user cache management."""
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import urllib.request
import zipfile

_FLAT = "https://api.nuget.org/v3-flatcontainer"


def _version_key(version):
    release, _, pre = version.split("+", 1)[0].partition("-")
    return (tuple(int(p) if p.isdigit() else p.lower() for p in release.split(".")), not bool(pre))


def _cache_root():
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "UltraDES" / "assemblies"
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "ultrades" / "assemblies"


def _fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "UltraDES-Python"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def ensure_assembly():
    package = os.environ.get("ULTRADES_NUGET_PACKAGE", "UltraDES")
    requested = os.environ.get("ULTRADES_NUGET_VERSION")
    versions = json.loads(_fetch(f"{_FLAT}/{package.lower()}/index.json", 30)).get("versions", [])
    version = requested or (sorted((v for v in versions if "-" not in v), key=_version_key)[-1] if versions else None)
    if not version:
        raise RuntimeError(f"No stable NuGet versions found for {package!r}")
    target = _cache_root() / package.lower() / version.lower() / "UltraDES.dll"
    if target.is_file() and target.stat().st_size:
        return target
    payload = _fetch(f"{_FLAT}/{package.lower()}/{version.lower()}/{package.lower()}.{version.lower()}.nupkg", 60)
    with zipfile.ZipFile(__import__("io").BytesIO(payload)) as archive:
        members = [n for n in archive.namelist() if n.replace("\\", "/").lower().endswith("/ultrades.dll")]
        if not members:
            raise RuntimeError(f"UltraDES.dll was not found in NuGet package {package} {version}")
        selected = min(members, key=lambda n: ("netstandard2.0" not in n.lower(), n.lower()))
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as out:
            temp = Path(out.name)
            with archive.open(selected) as source:
                shutil.copyfileobj(source, out)
    temp.replace(target)
    return target
