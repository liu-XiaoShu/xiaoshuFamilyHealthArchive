from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from .models import FamilyRelationship, CustomUser, UserProfile, DefaultAvatar

# 获取自定义用户模型
CustomUser = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义JWT令牌获取序列化器
    扩展默认实现以包含更多用户信息
    """
    def validate(self, attrs):
        """重写验证方法添加自定义逻辑"""
        # 调用父类验证获取基础令牌
        data = super().validate(attrs)
        # 确保返回access和refresh令牌
        refresh = self.get_token(self.user)
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        # 添加用户信息到响应中
        data['user'] = UserSerializer(self.user).data
        return data

class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    用于用户资料的读取与更新
    """
    family_members = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    gender_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone', 'birth_date', 'gender', 'gender_display',
            'blood_type', 'hobbies', 'emergency_contact', 
            'family_members', 'avatar'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True}
        }

    def get_family_members(self, obj):
        """获取已验证的家庭成员列表"""
        relations = obj.from_relationships.filter(verified=True)
        family_members = []
        for rel in relations:
            member = rel.to_user
            family_members.append({
                'id': member.id,
                'username': member.username,
                'relation': rel.get_relation_type_display()
            })
        return family_members
        
    def get_gender_display(self, obj):
        """获取性别显示名称"""
        return dict(obj.GENDER_CHOICES).get(obj.gender, '未知')

    def get_avatar(self, obj):
        """获取用户头像URL"""
        try:
            # 如果用户已上传自定义头像
            if hasattr(obj, 'profile') and obj.profile and obj.profile.avatar:
                return obj.profile.avatar.url
                
            # 如果没有上传头像，则获取默认头像
            if hasattr(obj, 'profile') and obj.profile:
                # 尝试通过模型获取默认头像
                default_avatar_url = obj.profile.get_default_avatar()
                if default_avatar_url:
                    return default_avatar_url
                    
            # 如果还是没有，则根据性别和年龄直接获取对应类别的默认头像
            from .models import DefaultAvatar
            
            # 确定用户类别
            gender = obj.gender or 'male'  # 默认为男性
            
            # 计算年龄
            age = None
            if obj.birth_date:
                from django.utils import timezone
                today = timezone.now().date()
                age = today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
            
            # 根据年龄和性别确定头像类别
            category = None
            if gender.lower() == 'male':
                if age and age < 20:
                    category = 'male_child'
                elif age and age >= 50:
                    category = 'male_elder'
                else:
                    category = 'male_adult'
            else:  # female or other
                if age and age < 20:
                    category = 'female_child'
                elif age and age >= 50:
                    category = 'female_elder'
                else:
                    category = 'female_adult'
                    
            # 获取默认头像
            default_avatar = DefaultAvatar.objects.filter(category=category).first()
            if default_avatar and default_avatar.image:
                return default_avatar.image.url
                
            # 最后尝试获取任何可用的默认头像
            any_avatar = DefaultAvatar.objects.first()
            if any_avatar and any_avatar.image:
                return any_avatar.image.url
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取头像URL失败: {str(e)}")
            
        # 如果所有尝试都失败，使用一个静态默认头像
        return "/static/images/default-avatar.png"

    def update(self, instance, validated_data):
        """处理用户更新操作"""
        # 单独处理密码更新
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class FamilyRelationshipSerializer(serializers.ModelSerializer):
    """
    家庭成员关系序列化器
    用于管理用户之间的家庭关系
    """
    # 显示关系类型的中文名称
    relation_type_display = serializers.CharField(
        source='get_relation_type_display',
        read_only=True,
        label=_("关系类型显示"),
        help_text=_("关系类型的中文显示")
    )

    class Meta:
        model = FamilyRelationship
        fields = '__all__'
        extra_kwargs = {
            'from_user': {
                'read_only': True,
                'help_text': _("自动关联当前登录用户")
            },
            'verified': {
                'read_only': True,
                'help_text': _("需对方确认后才变为True")
            }
        }

    def validate_to_user(self, value):
        """验证目标用户有效性"""
        # 不能与自己建立关系
        if value == self.context['request'].user:
            raise serializers.ValidationError(_("不能添加自己为家庭成员"))
        return value

class RegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    处理新用户注册逻辑
    """
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label=_("确认密码"),
        help_text=_("请再次输入密码以确认")
    )
    
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        label=_("手机号码"),
        help_text=_("请输入有效的手机号码")
    )
    
    gender = serializers.ChoiceField(
        choices=CustomUser.GENDER_CHOICES,
        required=False,
        label=_("性别"),
        help_text=_("用户性别")
    )
    
    birth_date = serializers.DateField(
        required=False,
        label=_("出生日期"),
        help_text=_("格式：YYYY-MM-DD")
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'gender', 'birth_date', 'password', 'password_confirm')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'min_length': 8,
                'help_text': _("至少8个字符，包含字母和数字")
            },
            'email': {
                'required': True,
                'help_text': _("请输入有效的电子邮件地址")
            }
        }

    def validate(self, data):
        """注册数据验证"""
        # 检查密码匹配
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _("两次输入的密码不一致")
            })
        # 检查邮箱唯一性
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': _("该邮箱已被注册")
            })
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        """创建用户实例"""
        # 移除确认密码字段
        validated_data.pop('password_confirm')
        
        # 获取额外字段
        phone = validated_data.pop('phone', None)
        gender = validated_data.pop('gender', None)
        birth_date = validated_data.pop('birth_date', None)
        
        # 创建用户并设置密码
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # 设置额外字段
        if phone:
            user.phone = phone
        if gender:
            user.gender = gender
        if birth_date:
            user.birth_date = birth_date
            
        # 保存更改
        if phone or gender or birth_date:
            user.save()
            
        # 创建关联的用户资料
        profile = UserProfile.objects.create(user=user)
        
        # 根据用户性别和年龄选择默认头像
        # 计算年龄
        age = None
        if birth_date:
            from django.utils import timezone
            today = timezone.now().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # 确定适当的默认头像类别
        if gender:
            avatar_category = None
            if gender.lower() == 'male':
                if age is not None and age < 20:
                    avatar_category = 'male_child'
                elif age is not None and age >= 50:
                    avatar_category = 'male_elder'
                else:
                    avatar_category = 'male_adult'
            else:  # female or other
                if age is not None and age < 20:
                    avatar_category = 'female_child'
                elif age is not None and age >= 50:
                    avatar_category = 'female_elder'
                else:
                    avatar_category = 'female_adult'
                
            # 尝试获取对应类别的默认头像
            if avatar_category:
                try:
                    from django.core.files import File
                    from django.conf import settings
                    import os
                    
                    # 获取默认头像
                    default_avatar = DefaultAvatar.objects.filter(category=avatar_category).first()
                    if default_avatar and default_avatar.image:
                        # 复制默认头像到用户头像
                        profile.avatar = default_avatar.image
                        profile.save()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"设置默认头像失败: {str(e)}")
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """用户档案序列化器"""
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'birth_date', 'blood_type', 'hobbies', 'emergency_contact',
        ]
        read_only_fields = ['id']

    def validate_emergency_contact(self, value):
        """验证紧急联系人格式"""
        if value and not value.count('-') == 2:
            raise serializers.ValidationError("格式错误，请使用'姓名-关系-电话'格式")
        return value

class UserAvatarSerializer(serializers.ModelSerializer):
    """用户头像序列化器"""
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'avatar_url']
        read_only_fields = ['avatar_url']
        
    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

class DefaultAvatarSerializer(serializers.ModelSerializer):
    """默认头像序列化器"""
    category_display = serializers.SerializerMethodField()
    
    class Meta:
        model = DefaultAvatar
        fields = ['id', 'category', 'category_display', 'image', 'description']
        read_only_fields = ['id']
        
    def get_category_display(self, obj):
        return obj.get_category_display()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        return attrs

class UserHealthInfoSerializer(serializers.ModelSerializer):
    """用户健康信息序列化器"""
    allergies_list = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'height', 'weight', 'allergies', 'allergies_list', 'notes'
        ]
        
    def get_allergies_list(self, obj):
        return obj.get_allergies_list
        
    def validate_height(self, value):
        """验证身高合理性"""
        if value and (value < 10 or value > 300):
            raise serializers.ValidationError("身高数值不合理")
        return value
        
    def validate_weight(self, value):
        """验证体重合理性"""
        if value and (value < 1 or value > 500):
            raise serializers.ValidationError("体重数值不合理")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """密码修改序列化器"""
    current_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """验证新密码强度"""
        validate_password(value)
        return value

