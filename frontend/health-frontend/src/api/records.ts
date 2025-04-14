// 健康记录API
import api from './index'
import type { AxiosResponse } from 'axios'
import { API_BASE_URL } from './config'

// 接口定义

// 体检记录类型
export interface PhysicalExam {
  id?: number
  exam_date: string
  hospital: string
  exam_type: string
  height?: number
  weight?: number
  blood_pressure?: string
  blood_sugar?: number
  heart_rate?: number
  report?: File | string
  report_url?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

// 就医记录类型
export interface MedicalRecord {
  id?: number
  visit_date: string
  hospital: string
  department: string
  doctor: string
  diagnosis: string
  symptoms: string
  treatment: string
  follow_up?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

// 用药记录类型
export interface MedicationRecord {
  id?: number
  medication_name: string
  start_date: string
  end_date?: string
  dosage: string
  frequency: string
  status: 'active' | 'completed' | 'discontinued'
  prescribed_by?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

// 疫苗接种记录
export interface VaccinationRecord {
  id?: number
  vaccine_name: string
  vaccine_type: string
  vaccination_date: string
  next_dose_date?: string
  administered_by: string
  notes?: string
  created_at?: string
  updated_at?: string
}

// 健康统计信息
export interface HealthStatistics {
  medical_records_count: number
  latest_medical_record?: {
    visit_date: string
    hospital: string
    diagnosis: string
  }
  medication_records_count: number
  active_medications_count: number
  latest_medication?: {
    medication_name: string
    status: string
  }
  vaccinations_count: number
  latest_vaccination?: {
    vaccine_name: string
    vaccination_date: string
  }
  physical_exams_count: number
  latest_physical_exam?: {
    exam_date: string
    hospital: string
    exam_type: string
  }
  upcoming_follow_ups?: Array<{
    type: string
    date: string
    detail: string
  }>
}

// 健康趋势
export interface HealthTrend {
  dates: string[]
  weight?: number[]
  height?: number[]
  blood_pressure?: {
    systolic: number[]
    diastolic: number[]
  }
  blood_sugar?: number[]
  heart_rate?: number[]
  medications_count?: number[]
  medical_visits_count?: number[]
}

// 最近活动
export interface RecentActivity {
  id: number
  type: 'medical' | 'medication' | 'vaccination' | 'physical'
  date: string
  title: string
  description: string
  link?: string
}

// API 函数
export const recordsApi = {
  // 体检记录API
  getPhysicalExams: (): Promise<AxiosResponse<PhysicalExam[]>> => {
    return api.get('/records/physical-exam/')
  },

  getPhysicalExam: (id: number): Promise<AxiosResponse<PhysicalExam>> => {
    return api.get(`/records/physical-exam/${id}/`)
  },

  createPhysicalExam: (data: FormData): Promise<AxiosResponse<PhysicalExam>> => {
    console.log('创建体检记录数据:', data)
    return api.post('/records/physical-exam/', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  updatePhysicalExam: (id: number, data: FormData): Promise<AxiosResponse<PhysicalExam>> => {
    console.log('更新体检记录数据:', id, data)
    return api.patch(`/records/physical-exam/${id}/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  deletePhysicalExam: (id: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/records/physical-exam/${id}/`)
  },

  getPhysicalExamReport: (id: number): Promise<AxiosResponse<Blob>> => {
    return api.get(`/records/physical-exam/${id}/report/`, {
      responseType: 'blob'
    })
  },

  // 就医记录API
  getMedicalRecords: (): Promise<AxiosResponse<MedicalRecord[]>> => {
    return api.get('/records/medical/')
  },

  getMedicalRecord: (id: number): Promise<AxiosResponse<MedicalRecord>> => {
    return api.get(`/records/medical/${id}/`)
  },

  createMedicalRecord: (data: MedicalRecord): Promise<AxiosResponse<MedicalRecord>> => {
    console.log('创建就医记录数据:', data)
    return api.post('/records/medical/', data)
  },

  updateMedicalRecord: (id: number, data: Partial<MedicalRecord>): Promise<AxiosResponse<MedicalRecord>> => {
    console.log('更新就医记录数据:', id, data)
    return api.patch(`/records/medical/${id}/`, data)
  },

  deleteMedicalRecord: (id: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/records/medical/${id}/`)
  },

  // 用药记录API
  getMedicationRecords: (): Promise<AxiosResponse<MedicationRecord[]>> => {
    return api.get('/records/medication/')
  },

  getMedicationRecord: (id: number): Promise<AxiosResponse<MedicationRecord>> => {
    return api.get(`/records/medication/${id}/`)
  },

  createMedicationRecord: (data: MedicationRecord): Promise<AxiosResponse<MedicationRecord>> => {
    console.log('创建用药记录数据:', data)
    return api.post('/records/medication/', data)
  },

  updateMedicationRecord: (id: number, data: Partial<MedicationRecord>): Promise<AxiosResponse<MedicationRecord>> => {
    console.log('更新用药记录数据:', id, data)
    return api.patch(`/records/medication/${id}/`, data)
  },

  deleteMedicationRecord: (id: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/records/medication/${id}/`)
  },

  // 疫苗接种记录API
  getVaccinationRecords: (): Promise<AxiosResponse<VaccinationRecord[]>> => {
    return api.get('/records/vaccination/')
  },

  getVaccinationRecord: (id: number): Promise<AxiosResponse<VaccinationRecord>> => {
    return api.get(`/records/vaccination/${id}/`)
  },

  createVaccinationRecord: (data: VaccinationRecord): Promise<AxiosResponse<VaccinationRecord>> => {
    console.log('创建疫苗接种记录数据:', data)
    return api.post('/records/vaccination/', data)
  },

  updateVaccinationRecord: (id: number, data: Partial<VaccinationRecord>): Promise<AxiosResponse<VaccinationRecord>> => {
    console.log('更新疫苗接种记录数据:', id, data)
    return api.patch(`/records/vaccination/${id}/`, data)
  },

  deleteVaccinationRecord: (id: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/records/vaccination/${id}/`)
  },

  // 统计信息API
  getHealthStatistics: (): Promise<AxiosResponse<HealthStatistics>> => {
    return api.get('/records/overview/statistics/')
  },

  getMedicalStatistics: (): Promise<AxiosResponse<any>> => {
    return api.get('/records/medical/statistics/')
  },

  getMedicationStatistics: (): Promise<AxiosResponse<any>> => {
    return api.get('/records/medication/statistics/')
  },

  getVaccinationStatistics: (): Promise<AxiosResponse<any>> => {
    return api.get('/records/vaccination/statistics/')
  },

  getPhysicalExamStatistics: (): Promise<AxiosResponse<any>> => {
    return api.get('/records/physical-exam/statistics/')
  },

  // 健康趋势API
  getHealthTrends: (): Promise<AxiosResponse<HealthTrend>> => {
    return api.get('/records/overview/health-trends/')
  },

  // 最近活动API
  getRecentActivities: (): Promise<AxiosResponse<RecentActivity[]>> => {
    return api.get('/records/overview/recent-activities/')
  }
} 