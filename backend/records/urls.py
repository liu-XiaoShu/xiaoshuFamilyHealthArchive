# records/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicalRecordViewSet,
    MedicationRecordViewSet,
    VaccinationRecordViewSet,
    PhysicalExamViewSet,
    HealthOverviewAPI
)

router = DefaultRouter()
router.register(r'medical', MedicalRecordViewSet)
router.register(r'medication', MedicationRecordViewSet)
router.register(r'vaccination', VaccinationRecordViewSet)
router.register(r'physical', PhysicalExamViewSet)
router.register(r'overview', HealthOverviewAPI, basename='overview')

app_name = 'records'

urlpatterns = [
    path('', include(router.urls)),
    # 直接添加健康统计相关API端点
    path('overview/statistics/', HealthOverviewAPI.as_view({'get': 'statistics'}), name='statistics'),
    path('overview/health-trends/', HealthOverviewAPI.as_view({'get': 'health_trends'}), name='health_trends'),
    path('overview/recent-activities/', HealthOverviewAPI.as_view({'get': 'recent_activities'}), name='recent_activities'),
]
