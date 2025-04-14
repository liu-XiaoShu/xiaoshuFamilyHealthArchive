from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, FamilyRelationship

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    自定义用户管理后台配置
    扩展默认用户管理界面，添加健康管理系统特有字段
    """
    # 定义列表页显示字段
    list_display = (
        'username', 'email', 'birth_date',
        'blood_type', 'is_staff', 'date_joined'
    )
    # 右侧过滤器配置
    list_filter = (
        'is_staff', 'is_superuser', 'is_active',
        'blood_type', 'date_joined'
    )
    # 搜索字段配置
    search_fields = (
        'username', 'email', 'emergency_contact'
    )
    # 分页设置（每页显示数量）
    list_per_page = 20
    # 表单字段分组布局
    fieldsets = (
        # 基础信息分组
        (None, {
            'fields': ('username', 'password')
        }),
        # 个人资料分组
        (_('个人信息'), {
            'fields': (
                'email', 'birth_date', 'blood_type',
                'hobbies', 'emergency_contact'
            )
        }),
        # 权限分组
        (_('权限管理'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)  # 默认折叠
        }),
        # 时间信息分组
        (_('重要日期'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        })
    )
    # 添加用户表单字段配置
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1',
                'password2', 'birth_date', 'blood_type'
            ),
        }),
    )
    # 自定义显示方法
    def get_formatted_birth_date(self, obj):
        """格式化显示出生日期"""
        return obj.birth_date.strftime('%Y-%m-%d') if obj.birth_date else '-'
    get_formatted_birth_date.short_description = _('出生日期')
    # 自定义管理动作
    actions = ['activate_users', 'deactivate_users']
    def activate_users(self, request, queryset):
        """批量激活用户"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个用户')
    activate_users.short_description = _('激活选中用户')
    def deactivate_users(self, request, queryset):
        """批量停用用户"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个用户')
    deactivate_users.short_description = _('停用选中用户')

@admin.register(FamilyRelationship)
class FamilyRelationshipAdmin(admin.ModelAdmin):
    """
    家庭成员关系管理后台配置
    管理用户之间的家庭关系
    """
    # 列表显示字段
    list_display = (
        'from_user', 'to_user',
        'get_relation_type_display',
        'verified', 'created_at'
    )
    # 可编辑字段（直接列表页编辑）
    list_editable = ('verified',)
    # 过滤器配置
    list_filter = (
        'relation_type', 'verified',
        'created_at'
    )
    # 搜索字段配置
    search_fields = (
        'from_user__username',
        'to_user__username'
    )
    # 字段分组布局
    fieldsets = (
        (None, {
            'fields': (
                'from_user', 'to_user',
                'relation_type', 'verified'
            )
        }),
        (_('元数据'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    # 只读字段配置
    readonly_fields = ('created_at',)
    # 自定义验证保存
    def save_model(self, request, obj, form, change):
        """保存前的额外验证"""
        if obj.from_user == obj.to_user:
            from django.contrib import messages
            messages.error(request, _('不能创建用户与自身的关系'))
            return
        super().save_model(request, obj, form, change)

