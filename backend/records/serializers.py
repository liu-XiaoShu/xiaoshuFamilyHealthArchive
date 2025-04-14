from rest_framework import serializers
from django.utils import timezone
from .models import (
    MedicalRecord,
    MedicationRecord,
    VaccinationRecord,
    PhysicalExam,
    Reminder
)
from users.serializers import UserProfileSerializer
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class MedicationRecordSerializer(serializers.ModelSerializer):
    """
    用药记录序列化器
    处理药物信息的创建和更新
    包含用药提醒设置验证
    """
    medical_record = serializers.PrimaryKeyRelatedField(
        queryset=MedicalRecord.objects.all(),
        help_text=_('关联的医疗记录ID')
    )
    frequency_display = serializers.CharField(
        source='get_frequency_display',
        read_only=True,
        help_text=_('用药频率显示名称')
    )
    remaining_days = serializers.SerializerMethodField(
        help_text=_('剩余用药天数（如已设置结束日期）')
    )

    class Meta:
        model = MedicationRecord
        fields = [
            'id', 'medical_record', 'drug_name', 'dosage',
            'frequency', 'frequency_display', 'start_date', 'end_date',
            'reminder_enabled', 'reminder_time', 'remaining_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_remaining_days(self, obj):
        """计算剩余用药天数"""
        if obj.end_date:
            delta = obj.end_date - timezone.now().date()
            return max(delta.days, 0)
        return None

    def validate(self, data):
        """自定义验证"""
        # 验证用药频率
        if 'frequency' in data and data['frequency'] not in dict(MedicationRecord.Frequency.choices):
            raise serializers.ValidationError({"frequency": "无效的用药频率"})
            
        # 验证开始和结束日期
        if 'end_date' in data and 'start_date' in data:
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({"end_date": "结束日期不能早于开始日期"})
                
        # 验证提醒时间
        if data.get('reminder_enabled') and not data.get('reminder_time'):
            raise serializers.ValidationError({"reminder_time": "启用提醒时必须设置提醒时间"})
            
        return data


class MedicalRecordSerializer(serializers.ModelSerializer):
    """就医记录序列化器"""
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'user', 'visit_date', 'hospital', 'department',
            'doctor', 'chief_complaint', 'diagnosis', 'treatment',
            'follow_up_date', 'cost', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        """自定义验证"""
        # 验证就诊日期
        if data['visit_date'] > timezone.now().date():
            raise serializers.ValidationError("就诊日期不能晚于今天")
            
        # 验证复诊日期
        if data.get('follow_up_date'):
            if data['follow_up_date'] < data['visit_date']:
                raise serializers.ValidationError("复诊日期不能早于就诊日期")
                
        # 验证费用
        if data.get('cost') is not None and data['cost'] < 0:
            raise serializers.ValidationError("费用不能为负数")
            
        return data


class VaccinationRecordSerializer(serializers.ModelSerializer):
    """
    疫苗接种记录序列化器
    处理疫苗数据的验证和展示
    包含剂次唯一性验证
    """
    # 显示疫苗类型中文名称
    vaccine_type_display = serializers.CharField(
        source='get_vaccine_type_display',
        read_only=True,
        help_text=_('疫苗类型显示名称')
    )
    
    # 兼容前端API
    hospital = serializers.CharField(
        source='institution',
        required=False,
        help_text=_('接种医院(兼容字段)')
    )
    
    next_dose_date = serializers.DateField(
        source='next_due_date',
        required=False,
        help_text=_('下次接种日期(兼容字段)')
    )
    
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = VaccinationRecord
        fields = [
            'id', 'user', 'vaccine_type', 'vaccine_type_display', 
            'dose_number', 'vaccination_date', 'next_due_date', 'next_dose_date',
            'institution', 'hospital', 'batch_number'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        """自定义验证"""
        # 验证接种日期
        if data['vaccination_date'] > timezone.now().date():
            raise serializers.ValidationError("接种日期不能晚于今天")
            
        # 验证剂次
        if data['dose_number'] <= 0:
            raise serializers.ValidationError("剂次必须大于0")
            
        # 验证疫苗类型
        valid_vaccines = ['乙肝', '卡介苗', '脊灰', '百白破', '麻疹', '其他']
        if data['vaccine_type'] not in valid_vaccines:
            raise serializers.ValidationError("无效的疫苗类型")
            
        return data

    def create(self, validated_data):
        """创建疫苗接种记录"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("必须登录才能创建接种记录")
        
        validated_data['user'] = request.user
        return super().create(validated_data)

class PhysicalExamSerializer(serializers.ModelSerializer):
    """
    体检报告序列化器
    处理体检数据的序列化和BMI计算
    包含血压格式验证
    """
    # 计算字段
    bmi = serializers.SerializerMethodField(
        help_text=_('体质指数（自动计算）')
    )
    # 文件处理
    report_url = serializers.FileField(
        source='report_pdf',
        read_only=True,
        help_text=_('体检报告下载URL')
    )
    # 允许前端上传PDF报告文件（可选）
    report_pdf = serializers.FileField(
        required=False,
        allow_null=True,
        help_text=_('体检报告PDF文件（可选）')
    )
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = PhysicalExam
        fields = [
            'id', 'user', 'exam_date', 'height', 'weight',
            'bmi', 'blood_pressure', 'heart_rate', 'temperature',
            'blood_type', 'blood_sugar', 'cholesterol', 'notes',
            'report_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'bmi', 'created_at', 'updated_at']

    def get_bmi(self, obj):
        """从模型方法获取BMI值"""
        return obj.calculate_bmi()

    def validate(self, data):
        """自定义验证"""
        # 验证体检日期
        if data['exam_date'] > timezone.now().date():
            raise serializers.ValidationError("体检日期不能晚于今天")
            
        # 验证身高体重
        if data['height'] <= 0 or data['weight'] <= 0:
            raise serializers.ValidationError("身高和体重必须大于0")
            
        # 验证血压格式
        if data.get('blood_pressure'):
            try:
                systolic, diastolic = map(int, data['blood_pressure'].split('/'))
                if systolic <= 0 or diastolic <= 0:
                    raise ValueError
            except (ValueError, AttributeError):
                raise serializers.ValidationError("血压格式不正确，应为'收缩压/舒张压'")
                
        return data

    def create(self, validated_data):
        """创建体检报告"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("必须登录才能创建体检报告")
        
        validated_data['user'] = request.user
        return super().create(validated_data)

class ReminderSerializer(serializers.ModelSerializer):
    """提醒记录序列化器"""
    class Meta:
        model = Reminder
        fields = [
            'id', 'user', 'title', 'description',
            'reminder_time', 'is_completed', 'record_type',
            'record_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        """自定义验证"""
        # 验证提醒时间
        if data['reminder_time'] < timezone.now():
            raise serializers.ValidationError("提醒时间不能早于当前时间")
            
        # 验证记录类型
        valid_types = ['medical', 'medication', 'vaccination', 'physical_exam']
        if data['record_type'] not in valid_types:
            raise serializers.ValidationError("无效的记录类型")
            
        return data

