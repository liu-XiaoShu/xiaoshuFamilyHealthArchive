from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

class HealthCheckView(APIView):
    """健康检查API视图"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """返回健康状态信息"""
        return Response({
            "status": "healthy", 
            "message": "小树家健康管理系统API正常运行"
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """函数式健康检查视图"""
    return Response({
        "status": "healthy", 
        "message": "小树家健康管理系统API正常运行"
    }) 