from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    MedicalRecord,
    MedicationRecord,
    VaccinationRecord,
    PhysicalExam
)

User = get_user_model()

class MedicalModelTests(TestCase):
    """
    核心模型测试类
    验证各模型的基础功能和业务逻辑
    """
    def setUp(self):
        """初始化测试数据"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        # 创建医疗记录测试文件
        self.test_file = SimpleUploadedFile(
            name='test_report.pdf',
            content=b'file_content',
            content_type='application/pdf'
        )

    def test_create_medical_record(self):
        """测试医疗记录创建及文件处理"""
        record = MedicalRecord.objects.create(
            user=self.user,
            record_type='OP',
            diagnosis='Sample Diagnosis',
            attachment=self.test_file,
            occurrence_date='2024-01-01'
        )
        # 验证基础字段
        self.assertEqual(record.diagnosis, 'Sample Diagnosis')
        self.assertTrue(record.attachment.name.endswith('.pdf'))

        # 验证自动生成字段
        self.assertIsNotNone(record.created_at)

    def test_medication_duration_calculation(self):
        """测试用药周期计算逻辑"""
        medical_record = MedicalRecord.objects.create(
            user=self.user,
            occurrence_date='2024-01-01'
        )
        medication = MedicationRecord.objects.create(
            medical_record=medical_record,
            drug_name='Aspirin',
            start_date='2024-01-01',
            end_date='2024-01-07'
        )
        # 验证持续天数计算
        self.assertEqual(medication.duration_days(), 7)
        # 测试无结束日期情况
        medication.end_date = None
        self.assertIsNone(medication.duration_days())

    def test_vaccine_dose_uniqueness(self):
        """测试疫苗剂次唯一性约束"""
        VaccinationRecord.objects.create(
            user=self.user,
            vaccine_type='COVID',
            dose_number=1,
            vaccination_date='2024-01-01'
        )
        # 尝试创建重复剂次应抛出错误
        with self.assertRaises(Exception):
            VaccinationRecord.objects.create(
                user=self.user,
                vaccine_type='COVID',
                dose_number=1
            )

    def test_bmi_calculation(self):
        """测试BMI自动计算逻辑"""
        exam = PhysicalExam.objects.create(
            user=self.user,
            height=175,  # 厘米
            weight=70,    # 公斤
            exam_date='2024-01-01',
            heart_rate=70  # 添加 heart_rate 字段
        )
        # 计算预期BMI值：70 / (1.75^2) ≈ 22.86
        expected_bmi = round(70 / (1.75 ** 2), 2)
        self.assertEqual(exam.calculate_bmi(), expected_bmi)
        # 测试无身高体重数据
        exam.height = None
        self.assertIsNone(exam.calculate_bmi())

class MedicalAPITests(TestCase):
    """
    API端点测试类
    验证REST接口的功能和权限控制
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            password='testpass'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staffpass',
            is_staff=True
        )
        # 创建测试数据
        self.medical_record = MedicalRecord.objects.create(
            user=self.user,
            diagnosis='API Test Diagnosis',
            occurrence_date='2024-01-01'
        )
        # 认证普通用户
        self.client.force_authenticate(user=self.user)

    def test_medical_record_list(self):
        """测试医疗记录列表权限控制"""
        # 创建其他用户的记录
        other_user = User.objects.create_user(username='other')
        MedicalRecord.objects.create(
            user=other_user,
            diagnosis='Other',
            occurrence_date='2024-01-01'
        )
        response = self.client.get('/api/medical-records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 验证只能看到自己的记录
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['diagnosis'], 'API Test Diagnosis')

    def test_create_medication(self):
        """测试创建用药记录流程"""
        payload = {
            'medical_record': self.medical_record.id,
            'drug_name': 'Paracetamol',
            'dosage': '500mg',
            'frequency': 'QD',
            'start_date': '2024-03-01'
        }
        response = self.client.post('/api/medications/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 验证关联关系
        medication = MedicationRecord.objects.get(id=response.data['id'])
        self.assertEqual(medication.medical_record, self.medical_record)

    def test_admin_access(self):
        """测试管理员权限覆盖"""
        # 使用管理员身份
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(f'/api/medical-records/{self.medical_record.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_access(self):
        """测试未授权访问防护"""
        # 清除认证
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/medical-records/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ValidationTests(TestCase):
    """
    数据验证测试类
    验证序列化器的自定义校验规则
    """
    def setUp(self):
        self.user = User.objects.create_user(username='validator')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_future_medical_date(self):
        """测试未来日期校验"""
        payload = {
            'diagnosis': 'Invalid Date',
            'occurrence_date': '2025-01-01'
        }
        response = self.client.post('/api/medical-records/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('occurrence_date', response.data)

    def test_blood_pressure_format(self):
        """测试血压格式验证"""
        invalid_payloads = [
            {'blood_pressure': '120-80'},  # 错误分隔符
            {'blood_pressure': '90/150'},  # 舒张压高于收缩压
            {'blood_pressure': 'string'}   # 非数字
        ]

        for data in invalid_payloads:
            response = self.client.post('/api/physical-exams/', data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('blood_pressure', response.data)

    def test_vaccine_dose_range(self):
        """测试疫苗剂次范围校验"""
        payload = {
            'vaccine_type': 'HPV',
            'dose_number': 11  # 超过最大值
        }
        response = self.client.post('/api/vaccinations/', payload)
        self.assertContains(response, '1-10', status_code=400)

class FileUploadTests(TestCase):
    """
    文件上传测试类
    验证医疗文件上传和处理逻辑
    """
    def setUp(self):
        self.user = User.objects.create_user(username='fileuser')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_pdf_upload(self):
        """测试合法PDF文件上传"""
        test_file = SimpleUploadedFile(
            name='valid.pdf',
            content=b'%PDF-1.4 mock content',
            content_type='application/pdf'
        )
        response = self.client.post('/api/medical-records/', {
            'diagnosis': 'PDF Test',
            'attachment': test_file
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attachment_url', response.data)

    def test_invalid_file_type(self):
        """测试非法文件类型拦截"""
        test_file = SimpleUploadedFile(
            name='invalid.exe',
            content=b'malicious content',
            content_type='application/exe'
        )
        response = self.client.post('/api/medical-records/', {
            'diagnosis': 'Invalid File',
            'attachment': test_file
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Unsupported file type', str(response.data))

