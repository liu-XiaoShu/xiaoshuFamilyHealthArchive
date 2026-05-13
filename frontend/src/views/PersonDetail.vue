<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { http, apiError } from '../api/http'
import type { ExamSession, Person } from '../api/types'
import { resolveMemberAvatarSrc } from '../utils/memberAvatar'
import NavBackLink from '../components/NavBackLink.vue'
import CollapseTextToggle from '../components/CollapseTextToggle.vue'
import ReportDetailBadgeIcon from '../components/ReportDetailBadgeIcon.vue'
import TrendsChartBadgeIcon from '../components/TrendsChartBadgeIcon.vue'
import { GENDER_SELECT_OPTIONS, personGenderForSelect } from '../constants/personForm'

const genderOptions = GENDER_SELECT_OPTIONS

const props = defineProps<{ personId: string }>()
const router = useRouter()
const person = ref<Person | null>(null)
const sessions = ref<ExamSession[]>([])
const err = ref('')
const loading = ref(false)

const edit = ref({
  name: '',
  gender: '',
  birth_date: '',
  member_role: '',
})

const sessionForm = ref({
  report_at: '',
  institution: '',
  notes: '',
})

const pid = computed(() => Number(props.personId))

/** 批次超过该条数时出现折叠：收起时仍完整展示前 N 条，仅隐藏其后批次 */
const SESSIONS_TABLE_TRUNCATE_AFTER = 10
/** true：收起多余批次（保留前 SESSIONS_TABLE_TRUNCATE_AFTER 条始终可见） */
const sessionsBatchCollapsed = ref(false)

const sessionsBatchCollapsible = computed(
  () => sessions.value.length > SESSIONS_TABLE_TRUNCATE_AFTER,
)

const sessionsRowsVisible = computed(() => {
  const list = sessions.value
  if (list.length <= SESSIONS_TABLE_TRUNCATE_AFTER) return list
  if (!sessionsBatchCollapsed.value) return list
  return list.slice(0, SESSIONS_TABLE_TRUNCATE_AFTER)
})

watch(
  () => [pid.value, sessions.value.length] as const,
  ([_id, len], prev) => {
    const prevLen = prev?.[1]
    if (len <= SESSIONS_TABLE_TRUNCATE_AFTER) {
      sessionsBatchCollapsed.value = false
      return
    }
    if (prevLen === undefined || prevLen <= SESSIONS_TABLE_TRUNCATE_AFTER) {
      sessionsBatchCollapsed.value = true
    }
  },
  { immediate: true },
)

function toggleSessionsBatchList() {
  sessionsBatchCollapsed.value = !sessionsBatchCollapsed.value
}

const avatarInputRef = ref<HTMLInputElement | null>(null)
const avatarUploading = ref(false)
/** 上传/删除头像后递增，强制刷新同源头像缓存 */
const avatarBust = ref(0)

/** 个人信息编辑弹层（资料表单 + 头像） */
const showProfileEditor = ref(false)
/** 弹层内保存 / 头像操作的错误提示（与页面其它 err 区分） */
const profileEditorErr = ref('')

/** 导出筛选：日期 + 时刻分开（Firefox 等对 datetime-local 时间部分支持差） */
const exportMeasuredFromDate = ref('')
const exportMeasuredFromTime = ref('')
const exportMeasuredToDate = ref('')
const exportMeasuredToTime = ref('')
const exportReportFromDate = ref('')
const exportReportFromTime = ref('')
const exportReportToDate = ref('')
const exportReportToTime = ref('')

const exportBusy = ref(false)
const exportErr = ref('')

/** 未选「时刻」时：从/含下限用当日 0 点，至/含上限用当日 23:59:59（含秒边界） */
function dateTimePartsToUtcIso(
  dateStr: string,
  timeStr: string,
  emptyTimeBoundary: 'start' | 'end',
): string | null {
  const d = dateStr.trim()
  if (!d) return null
  let t = timeStr.trim()
  if (!t) {
    t = emptyTimeBoundary === 'end' ? '23:59:59' : '00:00:00'
  } else if (/^\d{2}:\d{2}$/.test(t)) {
    t = `${t}:00`
  }
  const dp = d.split('-').map(Number)
  const y = dp[0]
  const mo = dp[1]
  const day = dp[2]
  const tp = t.split(':').map(Number)
  const h = tp[0] ?? 0
  const mi = tp[1] ?? 0
  const sec = tp[2] ?? 0
  if ([y, mo, day, h, mi, sec].some((n) => Number.isNaN(n))) return null
  const dt = new Date(y, mo! - 1, day!, h, mi, sec)
  if (Number.isNaN(dt.getTime())) return null
  return dt.toISOString()
}

/** POST /export 的请求体（仅包含有值的筛选项） */
function buildExportFiltersBody(): Record<string, string> {
  const out: Record<string, string> = {}
  const mf = dateTimePartsToUtcIso(
    exportMeasuredFromDate.value,
    exportMeasuredFromTime.value,
    'start',
  )
  const mt = dateTimePartsToUtcIso(exportMeasuredToDate.value, exportMeasuredToTime.value, 'end')
  const rf = dateTimePartsToUtcIso(
    exportReportFromDate.value,
    exportReportFromTime.value,
    'start',
  )
  const rt = dateTimePartsToUtcIso(exportReportToDate.value, exportReportToTime.value, 'end')
  if (mf) out.measured_from = mf
  if (mt) out.measured_to = mt
  if (rf) out.report_from = rf
  if (rt) out.report_to = rt
  return out
}

