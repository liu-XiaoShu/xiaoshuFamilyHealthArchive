from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import re
from datetime import datetime
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
import structlog
from .storage import EncryptedFileStorage
from django.conf import settings
from django.utils import timezone

logger = structlog.get_logger(__name__)

def validate_file_size(file):
    """验证文件大小不超过10MB"""
    max_size_mb = 10
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"文件大小不能超过{max_size_mb}MB")

def validate_file_name(file):
    """验证文件名不包含非法字符"""
    if not re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', file.name):
        raise ValidationError("文件名包含非法字符或格式不正确")

class AuditModelMixin:
    """审计日志混入类"""
    
    def log_action(self, user_id, action_flag, change_message=''):
        """记录模型操作日志"""
        LogEntry.objects.log_action(
            user_id=user_id,
            content_type_id=self.get_content_type_id(),
            object_id=self.pk,
            object_repr=str(self),
            action_flag=action_flag,
            change_message=change_message
        )
        
        # 结构化日志记录
        logger.info(
            "record_audit_log",
            user_id=user_id,
            model=self.__class__.__name__,
            object_id=self.pk,
            action=action_flag,
            message=change_message
        )

class MedicalRecord(models.Model):
    """就医记录模型"""
    DEPARTMENT_CHOICES = [
        ('internal', '内科'),
        ('surgery', '外科'),
        ('pediatrics', '儿科'),
        ('obstetrics', '妇产科'),
        ('ophthalmology', '眼科'),
        ('ent', '耳鼻喉科'),
        ('dental', '口腔科'),
        ('dermatology', '皮肤科'),
        ('psychiatry', '精神科'),
        ('tcm', '中医科'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_records')
    visit_date = models.DateField('就诊日期', default=timezone.now)
    hospital = models.CharField('医院', max_length=100, default='未知医院')
    department = models.CharField('科室', max_length=20, choices=DEPARTMENT_CHOICES, default='internal')
    doctor = models.CharField('医生', max_length=50, default='未知医生')
    chief_complaint = models.TextField('主诉', default='无')
    diagnosis = models.TextField('诊断结果', default='待诊断')
    treatment = models.TextField('处理方案', default='待处理')
    follow_up_date = models.DateField('复诊日期', null=True, blank=True)
    cost = models.DecimalField('费用', max_digits=10, decimal_places=2, default=0)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '就医记录'
        verbose_name_plural = verbose_name
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.user.username} - {self.hospital} - {self.visit_date}"

class MedicalAttachment(models.Model):
    """就医记录附件"""
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='attachments')
    name = models.CharField('文件名', max_length=255)
    file = models.FileField('文件', upload_to='medical_records/')
    size = models.IntegerField('文件大小')
    upload_time = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        verbose_name = '就医记录附件'
        verbose_name_plural = verbose_name
        ordering = ['-upload_time']

    def __str__(self):
        return self.name

