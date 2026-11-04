"""UltraDES Python package initialization."""
from __future__ import annotations

import os
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
import sys
from typing import Optional

_RUNTIME_ENV_VAR = "ULTRADES_RUNTIME"
_PACKAGE_DIR = Path(__file__).resolve().parent
_ULTRADES_DLL = _PACKAGE_DIR / "UltraDES.dll"
_DLL_DIRECTORY_HANDLE = None
_NUGET_CONTAINER = "https://api.nuget.org/v3-flatcontainer"


def _ensure_ultrades_dll() -> None:
    """Fetch the UltraDES assembly from NuGet on first use."""
    if _ULTRADES_DLL.exists():
        return
    package = os.environ.get("ULTRADES_NUGET_PACKAGE", "UltraDES")
    version = os.environ.get("ULTRADES_NUGET_VERSION")
    headers = {"User-Agent": "UltraDES-Python"}
    if not version:
        url = f"{_NUGET_CONTAINER}/{package.lower()}/index.json"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            versions = json.loads(response.read().decode("utf-8")).get("versions", [])
        if not versions:
            raise RuntimeError(f"No NuGet versions found for {package!r}")
        version = versions[-1]
    url = f"{_NUGET_CONTAINER}/{package.lower()}/{version.lower()}/{package.lower()}.{version.lower()}.nupkg"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    with zipfile.ZipFile(__import__("io").BytesIO(payload)) as archive:
        candidates = [n for n in archive.namelist() if n.replace("\\", "/").lower().endswith("/ultrades.dll")]
        if not candidates:
            raise RuntimeError(f"UltraDES.dll was not found in NuGet package {package} {version}")
        selected = sorted(candidates, key=lambda n: ("netstandard2.0" not in n.lower(), n.lower()))[0]
        _PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=_PACKAGE_DIR, delete=False) as target:
            temp_path = Path(target.name)
            with archive.open(selected) as source:
                shutil.copyfileobj(source, target)
    temp_path.replace(_ULTRADES_DLL)


def _add_package_dir_to_loader_path() -> None:
    """Make the packaged .NET assembly discoverable on Windows, macOS and Linux."""

    global _DLL_DIRECTORY_HANDLE
    package_dir = str(_PACKAGE_DIR)
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    # Python 3.8+ on Windows no longer searches PATH for DLL dependencies.
    # Keeping this handle alive preserves the directory for the process.
    if os.name == "nt" and hasattr(os, "add_dll_directory"):
        _DLL_DIRECTORY_HANDLE = os.add_dll_directory(package_dir)


def _load_pythonnet_runtime() -> None:
    """Ensure the pythonnet runtime is loaded.

    ``ULTRADES_RUNTIME`` can force a pythonnet runtime (for example ``mono`` on
    older Unix installations).  Without an explicit preference we try CoreCLR
    first, then Mono, so notebooks on Windows, macOS and Linux get a useful
    fallback without pythonnet defaulting to Mono on Linux.
    """

    _add_package_dir_to_loader_path()
    last_error: Optional[Exception] = None

    try:
        from pythonnet import load  # type: ignore
    except ImportError as exc:  # pragma: no cover - pythonnet is a hard dependency
        raise ImportError("pythonnet is required to use the ultrades package") from exc

    runtime_preference: Optional[str] = os.environ.get(_RUNTIME_ENV_VAR)
    runtime_candidates = [runtime_preference] if runtime_preference else []
    runtime_candidates.extend(["coreclr", "mono"])

    for candidate in runtime_candidates:
        if not candidate:
            continue
        try:
            load(candidate)
            break
        except Exception as exc:  # pragma: no cover - depends on environment
            last_error = exc
            if "already" in str(exc).lower():
                try:
                    import clr  # type: ignore  # noqa: F401
                    return
                except Exception:
                    pass
    else:
        raise RuntimeError(
            "Unable to load a pythonnet runtime. Set ULTRADES_RUNTIME=coreclr or "
            f"ULTRADES_RUNTIME=mono to choose one explicitly. Last error: {last_error}"
        )

    import clr  # type: ignore  # noqa: F401


def add_ultrades_reference() -> None:
    """Load the packaged UltraDES assembly with an absolute-path fallback."""

    _add_package_dir_to_loader_path()
    _ensure_ultrades_dll()
    import clr  # type: ignore

    try:
        clr.AddReference("UltraDES")
    except Exception:
        if not _ULTRADES_DLL.exists():
            raise FileNotFoundError(
                f"UltraDES assembly not found at {_ULTRADES_DLL}. Reinstall the package "
                "or build it with network access so setup.py can fetch the NuGet package."
            )
        clr.AddReference(str(_ULTRADES_DLL))


_load_pythonnet_runtime()

__all__ = ["add_ultrades_reference", "automata", "petrinets"]
