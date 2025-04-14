from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from .views import HealthCheckView, health_check

# 初始化DRF默认路由器（自动生成API根视图）
router = routers.DefaultRouter(trailing_slash=False)

# ------------------------- 主URL配置 -------------------------
urlpatterns = [
    # 管理后台路由
    path('admin/docs/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    # REST框架认证端点（登录/注销）
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 应用模块路由（分模块管理）
    path('api/users/', include('users.urls')),
    path('api/records/', include('records.urls')),
    # API文档生成端点
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # 健康检查端点
    path('api/health/', health_check, name='health-check'),
    path('api/health-class/', HealthCheckView.as_view(), name='health-class'),
]

# ------------------------- 开发环境扩展配置 -------------------------
if settings.DEBUG:
    # 本地媒体文件服务（生产环境应使用Nginx等处理）
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 自定义错误页面（开发环境演示用）
    from django.views import defaults as default_views
    urlpatterns += [
        re_path(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request')}),
        re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        re_path(r'^500/$', default_views.server_error),
    ]

# ------------------------- 第三方服务集成 -------------------------
# Sentry测试路由（需安装sentry-sdk）
if hasattr(settings, 'SENTRY_DSN'):
    def trigger_error(request):
        division_by_zero = 1 / 0
    urlpatterns += [
        path('sentry-debug/', trigger_error),
    ]

# ------------------------- 安全增强配置 -------------------------
# 安全中间件路由重定向（需在settings启用SecurityMiddleware）
if not settings.DEBUG:
    urlpatterns = [
        # 安全头中间件路由
        # path('', include('csp.urls')),
    ] + urlpatterns

# ------------------------- 扩展路由建议 -------------------------
"""
可选的扩展路由配置（按需取消注释）：
1. 监控系统集成：
   path('prometheus/', include('django_prometheus.urls')),

2. GraphQL端点：
   from graphene_django.views import GraphQLView
   path('graphql/', GraphQLView.as_view(graphiql=True)),

3. WebSocket路由：
   path('ws/', include('notifications.routing.websocket_urlpatterns')),

4. 限流策略配置：
   from rest_framework.throttling import AnonRateThrottle
   urlpatterns += [path('api/limited/', AnonRateThrottle.as_view())]
"""

