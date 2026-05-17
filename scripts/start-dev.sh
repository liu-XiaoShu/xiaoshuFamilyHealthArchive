#!/usr/bin/env bash
# 一键启动后端（8000）+ 前端开发（5173），便于局域网测试含 CSV 上传。
# 用法：在项目根目录执行  ./scripts/start-dev.sh
# 可选：./scripts/start-dev.sh --reset-admin-password   # 重置管理员口令为默认值（须配合 FH_ADMIN_PASSWORD）
# 环境变量 PYTHON_BIN=/usr/bin/python3.8 可指定 Python。

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FH_FORCE_RESET_ADMIN_FLAG=0
for _arg in "$@"; do
  if [[ "${_arg}" == "--reset-admin-password" || "${_arg}" == "--force-reset-password" ]]; then
    FH_FORCE_RESET_ADMIN_FLAG=1
  fi
done
if [[ "${FH_FORCE_RESET_ADMIN_FLAG}" -eq 1 ]]; then
  export FH_FORCE_RESET_ADMIN=1
  echo "WARN: FH_FORCE_RESET_ADMIN=1 — 将把管理员口令重置为 FH_ADMIN_PASSWORD（未设置则用默认）；启动后请及时修改。"
fi

kill_tcp_port() {
  local port="$1"
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" 2>/dev/null || true
  fi
  local p
  p="$(lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${p}" ]]; then
    # shellcheck disable=SC2086
    kill ${p} 2>/dev/null || true
  fi
}

PYBIN="${PYTHON_BIN:-}"
if [[ -z "${PYBIN}" ]]; then
  if command -v python3 >/dev/null 2>&1; then PYBIN=python3
  elif command -v python3.8 >/dev/null 2>&1; then PYBIN=python3.8
  else PYBIN=python3
  fi
fi

# 将常见 Node 安装目录加入 PATH（未装到系统 PATH 时仍可启动前端）
for _node_dir in \
  "${NODE_HOME:-}" \
  "${HOME}/.local/node/bin" \
  "${NVM_DIR:-$HOME/.nvm}/versions/node/$(cat "${NVM_DIR:-$HOME/.nvm}/alias/default" 2>/dev/null)/bin"; do
  if [[ -n "${_node_dir}" && -x "${_node_dir}/npm" ]]; then
    export PATH="${_node_dir}:${PATH}"
    break
  fi
done

if ! command -v npm >/dev/null 2>&1; then
  echo "错误: 未找到 npm（Node.js）。前端无法启动。" >&2
  echo "  请先安装 Node.js LTS（建议 20+），并在 frontend 目录执行: npm install" >&2
  echo "  安装示例: nvm install --lts  或  https://nodejs.org/" >&2
  echo "  若已安装到自定义目录: export PATH=\"/path/to/node/bin:\$PATH\"" >&2
  exit 1
fi

NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)"
if [[ "${NODE_MAJOR}" -lt 18 ]]; then
  echo "错误: Node.js 版本过低（当前 $(node -v)，需要 >= 18，Vite 6 无法运行）。" >&2
  echo "  Ubuntu 自带 nodejs 常为 10.x，请改用 LTS：nvm install --lts  或安装到 ~/.local/node" >&2
  exit 1
fi

echo "== 释放端口 8000、5173（如有占用）…"
kill_tcp_port 8000
kill_tcp_port 5173
sleep 1

echo "== 启动后端 FastAPI → 0.0.0.0:8000"
(
  cd "${ROOT}/backend"
  PYTHONPATH=. exec "${PYBIN}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
) &
BACK_PID=$!

echo "== 启动前端 Vite → 0.0.0.0:5173（含 /api 代理）"
(
  cd "${ROOT}/frontend"
  exec npm run dev
) &
FRONT_PID=$!

cleanup() {
  echo ""
  echo "== 停止进程…"
  kill "${FRONT_PID}" "${BACK_PID}" 2>/dev/null || true
  kill_tcp_port 5173
  kill_tcp_port 8000
}
trap cleanup EXIT INT TERM

echo ""
echo "  后端健康检查: http://127.0.0.1:8000/api/health"
echo "  前端开发页:   http://127.0.0.1:5173"
echo "  局域网访问:   http://本机局域网IP:5173（上传 CSV 走代理到后端）"
echo "  仅后端+静态:  先 cd frontend && npm run build，再单独起后端，浏览器打开 http://IP:8000"
echo ""
echo "按 Ctrl+C 停止前后端。"
echo ""

wait
