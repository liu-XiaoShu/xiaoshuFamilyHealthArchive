"""
自定义安全中间件
用于增强应用的安全性
"""

from django.http import HttpResponseForbidden
from django.conf import settings
import re
import structlog

logger = structlog.get_logger(__name__)

class SecurityMiddleware:
    """
    安全增强中间件
    - IP白名单检查
    - 敏感操作记录
    - 异常访问检测
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # 编译IP白名单正则表达式
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        self.ip_patterns = [re.compile(ip.replace('*', r'\d+')) for ip in self.allowed_ips]
        
    def __call__(self, request):
        # 获取客户端IP
        client_ip = self.get_client_ip(request)
        
        # 检查IP白名单（如果配置了的话）
        if self.allowed_ips and not self.is_ip_allowed(client_ip):
            logger.warning(
                "blocked_ip_access",
                ip=client_ip,
                path=request.path,
                method=request.method
            )
            return HttpResponseForbidden('Access Denied')
            
        # 记录敏感操作
        if self.is_sensitive_operation(request):
            logger.info(
                "sensitive_operation",
                ip=client_ip,
                user_id=request.user.id if request.user.is_authenticated else None,
                path=request.path,
                method=request.method
            )
            
        response = self.get_response(request)
        
        # 添加安全响应头
        self.add_security_headers(request, response)
        
        return response
        
    def get_client_ip(self, request):
        """获取客户端真实IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
        
    def is_ip_allowed(self, ip):
        """检查IP是否在白名单中"""
        return any(pattern.match(ip) for pattern in self.ip_patterns)
        
    def is_sensitive_operation(self, request):
        """判断是否是敏感操作"""
        sensitive_paths = [
            r'/api/medical/',
            r'/api/users/',
            r'/admin/',
        ]
        sensitive_methods = ['POST', 'PUT', 'DELETE', 'PATCH']
        
        return (
            any(re.match(path, request.path) for path in sensitive_paths) and
            request.method in sensitive_methods
        )
        
    def add_security_headers(self, request, response):
        """添加安全响应头"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Feature-Policy'] = "camera 'none'; microphone 'none'"
        
        # 只在HTTPS连接中设置某些头
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response 