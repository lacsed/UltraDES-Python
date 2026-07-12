"""Packaging helpers for UltraDES-Python.

The Python wrapper needs the managed UltraDES assembly.  During build we try to
fetch the newest UltraDES package from NuGet and copy its DLL into the Python
package.  If the network is unavailable (common in some CI/offline notebooks),
the repository-bundled DLL is kept as a fallback.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import urllib.request
import zipfile

import setuptools
from setuptools.command.build_py import build_py as _build_py

PACKAGE_DIR = Path(__file__).parent / "ultrades"
ASSEMBLY_NAME = "UltraDES.dll"
NUGET_PACKAGE_ID = os.environ.get("ULTRADES_NUGET_PACKAGE", "UltraDES")
NUGET_VERSION = os.environ.get("ULTRADES_NUGET_VERSION")
NUGET_FLAT_CONTAINER = "https://api.nuget.org/v3-flatcontainer"


def _version_key(version: str) -> tuple:
    """Return a sortable key for NuGet semantic versions without extra deps."""

    public_version = version.split("+", 1)[0]
    release, separator, prerelease = public_version.partition("-")
    release_key = tuple(int(part) if part.isdigit() else part for part in release.split("."))
    prerelease_key = tuple(
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"[.-]", prerelease)
        if part
    )
    return (release_key, separator == "", prerelease_key)


def _read_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "UltraDES-Python setup.py"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _latest_nuget_version(package_id: str) -> str:
    index_url = f"{NUGET_FLAT_CONTAINER}/{package_id.lower()}/index.json"
    versions = _read_json(index_url).get("versions", [])
    if not versions:
        raise RuntimeError(f"No NuGet versions found for {package_id!r}")
    return sorted(versions, key=_version_key)[-1]


def _select_assembly(candidates: list[str]) -> str:
    """Choose the most portable UltraDES.dll from a NuGet package."""

    preferred_frameworks = (
        "netstandard2.0",
        "netstandard2.1",
        "net8.0",
        "net7.0",
        "net6.0",
        "net5.0",
        "netcoreapp",
        "net48",
        "net472",
        "net461",
        "net45",
    )

    def score(path: str) -> tuple[int, int, str]:
        lowered = path.lower().replace("\\", "/")
        framework_score = next(
            (index for index, framework in enumerate(preferred_frameworks) if f"/{framework}" in lowered),
            len(preferred_frameworks),
        )
        # Prefer lib/ assemblies over build/analyzers/tools content.
        location_score = 0 if lowered.startswith("lib/") else 1
        return (framework_score, location_score, lowered)

    return sorted(candidates, key=score)[0]


def download_ultrades_from_nuget(destination: Path) -> str:
    """Download UltraDES.dll from NuGet into *destination* and return version."""

    package_id = NUGET_PACKAGE_ID
    version = NUGET_VERSION or _latest_nuget_version(package_id)
    package_url = (
        f"{NUGET_FLAT_CONTAINER}/{package_id.lower()}/{version.lower()}/"
        f"{package_id.lower()}.{version.lower()}.nupkg"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        nupkg_path = Path(tmpdir) / f"{package_id}.{version}.nupkg"
        request = urllib.request.Request(package_url, headers={"User-Agent": "UltraDES-Python setup.py"})
        with urllib.request.urlopen(request, timeout=60) as response:
            nupkg_path.write_bytes(response.read())

        with zipfile.ZipFile(nupkg_path) as archive:
            candidates = [
                name
                for name in archive.namelist()
                if name.replace("\\", "/").lower().endswith(f"/{ASSEMBLY_NAME.lower()}")
            ]
            if not candidates:
                raise RuntimeError(f"{ASSEMBLY_NAME} was not found in {package_id} {version}")
            selected = _select_assembly(candidates)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(selected) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
    return version


class build_py(_build_py):
    """Download the current UltraDES assembly before building Python modules."""

    def run(self) -> None:
        destination = PACKAGE_DIR / ASSEMBLY_NAME
        if os.environ.get("ULTRADES_SKIP_NUGET_DOWNLOAD") == "1":
            self.announce("Skipping UltraDES NuGet download by request", level=2)
        else:
            try:
                version = download_ultrades_from_nuget(destination)
                self.announce(f"Downloaded {NUGET_PACKAGE_ID} {version} from NuGet", level=2)
            except Exception as exc:
                if not destination.exists():
                    raise RuntimeError(
                        "Unable to download UltraDES.dll from NuGet and no bundled fallback exists. "
                        "Set ULTRADES_NUGET_VERSION to a known version or provide ultrades/UltraDES.dll."
                    ) from exc
                self.announce(
                    f"Warning: could not download UltraDES from NuGet ({exc}); using bundled {destination}",
                    level=3,
                )
        super().run()


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ultrades-python",
    version="0.0.7",
    author="LACSED Developers",
    author_email="lacsed.ufmg@gmail.com",
    description="A library for analysis and control of Discrete Event Systems",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lacsed/ultrades",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pycparser",
        "pythonnet>=3.0.0",
        "ipython",
    ],
    package_data={"ultrades": [ASSEMBLY_NAME]},
    include_package_data=True,
    cmdclass={"build_py": build_py},
    python_requires=">=3.8",
)
