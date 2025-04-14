#!/bin/bash

# 激活虚拟环境
source ../.venv/bin/activate

# 设置环境变量
export PYTHONPATH=/home/liushk/work/github/xiaoshuHomeHealth/backend
export DJANGO_SETTINGS_MODULE=backend.settings
export DJANGO_AUTORELOAD_COMMAND=$(which python3)

# 启动服务器
exec python3 manage.py runserver 0.0.0.0:8000 