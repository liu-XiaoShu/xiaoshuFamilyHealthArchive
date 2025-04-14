"""
WSGI配置
为项目提供Web服务器网关接口
"""

import os
from django.core.wsgi import get_wsgi_application

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 初始化Django WSGI应用
application = get_wsgi_application()

# 添加Whitenoise静态文件支持（可选）
if os.environ.get('USE_WHITENOISE', 'False') == 'True':
    from whitenoise import WhiteNoise
    application = WhiteNoise(
        application,
        root=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
        prefix='/static/'
    )

# ------------------------- 生产环境扩展配置 -------------------------
if os.environ.get('ENV') == 'production':
    # 安全头中间件（需安装django-secure）
    from secure.middleware import SecureMiddleware
    application = SecureMiddleware(application)
    # GZip压缩中间件
    from django.middleware.gzip import GZipMiddleware
    application = GZipMiddleware(application)
    # 请求日志中间件
    from django_requests_logger.middleware import RequestsLoggerMiddleware
    application = RequestsLoggerMiddleware(application)

# ------------------------- 开发环境扩展配置 -------------------------
if os.environ.get('DEBUG') == 'True':
    # 自动重载中间件（开发服务器自带，无需单独配置）
    pass

# ------------------------- 性能优化配置 -------------------------
# 预热Django ORM（首次请求前初始化）
try:
    from django.db import connection
    connection.ensure_connection()
except Exception as e:
    print(f"数据库连接预热失败: {str(e)}")

# ------------------------- 监控集成配置 -------------------------
if os.environ.get('ENABLE_METRICS'):
    # Prometheus监控中间件（需安装django-prometheus）
    from prometheus_client import make_wsgi_app
    from django.urls import path
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    application = DispatcherMiddleware(application, {
        '/metrics': make_wsgi_app()
    })

# ------------------------- 扩展配置建议 -------------------------
"""
可选扩展配置（按需取消注释）：
1. Sentry错误监控：
   from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
   application = SentryWsgiMiddleware(application)

2. 请求限流：
   from slowapi.middleware import LimiterMiddleware
   application = LimiterMiddleware(application)

3. 缓存中间件：
   from django.middleware.cache import CacheMiddleware
   application = CacheMiddleware(application)

4. 内容安全策略：
   from csp.middleware import CSPMiddleware
   application = CSPMiddleware(application)
"""

# ------------------------- WSGI服务器配置示例 -------------------------
"""
Gunicorn启动命令（建议生产环境使用）：
gunicorn backend.wsgi:application \
  --workers=4 \
  --bind=0.0.0.0:8000 \
  --timeout=120 \
  --access-logfile=-
uWSGI配置示例（uwsgi.ini）：
[uwsgi]
module = backend.wsgi:application
master = true
processes = 5
socket = :8000
vacuum = true
"""

if __name__ == '__main__':
    # 开发服务器启动（仅用于测试）
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver'])