class MedicationRecord(models.Model):
    """
    用药记录模型
    跟踪用户的药物使用情况
    """
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='medications',
        verbose_name=_('关联医疗记录')
    )
    # 药物信息
    drug_name = models.CharField(
        max_length=100,
        verbose_name=_('药品名称')
    )
    dosage = models.CharField(
        max_length=50,
        verbose_name=_('剂量规格'),
        help_text=_('例如：500mg/片')
    )
    # 用药频率选项
    class Frequency(models.TextChoices):
        QD = 'QD', _('每日一次')
        BID = 'BID', _('每日两次')
        TID = 'TID', _('每日三次')
        QW = 'QW', _('每周一次')
        PRN = 'PRN', _('按需服用')
    frequency = models.CharField(
        max_length=3,
        choices=Frequency.choices,
        default=Frequency.QD,
        verbose_name=_('用药频率')
    )
    # 时间管理
    start_date = models.DateField(
        verbose_name=_('开始日期')
    )
    end_date = models.DateField(
        verbose_name=_('结束日期'),
        blank=True,
        null=True
    )
    # 用药提醒
    reminder_enabled = models.BooleanField(
        default=False,
        verbose_name=_('启用提醒')
    )
    reminder_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name=_('提醒时间')
    )

    class Meta:
        verbose_name = _('用药记录')
        verbose_name_plural = _('用药记录')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['medical_record']),
            models.Index(fields=['drug_name']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    def __str__(self):
        return f"{self.drug_name} ({self.get_frequency_display()})"

    def duration_days(self):
        """计算用药持续天数"""
        if self.end_date:
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(self.end_date, '%Y-%m-%d').date()
            return (end_date - start_date).days + 1
        return None

class VaccinationRecord(models.Model):
    """
    疫苗接种记录模型
    记录用户的疫苗注射历史
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='vaccinations',
        verbose_name=_('接种用户')
    )
    # 疫苗类型选项
    class VaccineType(models.TextChoices):
        COVID = 'CV', _('新冠疫苗')
        FLU = 'FL', _('流感疫苗')
        HPV = 'HPV', _('HPV疫苗')
        HEPB = 'HB', _('乙肝疫苗')
    vaccine_type = models.CharField(
        max_length=3,
        choices=VaccineType.choices,
        verbose_name=_('疫苗类型')
    )
    # 接种信息
    dose_number = models.PositiveSmallIntegerField(
        verbose_name=_('剂次'),
        help_text=_('当前接种的是第几剂')
    )
    vaccination_date = models.DateField(
        verbose_name=_('接种日期')
    )
    next_due_date = models.DateField(
        verbose_name=_('下次接种日期'),
        blank=True,
        null=True
    )
    # 接种机构
    institution = models.CharField(
        max_length=200,
        verbose_name=_('接种机构')
    )
    batch_number = models.CharField(
        max_length=50,
        verbose_name=_('疫苗批号')
    )

    class Meta:
        verbose_name = _('疫苗接种记录')
        verbose_name_plural = _('疫苗接种记录')
        unique_together = ['user', 'vaccine_type', 'dose_number']
        indexes = [
            models.Index(fields=['user', 'vaccine_type']),
            models.Index(fields=['vaccination_date']),
        ]
    def __str__(self):
        return f"{self.user}的{self.get_vaccine_type_display()}第{self.dose_number}剂"

class PhysicalExam(AuditModelMixin, models.Model):
    """
    体检报告模型
    存储用户的定期体检数据
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='physical_exams',
        verbose_name=_('所属用户')
    )
    exam_date = models.DateField(
        verbose_name=_('体检日期')
    )
    height = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_('身高(cm)')
    )
    weight = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_('体重(kg)')
    )
    blood_pressure = models.CharField(
        max_length=7,
        verbose_name=_('血压(mmHg)'),
        help_text=_('格式：收缩压/舒张压 如：120/80')
    )
    heart_rate = models.PositiveSmallIntegerField(
        verbose_name=_('心率(bpm)')
    )
    # 血液检查结果
    blood_glucose = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name=_('空腹血糖(mmol/L)')
    )
    cholesterol = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name=_('总胆固醇(mmol/L)')
    )
    # 报告文件
    report_pdf = models.FileField(
        upload_to='physical_exams/%Y/%m/',
        storage=EncryptedFileStorage(),
        verbose_name=_('体检报告PDF'),
        help_text=_('上传体检报告PDF文件（最大10MB，文件将被加密存储）'),
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            validate_file_size,
            validate_file_name,
        ]
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('上传时间')
    )

    class Meta:
        verbose_name = _('体检报告')
        verbose_name_plural = _('体检报告')
        ordering = ['-exam_date']
        indexes = [
            models.Index(fields=['user', 'exam_date']),
            models.Index(fields=['created_at']),
        ]
    def calculate_bmi(self):
        """计算体质指数BMI"""
        if self.height and self.weight:
            return round(self.weight / ((self.height/100) ** 2), 1)
        return None
    calculate_bmi.short_description = _('体质指数')

    def __str__(self):
        return f"{self.user}的{self.exam_date}体检报告"

