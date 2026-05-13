<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  Chart,
  Filler,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  TimeScale,
  Title,
  Tooltip,
} from 'chart.js'
import annotationPlugin from 'chartjs-plugin-annotation'
import 'chartjs-adapter-date-fns'
import { RouterLink } from 'vue-router'
import { http, apiError } from '../api/http'
import type { Observation, Person } from '../api/types'
import NavBackLink from '../components/NavBackLink.vue'
import TrendsChartBadgeIcon from '../components/TrendsChartBadgeIcon.vue'
import { resolveMemberAvatarSrc } from '../utils/memberAvatar'
import { mergeRefBandFromLatestPoint } from '../utils/refRangeParse'
import {
  parseNumericValue,
  parseQualitativeTrendValue,
  qualitativeOrdinalLabel,
} from '../utils/numericParse'

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Title,
  Tooltip,
  Legend,
  Filler,
  annotationPlugin,
)

const props = defineProps<{ personId: string }>()
const route = useRoute()

const pid = Number(props.personId)
const err = ref('')
const loading = ref(true)
const person = ref<Person | null>(null)
const observations = ref<Observation[]>([])
const selectedIndicatorId = ref<number | null>(null)
/** 从报告页深链而来但该细项尚不足以成图时的说明 */
const deepLinkBanner = ref('')

const canvasEl = ref<HTMLCanvasElement | null>(null)
const chartInst = shallowRef<Chart | null>(null)

interface TrendSeries {
  id: number
  label: string
  unit: string | null
  /** 定量曲线展示数值区间；定性曲线展示阴性/阳性等级（纵轴刻度文案见 qualitativeOrdinalLabel） */
  valueKind: 'numeric' | 'qualitative'
  points: {
    x: number
    y: number
    refText: string | null
    measuredAt: string
    abnormal: boolean | null
    rawDisplay: string
  }[]
}

interface TrendPtInternal {
  t: number
  y: number
  refText: string | null
  measuredAt: string
  abnormal: boolean | null
  rawDisplay: string
  kind: 'numeric' | 'qualitative'
}

const seriesList = computed((): TrendSeries[] => {
  const map = new Map<number, { label: string; unit: string | null; pts: TrendPtInternal[] }>()

  for (const o of observations.value) {
    if (o.indicator_is_narrative) continue
    const trimmed = o.value_text?.trim()
    if (!trimmed) continue

    let kind: 'numeric' | 'qualitative'
    let y: number

    const num = parseNumericValue(trimmed)
    if (num !== null) {
      kind = 'numeric'
      y = num
    } else {
      const q = parseQualitativeTrendValue(trimmed)
      if (q === null) continue
      kind = 'qualitative'
      y = q
    }

    const t = new Date(o.measured_at).getTime()
    const label = o.indicator_parent_name
      ? `${o.indicator_parent_name} › ${o.indicator_name}`
      : o.indicator_name

    let g = map.get(o.indicator_id)
    if (!g) {
      g = { label, unit: o.indicator_unit ?? null, pts: [] }
      map.set(o.indicator_id, g)
    }
    if (o.indicator_unit && !g.unit) g.unit = o.indicator_unit

    g.pts.push({
      t,
      y,
      refText: o.ref_text,
      measuredAt: o.measured_at,
      abnormal: o.abnormal,
      rawDisplay: trimmed,
      kind,
    })
  }

  const out: TrendSeries[] = []
  for (const [id, g] of map) {
    const numericPts = g.pts.filter((p) => p.kind === 'numeric')
    const qualPts = g.pts.filter((p) => p.kind === 'qualitative')

    let chosen: TrendPtInternal[]
    let valueKind: 'numeric' | 'qualitative'

    if (numericPts.length >= 2) {
      chosen = numericPts
      valueKind = 'numeric'
    } else if (qualPts.length >= 2) {
      chosen = qualPts
      valueKind = 'qualitative'
    } else continue

    chosen.sort((a, b) => a.t - b.t)

    out.push({
      id,
      label: g.label,
      unit: g.unit,
      valueKind,
      points: chosen.map((p) => ({
        x: p.t,
        y: p.y,
        refText: p.refText,
        measuredAt: p.measuredAt,
        abnormal: p.abnormal,
        rawDisplay: p.rawDisplay,
      })),
    })
  }

  out.sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
  return out
})

