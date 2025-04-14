from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class RecordsConfig(AppConfig):
    """
    健康记录应用配置类
    用于设置应用的元数据和初始化行为
    """
    # 指定自动生成的主键字段类型（Django 3.2+ 默认配置）
    default_auto_field = 'django.db.models.BigAutoField'
    # 应用名称（Python路径格式）
    name = 'records'
    # 人类可读的应用名称（用于管理界面显示）
    verbose_name = _('健康档案管理')

    def ready(self):
        """
        应用初始化方法
        当Django启动时会自动调用
        用于注册信号处理器等初始化操作
        """
        # 示例：注册信号处理器（需要时取消注释）
        # from . import signals

        # 示例：添加自定义系统检查
        # from django.core.checks import register
        # from .checks import example_check
        # register(example_check)
        # 初始化健康档案相关配置
        self._initialize_health_records()

    def _initialize_health_records(self):
        """
        私有方法：执行应用特定的初始化配置
        可以在此处添加：
        - 默认数据创建
        - 第三方服务注册
        - 运行时配置验证
        """
        # 示例：创建默认分类（需要时取消注释）
        # from .models import Category
        # if not Category.objects.exists():
        #     Category.objects.create(name="默认分类")

        # 示例：验证配置文件
        # from django.conf import settings
        # if not hasattr(settings, 'HEALTH_RECORD_STORAGE'):
        #     raise ImproperlyConfigured("缺少健康档案存储配置")
        pass

