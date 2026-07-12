from pathlib import Path


def test_packaging_declares_modern_build_backend_and_dll_manifest():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    manifest = Path("MANIFEST.in").read_text(encoding="utf-8")
    setup_py = Path("setup.py").read_text(encoding="utf-8")

    assert "setuptools.build_meta" in pyproject
    assert "include ultrades/UltraDES.dll" in manifest
    assert 'license="MIT"' in setup_py
    assert 'package_data={"ultrades": [ASSEMBLY_NAME]}' in setup_py
