"""
ASGI（异步服务器网关接口）配置
为项目提供异步Web服务器支持，处理WebSocket等协议
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# 设置Django环境变量（优先从环境变量读取）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 初始化Django ASGI应用（用于处理传统HTTP请求）
django_asgi_app = get_asgi_application()

# 应用生命周期事件处理（可选）
async def lifespan_handler(scope, receive, send):
    """处理ASGI应用生命周期事件"""
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                # 服务器启动时执行初始化操作
                print("ASGI服务器启动...")
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                # 服务器关闭时执行清理操作
                print("ASGI服务器关闭...")
                await send({'type': 'lifespan.shutdown.complete'})
                break

# 导入WebSocket路由（需安装channels）
try:
    from records.routing import websocket_urlpatterns
    has_channels = True
except ImportError:
    has_channels = False

# 主协议路由配置
application = ProtocolTypeRouter({
    # HTTP协议处理（兼容WSGI）
    "http": django_asgi_app,
    # WebSocket协议处理（需安装channels）
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ) if has_channels else None,
    # 生命周期事件处理
    "lifespan": lifespan_handler,
})

# ------------------------- 可选扩展配置 -------------------------

# 生产环境中间件配置（示例）
if os.environ.get('ENV') == 'production':
    from django.core.handlers.asgi import ASGIHandler
    from django.middleware.security import SecurityMiddleware
    # 包装安全中间件
    application = SecurityMiddleware(application)

# 性能监控集成（示例）
if os.environ.get('ENABLE_METRICS'):
    from prometheus_client import make_asgi_app
    metrics_app = make_asgi_app()
    application = ProtocolTypeRouter({
        "http": URLRouter([
            # 将/metrics路由指向监控应用
            (r'^metrics', metrics_app),
            (r'^', application),
        ]),
        "websocket": application['websocket'],
        "lifespan": application['lifespan'],
    })

# 开发环境详细日志（示例）
if os.environ.get('DEBUG') == 'True':
    from rich.traceback import install
    install(show_locals=True)

