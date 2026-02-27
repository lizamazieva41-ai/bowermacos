#!/bin/bash
# Chạy app với .venv_lib trên PYTHONPATH (dùng khi venv bị lỗi quyền, đã cài slowapi vào .venv_lib)
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/.venv_lib"
exec python main.py "$@"
