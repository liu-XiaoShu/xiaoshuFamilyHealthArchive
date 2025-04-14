#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # 设置环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    os.environ.setdefault('DJANGO_ENV', 'development')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 如果是runserver命令且没有--noreload参数，则添加--noreload参数
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and '--noreload' not in sys.argv:
        sys.argv.append('--noreload')
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
