from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import FamilyRelationship

# 获取自定义用户模型
CustomUser = get_user_model()

class UserModelTests(APITestCase):
    """
    用户模型单元测试类
    测试自定义用户模型的核心功能
    """
    def setUp(self):
        """初始化测试数据"""
        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Testpass123',
            birth_date='1990-01-01',
            blood_type='A'
        )

    def test_user_creation(self):
        """测试用户创建功能"""
        self.assertEqual(self.test_user.email, 'test@example.com')
        self.assertTrue(self.test_user.check_password('Testpass123'))
        self.assertFalse(self.test_user.is_staff)  # 默认非管理员

    def test_user_str_representation(self):
        """测试用户对象的字符串表示"""
        self.assertEqual(str(self.test_user), 'testuser')

    def test_required_fields(self):
        """测试必填字段验证"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='',
                email='invalid@example.com',
                password='testpass'
            )

class AuthAPITests(APITestCase):
    """
    认证相关API测试类
    覆盖注册和登录流程
    """
    def test_user_registration(self):
        """测试新用户注册流程"""
        url = reverse('user-register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Newpass123',
            'password_confirm': 'Newpass123',
            'birth_date': '2000-01-01',
            'blood_type': 'O'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertIn('user', response.data)

    def test_jwt_authentication(self):
        """测试JWT令牌获取"""
        # 先创建测试用户
        CustomUser.objects.create_user(
            username='authuser',
            password='authtest',
            email='auth@example.com'
        )
        url = reverse('token_obtain_pair')
        data = {
            'username': 'authuser',
            'password': 'authtest'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class UserProfileAPITests(APITestCase):
    """
    用户资料API测试类
    测试个人资料管理功能
    """
    def setUp(self):
        """创建测试用户并获取令牌"""
        self.user = CustomUser.objects.create_user(
            username='profileuser',
            password='profiletest',
            email='profile@example.com'
        )
        self.client = APIClient()
        # 获取JWT令牌
        auth_url = reverse('token_obtain_pair')
        auth_data = {'username': 'profileuser', 'password': 'profiletest'}
        token = self.client.post(auth_url, auth_data, format='json').data['access']
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_retrieve_profile(self):
        """测试获取用户资料"""
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')

    def test_update_profile(self):
        """测试更新用户资料"""
        url = reverse('user-profile')
        data = {
            'email': 'updated@example.com',
            'birth_date': '1995-05-05'
        }
        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, 'updated@example.com')

class FamilyRelationshipAPITests(APITestCase):
    """
    家庭成员关系API测试类
    测试关系管理功能
    """
    def setUp(self):
        """创建测试用户和关系数据"""
        self.user1 = CustomUser.objects.create_user(
            username='familyuser1',
            password='familytest'
        )
        self.user2 = CustomUser.objects.create_user(
            username='familyuser2',
            password='familytest'
        )
        # 用户1的客户端
        self.client1 = APIClient()
        token = self.get_token(self.user1)
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        # 用户2的客户端
        self.client2 = APIClient()
        token = self.get_token(self.user2)
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def get_token(self, user):
        """辅助方法：获取用户JWT令牌"""
        auth_url = reverse('token_obtain_pair')
        response = self.client.post(auth_url, {
            'username': user.username,
            'password': 'familytest'
        }, format='json')
        return response.data['access']

    def test_create_relationship(self):
        """测试创建家庭成员关系"""
        url = reverse('familyrelationship-list')
        data = {
            'to_user': self.user2.id,
            'relation_type': 'parent'
        }
        response = self.client1.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FamilyRelationship.objects.count(), 1)

    def test_self_relationship_prevention(self):
        """测试防止创建自我关系"""
        url = reverse('familyrelationship-list')
        data = {
            'to_user': self.user1.id,  # 尝试与自己建立关系
            'relation_type': 'spouse'
        }
        response = self.client1.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PermissionTests(APITestCase):
    """
    权限验证测试类
    测试系统权限控制逻辑
    """
    def setUp(self):
        """创建测试用户"""
        self.user = CustomUser.objects.create_user(
            username='permuser',
            password='permpass'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='otherpass'
        )
        # 获取测试用户令牌
        self.client = APIClient()
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def get_token(self, user):
        """辅助方法：获取用户JWT令牌"""
        auth_url = reverse('token_obtain_pair')
        response = self.client.post(auth_url, {
            'username': user.username,
            'password': user.password
        }, format='json')
        return response.data['access']

    def test_unauthenticated_access(self):
        """测试未认证访问保护端点"""
        self.client.credentials()  # 清除认证信息
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cross_user_access_prevention(self):
        """测试防止越权访问其他用户数据"""
        # 创建属于other_user的关系
        rel = FamilyRelationship.objects.create(
            from_user=self.other_user,
            to_user=self.user,
            relation_type='child'
        )
        # 尝试用测试用户访问该关系
        url = reverse('familyrelationship-detail', args=[rel.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