const activeSeries = computed(() =>
  selectedIndicatorId.value == null
    ? null
    : seriesList.value.find((s) => s.id === selectedIndicatorId.value) ?? null,
)

/** 图示参考区间：仅定量曲线；取自当前序列时间上最后一条且能解析出数字的参考文案 */
const activeRefBand = computed(() =>
  activeSeries.value && activeSeries.value.valueKind === 'numeric'
    ? mergeRefBandFromLatestPoint(activeSeries.value.points)
    : null,
)

/** 有至少一条观测的细项（含叙述类、纯文字等），用于下拉框 */
const allIndicatorOptions = computed(() => {
  const m = new Map<number, { id: number; label: string; count: number }>()
  for (const o of observations.value) {
    const label = o.indicator_parent_name
      ? `${o.indicator_parent_name} › ${o.indicator_name}`
      : o.indicator_name
    const prev = m.get(o.indicator_id)
    if (!prev) m.set(o.indicator_id, { id: o.indicator_id, label, count: 1 })
    else prev.count += 1
  }
  return [...m.values()].sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
})

const chartEligibleIds = computed(() => new Set(seriesList.value.map((s) => s.id)))

/** 当前选中细项的全部原始记录（时间正序），含无法参与曲线的文本/叙述类 */
const historyRows = computed(() => {
  const id = selectedIndicatorId.value
  if (id == null) return []
  return observations.value
    .filter((o) => o.indicator_id === id)
    .slice()
    .sort((a, b) => new Date(a.measured_at).getTime() - new Date(b.measured_at).getTime())
})

function parseIndicatorQuery(q: unknown): number | null {
  const raw = Array.isArray(q) ? q[0] : q
  if (raw == null || raw === '') return null
  const n = Number(raw)
  return Number.isFinite(n) ? n : null
}

/** 根据路由 ?indicator= 选择细项；任意有记录的细项均可查看历年表格 */
function pickIndicatorAfterLoad() {
  const opts = allIndicatorOptions.value
  const pref = parseIndicatorQuery(route.query.indicator)
  const idsFromObs = new Set(observations.value.map((o) => o.indicator_id))

  const persistOrFirst = (): number | null => {
    const cur = selectedIndicatorId.value
    if (cur != null && opts.some((o) => o.id === cur)) return cur
    return opts[0]?.id ?? null
  }

  if (pref != null && idsFromObs.has(pref)) {
    deepLinkBanner.value = ''
    selectedIndicatorId.value = pref
    return
  }

  if (pref != null) {
    deepLinkBanner.value = '链接中的细项在当前成员数据中不存在或已无记录。'
    selectedIndicatorId.value = persistOrFirst()
    return
  }

  deepLinkBanner.value = ''
  selectedIndicatorId.value = persistOrFirst()
}

function onIndicatorSelect(e: Event) {
  deepLinkBanner.value = ''
  const v = (e.target as HTMLSelectElement).value
  selectedIndicatorId.value = v === '' ? null : Number(v)
}

