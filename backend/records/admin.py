from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    MedicalRecord,
    MedicationRecord,
    VaccinationRecord,
    PhysicalExam,
    MedicalAttachment
)

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """就医记录管理"""
    list_display = ['id', 'user', 'hospital', 'department', 'visit_date']
    list_filter = ['department', 'visit_date', 'created_at']
    search_fields = ['hospital', 'doctor', 'diagnosis']
    date_hierarchy = 'visit_date'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': (
                'user', 'visit_date', 'hospital',
                'department', 'doctor'
            )
        }),
        ('诊疗信息', {
            'fields': (
                'chief_complaint', 'diagnosis',
                'treatment', 'follow_up_date',
                'cost', 'notes'
            )
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MedicationRecord)
class MedicationRecordAdmin(admin.ModelAdmin):
    """
    用药记录管理配置
    优化药品信息的管理界面
    """
    list_display = (
        'drug_name',
        'medical_record_link',
        'formatted_duration',
        'reminder_status'
    )
    list_filter = (
        'frequency',
        'reminder_enabled'
    )
    search_fields = (
        'drug_name',
        'medical_record__diagnosis'
    )
    raw_id_fields = ('medical_record',)
    # 自定义字段方法
    def medical_record_link(self, obj):
        """创建医疗记录管理链接"""
        url = f'/admin/records/medicalrecord/{obj.medical_record.id}/change/'
        return f'<a href="{url}">{obj.medical_record.truncated_diagnosis}</a>'
    medical_record_link.short_description = _('关联记录')
    medical_record_link.allow_tags = True

    def formatted_duration(self, obj):
        """显示用药周期"""
        if obj.end_date:
            return f'{obj.start_date} 至 {obj.end_date}'
        return f'{obj.start_date} 起'
    formatted_duration.short_description = _('用药周期')

    def reminder_status(self, obj):
        """显示提醒状态"""
        if obj.reminder_enabled:
            return f'每日 {obj.reminder_time.strftime("%H:%M")}'
        return '未启用'
    reminder_status.short_description = _('提醒状态')

@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    """
    疫苗接种管理配置
    管理疫苗注射记录
    """
    list_display = (
        'user',
        'vaccine_type',
        'dose_number',
        'vaccination_date',
        'next_due_status'
    )
    list_filter = (
        'vaccine_type',
        'dose_number'
    )

    search_fields = (
        'user__username',
        'institution'
    )
    # 自定义字段
    def next_due_status(self, obj):
        """显示下次接种状态"""
        from django.utils import timezone
        if obj.next_due_date:
            if obj.next_due_date < timezone.now().date():
                return '已过期'
            return f'需在 {obj.next_due_date} 前接种'
        return '无需后续接种'
    next_due_status.short_description = _('接种状态')

@admin.register(PhysicalExam)
class PhysicalExamAdmin(admin.ModelAdmin):
    """
    体检报告管理配置
    管理结构化体检数据
    """
    list_display = (
        'user',
        'exam_date',
        'bmi_display',
        'blood_pressure',
        'report_link'
    )
    list_filter = (
        'exam_date',
        ('user', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = (
        'user__username',
        'institution'
    )
    # 表单验证
    def save_model(self, request, obj, form, change):
        """保存前验证血压格式"""
        if '/' not in obj.blood_pressure:
            from django.core.exceptions import ValidationError
            raise ValidationError("血压格式必须为 收缩压/舒张压")
        super().save_model(request, obj, form, change)

    # 自定义字段
    def bmi_display(self, obj):
        """显示BMI及分类"""
        bmi = obj.calculate_bmi()
        if not bmi:
            return '-'
        status = '正常'
        if bmi < 18.5:
            status = '偏瘦'
        elif bmi >= 24:
            status = '超重'
        return f'{bmi} ({status})'
    bmi_display.short_description = _('体质指数')

    def report_link(self, obj):
        """生成报告下载链接"""
        if obj.report_pdf:
            return f'<a href="{obj.report_pdf.url}" download>下载报告</a>'
        return '-'
    report_link.short_description = _('体检报告')
    report_link.allow_tags = True

@admin.register(MedicalAttachment)
class MedicalAttachmentAdmin(admin.ModelAdmin):
    """就医记录附件管理"""
    list_display = ['id', 'record', 'name', 'size', 'upload_time']
    list_filter = ['upload_time']
    search_fields = ['name']
    readonly_fields = ['size', 'upload_time']

# 可选：添加全局管理配置
admin.site.site_header = _('健康档案管理系统')
admin.site.site_title = _('健康数据管理')
admin.site.index_title = _('仪表板')

