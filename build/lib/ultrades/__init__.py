"""UltraDES Python package initialization."""
from __future__ import annotations

import os
from typing import Optional
import sys, ultrades, os
sys.path.append(os.path.dirname(ultrades.__file__))

_RUNTIME_ENV_VAR = "ULTRADES_RUNTIME"


def _load_pythonnet_runtime() -> None:
    """Ensure the pythonnet runtime is loaded.

    The package historically relied on Mono being available. When running on
    environments such as Google Colab Mono is usually absent and pythonnet must
    be explicitly instructed to use the ``coreclr`` runtime.  This helper tries
    to import :mod:`clr` directly, loading Mono by default when available.  If
    the import fails we progressively fall back to ``mono`` and then ``coreclr``
    using :func:`pythonnet.load`.
    """

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

    # First try Mono (the historical dependency).  If it fails we attempt
    # CoreCLR which is available on platforms such as Google Colab.
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
            "Unable to load a pythonnet runtime. Last error: %s" % last_error
        )

    # Import clr after a runtime has been loaded so it is available for the
    # rest of the package.
    import clr  # type: ignore  # noqa: F401


_load_pythonnet_runtime()

__all__ = ["automata", "petrinets"]
