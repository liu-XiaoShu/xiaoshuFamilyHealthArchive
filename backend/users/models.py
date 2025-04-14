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

    def get_default_avatar(self):
        """
        根据用户的性别和年龄获取相应的默认头像
        """
        user = self.user
        
        # 如果用户已有头像，直接返回
        if self.avatar and os.path.exists(self.avatar.path):
            return self.avatar.url
            
        # 确定用户类别
        gender = user.gender or 'male'  # 默认为男性
        
        # 计算年龄
        age = None
        if user.birth_date:
            today = date.today()
            age = today.year - user.birth_date.year - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
        
        # 根据年龄和性别确定头像类别
        category = None
        if gender.lower() == 'male':
            if age is not None and age < 20:
                category = 'male_child'
            elif age is not None and age >= 50:
                category = 'male_elder'
            else:
                category = 'male_adult'
        else:  # female or other
            if age is not None and age < 20:
                category = 'female_child'
            elif age is not None and age >= 50:
                category = 'female_elder'
            else:
                category = 'female_adult'
        
        # 查找默认头像
        try:
            default_avatar = DefaultAvatar.objects.get(category=category)
            return default_avatar.image.url
        except DefaultAvatar.DoesNotExist:
            # 如果找不到特定类别的头像，尝试使用任何可用的默认头像
            try:
                default_avatar = DefaultAvatar.objects.first()
                if default_avatar:
                    return default_avatar.image.url
            except:
                pass
                
        return None  # 如果没有默认头像可用

class DefaultAvatar(models.Model):
    """
    默认头像模型
    根据用户性别和年龄段提供默认头像
    """
    AVATAR_CATEGORIES = [
        ('male_child', _('男性儿童')),
        ('female_child', _('女性儿童')),
        ('male_adult', _('男性成年')),
        ('female_adult', _('女性成年')),
        ('male_elder', _('男性老年')),
        ('female_elder', _('女性老年')),
    ]
    
    # 头像文件名映射
    AVATAR_FILE_NAMES = {
        'male_child': 'male_child_avatar.png',
        'female_child': 'girl_child_avatar.png',
        'male_adult': 'Male_middle-aged_avatar.png',
        'female_adult': 'female_middle-aged_avatar.png',
        'male_elder': 'male_elderly_avatar.png',
        'female_elder': 'female_elderly_avatar.png',
    }
    
    category = models.CharField(
        verbose_name=_('头像类别'),
        max_length=20,
        choices=AVATAR_CATEGORIES,
        unique=True,
        help_text=_('头像适用的用户类别')
    )
    
    image = models.ImageField(
        upload_to='default_avatars/',
        verbose_name=_('头像图片'),
        help_text=_('默认头像图片文件')
    )
    
    description = models.CharField(
        max_length=100,
        verbose_name=_('描述'),
        help_text=_('头像的简要描述'),
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('创建时间')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('更新时间')
    )
    
    class Meta:
        verbose_name = _('默认头像')
        verbose_name_plural = _('默认头像')
        
    def __str__(self):
        return f"{self.get_category_display()}"

    @classmethod
    def get_avatar_filename(cls, category):
        """返回指定类别的默认文件名"""
        return cls.AVATAR_FILE_NAMES.get(category, '')

