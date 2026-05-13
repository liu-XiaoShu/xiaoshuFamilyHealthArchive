export interface Person {
  id: number
  name: string
  gender: string | null
  birth_date: string | null
  /** 家庭内角色，如父亲、儿子等 */
  member_role: string | null
  /** 自定义头像 GET 路径（同源相对路径）；未设置则用占位头像 */
  avatar_url?: string | null
  /** 来自报告指标「血型」，按自然年覆盖解析 */
  blood_type: string | null
  /** 来自报告指标「身高」 */
  height_cm: number | null
  /** 来自报告指标「体重」 */
  weight_kg: number | null
  notes: string | null
  created_at: string
  /** 当前仍为异常的细项数量（详情与列表接口均返回） */
  current_abnormal_count?: number
  /** 当前在自然年规则下判为正常的细项数量（有观测记录的指标维度） */
  current_normal_indicator_count?: number
}

export interface CurrentAbnormalItem {
  indicator_id: number
  indicator_name: string
  indicator_category: string
  indicator_is_narrative: boolean
  indicator_parent_name: string | null
  basis_label: string
  observation_id: number
  measured_at: string
  session_report_at: string
  value_text: string | null
  ref_text: string | null
  abnormal: boolean | null
  remarks: string | null
  findings_text: string | null
  conclusion_text: string | null
  organ_names: string[]
}

export interface ExamSession {
  id: number
  person_id: number
  report_at: string
  institution: string | null
  notes: string | null
  created_at: string
}

export interface Organ {
  id: number
  name: string
  gender_scope: string
  sort_order: number
}

export interface Indicator {
  id: number
  parent_id: number | null
  name: string
  category: string
  is_narrative: boolean
  unit: string | null
  ref_range_hint: string | null
  organ_ids: number[]
}

export interface Observation {
  id: number
  session_id: number
  indicator_id: number
  measured_at: string
  value_text: string | null
  ref_text: string | null
  abnormal: boolean | null
  remarks: string | null
  findings_text: string | null
  conclusion_text: string | null
  indicator_name: string
  indicator_category: string
  indicator_is_narrative: boolean
  indicator_parent_id: number | null
  indicator_parent_name: string | null
  indicator_unit: string | null
  organ_ids: number[]
  organ_names: string[]
  session_report_at: string
  /** 「当前异常」列表映射项：后端判定说明（可选） */
  basis_label?: string
}
