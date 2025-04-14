import { defineStore } from 'pinia'
import { recordsApi } from '@/api/records'
import type { PhysicalExam, MedicalRecord, MedicationRecord, VaccinationRecord } from '@/api/records'

interface RecordsState {
  physicalExams: PhysicalExam[]
  medicalRecords: MedicalRecord[]
  medicationRecords: MedicationRecord[]
  vaccinationRecords: VaccinationRecord[]
  loading: boolean
  error: string | null
}

export const useRecordsStore = defineStore('records', {
  state: (): RecordsState => ({
    physicalExams: [],
    medicalRecords: [],
    medicationRecords: [],
    vaccinationRecords: [],
    loading: false,
    error: null
  }),

  getters: {
    getPhysicalExamById: (state) => (id: number) => {
      return state.physicalExams.find(exam => exam.id === id)
    },

    getMedicalRecordById: (state) => (id: number) => {
      return state.medicalRecords.find(record => record.id === id)
    },

    getMedicationRecordById: (state) => (id: number) => {
      return state.medicationRecords.find(record => record.id === id)
    },

    getVaccinationRecordById: (state) => (id: number) => {
      return state.vaccinationRecords.find(record => record.id === id)
    }
  },

  actions: {
    // 体检记录
    async fetchPhysicalExams() {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.getPhysicalExams()
        this.physicalExams = response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取体检记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createPhysicalExam(data: PhysicalExam) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.createPhysicalExam(data)
        this.physicalExams.push(response.data)
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '创建体检记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updatePhysicalExam(id: number, data: PhysicalExam) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.updatePhysicalExam(id, data)
        const index = this.physicalExams.findIndex(exam => exam.id === id)
        if (index !== -1) {
          this.physicalExams[index] = response.data
        }
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '更新体检记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deletePhysicalExam(id: number) {
      this.loading = true
      this.error = null
      try {
        await recordsApi.deletePhysicalExam(id)
        this.physicalExams = this.physicalExams.filter(exam => exam.id !== id)
      } catch (error: any) {
        this.error = error.response?.data?.detail || '删除体检记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 医疗记录
    async fetchMedicalRecords() {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.getMedicalRecords()
        this.medicalRecords = response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取医疗记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createMedicalRecord(data: MedicalRecord) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.createMedicalRecord(data)
        this.medicalRecords.push(response.data)
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '创建医疗记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateMedicalRecord(id: number, data: MedicalRecord) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.updateMedicalRecord(id, data)
        const index = this.medicalRecords.findIndex(record => record.id === id)
        if (index !== -1) {
          this.medicalRecords[index] = response.data
        }
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '更新医疗记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteMedicalRecord(id: number) {
      this.loading = true
      this.error = null
      try {
        await recordsApi.deleteMedicalRecord(id)
        this.medicalRecords = this.medicalRecords.filter(record => record.id !== id)
      } catch (error: any) {
        this.error = error.response?.data?.detail || '删除医疗记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 用药记录
    async fetchMedicationRecords() {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.getMedicationRecords()
        this.medicationRecords = response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取用药记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createMedicationRecord(data: MedicationRecord) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.createMedicationRecord(data)
        this.medicationRecords.push(response.data)
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '创建用药记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateMedicationRecord(id: number, data: MedicationRecord) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.updateMedicationRecord(id, data)
        const index = this.medicationRecords.findIndex(record => record.id === id)
        if (index !== -1) {
          this.medicationRecords[index] = response.data
        }
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '更新用药记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteMedicationRecord(id: number) {
      this.loading = true
      this.error = null
      try {
        await recordsApi.deleteMedicationRecord(id)
        this.medicationRecords = this.medicationRecords.filter(record => record.id !== id)
      } catch (error: any) {
        this.error = error.response?.data?.detail || '删除用药记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 疫苗接种记录
    async fetchVaccinationRecords() {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.getVaccinationRecords()
        this.vaccinationRecords = response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取疫苗接种记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createVaccinationRecord(data: VaccinationRecord) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.createVaccinationRecord(data)
        this.vaccinationRecords.push(response.data)
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '创建疫苗接种记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateVaccinationRecord(id: number, data: VaccinationRecord) {
      this.loading = true
      this.error = null
      try {
        const response = await recordsApi.updateVaccinationRecord(id, data)
        const index = this.vaccinationRecords.findIndex(record => record.id === id)
        if (index !== -1) {
          this.vaccinationRecords[index] = response.data
        }
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.detail || '更新疫苗接种记录失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteVaccinationRecord(id: number) {
      this.loading = true
      this.error = null
      try {
        await recordsApi.deleteVaccinationRecord(id)
        this.vaccinationRecords = this.vaccinationRecords.filter(record => record.id !== id)
      } catch (error: any) {
        this.error = error.response?.data?.detail || '删除疫苗接种记录失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 