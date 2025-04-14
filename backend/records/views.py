from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import (
    MedicalRecord,
    MedicationRecord,
    VaccinationRecord,
    PhysicalExam,
    Reminder
)
from .serializers import (
    MedicalRecordSerializer,
    MedicationRecordSerializer,
    VaccinationRecordSerializer,
    PhysicalExamSerializer,
    ReminderSerializer
)
from .permissions import IsOwnerOrStaff
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count
from django.shortcuts import render
from django.utils import timezone
from datetime import date
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)

# 辅助函数：计算年龄
def calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

class MedicalRecordViewSet(viewsets.ModelViewSet):
    """就医记录视图集"""
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        """只返回当前用户的记录"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建记录时自动设置用户"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取就医记录统计信息"""
        stats = self.get_queryset().aggregate(
            total=Count('id'),
            hospital_count=Count('hospital', distinct=True),
            department_count=Count('department', distinct=True)
        )
        return Response(stats)

class MedicationRecordViewSet(viewsets.ModelViewSet):
    """用药记录视图集"""
    queryset = MedicationRecord.objects.all()
    serializer_class = MedicationRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    
    def get_queryset(self):
        """获取当前用户的用药记录"""
        return self.queryset.filter(medical_record__user=self.request.user)

    def perform_create(self, serializer):
        """创建记录时处理关联"""
        # 获取医疗记录
        medical_record_id = serializer.validated_data.get('medical_record').id
        try:
            medical_record = MedicalRecord.objects.get(id=medical_record_id, user=self.request.user)
            # 保存用药记录并关联到正确的医疗记录
            serializer.save(medical_record=medical_record)
            logger.info(f"创建用药记录成功: {serializer.instance.id}")
        except MedicalRecord.DoesNotExist:
            logger.error(f"创建用药记录失败: 医疗记录不存在或不属于当前用户")
            raise ValidationError({"medical_record": "所选医疗记录不存在或不属于当前用户"})
        except Exception as e:
            logger.error(f"创建用药记录异常: {str(e)}")
            raise ValidationError({"detail": str(e)})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取用药记录统计信息"""
        try:
            stats = self.get_queryset().aggregate(
                total=Count('id'),
                active_medications=Count('id', filter=Q(end_date__gt=timezone.now().date()))
            )
            return Response(stats)
        except Exception as e:
            logger.error(f"获取用药统计信息失败: {str(e)}")
            return Response({"detail": "获取统计信息失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VaccinationRecordViewSet(viewsets.ModelViewSet):
    """疫苗接种记录视图集"""
    queryset = VaccinationRecord.objects.all()
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        """获取当前用户的疫苗接种记录"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建记录时自动关联当前用户"""
        try:
            serializer.save(user=self.request.user)
            logger.info(f"创建疫苗接种记录成功: {serializer.instance.id}")
        except Exception as e:
            logger.error(f"创建疫苗接种记录失败: {str(e)}")
            raise ValidationError({"detail": str(e)})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取疫苗接种统计信息"""
        try:
            stats = self.get_queryset().aggregate(
                total=Count('id'),
                pending_next_dose=Count('id', filter=Q(next_due_date__isnull=False))
            )
            return Response(stats)
        except Exception as e:
            logger.error(f"获取疫苗接种统计信息失败: {str(e)}")
            return Response({"detail": "获取统计信息失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PhysicalExamViewSet(viewsets.ModelViewSet):
    """体检记录视图集"""
    queryset = PhysicalExam.objects.all()
    serializer_class = PhysicalExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """获取用户的体检报告"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """关联当前用户并验证数据"""
        # 手动验证血压格式（补充序列化器验证）
        bp = serializer.validated_data.get('blood_pressure')
        if bp and len(bp.split('/')) != 2:
            raise ValidationError({'blood_pressure': '血压格式错误'})
            
        # 确保report_pdf是可选的，而不是必填的
        data = serializer.validated_data
        if 'report_pdf' not in data:
            logger.info("体检记录创建：report_pdf字段为空，继续创建记录")
        
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取体检记录统计信息"""
        stats = self.get_queryset().aggregate(
            total=Count('id'),
            abnormal_count=Count('id', filter=Q(result='abnormal'))
        )
        return Response(stats)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """获取最近一次体检报告"""
        exam = self.get_queryset().last()
        serializer = self.get_serializer(exam)
        return Response(serializer.data)

