from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
import re
from datetime import date
from django.core.files import File
import os
from io import BytesIO
import requests

class CustomUser(AbstractUser):
    """
    扩展的定制用户模型，包含健康管理系统所需的额外字段
    继承自Django内置的AbstractUser基础模型
    """
    # 性别字段
    GENDER_CHOICES = [
        ('male', _('男')),
        ('female', _('女')),
        ('other', _('其他'))
    ]
    
    gender = models.CharField(
        verbose_name=_('性别'),
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        default='',
        help_text=_('用户的性别')
    )
    
    # 手机号字段
    phone = models.CharField(
        verbose_name=_('手机号码'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('用户的联系电话，用于紧急联系和找回密码')
    )
    # 出生日期字段
    birth_date = models.DateField(
        verbose_name=_('出生日期'),  # 后台显示名称
        help_text=_('格式：YYYY-MM-DD，用于计算年龄和健康评估'),  # 帮助提示
        null=True,  # 允许数据库存储空值
        blank=True,  # 允许表单提交时为空
        error_messages={  # 自定义错误消息
            'invalid': _('请输入有效的日期格式（YYYY-MM-DD）')
        }
    )
    # 血型选择字段
    blood_type = models.CharField(
        verbose_name=_('血型'),
        max_length=5,
        choices=[  # 可选值列表
            ('A', 'A型'),
            ('B', 'B型'),
            ('AB', 'AB型'),
            ('O', 'O型')
        ],
        help_text=_('请从下拉列表中选择正确的血型分类'),
        blank=True,  # 允许表单为空
        default=''   # 默认空值
    )
    # 兴趣爱好字段
    hobbies = models.TextField(
        verbose_name=_('兴趣爱好'),
        help_text=_('用逗号分隔多个爱好（例如：游泳, 阅读，最多200字）'),
        max_length=200,  # 最大长度限制
        blank=True,
        null=True  # 允许数据库存储空值
    )

    # 紧急联系人验证器
    emergency_contact_validator = RegexValidator(
        regex=r'^[\u4e00-\u9fa5]{2,10}-[\u4e00-\u9fa5]{2,10}-1[3-9]\d{9}$',
        message=_('格式错误。请使用"姓名-关系-手机号"格式，例如：张三-父亲-13800138000')
    )
    
    emergency_contact = models.CharField(
        verbose_name=_('紧急联系人'),
        max_length=100,
        help_text=_('格式：姓名-关系-联系电话（例如：张三-父亲-13800138000）'),
        blank=True,
        validators=[emergency_contact_validator]
    )

    # 家庭成员多对多关系（使用中间模型）
    family_members = models.ManyToManyField(
        'self',  # 自关联
        verbose_name=_('家庭成员'),
        through='FamilyRelationship',  # 通过中间模型
        symmetrical=False,  # 非对称关系
        blank=True,  # 允许空值
        help_text=_('通过下方家庭成员关系表管理关联')
    )

    # 添加related_name来避免命名冲突
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    avatar = models.ImageField(
        verbose_name=_('个人头像'),
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text=_('用户的个人头像，如未上传将使用默认头像')
    )

    class Meta:
        # 后台管理系统显示名称
        verbose_name = _('用户健康档案')
        verbose_name_plural = _('用户健康档案')
        # 默认排序规则
        ordering = ['-date_joined']
        # 权限配置
        permissions = [
            ("can_manage_users", _("可以管理普通用户权限")),
        ]

    def __str__(self):
        """对象字符串表示形式，用于后台显示"""
        return f"{self.username}的健康档案（ID：{self.id}）"

    def clean(self):
        """模型级数据验证"""
        super().clean()
        # 验证出生日期
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError({'birth_date': _('出生日期不能晚于今天')})
        
        # 验证血型格式
        if self.blood_type and self.blood_type not in dict(self._meta.get_field('blood_type').choices):
            raise ValidationError({'blood_type': _('无效的血型选择')})
        
        # 验证兴趣爱好格式
        if self.hobbies:
            hobbies_list = [h.strip() for h in self.hobbies.split(',')]
            if any(len(h) > 20 for h in hobbies_list):
                raise ValidationError({'hobbies': _('单个兴趣爱好不能超过20个字符')})
            if len(hobbies_list) > 10:
                raise ValidationError({'hobbies': _('兴趣爱好不能超过10个')})

    def get_age(self):
        """计算用户年龄"""
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def get_age_group(self):
        """获取用户年龄段"""
        age = self.get_age()
        if age is None:
            return 'young'  # 默认为青年
        if age <= 12:
            return 'child'
        elif age <= 17:
            return 'teen'
        elif age <= 35:
            return 'young'
        elif age <= 55:
            return 'middle'
        else:
            return 'elder'

    def get_default_avatar(self):
        """获取默认头像URL"""
        if self.avatar:
            return self.avatar.url
        
        try:
            default_avatar = DefaultAvatar.objects.get(
                gender=self.gender or 'other',
                age_group=self.get_age_group()
            )
            return default_avatar.avatar.url
        except DefaultAvatar.DoesNotExist:
            # 如果没有找到对应的默认头像，返回一个通用默认头像
            return '/static/images/default_avatar.png'


class FamilyRelationship(models.Model):
    """
    家庭成员关系中间模型
    记录用户之间的家庭关系及验证状态
    """
    # 关系类型选项
    RELATION_CHOICES = [
        ('parent', _('父母')),
        ('child', _('子女')),
        ('spouse', _('配偶')),
        ('sibling', _('兄弟姐妹')),
        ('other', _('其他关系'))
    ]

    # 发起关系的用户（外键）
    from_user = models.ForeignKey(
        CustomUser,
        verbose_name=_('用户'),
        on_delete=models.CASCADE,  # 级联删除
        related_name='from_relationships',  # 反向关系名称
        help_text=_('选择要建立关系的主体用户')
    )

    # 目标用户（外键）
    to_user = models.ForeignKey(
        CustomUser,
        verbose_name=_('家庭成员'),
        on_delete=models.CASCADE,
        related_name='to_relationships',
        help_text=_('选择要关联的家庭成员')
    )

    # 关系类型字段
    relation_type = models.CharField(
        verbose_name=_('关系类型'),
        max_length=20,
        choices=RELATION_CHOICES,
        help_text=_('请选择最准确的关系描述')
    )

    # 验证状态字段
    verified = models.BooleanField(
        verbose_name=_('已验证'),
        default=False,
        help_text=_('表示对方是否确认此关系')
    )

    # 关系建立时间（自动记录）
    created_at = models.DateTimeField(
        verbose_name=_('建立时间'),
        auto_now_add=True,  # 自动设置创建时间
        help_text=_('关系记录的创建时间')
    )

    class Meta:
        # 数据库唯一性约束
        unique_together = ('from_user', 'to_user', 'relation_type')
        # 后台显示名称
        verbose_name = _('家庭成员关系')
        verbose_name_plural = _('家庭成员关系')
        # 默认排序
        ordering = ['-created_at']

    def __str__(self):
        """友好的显示格式"""
        return f"{self.from_user} → {self.to_user} ({self.get_relation_type_display()})"

    def clean(self):
        """自定义验证逻辑"""
        # 禁止用户与自己建立关系
        if self.from_user == self.to_user:
            raise ValidationError(_('不能与自己建立家庭关系'))

        # 检查反向关系是否已存在
        if FamilyRelationship.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user,
            relation_type=self.relation_type
        ).exists():
            raise ValidationError(_('反向关系已存在，请直接修改现有记录'))


