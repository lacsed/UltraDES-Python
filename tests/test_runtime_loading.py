from pythonnet import get_runtime_info

import ultrades  # noqa: F401 - imports package and initializes pythonnet


def test_default_runtime_is_coreclr():
    assert get_runtime_info().kind == "CoreCLR"