class HealthOverviewAPI(viewsets.ViewSet):
    """健康总览API"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取健康记录总览统计"""
        user = request.user
        medical_records = MedicalRecord.objects.filter(user=user)
        medication_records = MedicationRecord.objects.filter(medical_record__user=user)
        vaccination_records = VaccinationRecord.objects.filter(user=user)
        physical_exams = PhysicalExam.objects.filter(user=user)

        # 统计数据
        stats = {
            'medical_records': {
                'total': medical_records.count(),
                'by_department': list(medical_records.values('department').annotate(count=Count('id')))
            },
            'medication_records': {
                'total': medication_records.count(),
                'active': medication_records.filter(end_date__gt=timezone.now().date()).count(),
            },
            'vaccination_records': {
                'total': vaccination_records.count(),
                'pending_next_dose': vaccination_records.filter(next_due_date__isnull=False).count(),
            },
            'physical_exams': {
                'total': physical_exams.count(),
                'abnormal': physical_exams.filter(result='abnormal').count(),
            }
        }
        
        # 添加最近记录的序列化数据
        stats['medical_records']['recent'] = MedicalRecordSerializer(
            medical_records.order_by('-visit_date')[:5], many=True
        ).data
        
        stats['medication_records']['recent'] = MedicationRecordSerializer(
            medication_records.order_by('-start_date')[:5], many=True
        ).data
        
        stats['vaccination_records']['recent'] = VaccinationRecordSerializer(
            vaccination_records.order_by('-vaccination_date')[:5], many=True
        ).data
        
        stats['physical_exams']['recent'] = PhysicalExamSerializer(
            physical_exams.order_by('-exam_date')[:5], many=True
        ).data
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def health_trends(self, request):
        """获取健康趋势数据"""
        user = request.user
        
        try:
            physical_exams = PhysicalExam.objects.filter(user=user).order_by('exam_date')
            
            # 确保日期格式化为字符串
            trends = {
                'dates': [],
                'weight': [],
                'bloodPressure': {
                    'systolic': [],
                    'diastolic': []
                },
                'bloodSugar': [], 
                'heart_rate': []
            }
            
            for exam in physical_exams:
                # 格式化日期为ISO标准格式
                trends['dates'].append(exam.exam_date.isoformat() if exam.exam_date else None)
                trends['weight'].append(float(exam.weight) if exam.weight else None)
                
                # 解析血压
                try:
                    systolic, diastolic = map(int, exam.blood_pressure.split('/'))
                    trends['bloodPressure']['systolic'].append(systolic)
                    trends['bloodPressure']['diastolic'].append(diastolic)
                except (ValueError, AttributeError):
                    trends['bloodPressure']['systolic'].append(None)
                    trends['bloodPressure']['diastolic'].append(None)
                    
                trends['heart_rate'].append(exam.heart_rate)
                
                # 血糖从其他字段获取，如果不存在则使用None
                trends['bloodSugar'].append(float(exam.blood_glucose) if hasattr(exam, 'blood_glucose') and exam.blood_glucose else None)
            
            return Response(trends)
            
        except Exception as e:
            logger.error(f"获取健康趋势数据失败: {str(e)}")
            return Response({
                'detail': f"获取健康趋势数据失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """获取最近的健康活动"""
        user = request.user
        
        try:
            # 获取所有类型的最近记录
            medical = MedicalRecord.objects.filter(user=user).order_by('-visit_date')[:5]
            medication = MedicationRecord.objects.filter(medical_record__user=user).order_by('-start_date')[:5]
            vaccination = VaccinationRecord.objects.filter(user=user).order_by('-vaccination_date')[:5]
            physical = PhysicalExam.objects.filter(user=user).order_by('-exam_date')[:5]
            
            activities = []
            
            # 合并并排序所有活动
            for record in medical:
                activities.append({
                    'id': record.id,
                    'type': 'medical',
                    'date': record.visit_date.isoformat() if record.visit_date else None,
                    'title': f'就医记录',
                    'description': f'就医于{record.hospital}{record.department}'
                })
                
            for record in medication:
                activities.append({
                    'id': record.id,
                    'type': 'medication',
                    'date': record.start_date.isoformat() if record.start_date else None,
                    'title': f'用药记录',
                    'description': f'开始服用{record.drug_name}'
                })
                
            for record in vaccination:
                activities.append({
                    'id': record.id,
                    'type': 'vaccination',
                    'date': record.vaccination_date.isoformat() if record.vaccination_date else None,
                    'title': f'疫苗接种',
                    'description': f'接种{record.get_vaccine_type_display()}疫苗'
                })
                
            for record in physical:
                activities.append({
                    'id': record.id,
                    'type': 'physical',
                    'date': record.exam_date.isoformat() if record.exam_date else None,
                    'title': f'体检记录',
                    'description': f'在{record.institution}进行体检'
                })
            
            # 按日期排序，最近的在前
            activities.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
            
            return Response(activities[:10])  # 只返回最近的10条活动
            
        except Exception as e:
            logger.error(f"获取最近活动失败: {str(e)}")
            return Response({
                'detail': f"获取最近活动失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecordListView(ListView):
    """展示记录列表的视图"""
    model = MedicalRecord
    template_name = 'records/record_list.html'
    context_object_name = 'records'

    def get_queryset(self):
        """返回当前用户的记录列表"""
        return MedicalRecord.objects.filter(user=self.request.user)

class RecordCreateView(CreateView):
    """处理记录创建的视图"""
    model = MedicalRecord
    fields = ['record_type', 'diagnosis', 'symptoms', 'treatment', 'occurrence_date', 'attachment']
    template_name = 'records/record_form.html'

    def form_valid(self, form):
        """在保存表单之前设置用户"""
        form.instance.user = self.request.user
        return super().form_valid(form)

