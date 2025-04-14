#!/bin/bash

# 设置环境变量
export DJANGO_ENV=development
export PYTHONPATH=/home/liushk/work/github/xiaoshuHomeHealth/backend
export DJANGO_SETTINGS_MODULE=backend.settings

# 启动服务器（禁用自动重载）
python3 manage.py runserver 0.0.0.0:8000 --noreload
