from rest_framework import serializers
from django.utils import timezone
from .models import (
    MedicalRecord,
    MedicationRecord,
    VaccinationRecord,
    PhysicalExam,
    MedicalAttachment
)
from users.serializers import UserProfileSerializer
from django.utils.translation import gettext_lazy as _

class MedicationRecordSerializer(serializers.ModelSerializer):
    """
    用药记录序列化器
    处理药物信息的创建和更新
    包含用药提醒设置验证
    """
    # 显示关联医疗记录ID
    medical_record = serializers.PrimaryKeyRelatedField(
        queryset=MedicalRecord.objects.all(),
        help_text=_('关联的医疗记录ID')
    )
    # 显示用药频率中文名称
    frequency_display = serializers.CharField(
        source='get_frequency_display',
        read_only=True,
        help_text=_('用药频率显示名称')
    )
    # 计算剩余天数（只读）
    remaining_days = serializers.SerializerMethodField(
        help_text=_('剩余用药天数（如已设置结束日期）')
    )

    class Meta:
        model = MedicationRecord
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def get_remaining_days(self, obj):
        """计算剩余用药天数"""
        if obj.end_date:
            delta = obj.end_date - timezone.now().date()
            return max(delta.days, 0)
        return None

    def validate(self, data):
        """验证日期逻辑"""
        # 结束日期不能早于开始日期
        if data.get('end_date') and data['end_date'] < data['start_date']:
            raise serializers.ValidationError({
                'end_date': _('结束日期不能早于开始日期')
            })
        # 如果启用提醒必须设置时间
        if data.get('reminder_enabled') and not data.get('reminder_time'):
            raise serializers.ValidationError({
                'reminder_time': _('启用提醒必须设置具体时间')
            })
        return data


class MedicalAttachmentSerializer(serializers.ModelSerializer):
    """就医记录附件序列化器"""
    class Meta:
        model = MedicalAttachment
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class MedicalRecordSerializer(serializers.ModelSerializer):
    """就医记录序列化器"""
    attachments = MedicalAttachmentSerializer(many=True, read_only=True)
    department_display = serializers.CharField(source='get_department_display', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


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
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate_dose_number(self, value):
        """验证剂次数值合理性"""
        if value < 1 or value > 10:
            raise serializers.ValidationError(_("剂次应在1-10之间"))
        return value

    def validate(self, data):
        """剂次唯一性验证"""
        if self.instance is None:  # 创建操作
            exists = VaccinationRecord.objects.filter(
                user=self.context['request'].user,
                vaccine_type=data['vaccine_type'],
                dose_number=data['dose_number']
            ).exists()
            if exists:
                raise serializers.ValidationError(_("该疫苗剂次已存在"))
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
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def get_bmi(self, obj):
        """从模型方法获取BMI值"""
        return obj.calculate_bmi()

    def validate_blood_pressure(self, value):
        """验证血压格式"""
        if not '/' in value:
            raise serializers.ValidationError("血压格式错误，应为'收缩压/舒张压'")
        try:
            systolic, diastolic = map(int, value.split('/'))
            if not (60 <= systolic <= 200 and 40 <= diastolic <= 120):
                raise serializers.ValidationError("血压数值超出正常范围")
        except ValueError:
            raise serializers.ValidationError("血压必须是数字")
        return value

    def validate_exam_date(self, value):
        """验证体检日期不能是未来日期"""
        if value > timezone.now().date():
            raise serializers.ValidationError("体检日期不能是未来日期")
        return value

    def create(self, validated_data):
        """创建体检报告"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("必须登录才能创建体检报告")
        
        validated_data['user'] = request.user
        return super().create(validated_data)