class UserProfile(models.Model):
    """
    用户详细资料模型
    存储用户的扩展信息，包含头像等个性化数据
    """
    # 关联到主用户模型的一对一关系
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('用户')
    )
    
    # 用户头像
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('用户头像')
    )
    
    # 身高（厘米）
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('身高(cm)')
    )
    
    # 体重（千克）
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('体重(kg)')
    )
    
    # 过敏物质
    allergies = models.TextField(
        verbose_name=_('过敏物质'),
        help_text=_('逗号分隔的过敏源列表'),
        blank=True,
        null=True
    )
    
    # 备注信息
    notes = models.TextField(
        verbose_name=_('健康备注'),
        help_text=_('其他相关健康信息'),
        blank=True,
        null=True
    )
    
    # 更新时间
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('最后更新时间')
    )
    
    class Meta:
        verbose_name = _('用户详细资料')
        verbose_name_plural = _('用户详细资料')
        
    def __str__(self):
        return f"{self.user.username}的详细资料"
    
    @property
    def get_allergies_list(self):
        """将过敏物质文本转换为列表"""
        if self.allergies:
            return [item.strip() for item in self.allergies.split(',')]
        return []


class DefaultAvatar(models.Model):
    """
    默认头像模型
    基于用户年龄段和性别提供默认头像
    """
    GENDER_CHOICES = [
        ('male', _('男')),
        ('female', _('女')),
        ('other', _('其他'))
    ]

    AGE_GROUP_CHOICES = [
        ('child', _('儿童')),      # 0-12岁
        ('teen', _('青少年')),     # 13-17岁
        ('young', _('青年')),      # 18-35岁
        ('middle', _('中年')),     # 36-55岁
        ('elder', _('老年'))       # 56岁以上
    ]

    gender = models.CharField(
        verbose_name=_('性别'),
        max_length=10,
        choices=GENDER_CHOICES,
        help_text=_('头像对应的性别')
    )

    age_group = models.CharField(
        verbose_name=_('年龄段'),
        max_length=10,
        choices=AGE_GROUP_CHOICES,
        help_text=_('头像对应的年龄段')
    )

    avatar = models.ImageField(
        verbose_name=_('默认头像'),
        upload_to='default_avatars/',
        help_text=_('上传对应性别和年龄段的默认头像图片')
    )

    class Meta:
        verbose_name = _('默认头像')
        verbose_name_plural = _('默认头像')
        unique_together = ['gender', 'age_group']

    def __str__(self):
        return f"{self.get_gender_display()}-{self.get_age_group_display()}"

