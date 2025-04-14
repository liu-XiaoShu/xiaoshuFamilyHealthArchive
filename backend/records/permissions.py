from rest_framework import permissions

class IsOwnerOrStaff(permissions.BasePermission):
    """自定义权限类，允许对象的所有者或工作人员访问"""

    def has_object_permission(self, request, view, obj):
        # 允许所有请求方法的工作人员访问
        if request.user.is_staff:
            return True

        # 仅允许对象的所有者访问
        return obj.user == request.user 