async function load() {
  loading.value = true
  err.value = ''
  person.value = null
  try {
    const [{ data: p }, { data }] = await Promise.all([
      http.get<Person>(`/api/persons/${pid}`),
      http.get<Observation[]>(`/api/persons/${pid}/observations`),
    ])
    person.value = p
    observations.value = data
    pickIndicatorAfterLoad()
  } catch (e) {
    err.value = apiError(e)
    person.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => route.query.indicator,
  async () => {
    if (loading.value || observations.value.length === 0) return
    pickIndicatorAfterLoad()
    await renderChart()
  },
)

/** 与报告详情明细表一致的本地时间戳格式 */
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

/** 历年表格「报告内容」列：叙述类用所见/结论；其他用报告值与备注 */
function observationHistoryContent(o: Observation): string {
  if (o.indicator_is_narrative) {
    const body = [o.findings_text, o.conclusion_text].filter(Boolean).join('；')
    const bits = [body, o.remarks?.trim()].filter(Boolean)
    return bits.join(' · ') || '—'
  }
  const bits = [o.value_text?.trim(), o.remarks?.trim()].filter(Boolean)
  return bits.join(' · ') || '—'
}

function destroyChart() {
  chartInst.value?.destroy()
  chartInst.value = null
}

async function renderChart() {
  await nextTick()
  destroyChart()
  const canvas = canvasEl.value
  const series = activeSeries.value
  if (!canvas || !series || series.points.length < 2) return

  const isQual = series.valueKind === 'qualitative'
  const unit = series.unit
  const band = isQual ? null : activeRefBand.value

  const ys = series.points.map((p) => p.y)
  let minY: number
  let maxY: number
  if (isQual) {
    minY = Math.min(Math.min(...ys) - 0.35, -0.15)
    maxY = Math.max(Math.max(...ys) + 0.35, 1.15)
  } else {
    minY = Math.min(...ys)
    maxY = Math.max(...ys)
    const span = maxY - minY || Math.abs(maxY) || 1
    const pad = span * 0.12 || 0.01
    minY -= pad
    maxY += pad
    if (band?.low != null) minY = Math.min(minY, band.low - pad)
    if (band?.high != null) maxY = Math.max(maxY, band.high + pad)
  }

  const annotations: Record<string, Record<string, unknown>> = {}
  if (!isQual && band?.low != null && band.high != null) {
    annotations.refBand = {
      type: 'box',
      yMin: band.low,
      yMax: band.high,
      backgroundColor: 'rgba(34, 197, 94, 0.14)',
      borderWidth: 0,
      drawTime: 'beforeDatasetsDraw',
    }
  } else if (!isQual && band?.low != null) {
    annotations.refLower = {
      type: 'line',
      yMin: band.low,
      yMax: band.low,
      borderColor: 'rgba(22, 163, 74, 0.85)',
      borderDash: [6, 6],
      borderWidth: 2,
    }
  } else if (!isQual && band?.high != null) {
    annotations.refUpper = {
      type: 'line',
      yMin: band.high,
      yMax: band.high,
      borderColor: 'rgba(22, 163, 74, 0.85)',
      borderDash: [6, 6],
      borderWidth: 2,
    }
  }

  const abnormalPalette = series.points.map((p) =>
    p.abnormal === true ? '#f87171' : '#38bdf8',
  )
  const abnormalBorder = series.points.map((p) =>
    p.abnormal === true ? '#dc2626' : '#0369a1',
  )
  const radii = series.points.map((p) => (p.abnormal === true ? 8 : 5))

  const titleLines: string[] = [series.label + (unit ? ` （${unit}）` : '')]
  if (isQual) {
    titleLines.push('定性 · 纵轴：阴性(0) — 弱阳/可疑(0.5) — 阳性(1)')
  } else if (band) {
    titleLines.push(`参考区间（图示）：${band.rawLabel}`)
  }

  const yAxisBase = {
    min: minY,
    max: maxY,
    title: {
      display: true as const,
      text: isQual ? '定性等级（示意）' : unit ? `数值（${unit}）` : '数值',
      color: '#94a3b8',
    },
    grid: { color: 'rgba(148, 163, 184, 0.12)' },
    border: { color: 'rgba(148, 163, 184, 0.25)' },
  }

  chartInst.value = new Chart(canvas, {
    type: 'line',
    data: {
      datasets: [
        {
          label: series.label,
          data: series.points.map((p) => ({ x: p.x, y: p.y })),
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.14)',
          fill: true,
          stepped: isQual ? 'middle' : false,
          tension: isQual ? 0 : 0.25,
          pointRadius: radii,
          pointHoverRadius: series.points.map((p) => (p.abnormal === true ? 10 : 7)),
          pointBackgroundColor: abnormalPalette,
          pointBorderColor: abnormalBorder,
          pointBorderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        annotation: {
          annotations,
        },
        title: {
          display: true,
          text: titleLines,
          font: { size: 13, weight: 'bold' },
          color: '#e2e8f0',
          padding: { bottom: 10 },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.94)',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(56, 189, 248, 0.35)',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            title(ts) {
              const t = ts[0]?.parsed.x
              if (t == null) return ''
              return new Date(t).toLocaleString('zh-CN')
            },
            afterLabel: (item) => {
              const i = item.dataIndex
              const p = series.points[i]
              const bits: string[] = []
              if (series.valueKind === 'qualitative') {
                bits.push(`刻度示意：${qualitativeOrdinalLabel(p.y)}`)
              }
              if (p?.refText) bits.push(`参考：${p.refText}`)
              if (p?.abnormal === true) bits.push('标记：异常')
              else if (p?.abnormal === false) bits.push('标记：正常')
              return bits.join('\n')
            },
            label(ctx) {
              const i = ctx.dataIndex
              const p = series.points[i]
              if (series.valueKind === 'qualitative') {
                return `结果：${p.rawDisplay}`
              }
              const y = ctx.parsed.y
              if (y == null) return ''
              return `数值：${y}${unit ? ' ' + unit : ''}`
            },
          },
        },
      },
      scales: {
        x: {
          type: 'time',
          time: {
            displayFormats: {
              hour: 'M/d HH:mm',
              day: 'yyyy-MM-dd',
              month: 'yyyy-MM',
            },
          },
          title: { display: true, text: '时间', color: '#94a3b8' },
          ticks: { color: '#94a3b8', maxRotation: 40 },
          grid: { color: 'rgba(148, 163, 184, 0.12)' },
          border: { color: 'rgba(148, 163, 184, 0.25)' },
        },
        y: {
          ...yAxisBase,
          ticks: { color: '#94a3b8' },
          ...(isQual
            ? {
                afterBuildTicks: (scale) => {
                  const uniq = [...new Set(series.points.map((pt) => pt.y))].sort((a, b) => a - b)
                  interface TickStub {
                    value: number
                  }
                  scale.ticks = uniq.map((value) => ({
                    value,
                    label: qualitativeOrdinalLabel(value),
                  })) as TickStub[]
                },
              }
            : {}),
        },
      },
    },
  })
}

