// 体检记录类型
export interface PhysicalExam {
  id?: number
  user_id?: number
  exam_date: string
  hospital: string
  exam_type: string
  height: number
  weight: number
  systolic_pressure: number
  diastolic_pressure: number
  heart_rate: number
  temperature: number
  exam_items: string[]
  result: 'normal' | 'abnormal'
  abnormal_items?: { name: string; value: string; reference: string }[]
  doctor_advice?: string
  next_exam_date?: string
  notes?: string
}

// 就医记录类型
export interface MedicalRecord {
  id?: number
  user_id?: number
  visit_date: string
  hospital: string
  department: string
  doctor_name?: string
  reason: string
  diagnosis?: string
  prescriptions?: string[]
  notes?: string
}

// 用药记录类型
export interface MedicationRecord {
  id?: number
  medical_record: number
  drug_name: string
  dosage: string
  frequency: 'QD' | 'BID' | 'TID' | 'QW' | 'PRN'
  start_date: string
  end_date?: string
  reminder_enabled: boolean
  reminder_time?: string
  notes?: string
}

// 疫苗接种记录类型
export interface VaccinationRecord {
  id?: number
  user_id?: number
  vaccine_name: string
  vaccine_type: string
  hospital: string
  vaccination_date: string
  dose_number: number
  batch_number?: string
  manufacturer?: string
  site: string
  next_dose_date?: string
  reactions?: string[]
  allergy_details?: string
  notes?: string
}

// 体检报告接口
export interface PhysicalExamReport {
  id: number
  user: number
  exam_date: string
  height: number
  weight: number
  blood_pressure: string
  heart_rate: number
  blood_glucose?: number
  cholesterol?: number
  report_pdf?: string
  created_at: string
}

// 分页响应接口
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// 就医记录表单数据类型
export interface MedicalRecordFormData {
  visitDate: string
  hospital: string
  department: string
  reason: string
  diagnosis: string
  prescription: string[]
  attachments?: File[]
}

// 用药记录表单数据类型
export interface MedicationRecordFormData {
  medicationName: string
  dosage: string
  frequency: string
  startDate: string
  endDate: string
  sideEffects: string[]
  notes?: string
}

// 疫苗接种记录表单数据类型
export interface VaccinationRecordFormData {
  vaccineName: string
  vaccinationDate: string
  manufacturer: string
  batchNumber: string
  vaccinationSite: string
  nextDoseDate?: string
  reactions: string[]
  notes?: string
}

// 体检记录表单数据类型
export interface PhysicalExamFormData {
  examDate: string
  hospital: string
  height: number
  weight: number
  bloodPressure: string
  heartRate: number
  abnormalItems?: string[]
  attachments?: File[]
  notes?: string
}

// 健康概览数据类型
export interface HealthOverview {
  recentVisits: number
  activeMedications: number
  upcomingVaccinations: number
  latestPhysicalExam?: {
    date: string
    hospital: string
    bmi: number
  }
}

// 健康趋势数据类型
export interface HealthTrend {
  date: string
  weight?: number
  bloodPressure?: string
  heartRate?: number
  bmi?: number
}

// 最近活动数据类型
export interface RecentActivity {
  id: string
  type: 'medical' | 'medication' | 'vaccination' | 'physical'
  date: string
  title: string
  description: string
}

// 记录相关的类型定义

export interface BaseRecord {
  id: number
  user_id: number
  created_at: string
  updated_at: string
  description?: string
}

// 体检记录
export interface PhysicalExam extends BaseRecord {
  date: string
  hospital: string
  doctor: string
  height?: number
  weight?: number
  blood_pressure?: string
  heart_rate?: number
  blood_oxygen?: number
  temperature?: number
  report_url?: string
}

// 就诊记录
export interface MedicalRecord extends BaseRecord {
  diagnosis: string
  treatment: string
  hospital: string
  doctor: string
  date: string
  is_follow_up: boolean
  symptoms: string
  prescription_url?: string
}

// 用药记录
export interface MedicationRecord extends BaseRecord {
  name: string
  dosage: string
  frequency: string
  start_date: string
  end_date?: string
  prescriber?: string
  pharmacy?: string
  is_ongoing: boolean
  notes?: string
}

// 疫苗接种记录
export interface VaccinationRecord extends BaseRecord {
  vaccine_name: string
  manufacturer: string
  batch_number: string
  date: string
  location: string
  next_dose_date?: string
  certificate_url?: string
}

// 异常器官相关记录
export interface RelatedRecord {
  id: number
  type: string // 'medical' | 'medication' | 'vaccination' | 'physical-exam'
  title: string
  date: string
  summary: string
}

// 健康统计数据
export interface HealthStatistics {
  totalRecords: number
  medicalRecords: number
  medicationRecords: number
  vaccinationRecords: number
  physicalExams: number
}

// 健康趋势数据点
export interface HealthTrendPoint {
  date: string
  value: number
}

// 健康趋势数据
export interface HealthTrend {
  category: string // 'blood_pressure', 'heart_rate', 'weight', etc.
  label: string
  unit: string
  data: HealthTrendPoint[]
}

// 最近活动
export interface RecentActivity extends BaseRecord {
  id: number
  type: string // 'medical' | 'medication' | 'vaccination' | 'physical-exam'
  title: string
  date: string
  description: string
  icon?: string
} 