function filenameFromContentDisposition(header: string | null): string | null {
  if (!header) return null
  const star = /filename\*=UTF-8''([^;\n]+)/i.exec(header)
  if (star) {
    try {
      return decodeURIComponent(star[1].trim())
    } catch {
      /* fall through */
    }
  }
  const m = /filename="([^"]+)"/.exec(header)
  return m ? m[1] : null
}

async function triggerExportCsvDownload(url: string) {
  exportErr.value = ''
  exportBusy.value = true
  try {
    const res = await fetch(url, {
      method: 'GET',
      cache: 'no-store',
      headers: { 'Cache-Control': 'no-cache', Pragma: 'no-cache' },
    })
    if (!res.ok) {
      const text = await res.text()
      exportErr.value = text.slice(0, 400) || `导出失败（HTTP ${res.status}）`
      return
    }
    const blob = await res.blob()
    const fname =
      filenameFromContentDisposition(res.headers.get('Content-Disposition')) ||
      `person_${pid.value}_health_export.csv`
    const objectUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = objectUrl
    a.download = fname
    a.rel = 'noopener'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(objectUrl)
  } catch (e) {
    exportErr.value = e instanceof Error ? e.message : String(e)
  } finally {
    exportBusy.value = false
  }
}

async function triggerExportCsvPost(body: Record<string, string>) {
  exportErr.value = ''
  exportBusy.value = true
  try {
    const res = await fetch(`/api/persons/${pid.value}/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      },
      cache: 'no-store',
      body: JSON.stringify(body),
    })
    if (!res.ok) {
      const text = await res.text()
      exportErr.value = text.slice(0, 400) || `导出失败（HTTP ${res.status}）`
      return
    }
    const blob = await res.blob()
    const fname =
      filenameFromContentDisposition(res.headers.get('Content-Disposition')) ||
      `person_${pid.value}_health_export.csv`
    const objectUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = objectUrl
    a.download = fname
    a.rel = 'noopener'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(objectUrl)
  } catch (e) {
    exportErr.value = e instanceof Error ? e.message : String(e)
  } finally {
    exportBusy.value = false
  }
}

function downloadExportAll() {
  void triggerExportCsvDownload(`/api/persons/${pid.value}/export`)
}

/** 条件导出：使用 POST JSON，避免 GET 查询串中 from 等参数被代理/中间层丢弃；时间用本地日历分量解析再转 UTC。 */
function downloadExportFiltered() {
  const body = buildExportFiltersBody()
  if (Object.keys(body).length === 0) {
    void triggerExportCsvDownload(`/api/persons/${pid.value}/export`)
    return
  }
  void triggerExportCsvPost(body)
}

function clearExportFilters() {
  exportMeasuredFromDate.value = ''
  exportMeasuredFromTime.value = ''
  exportMeasuredToDate.value = ''
  exportMeasuredToTime.value = ''
  exportReportFromDate.value = ''
  exportReportFromTime.value = ''
  exportReportToDate.value = ''
  exportReportToTime.value = ''
}

function ageLabel(birth: string | null): string {
  if (!birth) return '—'
  const b = new Date(birth + 'T12:00:00')
  const t = new Date()
  let y = t.getFullYear() - b.getFullYear()
  const m = t.getMonth() - b.getMonth()
  if (m < 0 || (m === 0 && t.getDate() < b.getDate())) y--
  return y >= 0 ? `${y} 岁` : '—'
}

const tipBatchCsv =
  '1、编码：UTF-8 编码（Excel 可「另存为 CSV UTF-8」）；简体 Windows 下「ANSI CSV」也可识别。\n\n' +
  '2、同一批次内报告时间可与上一行留空沿用；机构 / 批次备注在同一批次内也可留空沿用。\n\n' +
  '3、可选列 institution（机构）、session_notes（批次备注）写入该批次。指标须与系统中叶子指标名称一致，或使用 indicator_id；\n\n' +
  '4、indicator_category：physical/lab/imaging（或 体格/检验/影像），同名多条时必填。'

type HoverTipState = { text: string; x: number; y: number }

/** 与家庭成员列表页一致的鼠标跟随说明层 */
const hoverTip = ref<HoverTipState | null>(null)

function tipEnter(e: MouseEvent, text: string) {
  hoverTip.value = {
    text,
    x: e.clientX + 14,
    y: e.clientY + 14,
  }
}

function tipMove(e: MouseEvent) {
  const cur = hoverTip.value
  if (!cur) return
  hoverTip.value = {
    ...cur,
    x: e.clientX + 14,
    y: e.clientY + 14,
  }
}

function tipLeave() {
  hoverTip.value = null
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const [{ data: p }, { data: s }] = await Promise.all([
      http.get<Person>(`/api/persons/${pid.value}`),
      http.get<ExamSession[]>(`/api/persons/${pid.value}/sessions`),
    ])
    person.value = p
    sessions.value = s
    edit.value = {
      name: p.name,
      gender: personGenderForSelect(p.gender),
      birth_date: p.birth_date ?? '',
      member_role: p.member_role ?? '',
    }
    profileEditorErr.value = ''
  } catch (e) {
    err.value = apiError(e)
  } finally {
    loading.value = false
  }
}

function openProfileEditor() {
  tipLeave()
  profileEditorErr.value = ''
  const p = person.value
  if (p) {
    edit.value = {
      name: p.name,
      gender: personGenderForSelect(p.gender),
      birth_date: p.birth_date ?? '',
      member_role: p.member_role ?? '',
    }
  }
  showProfileEditor.value = true
}

function closeProfileEditor() {
  showProfileEditor.value = false
  profileEditorErr.value = ''
}

async function savePerson() {
  if (!person.value) return
  profileEditorErr.value = ''
  try {
    await http.patch(`/api/persons/${pid.value}`, {
      name: edit.value.name.trim(),
      gender: edit.value.gender || null,
      birth_date: edit.value.birth_date || null,
      member_role: edit.value.member_role.trim() || null,
    })
    await load()
    closeProfileEditor()
  } catch (e) {
    profileEditorErr.value = apiError(e)
  }
}

async function createSession() {
  if (!sessionForm.value.report_at) {
    err.value = '请选择报告时间'
    return
  }
  err.value = ''
  try {
    await http.post(`/api/persons/${pid.value}/sessions`, {
      report_at: new Date(sessionForm.value.report_at).toISOString(),
      institution: sessionForm.value.institution || null,
      notes: sessionForm.value.notes || null,
    })
    sessionForm.value = { report_at: '', institution: '', notes: '' }
    await load()
  } catch (e) {
    err.value = apiError(e)
  }
}

async function deleteSession(id: number) {
  if (!confirm('删除该批次及其全部检查明细？')) return
  try {
    await http.delete(`/api/persons/${pid.value}/sessions/by-id/${id}`)
    await load()
  } catch (e) {
    err.value = apiError(e)
  }
}

const csvImporting = ref(false)
const csvImportMsg = ref('')
const csvImportResult = ref<{ imported: number; errors: { line: number; detail: string }[] } | null>(
  null,
)
const csvFileRef = ref<HTMLInputElement | null>(null)

async function runCsvImport() {
  const input = csvFileRef.value
  const file = input?.files?.[0]
  if (!file) {
    csvImportMsg.value = '请先选择 CSV 文件'
    csvImportResult.value = null
    return
  }
  csvImportMsg.value = ''
  csvImportResult.value = null
  csvImporting.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await http.post<{
      imported: number
      errors: { line: number; detail: string }[]
    }>(`/api/persons/${pid.value}/import/observations-csv`, fd)
    csvImportResult.value = data
    if (input) input.value = ''
    await load()
  } catch (e) {
    csvImportMsg.value = apiError(e)
  } finally {
    csvImporting.value = false
  }
}

async function removeCustomAvatar() {
  if (!confirm('删除自定义头像并恢复默认缩写头像？')) return
  profileEditorErr.value = ''
  try {
    await http.delete(`/api/persons/${pid.value}/avatar`)
    avatarBust.value += 1
    await load()
  } catch (e) {
    profileEditorErr.value = apiError(e)
  }
}

async function onAvatarFileSelected(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  profileEditorErr.value = ''
  avatarUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    await http.post(`/api/persons/${pid.value}/avatar`, fd)
    avatarBust.value += 1
    await load()
  } catch (e) {
    profileEditorErr.value = apiError(e)
  } finally {
    avatarUploading.value = false
    input.value = ''
  }
}

/** 批次报告时间：固定格式 + 等宽数字显示，数字与字母易区分 */
function fmt(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  const y = d.getFullYear()
  const mo = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  const sec = String(d.getSeconds()).padStart(2, '0')
  return `${y}/${mo}/${day} ${h}:${min}:${sec}`
}

function fmtVitalNum(v: number | null | undefined): string {
  if (v == null || Number.isNaN(Number(v))) return '—'
  const n = Number(v)
  return Number.isInteger(n) ? String(n) : n.toFixed(1)
}

onMounted(load)
</script>

<template>
  <div v-if="loading && !person" class="loading-text card loading-card">加载中…</div>
  <template v-else-if="person">
    <div class="card">
      <p class="detail-back-row">
        <NavBackLink to="/" label="返回家庭成员页" variant="home" />
      </p>
      <section class="person-profile-hero" aria-labelledby="person-profile-heading">
        <p id="person-profile-heading" class="person-profile-eyebrow">成员健康档案</p>
        <div class="person-profile-top">
          <div class="person-profile-top-main">
            <img
              class="detail-avatar"
              :src="resolveMemberAvatarSrc(person, avatarBust)"
              width="96"
              height="96"
              alt=""
              loading="lazy"
              decoding="async"
              role="button"
              tabindex="0"
              title="个人信息编辑"
              @click="openProfileEditor"
              @keydown.enter.prevent="openProfileEditor"
              @keydown.space.prevent="openProfileEditor"
            />
            <div class="person-profile-title-block">
              <h2 class="person-profile-name">{{ person.name }}</h2>
              <p v-if="person.birth_date" class="person-profile-sub muted">
                出生日期 {{ person.birth_date }}
              </p>
            </div>
          </div>
          <button type="button" class="secondary btn-profile-edit" @click="openProfileEditor">
            个人信息编辑
          </button>
        </div>
        <div class="person-profile-magnet">
          <div class="person-profile-stats">
          <div class="profile-stat-tile profile-stat-tile-data">
            <span class="profile-stat-kicker">成员属性</span>
            <span class="profile-stat-value">{{ person.member_role?.trim() || '—' }}</span>
          </div>
          <div class="profile-stat-tile profile-stat-tile-data">
            <span class="profile-stat-kicker">性别</span>
            <span class="profile-stat-value">{{ person.gender?.trim() || '—' }}</span>
          </div>
          <div class="profile-stat-tile profile-stat-tile-data profile-stat-tile-age">
            <span class="profile-stat-kicker">年龄</span>
            <span class="profile-stat-value">{{ ageLabel(person.birth_date) }}</span>
          </div>
          <div class="profile-stat-tile profile-stat-tile-data profile-stat-tile-vitals">
            <span class="profile-stat-kicker">血型</span>
            <span class="profile-stat-value">{{ person.blood_type ?? '—' }}</span>
          </div>
          <div class="profile-stat-tile profile-stat-tile-data profile-stat-tile-vitals">
            <span class="profile-stat-kicker">身高</span>
            <span class="profile-stat-value profile-stat-num"
              >{{ fmtVitalNum(person.height_cm) }}<span class="profile-stat-unit"> cm</span></span
            >
          </div>
          <div class="profile-stat-tile profile-stat-tile-data profile-stat-tile-vitals">
            <span class="profile-stat-kicker">体重</span>
            <span class="profile-stat-value profile-stat-num"
              >{{ fmtVitalNum(person.weight_kg) }}<span class="profile-stat-unit"> kg</span></span
            >
          </div>
          <RouterLink
            class="profile-stat-tile profile-stat-tile-link profile-stat-tile-overview-abnorm-norm"
            :to="`/persons/${pid}/current-abnormals`"
          >
            <span class="profile-stat-kicker">异常 / 正常</span>
            <span class="profile-stat-value profile-stat-overview-counts profile-stat-num">
              <span class="profile-stat-overview-ab">{{ person.current_abnormal_count ?? 0 }}</span>
              <span class="profile-stat-overview-slash">/</span>
              <span class="profile-stat-overview-norm">{{
                person.current_normal_indicator_count ?? 0
              }}</span>
            </span>
            <span class="profile-stat-caption">数量概览 · 自然年覆盖 · 点击查看</span>
          </RouterLink>
          <RouterLink
            class="profile-stat-tile profile-stat-tile-link profile-stat-tile-reports profile-stat-tile-detail-magnet"
            :to="`/persons/${pid}/observations`"
          >
            <span class="profile-stat-kicker profile-stat-kicker-magnet-main">报告详情</span>
            <span class="profile-stat-detail-icon-wrap" aria-hidden="true">
              <ReportDetailBadgeIcon class="profile-stat-detail-icon" />
            </span>
            <span class="profile-stat-caption">按器官 · 类型 · 时间</span>
          </RouterLink>
          <RouterLink
            class="profile-stat-tile profile-stat-tile-link profile-stat-tile-reports profile-stat-tile-trends-magnet"
            :to="`/persons/${pid}/trends`"
          >
            <span class="profile-stat-kicker profile-stat-kicker-magnet-main">历年趋势图表</span>
            <span class="profile-stat-trends-chart-wrap" aria-hidden="true">
              <TrendsChartBadgeIcon class="profile-stat-trends-chart-icon" />
            </span>
            <span class="profile-stat-caption">按时间浏览 · 指标趋势对比</span>
          </RouterLink>
          </div>
        </div>
        <p class="muted detail-note">
          注意：血型、身高、体重取自<strong>体检报告指标</strong>（自然年覆盖：本年有记录则取本年最新一条有值记录，否则取更早的最近一条）。
        </p>
      </section>
      <div v-if="err" class="err">{{ err }}</div>
    </div>

    <div class="card report-enter-card">
      <div class="report-section-head">
        <h3 class="report-section-title">录入报告</h3>
        <hr class="report-section-rule" aria-hidden="true" />
      </div>

      <div class="report-enter-block">
        <div class="csv-heading-row">
          <h4
            class="report-subheading csv-heading-title batch-csv-hint"
            @mouseenter="(e) => tipEnter(e, tipBatchCsv)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
          >
            批量录入
          </h4>
          <a
            class="csv-template-download"
            :href="`/api/persons/${pid}/import/observations-csv/template`"
            target="_blank"
            rel="noreferrer"
          >
            <span class="csv-template-download-icon" aria-hidden="true">↓</span>
            下载导入模版
          </a>
        </div>
        <p class="muted detail-note">
          适合整张表一次性导入；请先点击右侧「下载导入模版」核对列名与字段说明。
        </p>
        <div class="csv-import-inner">
          <div class="csv-row">
            <input
              ref="csvFileRef"
              type="file"
              accept=".csv,text/csv"
              class="file-input"
            />
            <button type="button" :disabled="csvImporting" @click="runCsvImport">
              {{ csvImporting ? '导入中…' : '上传并导入' }}
            </button>
          </div>
          <p v-if="csvImportMsg" class="err">{{ csvImportMsg }}</p>
          <template v-if="csvImportResult">
            <p class="csv-summary">
              <template v-if="csvImportResult.imported === 0">
                未写入任何记录。
              </template>
              <template v-else>
                <span class="csv-summary-ok">成功</span>导入
                <strong>{{ csvImportResult.imported }}</strong> 条。
              </template>
              <template v-if="csvImportResult.errors.length">
                <span class="csv-summary-fail-tail">
                  <span class="csv-summary-bad">失败</span>
                  <strong>{{ csvImportResult.errors.length }}</strong> 条（见下表）。
                </span>
              </template>
            </p>
            <table v-if="csvImportResult.errors.length" class="csv-err-table">
              <thead>
                <tr>
                  <th>行号</th>
                  <th>原因</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(e, idx) in csvImportResult.errors" :key="idx">
                  <td>{{ e.line }}</td>
                  <td>{{ e.detail }}</td>
                </tr>
              </tbody>
            </table>
          </template>
        </div>
      </div>

      <div class="report-enter-block report-enter-block-split">
        <h4 class="report-subheading">手动录入</h4>
        <p class="muted detail-note">
          按体检<strong>批次</strong>逐个填写：先新建一条批次，再在列表中点击「录入明细」进入该批次的指标编辑。
        </p>
        <div class="row">
          <label
            >报告时间 *
            <input
              v-model="sessionForm.report_at"
              type="datetime-local"
              class="session-datetime-input"
            />
          </label>
          <label
            >机构
            <input v-model="sessionForm.institution" placeholder="医院/体检中心"
          /></label>
          <label
            >备注
            <input v-model="sessionForm.notes"
          /></label>
          <button type="button" @click="createSession">新建批次</button>
        </div>
        <table class="report-sessions-table">
          <thead>
            <tr>
              <th>报告时间</th>
              <th>机构</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in sessionsRowsVisible" :key="s.id">
              <td class="session-datetime">{{ fmt(s.report_at) }}</td>
              <td>{{ s.institution ?? '—' }}</td>
              <td>{{ s.notes ?? '—' }}</td>
              <td>
                <div class="cell-actions">
                  <button
                    type="button"
                    class="secondary"
                    @click="router.push(`/persons/${pid}/sessions/${s.id}`)"
                  >
                    录入明细
                  </button>
                  <button type="button" class="danger" @click="deleteSession(s.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
          <tbody v-if="sessionsBatchCollapsible">
            <tr class="sessions-table-toggle-row">
              <td colspan="4">
                <CollapseTextToggle
                  variant="block"
                  :expanded="!sessionsBatchCollapsed"
                  :label-collapsed="`展开其余 ${sessions.length - SESSIONS_TABLE_TRUNCATE_AFTER} 条`"
                  :label-expanded="`收起（仅前 ${SESSIONS_TABLE_TRUNCATE_AFTER} 条）`"
                  :meta="`共 ${sessions.length} 条`"
                  @toggle="toggleSessionsBatchList"
                />
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="sessions.length === 0" class="muted detail-note">
          暂无批次，请先新建批次或使用上方的 CSV 批量录入。
        </p>
      </div>
    </div>

    <div class="card report-export-card">
      <div class="report-section-head">
        <h3 class="report-section-title">导出报告</h3>
        <hr class="report-section-rule" aria-hidden="true" />
      </div>
      <div class="export-panel export-panel-card">
        <h4 class="report-subheading">导出为 CSV（便于 AI / 离线分析）</h4>
        <p class="muted detail-note">
          CSV 含成员基本信息、批次机构与备注、指标 ID / 单位 / 是否叙述型及每条明细。
          <strong>测量时间</strong>对应每条记录的测量时刻；<strong>批次报告时间</strong>对应体检批次。
          下列条件均为<strong>包含边界</strong>，且彼此之间为<strong>且（AND）</strong>关系；全部留空则与「导出全部」等价。
          每栏为<strong>日期</strong>与<strong>时刻</strong>分开选择（兼容 Firefox 等浏览器）；若只选日期不选时刻，则「从」侧取当日
          0:00，「至」侧取当日 23:59:59。
        </p>
        <div class="export-filters-wrap">
          <div class="export-filters-matrix" role="group" aria-label="导出时间筛选">
            <span class="export-filters-corner" aria-hidden="true"></span>
            <span class="export-filters-colhead">从</span>
            <span class="export-filters-colhead">至</span>

            <span class="export-filters-rowhead">测量时间</span>
            <div class="export-filter-cell">
              <div class="export-filter-dt-row">
                <input v-model="exportMeasuredFromDate" type="date" class="session-datetime-input" />
                <input v-model="exportMeasuredFromTime" type="time" step="1" class="session-datetime-input" />
              </div>
            </div>
            <div class="export-filter-cell">
              <div class="export-filter-dt-row">
                <input v-model="exportMeasuredToDate" type="date" class="session-datetime-input" />
                <input v-model="exportMeasuredToTime" type="time" step="1" class="session-datetime-input" />
              </div>
            </div>

            <span class="export-filters-rowhead">批次报告</span>
            <div class="export-filter-cell">
              <div class="export-filter-dt-row">
                <input v-model="exportReportFromDate" type="date" class="session-datetime-input" />
                <input v-model="exportReportFromTime" type="time" step="1" class="session-datetime-input" />
              </div>
            </div>
            <div class="export-filter-cell">
              <div class="export-filter-dt-row">
                <input v-model="exportReportToDate" type="date" class="session-datetime-input" />
                <input v-model="exportReportToTime" type="time" step="1" class="session-datetime-input" />
              </div>
            </div>
          </div>
        </div>
        <p class="export-actions">
          <button
            type="button"
            class="csv-template-download"
            :disabled="exportBusy"
            @click="downloadExportAll"
          >
            <span class="csv-template-download-icon" aria-hidden="true">↓</span>
            导出全部时间
          </button>
          <span class="export-actions-sep" aria-hidden="true">·</span>
          <button
            type="button"
            class="csv-template-download"
            :disabled="exportBusy"
            @click="downloadExportFiltered"
          >
            <span class="csv-template-download-icon" aria-hidden="true">↓</span>
            按上述条件导出
          </button>
          <span class="export-actions-sep" aria-hidden="true">·</span>
          <button type="button" class="secondary" @click="clearExportFilters">清空条件</button>
        </p>
        <p v-if="exportErr" class="err export-inline-err">{{ exportErr }}</p>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="showProfileEditor && person"
        class="profile-edit-overlay"
        role="presentation"
        @click.self="closeProfileEditor"
      >
        <div
          class="profile-edit-dialog card"
          role="dialog"
          aria-modal="true"
          aria-labelledby="profile-edit-title"
        >
          <div class="profile-edit-head">
            <h3 id="profile-edit-title">个人信息编辑</h3>
            <button type="button" class="secondary" @click="closeProfileEditor">关闭</button>
          </div>
          <div class="profile-edit-avatar-block">
            <img
              class="detail-avatar profile-edit-avatar-preview"
              :src="resolveMemberAvatarSrc(person, avatarBust)"
              width="64"
              height="64"
              alt=""
            />
            <div class="profile-edit-avatar-actions">
              <input
                ref="avatarInputRef"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                class="avatar-file-input"
                tabindex="-1"
                :disabled="avatarUploading"
                @change="onAvatarFileSelected"
              />
              <div class="avatar-toolbar profile-edit-toolbar">
                <button
                  type="button"
                  class="secondary"
                  :disabled="avatarUploading"
                  @click="avatarInputRef?.click()"
                >
                  {{ avatarUploading ? '上传中…' : '上传头像' }}
                </button>
                <button
                  v-if="person.avatar_url"
                  type="button"
                  class="secondary"
                  :disabled="avatarUploading"
                  @click="removeCustomAvatar"
                >
                  恢复默认头像
                </button>
              </div>
              <p class="muted detail-note profile-edit-hint">
                支持 JPG / PNG / WebP / GIF，最大 2MB。
              </p>
            </div>
          </div>
          <div v-if="profileEditorErr" class="err">{{ profileEditorErr }}</div>
          <div class="row profile-edit-fields">
            <label
              >姓名
              <input v-model="edit.name"
            /></label>
            <label
              >成员属性
              <input v-model="edit.member_role" placeholder="如：父亲、儿子、女儿"
            /></label>
            <label
              >性别（选填）
              <select v-model="edit.gender">
                <option
                  v-if="edit.gender && edit.gender !== '男' && edit.gender !== '女'"
                  :value="edit.gender"
                >
                  {{ edit.gender }}（请改选标准项）
                </option>
                <option v-for="opt in genderOptions" :key="'g-' + (opt.value || 'unset')" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </label>
            <label
              >出生日期
              <input v-model="edit.birth_date" type="date"
            /></label>
            <button type="button" @click="savePerson">保存资料</button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div
        v-if="hoverTip"
        class="member-list-tooltip"
        role="tooltip"
        :style="{ left: `${hoverTip.x}px`, top: `${hoverTip.y}px` }"
      >
        {{ hoverTip.text }}
      </div>
    </Teleport>
  </template>
</template>

<style scoped>
.detail-back-row {
  margin: 0 0 0.85rem;
}
.person-profile-hero {
  margin-bottom: 1.15rem;
  padding: 1.15rem 1.25rem;
  border-radius: calc(var(--radius-lg) + 2px);
  border: 1px solid rgba(148, 163, 184, 0.18);
  background:
    linear-gradient(
      145deg,
      rgba(56, 189, 248, 0.08) 0%,
      rgba(129, 140, 248, 0.06) 40%,
      rgba(15, 23, 42, 0.38) 100%
    ),
    var(--surface-inner);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.06) inset,
    0 14px 36px rgba(0, 0, 0, 0.22);
}
.person-profile-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.person-profile-top-main {
  display: flex;
  align-items: center;
  gap: 1.28rem;
  flex: 1;
  min-width: 0;
}
.person-profile-title-block {
  flex: 1;
  min-width: 12rem;
}
.btn-profile-edit {
  flex-shrink: 0;
  align-self: center;
}
@media (max-width: 540px) {
  .person-profile-top {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-profile-edit {
    width: 100%;
    align-self: stretch;
  }
}
.person-profile-name {
  margin: 0 0 0.25rem;
  font-size: clamp(1.65rem, 4.1vw, 2.15rem);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.15;
  color: var(--text-primary);
}
.person-profile-sub {
  margin: 0;
  font-size: clamp(0.9rem, 1.65vw, 1rem);
  letter-spacing: 0.03em;
}
.detail-note {
  margin: 0 0 0.85rem;
  font-size: 0.78rem;
  line-height: 1.55;
  max-width: 46rem;
}
.avatar-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}
.avatar-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
.profile-edit-overlay {
  position: fixed;
  inset: 0;
  z-index: 10040;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 1.25rem 1rem 2rem;
  overflow-y: auto;
  background: rgba(6, 10, 18, 0.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.profile-edit-dialog {
  width: min(38rem, 100%);
  margin-top: min(8vh, 3.5rem);
  margin-bottom: 2rem;
  position: relative;
}
.profile-edit-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.65rem;
  margin-bottom: 1rem;
}
.profile-edit-head h3 {
  margin: 0;
  font-size: 1.08rem;
  font-weight: 650;
  letter-spacing: -0.02em;
}
.profile-edit-avatar-block {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}
.profile-edit-avatar-preview {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}
.profile-edit-avatar-actions {
  flex: 1;
  min-width: 11rem;
}
.profile-edit-toolbar {
  margin-bottom: 0.35rem;
}
.profile-edit-hint {
  max-width: none;
}
.profile-edit-fields {
  margin-top: 0.35rem;
}
.person-profile-hero .detail-avatar {
  width: 96px;
  height: 96px;
  cursor: pointer;
  transition:
    transform 0.38s cubic-bezier(0.34, 1.45, 0.64, 1),
    box-shadow 0.32s ease,
    border-color 0.28s ease;
}
.person-profile-hero .detail-avatar:hover {
  transform: scale(1.055);
  border-color: rgba(56, 189, 248, 0.48);
  box-shadow:
    0 8px 28px rgba(0, 0, 0, 0.38),
    0 0 0 1px rgba(56, 189, 248, 0.32),
    0 0 28px rgba(56, 189, 248, 0.24);
}
.person-profile-hero .detail-avatar:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.65);
  outline-offset: 4px;
}
@media (prefers-reduced-motion: reduce) {
  .person-profile-hero .detail-avatar {
    transition: none;
  }
  .person-profile-hero .detail-avatar:hover {
    transform: none;
  }
  .profile-stat-detail-icon,
  .profile-stat-trends-chart-icon {
    transition: none;
  }
  .profile-stat-tile-detail-magnet:hover .profile-stat-detail-icon,
  .profile-stat-tile-trends-magnet:hover .profile-stat-trends-chart-icon {
    transform: none;
  }
}
.profile-edit-dialog .detail-avatar {
  width: 64px;
  height: 64px;
}
.detail-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
  background: rgba(148, 163, 184, 0.14);
  border: 2px solid rgba(148, 163, 184, 0.28);
  box-shadow:
    0 6px 22px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(56, 189, 248, 0.12);
}
.loading-card {
  text-align: center;
  padding: 2rem;
}
h3 {
  margin-top: 0;
}
.report-section-title {
  margin: 0 0 1rem;
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}
.report-section-head {
  margin-bottom: 1.1rem;
}
.report-section-head .report-section-title {
  margin-bottom: 0;
}
.report-section-rule {
  margin: 0.72rem 0 0;
  height: 1px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(
    90deg,
    rgba(56, 189, 248, 0.42) 0%,
    rgba(129, 140, 248, 0.26) 22%,
    rgba(148, 163, 184, 0.14) 55%,
    transparent 92%
  );
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.08);
}
.report-enter-card .report-section-head .report-section-title,
.report-export-card .report-section-head .report-section-title {
  font-size: 1.32rem;
}
.report-enter-block-split {
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle, rgba(148, 163, 184, 0.14));
}
.report-sessions-table .cell-actions {
  gap: 0.42rem;
}
.report-sessions-table .cell-actions button {
  padding: 0.32rem 0.62rem;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}
.sessions-table-toggle-row td {
  padding: 0.35rem 0.65rem 0.15rem;
  vertical-align: middle;
  border-top: 1px solid var(--border-subtle, rgba(148, 163, 184, 0.18));
  border-bottom: none;
  background: rgba(15, 23, 42, 0.35);
}
.report-subheading {
  margin: 0 0 0.55rem;
  font-size: 1.125rem;
  font-weight: 650;
  letter-spacing: -0.015em;
}
.csv-heading-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.65rem 1rem;
  margin-bottom: 0.35rem;
}
.csv-heading-row .csv-heading-title {
  margin-bottom: 0;
}
.csv-template-download {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  flex-shrink: 0;
  padding: 0.42rem 0.85rem;
  font-size: 0.875rem;
  font-weight: 650;
  letter-spacing: -0.02em;
  text-decoration: none;
  color: #bae6fd;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.38);
  border-radius: calc(var(--radius-sm, 8px) + 2px);
  box-shadow: 0 1px 0 rgba(56, 189, 248, 0.06);
  transition:
    background 0.15s ease,
    border-color 0.15s ease,
    color 0.15s ease,
    box-shadow 0.15s ease;
}
button.csv-template-download {
  cursor: pointer;
  font-family: inherit;
  border-style: solid;
}
button.csv-template-download:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.csv-template-download:hover:not(:disabled) {
  color: #e0f2fe;
  background: rgba(56, 189, 248, 0.18);
  border-color: rgba(125, 211, 252, 0.55);
  box-shadow:
    0 2px 12px rgba(56, 189, 248, 0.12),
    0 1px 0 rgba(56, 189, 248, 0.08);
}
.csv-template-download:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.65);
  outline-offset: 2px;
}
.csv-template-download-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.35em;
  height: 1.35em;
  font-size: 0.92em;
  line-height: 1;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(15, 23, 42, 0.35);
  border-radius: 6px;
}
.csv-template-download:hover:not(:disabled) .csv-template-download-icon {
  color: #7dd3fc;
}
.batch-csv-hint {
  cursor: default;
  text-decoration: underline;
  text-decoration-style: dotted;
  text-decoration-color: rgba(148, 163, 184, 0.55);
  text-underline-offset: 3px;
  text-decoration-thickness: 1px;
}
.member-list-tooltip {
  position: fixed;
  z-index: 10050;
  max-width: min(38rem, calc(100vw - 1.5rem));
  padding: 0.65rem 0.85rem;
  font-size: 0.875rem;
  line-height: 1.55;
  color: #f1f5f9;
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.38);
  border-radius: 10px;
  box-shadow:
    0 12px 40px rgba(0, 0, 0, 0.55),
    0 0 0 1px rgba(56, 189, 248, 0.12);
  pointer-events: none;
  white-space: pre-wrap;
  word-break: break-word;
}
.export-filters-wrap {
  margin-top: 0.65rem;
  padding: 0.02rem 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.export-filters-matrix {
  display: grid;
  grid-template-columns: minmax(4.8rem, 6rem) minmax(10.5rem, 1fr) minmax(10.5rem, 1fr);
  gap: 0.55rem 0.75rem;
  align-items: center;
  min-width: min(100%, 34rem);
  margin: 0 auto;
  padding: 0.75rem 0.85rem 0.8rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(56, 189, 248, 0.2);
  background: linear-gradient(
    160deg,
    rgba(15, 23, 42, 0.55) 0%,
    rgba(30, 41, 72, 0.35) 50%,
    rgba(15, 23, 42, 0.48) 100%
  );
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.export-filters-corner {
  min-height: 0.5rem;
}

.export-filters-colhead {
  font-size: 0.8rem;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(125, 211, 252, 0.72);
  text-align: center;
  padding-bottom: 0.05rem;
  border-bottom: 1px solid rgba(56, 189, 248, 0.12);
}

.export-filters-rowhead {
  font-size: 0.88rem;
  font-weight: 650;
  letter-spacing: 0.04em;
  color: rgba(226, 232, 240, 0.92);
  line-height: 1.35;
  padding-right: 0.15rem;
}

.export-filter-cell {
  min-width: 0;
}

.export-filter-dt-row {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.4rem;
}

.export-filter-dt-row .session-datetime-input {
  min-width: 0;
  flex: 1 1 0;
}

.export-filter-dt-row .session-datetime-input[type='date'] {
  flex: 1.15 1 8rem;
}

.export-filter-dt-row .session-datetime-input[type='time'] {
  flex: 1 1 6.5rem;
}

@media (max-width: 520px) {
  .export-filters-matrix {
    grid-template-columns: minmax(4.2rem, 5.2rem) minmax(0, 1fr) minmax(0, 1fr);
    gap: 0.5rem 0.45rem;
    padding: 0.65rem 0.55rem 0.7rem;
  }

  .export-filters-colhead {
    font-size: 0.76rem;
    letter-spacing: 0.1em;
  }

  .export-filters-rowhead {
    font-size: 0.82rem;
  }
}

.export-panel {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}
.export-actions {
  margin: 0.85rem 0 0;
  font-size: 0.875rem;
  line-height: 1.55;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.55rem;
}
.export-actions-sep {
  color: rgba(148, 163, 184, 0.55);
  font-weight: 700;
  user-select: none;
}
.export-inline-err {
  margin: 0.4rem 0 0;
  font-size: 0.82rem;
}
.csv-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
  margin-top: 0.65rem;
}
.file-input {
  font-size: var(--font-form-control);
}
.csv-summary {
  margin: 0.65rem 0 0;
  font-size: 0.92rem;
}
.csv-summary-ok,
.csv-summary-bad {
  font-size: 1.125em;
  vertical-align: baseline;
}
.csv-summary-ok {
  color: #4ade80;
  margin-right: 0.3em;
}
.csv-summary-bad {
  color: #dc2626;
  margin-right: 0.25em;
}
.csv-summary-fail-tail {
  margin-left: 0.55em;
}
.csv-import-inner > .err {
  color: #dc2626;
}
.csv-err-table {
  margin-top: 0.5rem;
  font-size: 0.82rem;
}
.csv-err-table th,
.csv-err-table td {
  color: #dc2626;
}

/* 成员档案 · 报告详情 / 历年趋势 · 同构导航磁贴 */
.profile-stat-tile-detail-magnet,
.profile-stat-tile-trends-magnet {
  align-items: center;
}

.profile-stat-kicker-magnet-main {
  letter-spacing: 0.085em;
  text-align: center;
  width: 100%;
}

.profile-stat-detail-icon-wrap,
.profile-stat-trends-chart-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 1.85rem;
  margin: 0.12rem 0 0.04rem;
}

.profile-stat-detail-icon,
.profile-stat-trends-chart-icon {
  width: 3rem;
  height: auto;
  display: block;
  filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.2));
  transition:
    filter 0.22s ease,
    transform 0.22s ease;
}

.profile-stat-tile-detail-magnet:hover .profile-stat-detail-icon,
.profile-stat-tile-trends-magnet:hover .profile-stat-trends-chart-icon {
  filter:
    drop-shadow(0 0 14px rgba(56, 189, 248, 0.45))
    drop-shadow(0 0 22px rgba(129, 140, 248, 0.18));
  transform: translateY(-1px);
}

.profile-stat-tile-trends-magnet:hover :deep(.pst-trends-endcap) {
  fill: #fff;
  filter: drop-shadow(0 0 4px rgba(56, 189, 248, 0.55));
}

.profile-stat-tile-detail-magnet .profile-stat-caption,
.profile-stat-tile-trends-magnet .profile-stat-caption {
  width: 100%;
  text-align: center;
}
</style>
