from django.utils.autoreload import DJANGO_AUTORELOAD_ENV
import os
import sys

def get_child_arguments():
    """自定义子进程参数，避免使用Cursor AppImage"""
    executable = sys.executable
    args = [executable] + sys.argv
    environ = {str(key): str(value) for key, value in os.environ.items()}
    return executable, args, environ 