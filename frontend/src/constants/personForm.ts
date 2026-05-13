/** 成员档案性别：与后端 organs 目录筛选一致（见 normalize_person_gender），空值为未填 */
export const GENDER_SELECT_OPTIONS = [
  { value: '', label: '不填' },
  { value: '男', label: '男' },
  { value: '女', label: '女' },
] as const

/** 下拉框用：将历史/别名规范为「男」「女」，否则保留原字面（用于额外 option，避免保存时误清空） */
export function personGenderForSelect(raw: string | null | undefined): string {
  if (raw == null) return ''
  const s = String(raw).trim()
  if (!s) return ''
  const low = s.toLowerCase()
  if (['男', 'm', 'male', '男性', '1'].includes(s) || low === 'male') return '男'
  if (['女', 'f', 'female', '女性', '2'].includes(s) || low === 'female') return '女'
  return s
}
