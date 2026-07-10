"""UltraDES Python package initialization."""
from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Optional

_RUNTIME_ENV_VAR = "ULTRADES_RUNTIME"
_PACKAGE_DIR = Path(__file__).resolve().parent
_ULTRADES_DLL = _PACKAGE_DIR / "UltraDES.dll"
_DLL_DIRECTORY_HANDLE = None


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

    ``ULTRADES_RUNTIME`` can force a pythonnet runtime (for example ``coreclr``
    in Google Colab/Jupyter images or ``mono`` on older Unix installations).
    Without an explicit preference we try the default import first, then Mono,
    then CoreCLR so notebooks on Windows, macOS and Linux get a useful fallback.
    """

    _add_package_dir_to_loader_path()

    try:
        import clr  # type: ignore  # noqa: F401 - imported for its side effect
        return
    except ImportError:
        pass

    try:
        from pythonnet import load  # type: ignore
    except ImportError as exc:  # pragma: no cover - pythonnet is a hard dependency
        raise ImportError("pythonnet is required to use the ultrades package") from exc

    runtime_preference: Optional[str] = os.environ.get(_RUNTIME_ENV_VAR)
    runtime_candidates = [runtime_preference] if runtime_preference else []
    runtime_candidates.extend(["mono", "coreclr"])

    last_error: Optional[Exception] = None
    for candidate in runtime_candidates:
        if not candidate:
            continue
        try:
            load(candidate)
            break
        except Exception as exc:  # pragma: no cover - depends on environment
            last_error = exc
    else:
        raise RuntimeError(
            "Unable to load a pythonnet runtime. Set ULTRADES_RUNTIME=coreclr or "
            f"ULTRADES_RUNTIME=mono to choose one explicitly. Last error: {last_error}"
        )

    import clr  # type: ignore  # noqa: F401


def add_ultrades_reference() -> None:
    """Load the packaged UltraDES assembly with an absolute-path fallback."""

    _add_package_dir_to_loader_path()
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
