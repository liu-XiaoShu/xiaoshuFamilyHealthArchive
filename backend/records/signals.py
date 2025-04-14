from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import MedicalRecord, MedicationRecord, VaccinationRecord, PhysicalExam
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=MedicalRecord)
def handle_medical_record_save(sender, instance, created, **kwargs):
    """
    处理就医记录保存后的操作
    """
    if created:
        # 发送通知邮件
        if instance.user.email:
            subject = '新的就医记录已创建'
            message = f'''
            您好 {instance.user.username}，
            
            您的新就医记录已成功创建：
            医院：{instance.hospital}
            科室：{instance.department}
            就诊日期：{instance.visit_date}
            
            感谢使用家庭健康档案系统！
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.user.email],
                fail_silently=True
            )

@receiver(post_save, sender=MedicationRecord)
def handle_medication_record_save(sender, instance, created, **kwargs):
    """
    处理用药记录保存后的操作
    """
    if created and instance.reminder_enabled:
        # 创建用药提醒
        from .models import Reminder
        Reminder.objects.create(
            user=instance.user,
            title=f'用药提醒：{instance.drug_name}',
            description=f'请按时服用{instance.drug_name}，剂量：{instance.dosage}',
            reminder_time=instance.next_dose_time,
            record_type='medication',
            record_id=instance.id
        )

@receiver(post_save, sender=VaccinationRecord)
def handle_vaccination_record_save(sender, instance, created, **kwargs):
    """
    处理疫苗接种记录保存后的操作
    """
    if created and instance.next_due_date:
        # 创建疫苗接种提醒
        from .models import Reminder
        Reminder.objects.create(
            user=instance.user,
            title=f'疫苗接种提醒：{instance.vaccine_type}',
            description=f'请按时接种{instance.vaccine_type}第{instance.dose_number + 1}剂',
            reminder_time=instance.next_due_date,
            record_type='vaccination',
            record_id=instance.id
        )

@receiver(post_save, sender=PhysicalExam)
def handle_physical_exam_save(sender, instance, created, **kwargs):
    """
    处理体检记录保存后的操作
    """
    if created:
        # 检查异常指标
        abnormal_indicators = []
        if instance.bmi and (instance.bmi < 18.5 or instance.bmi > 24):
            abnormal_indicators.append(f'BMI: {instance.bmi}')
        if instance.blood_pressure and instance.blood_pressure > '140/90':
            abnormal_indicators.append(f'血压: {instance.blood_pressure}')
            
        if abnormal_indicators:
            # 创建异常指标提醒
            from .models import Reminder
            Reminder.objects.create(
                user=instance.user,
                title='体检异常指标提醒',
                description=f'您的体检报告中有以下异常指标：{", ".join(abnormal_indicators)}',
                reminder_time=timezone.now(),
                record_type='physical_exam',
                record_id=instance.id
            )

@receiver(pre_delete, sender=MedicalRecord)
def handle_medical_record_delete(sender, instance, **kwargs):
    """
    处理就医记录删除前的操作
    """
    # 删除关联的附件
    if instance.attachment:
        instance.attachment.delete(save=False) 