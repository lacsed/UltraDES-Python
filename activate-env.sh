#!/usr/bin/env bash
# Source this file from UltraDES-Python to activate its local Python/.NET setup.
_ultrades_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DOTNET_ROOT="${_ultrades_dir}/../.dotnet"
export PATH="${DOTNET_ROOT}:${_ultrades_dir}/.venv/bin:${PATH}"
export PYTHONPATH="${_ultrades_dir}${PYTHONPATH:+:${PYTHONPATH}}"
unset _ultrades_dir
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.venv/bin/activate"