watch(
  () =>
    [activeSeries.value, loading.value, selectedIndicatorId.value, activeRefBand.value] as const,
  async () => {
    if (loading.value) return
    await renderChart()
  },
)

onMounted(async () => {
  await load()
  await renderChart()
})

onBeforeUnmount(() => destroyChart())
</script>

<template>
  <div v-if="loading && !person" class="loading-text card trends-loading-card">加载中…</div>
  <div v-else-if="!person" class="card trends-fallback-card">
    <p class="detail-back-row">
      <NavBackLink :to="`/persons/${pid}`" label="返回成员档案" />
    </p>
    <div v-if="err" class="err">{{ err }}</div>
    <p v-else class="muted">无法加载该成员或报告数据，请返回重试。</p>
  </div>
  <div v-else class="card trends-report-page">
    <p class="detail-back-row">
      <NavBackLink :to="`/persons/${pid}`" label="返回成员档案" />
    </p>
    <section class="person-profile-hero obs-report-hero trends-hero" aria-labelledby="trends-eyebrow">
      <p id="trends-eyebrow" class="person-profile-eyebrow">趋势图表</p>
      <div class="person-profile-top">
        <div class="person-profile-top-main">
          <RouterLink
            :to="`/persons/${pid}`"
            class="obs-hero-avatar-link"
            title="进入成员档案"
          >
            <img
              class="detail-avatar"
              :src="resolveMemberAvatarSrc(person)"
              width="96"
              height="96"
              alt=""
              loading="lazy"
              decoding="async"
            />
          </RouterLink>
          <div class="person-profile-title-block">
            <h2 class="person-profile-name">
              <RouterLink
                :to="`/persons/${pid}`"
                class="person-profile-name-link"
                title="进入成员档案"
              >
                {{ person.name }}
              </RouterLink>
            </h2>
            <p v-if="person.birth_date" class="person-profile-sub muted">
              出生日期 {{ person.birth_date }}
            </p>
          </div>
          <span class="person-hero-page-badge" aria-hidden="true">
            <TrendsChartBadgeIcon class="person-hero-page-badge-icon" />
          </span>
        </div>
      </div>
    </section>

    <div class="report-section-head">
      <h3 class="report-section-title">历年记录与曲线</h3>
      <hr class="report-section-rule" aria-hidden="true" />
    </div>

    <div class="obs-outbound-actions">
      <RouterLink
        class="obs-trends-outbound obs-outbound--report-detail"
        :to="`/persons/${pid}/observations`"
        title="全部检查细项 · 按器官 / 类型 / 时间"
      >
        <span class="obs-trends-icon-wrap" aria-hidden="true">
          <svg class="obs-trends-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M8 7h12M8 12h12M8 17h9"
            />
          </svg>
        </span>
        <span class="obs-trends-outbound-text">
          <span class="obs-trends-outbound-kicker">浏览</span>
          <span class="obs-trends-outbound-main">报告详情</span>
        </span>
        <svg class="obs-trends-outbound-chevron" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M10 8l4 4-4 4"
          />
        </svg>
      </RouterLink>
    </div>

    <p v-if="deepLinkBanner" class="deep-link-banner">{{ deepLinkBanner }}</p>
    <p class="muted mode-hintro">
      在下拉框中选择<strong>检查细项</strong>后，下方<strong>历年完整记录</strong>列出该细项全部原始数据（含<strong>叙述类</strong>、普通文字报告值及备注等）。
      若其中至少有 <strong>2 条</strong>非叙述记录且报告值可解析为<strong>数字</strong>或常见<strong>阴性/阳性</strong>等定性用语，上方将显示<strong>趋势曲线</strong>（下拉项旁标「曲线」）。
      定量曲线可参考最近一次<strong>数值参考范围</strong>显示<strong class="band-label">绿色区间或虚线</strong>。
      <strong class="legend-dot">●</strong><span class="legend-red">红</span>点表示该点对应记录标记为<strong>异常</strong>。
    </p>

    <div v-if="allIndicatorOptions.length === 0" class="muted trends-empty-msg">
      暂无报告明细，无法查看历年记录。
    </div>
    <template v-else>
      <div class="row pick">
        <label>
          检查细项
          <select :value="selectedIndicatorId ?? ''" @change="onIndicatorSelect">
            <option v-for="opt in allIndicatorOptions" :key="opt.id" :value="opt.id">
              {{ opt.label }}（{{ opt.count }} 条）{{ chartEligibleIds.has(opt.id) ? ' · 曲线' : '' }}
            </option>
          </select>
        </label>
      </div>

      <p
        v-if="selectedIndicatorId != null && !activeSeries && historyRows.length"
        class="curve-hint muted"
      >
        以下为该细项<strong>全部</strong>历年记录。若需趋势图，请满足：同一细项下不少于 2 条<strong>非叙述</strong>记录，且报告值为<strong>数字</strong>或常见<strong>阴性/阳性</strong>等系统可识别的定性用语。
      </p>

      <div v-if="activeSeries" class="chart-wrap">
        <canvas ref="canvasEl" />
      </div>

      <template v-if="historyRows.length">
        <div class="report-section-head trends-history-section-head">
          <h3 class="report-section-title">历年完整记录</h3>
          <hr class="report-section-rule" aria-hidden="true" />
        </div>
        <table class="history-table obs-detail-table">
          <thead>
            <tr>
              <th>测量时间</th>
              <th>批次报告</th>
              <th>报告内容</th>
              <th>参考</th>
              <th>异常</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="o in historyRows"
              :key="o.id"
              :class="{ 'row-abnormal': o.abnormal === true }"
            >
              <td class="session-datetime">{{ fmt(o.measured_at) }}</td>
              <td class="session-datetime">{{ fmt(o.session_report_at) }}</td>
              <td class="cell-content">
                <span v-if="o.indicator_is_narrative" class="tag-narr">叙述</span>
                {{ observationHistoryContent(o) }}
              </td>
              <td>{{ o.ref_text ?? '—' }}</td>
              <td :class="{ 'cell-abnormal': o.abnormal === true }">
                {{ o.abnormal === true ? '是' : o.abnormal === false ? '否' : '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </template>
    </template>
  </div>
</template>

<style scoped>
.detail-back-row {
  margin: 0 0 0.85rem;
}
.trends-loading-card {
  text-align: center;
  padding: 2rem;
}
.trends-fallback-card .detail-back-row {
  margin-bottom: 0.65rem;
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
.obs-report-hero.trends-hero {
  margin-bottom: 1.05rem;
}
.person-profile-top {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 0;
}
.person-profile-top-main {
  display: flex;
  align-items: center;
  gap: 1.28rem;
  flex: 1;
  min-width: 0;
}
.person-hero-page-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-inline-start: auto;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  pointer-events: none;
  cursor: default;
}
.person-hero-page-badge-icon {
  width: clamp(4.1rem, 7.2vw, 5.4rem);
  height: auto;
  display: block;
  filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.14));
  opacity: 0.97;
}
.person-profile-title-block {
  flex: 1;
  min-width: 12rem;
}
.person-profile-name {
  margin: 0 0 0.25rem;
  font-size: clamp(1.65rem, 4.1vw, 2.15rem);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.15;
}
.person-profile-name-link {
  color: var(--text-primary);
  text-decoration: none;
  text-underline-offset: 0.12em;
  transition: color 0.18s ease;
}
.person-profile-name-link:hover {
  color: #7dd3fc;
}
.person-profile-name-link:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.65);
  outline-offset: 4px;
  border-radius: 4px;
}
.person-profile-sub {
  margin: 0;
  font-size: clamp(0.9rem, 1.65vw, 1rem);
  letter-spacing: 0.03em;
}
.obs-hero-avatar-link {
  display: inline-flex;
  border-radius: 50%;
  flex-shrink: 0;
  text-decoration: none;
  color: inherit;
}
.detail-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
  background: rgba(148, 163, 184, 0.14);
  border: 2px solid rgba(148, 163, 184, 0.28);
  box-shadow:
    0 6px 22px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(56, 189, 248, 0.12);
  transition:
    transform 0.38s cubic-bezier(0.34, 1.45, 0.64, 1),
    box-shadow 0.32s ease,
    border-color 0.28s ease;
}
.obs-hero-avatar-link:hover .detail-avatar {
  transform: scale(1.055);
  border-color: rgba(56, 189, 248, 0.48);
  box-shadow:
    0 8px 28px rgba(0, 0, 0, 0.38),
    0 0 0 1px rgba(56, 189, 248, 0.32),
    0 0 28px rgba(56, 189, 248, 0.24);
}
.report-section-head {
  margin-bottom: 0;
}
.report-section-head .report-section-title {
  margin-bottom: 0;
}
.report-section-title {
  margin: 0 0 1rem;
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}
.report-section-rule {
  margin: 0.72rem 0 0.65rem;
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
.trends-history-section-head {
  margin-top: 0.25rem;
}
.obs-outbound-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0 0 1rem;
}
.obs-outbound--report-detail.obs-trends-outbound:focus-visible {
  outline-color: rgba(129, 140, 248, 0.6);
}
.obs-outbound--report-detail.obs-trends-outbound:hover {
  border-color: rgba(129, 140, 248, 0.32);
  background:
    linear-gradient(
      155deg,
      rgba(129, 140, 248, 0.1) 0%,
      rgba(56, 189, 248, 0.05) 55%,
      rgba(15, 23, 42, 0.45) 100%
    ),
    rgba(15, 23, 42, 0.42);
  box-shadow:
    0 1px 0 rgba(129, 140, 248, 0.07) inset,
    0 0 24px rgba(129, 140, 248, 0.1),
    0 12px 36px rgba(0, 0, 0, 0.16);
}
.obs-outbound--report-detail .obs-trends-icon-wrap {
  border-color: rgba(129, 140, 248, 0.35);
  background: linear-gradient(
    150deg,
    rgba(129, 140, 248, 0.2) 0%,
    rgba(56, 189, 248, 0.08) 100%
  );
  color: #a5b4fc;
}
.obs-outbound--report-detail.obs-trends-outbound:hover .obs-trends-icon-wrap {
  color: #e0e7ff;
  border-color: rgba(165, 180, 252, 0.45);
  transform: scale(1.04);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 0 22px rgba(129, 140, 248, 0.18);
}
.obs-trends-outbound {
  display: flex;
  align-items: center;
  gap: 0.78rem 1rem;
  max-width: 100%;
  width: 100%;
  padding: 0.52rem 0.78rem 0.52rem 0.58rem;
  border-radius: calc(var(--radius-md) + 2px);
  border: 1px solid rgba(148, 163, 184, 0.14);
  background:
    linear-gradient(
      155deg,
      rgba(17, 26, 46, 0.55) 0%,
      rgba(15, 23, 42, 0.35) 100%
    ),
    rgba(12, 18, 34, 0.25);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.04) inset,
    0 10px 32px rgba(0, 0, 0, 0.12);
  text-decoration: none;
  color: #cbd5e1;
  transition:
    border-color 0.22s ease,
    background 0.22s ease,
    box-shadow 0.22s ease,
    color 0.18s ease;
}
.obs-trends-outbound:hover {
  color: #e2e8f0;
  border-color: rgba(56, 189, 248, 0.28);
  background:
    linear-gradient(
      155deg,
      rgba(56, 189, 248, 0.08) 0%,
      rgba(129, 140, 248, 0.05) 55%,
      rgba(15, 23, 42, 0.45) 100%
    ),
    rgba(15, 23, 42, 0.4);
  box-shadow:
    0 1px 0 rgba(129, 140, 248, 0.06) inset,
    0 0 22px rgba(56, 189, 248, 0.08),
    0 12px 36px rgba(0, 0, 0, 0.16);
}
.obs-outbound--report-detail.obs-trends-outbound:hover {
  border-color: rgba(129, 140, 248, 0.32);
}
.obs-trends-outbound:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.55);
  outline-offset: 3px;
}
.obs-trends-icon-wrap {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.55rem;
  height: 2.55rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(56, 189, 248, 0.22);
  background: linear-gradient(
    150deg,
    rgba(56, 189, 248, 0.16) 0%,
    rgba(129, 140, 248, 0.07) 100%
  );
  color: #7dd3fc;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
  transition:
    transform 0.22s cubic-bezier(0.34, 1.35, 0.64, 1),
    border-color 0.22s ease,
    color 0.18s ease,
    box-shadow 0.22s ease;
}
.obs-trends-outbound:hover .obs-trends-icon-wrap {
  transform: scale(1.04);
}
.obs-trends-outbound:not(.obs-outbound--report-detail):hover .obs-trends-icon-wrap {
  color: #e0f2fe;
  border-color: rgba(125, 211, 252, 0.38);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 0 20px rgba(56, 189, 248, 0.15);
}
.obs-trends-icon {
  width: 1.35rem;
  height: 1.35rem;
  display: block;
}
.obs-trends-outbound-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.1rem;
  min-width: 0;
  flex: 1 1 auto;
}
.obs-trends-outbound-kicker {
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.92);
}
.obs-trends-outbound:hover .obs-trends-outbound-kicker {
  color: rgba(186, 230, 253, 0.78);
}
.obs-trends-outbound-main {
  font-size: var(--font-page-hero-eyebrow);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.3;
  color: #f1f5f9;
}
.obs-trends-outbound:hover .obs-trends-outbound-main {
  color: #fff;
}
.obs-trends-outbound-chevron {
  flex-shrink: 0;
  width: 1.35rem;
  height: 1.35rem;
  align-self: center;
  margin-left: 0.25rem;
  color: rgba(148, 163, 184, 0.45);
  transition: transform 0.2s ease, color 0.18s ease;
}
.obs-trends-outbound:hover .obs-trends-outbound-chevron {
  color: rgba(125, 211, 252, 0.95);
  transform: translateX(3px);
}
.obs-outbound--report-detail.obs-trends-outbound:hover .obs-trends-outbound-chevron {
  color: rgba(196, 181, 253, 0.95);
}
.mode-hintro {
  margin: 0 0 0.85rem;
  font-size: 0.85rem;
  max-width: 46rem;
  line-height: 1.55;
}
.trends-empty-msg {
  margin: 0.35rem 0 0;
}
.deep-link-banner {
  margin: 0 0 0.85rem;
  padding: 0.65rem 0.85rem;
  font-size: 0.88rem;
  line-height: 1.5;
  color: #fcd34d;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.38);
  border-radius: var(--radius-sm);
}
.pick {
  margin-bottom: 0.85rem;
}
.curve-hint {
  margin: 0 0 0.85rem;
  font-size: 0.88rem;
  line-height: 1.55;
}
.chart-wrap {
  position: relative;
  height: 380px;
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.04) inset;
}
.legend-dot {
  color: #f87171;
  margin-left: 0.35rem;
}
.legend-red {
  color: #f87171;
  font-weight: 650;
}
.band-label {
  color: #4ade80;
}
.cell-content {
  max-width: 28rem;
  line-height: 1.45;
  word-break: break-word;
}
.tag-narr {
  display: inline-block;
  margin-right: 0.35rem;
  padding: 0.08rem 0.38rem;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #a78bfa;
  background: rgba(129, 140, 248, 0.14);
  border: 1px solid rgba(129, 140, 248, 0.35);
  border-radius: 4px;
  vertical-align: middle;
}
@media (max-width: 540px) {
  .person-profile-top {
    flex-direction: column;
    align-items: stretch;
  }
}
@media (prefers-reduced-motion: reduce) {
  .detail-avatar {
    transition: none;
  }
  .obs-hero-avatar-link:hover .detail-avatar {
    transform: none;
  }
  .obs-trends-outbound:hover .obs-trends-icon-wrap {
    transform: none;
  }
  .obs-trends-outbound:hover .obs-trends-outbound-chevron {
    transform: none;
  }
}
</style>
