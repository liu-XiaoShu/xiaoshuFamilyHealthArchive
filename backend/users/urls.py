from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    CustomTokenObtainPairView, 
    UserProfileView, 
    user_logout,
    UserAvatarView,
    UserHealthInfoView,
    ChangePasswordView,
    DefaultAvatarViewSet
)

app_name = 'users'

# 创建路由器并注册ViewSet
router = DefaultRouter()
router.register(r'default-avatars', DefaultAvatarViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('logout/', user_logout, name='logout'),
    path('avatar/', UserAvatarView.as_view(), name='user_avatar'),
    path('health-info/', UserHealthInfoView.as_view(), name='user_health_info'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    # ViewSet路由
    path('', include(router.urls)),
] 