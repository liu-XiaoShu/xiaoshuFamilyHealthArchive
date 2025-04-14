from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class UsersConfig(AppConfig):
    """
    用户应用配置类
    管理用户模块的元数据和初始化设置
    继承自Django的AppConfig基类
    """

    # 应用名称（必须与apps目录名一致）
    name = 'users'
    # 应用标签（用于替代应用名的简短标识）
    #label = 'custom_users'
    # 国际化显示名称（后台显示用）
    verbose_name = _('用户与健康档案')
    # 默认自动字段类型（Django 3.2+要求显式设置）
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """
        应用就绪时执行的初始化操作
        在Django启动时自动调用
        典型用途：
        - 注册信号处理器
        - 执行初始化配置
        - 注册后台任务
        """
        # 延迟导入防止循环引用
        try:
            # 导入并注册信号处理器
            from . import signals  # noqa
        except ImportError:
            pass

        # 可以在此处添加其他初始化代码
        # 例如：注册定期清理任务
        # schedule.every().day.do(cleanup_expired_users)

