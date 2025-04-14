from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, logout, authenticate
from .models import FamilyRelationship, UserProfile, DefaultAvatar
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    FamilyRelationshipSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    UserHealthInfoSerializer,
    ChangePasswordSerializer,
    UserAvatarSerializer,
    DefaultAvatarSerializer
)
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
import os

logger = logging.getLogger(__name__)

# 获取自定义用户模型
CustomUser = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义JWT登录视图
    扩展默认实现以在响应中包含用户信息
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]  # 登录不需要认证

    def post(self, request, *args, **kwargs):
        """
        处理登录POST请求
        1. 调用父类方法获取基础响应
        2. 成功时添加完整的用户信息
        3. 保持错误处理逻辑不变
        """
        # 调用父类处理JWT认证
        response = super().post(request, *args, **kwargs)
        # 登录成功时(status_code=200)添加用户数据
        if response.status_code == status.HTTP_200_OK:
            try:
                # 获取登录用户实例
                user = CustomUser.objects.get(username=request.data['username'])
                # 将用户序列化数据添加到响应中
                response.data['user'] = UserSerializer(user).data
            except CustomUser.DoesNotExist:
                # 异常处理（理论上不会发生，因为已通过认证）
                return Response(
                    {'detail': '用户不存在'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return response

class RegisterView(generics.CreateAPIView):
    """
    用户注册API端点
    允许未认证用户创建新账户
    """
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    
    def create(self, request, *args, **kwargs):
        """处理用户注册请求"""
        # 使用序列化器验证数据
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 如果数据有效，创建用户
        user = serializer.save()
        
        # 根据性别和年龄设置默认头像
        try:
            gender = user.gender
            birth_date = user.birth_date
            profile = UserProfile.objects.get_or_create(user=user)[0]
            
            # 确定适当的默认头像类别
            avatar_category = None
            
            # 计算年龄
            age = None
            if birth_date:
                from django.utils import timezone
                today = timezone.now().date()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if gender == 'male':
                if age is not None and age < 20:
                    avatar_category = 'male_child'
                elif age is not None and age >= 50:
                    avatar_category = 'male_elder'
                else:
                    avatar_category = 'male_adult'
            elif gender == 'female':
                if age is not None and age < 20:
                    avatar_category = 'female_child'
                elif age is not None and age >= 50:
                    avatar_category = 'female_elder'
                else:
                    avatar_category = 'female_adult'
            else:
                # 默认使用成年男性头像
                avatar_category = 'male_adult'
            
            logger.info(f"用户{user.username}的默认头像类别: {avatar_category}")
            
            # 查找对应默认头像
            try:
                default_avatar = DefaultAvatar.objects.filter(category=avatar_category).first()
                if not default_avatar:
                    # 如果找不到特定类别，使用任何可用的默认头像
                    default_avatar = DefaultAvatar.objects.first()
                    
                if default_avatar and default_avatar.image:
                    # 设置用户头像
                    from django.core.files.base import ContentFile
                    import os
                    
                    # 读取默认头像文件
                    with default_avatar.image.open('rb') as f:
                        content = f.read()
                    
                    # 保存为用户头像
                    filename = os.path.basename(default_avatar.image.name)
                    profile.avatar.save(filename, ContentFile(content), save=True)
                    logger.info(f"已为用户 {user.username} 设置默认头像: {avatar_category}")
            except Exception as e:
                logger.error(f"设置默认头像文件失败: {str(e)}")
        except Exception as e:
            logger.error(f"设置默认头像失败: {str(e)}")
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        # 构建响应
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户个人资料管理端点
    支持以下操作：
    - GET /api/user/profile/ : 获取当前用户资料
    - PUT /api/user/profile/ : 完整更新用户资料
    - PATCH /api/user/profile/ : 部分更新用户资料
    """
    serializer_class = UserSerializer
    # 需要认证后才能访问
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """始终返回当前登录用户实例"""
        return self.request.user

    def perform_update(self, serializer):
        """
        处理更新操作的特殊逻辑
        1. 单独处理密码更新
        2. 普通字段的正常更新
        """
        # 提取密码字段（如果存在）
        password = self.request.data.get('password')
        if password:
            # 使用set_password方法安全更新密码
            user = self.get_object()
            user.set_password(password)
            user.save()
        # 保存其他字段的更新
        serializer.save()

class FamilyRelationshipViewSet(viewsets.ModelViewSet):
    """
    家庭成员关系管理视图集
    提供完整的CRUD操作：
    - GET /api/family/ : 列表查看当前用户的关系
    - POST /api/family/ : 创建新关系
    - GET /api/family/{id}/ : 查看单个关系详情
    - PUT /api/family/{id}/ : 更新关系
    - DELETE /api/family/{id}/ : 删除关系
    """
    serializer_class = FamilyRelationshipSerializer
    # 需要认证且只能操作自己的关系
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """过滤只返回当前用户发起的关系"""
        return FamilyRelationship.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        """创建时自动关联当前用户为发起者"""
        serializer.save(from_user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """删除关系前的额外验证"""
        instance = self.get_object()
        # 阻止删除已验证的关系
        if instance.verified:
            return Response(
                {'detail': '已验证的关系不可删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    用户登出视图
    """
    try:
        # 获取用户令牌
        refresh_token = request.data.get('refresh', None)
        if refresh_token:
            # 将令牌加入黑名单
            token = RefreshToken(refresh_token)
            token.blacklist()
        # 清除会话
        logout(request)
        return Response({"detail": "登出成功"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"用户登出失败: {str(e)}")
        return Response(
            {"detail": "无效的令牌或令牌已过期"},
            status=status.HTTP_400_BAD_REQUEST
        )

# 用户头像上传视图
class UserAvatarView(APIView):
    """
    用户头像上传端点
    允许已认证用户上传/更新头像
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, *args, **kwargs):
        """获取用户头像URL"""
        user = request.user
        
        try:
            # 尝试获取用户资料
            profile = user.profile
            
            # 如果有自定义头像，直接返回
            if profile.avatar:
                return Response({
                    'avatar_url': request.build_absolute_uri(profile.avatar.url)
                }, status=status.HTTP_200_OK)
                
            # 否则获取默认头像
            default_avatar_url = profile.get_default_avatar()
            if default_avatar_url:
                return Response({
                    'avatar_url': request.build_absolute_uri(default_avatar_url)
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"获取头像URL失败: {str(e)}")
            
        # 如果找不到头像，返回空
        return Response({
            'avatar_url': None
        }, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """处理头像上传请求"""
        if 'avatar' not in request.FILES:
            return Response(
                {'detail': '请选择要上传的头像'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = request.user
        
        # 获取资料对象，如果不存在则创建
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # 如果profile不存在，创建一个
            profile = UserProfile.objects.create(user=user)
            
        # 保存头像
        try:
            # 如果之前有头像，先删除
            if profile.avatar:
                # 删除旧头像文件
                if os.path.exists(profile.avatar.path):
                    os.remove(profile.avatar.path)
            
            # 保存新头像
            profile.avatar = request.FILES['avatar']
            profile.save()
            
            return Response({
                'detail': '头像上传成功',
                'avatar_url': request.build_absolute_uri(profile.avatar.url)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"头像上传失败: {str(e)}")
            return Response({
                'detail': f'头像上传失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 用户健康信息视图
class UserHealthInfoView(APIView):
    """
    用户健康信息管理端点
    支持获取和更新健康数据
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """获取用户健康信息"""
        user = request.user
        
        # 获取资料对象
        try:
            profile = user.profile
            serializer = UserHealthInfoSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({
                'height': None,
                'weight': None,
                'allergies': None,
                'allergies_list': [],
                'notes': None
            })
    
    def post(self, request, *args, **kwargs):
        """更新用户健康信息"""
        user = request.user
        
        # 获取资料对象，如果不存在则创建
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # 如果profile不存在，创建一个
            profile = UserProfile.objects.create(user=user)
        
        serializer = UserHealthInfoSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 更改密码视图
class ChangePasswordView(APIView):
    """
    更改密码端点
    允许已认证用户更新自己的密码
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """处理密码更新"""
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # 验证当前密码
            current_password = serializer.validated_data.get('current_password')
            if not user.check_password(current_password):
                return Response(
                    {'detail': '当前密码不正确'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 更新为新密码
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            
            return Response(
                {'detail': '密码更新成功'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 管理默认头像视图集
class DefaultAvatarViewSet(viewsets.ModelViewSet):
    """
    默认头像管理视图集
    管理员可完整操作，普通用户可查看
    """
    queryset = DefaultAvatar.objects.all()
    serializer_class = DefaultAvatarSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        """根据不同操作设置不同权限"""
        if self.action in ['list', 'retrieve']:
            # 允许已认证用户查看默认头像
            permission_classes = [IsAuthenticated]
        else:
            # 只允许管理员执行其他操作
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def update_avatars(self, request):
        """批量更新默认头像"""
        files = request.FILES
        result = []
        
        for category_key in ['male_child', 'female_child', 'male_adult', 'female_adult', 'male_elder', 'female_elder']:
            if category_key in files:
                # 处理图片，删除水印
                try:
                    from PIL import Image
                    from io import BytesIO
                    from django.core.files.base import ContentFile
                    
                    # 打开图片
                    img = Image.open(files[category_key])
                    
                    # 裁剪底部水印区域
                    width, height = img.size
                    crop_height = int(height * 0.95)  # 裁剪底部5%
                    img = img.crop((0, 0, width, crop_height))
                    
                    # 转换回文件
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    processed_image = ContentFile(buffer.getvalue())
                    
                    # 获取该类别对应的文件名
                    filename = DefaultAvatar.AVATAR_FILE_NAMES.get(category_key, f"{category_key}_avatar.png")
                    
                    # 更新或创建记录
                    avatar, created = DefaultAvatar.objects.update_or_create(
                        category=category_key,
                        defaults={
                            'description': f"默认{dict(DefaultAvatar.AVATAR_CATEGORIES).get(category_key)}头像"
                        }
                    )
                    
                    # 保存处理后的图片
                    avatar.image.save(filename, processed_image, save=True)
                    
                    result.append({
                        'category': category_key,
                        'filename': filename,
                        'status': 'created' if created else 'updated'
                    })
                except Exception as e:
                    return Response({
                        'error': f'处理{category_key}头像时出错: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(result, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """根据类别获取头像"""
        category = request.query_params.get('category')
        if not category:
            return Response({
                'error': '需要提供category参数'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            avatar = DefaultAvatar.objects.get(category=category)
            return Response({
                'image_url': request.build_absolute_uri(avatar.image.url),
                'category': avatar.category,
                'description': avatar.description
            }, status=status.HTTP_200_OK)
        except DefaultAvatar.DoesNotExist:
            return Response({
                'error': f'未找到类别为{category}的默认头像'
            }, status=status.HTTP_404_NOT_FOUND)

