#!/usr/bin/env bash
# 局域网健康数据安全自检：仅用独立 SQLite 文件，不写生产库 backend/data/family_health.db。
# 若环境里 pytest-metadata 等与 sys.executable 冲突，可先关闭三方插件：
#   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=.
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"
python3 -m pytest tests/test_security.py "${@}"
