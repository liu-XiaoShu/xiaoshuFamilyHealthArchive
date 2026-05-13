<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { http, apiError } from '../api/http'
import type { CurrentAbnormalItem, Observation, Person } from '../api/types'
import NavBackLink from '../components/NavBackLink.vue'
import ReportDetailBadgeIcon from '../components/ReportDetailBadgeIcon.vue'
import { resolveMemberAvatarSrc } from '../utils/memberAvatar'

const props = withDefaults(
  defineProps<{ personId: string; reportMode?: 'all' | 'current-abnormal' }>(),
  { reportMode: 'all' },
)

const observations = ref<Observation[]>([])
const person = ref<Person | null>(null)
/** 当前成员性别适用的器官顺序（用于「按器官」分组排序） */
const personOrgansOrdered = ref<{ name: string }[]>([])
const err = ref('')
const loading = ref(false)
const tab = ref<'organ' | 'type' | 'time'>('organ')
const abnormalOnly = ref(false)

const pid = computed(() => Number(props.personId))

function abnormalItemToObservation(it: CurrentAbnormalItem): Observation {
  return {
    id: it.observation_id,
    session_id: -1,
    indicator_id: it.indicator_id,
    measured_at: it.measured_at,
    value_text: it.value_text,
    ref_text: it.ref_text,
    abnormal: it.abnormal ?? true,
    remarks: it.remarks,
    findings_text: it.findings_text,
    conclusion_text: it.conclusion_text,
    indicator_name: it.indicator_name,
    indicator_category: it.indicator_category,
    indicator_is_narrative: it.indicator_is_narrative,
    indicator_parent_id: null,
    indicator_parent_name: it.indicator_parent_name,
    indicator_unit: null,
    organ_ids: [],
    organ_names: it.organ_names,
    session_report_at: it.session_report_at,
    basis_label: it.basis_label,
  }
}

async function loadPersonOrgansOrder() {
  try {
    const { data: orgs } = await http.get<{ name: string }[]>(
      `/api/persons/${pid.value}/organs`,
    )
    personOrgansOrdered.value = orgs
  } catch {
    try {
      const { data: orgsAll } = await http.get<{ name: string }[]>('/api/indicators/organs')
      personOrgansOrdered.value = orgsAll
    } catch {
      personOrgansOrdered.value = []
    }
  }
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const [{ data: p }, { data: obsRaw }] = await Promise.all([
      http.get<Person>(`/api/persons/${pid.value}`),
      props.reportMode === 'current-abnormal'
        ? http.get<CurrentAbnormalItem[]>(`/api/persons/${pid.value}/current-abnormals`)
        : http.get<Observation[]>(`/api/persons/${pid.value}/observations`),
    ])
    person.value = p
    observations.value =
      props.reportMode === 'current-abnormal'
        ? (obsRaw as CurrentAbnormalItem[]).map(abnormalItemToObservation)
        : (obsRaw as Observation[])

    await loadPersonOrgansOrder()
  } catch (e) {
    err.value = apiError(e)
    person.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.personId, props.reportMode] as const,
  () => {
    person.value = null
    void load()
  },
  { immediate: true },
)

const filteredObservations = computed(() => {
  if (props.reportMode === 'current-abnormal') return observations.value
  if (!abnormalOnly.value) return observations.value
  return observations.value.filter((o) => o.abnormal === true)
})

const organOrderIndex = computed(() => {
  const m = new Map<string, number>()
  personOrgansOrdered.value.forEach((x, i) => m.set(x.name, i))
  return m
})

const byOrgan = computed(() => {
  const m = new Map<string, Observation[]>()
  for (const o of filteredObservations.value) {
    const key =
      o.organ_names.length > 0 ? o.organ_names.join('、') : '（未关联器官）'
    if (!m.has(key)) m.set(key, [])
    m.get(key)!.push(o)
  }
  const UNKNOWN = 500_000
  function rankSection(key: string): number {
    if (key === '（未关联器官）') return Number.MAX_SAFE_INTEGER
    let best = UNKNOWN
    for (const part of key.split('、')) {
      const idx = organOrderIndex.value.get(part.trim())
      if (idx !== undefined) best = Math.min(best, idx)
    }
    return best
  }
  return Array.from(m.entries()).sort(([a], [b]) => {
    const ra = rankSection(a)
    const rb = rankSection(b)
    if (ra !== rb) return ra - rb
    return a.localeCompare(b, 'zh-CN')
  })
})

const catLabel: Record<string, string> = {
  physical: '基础体格',
  lab: '检验',
  imaging: '影像 / 检查',
}

const byType = computed(() => {
  const m = new Map<string, Observation[]>()
  for (const o of filteredObservations.value) {
    const key = catLabel[o.indicator_category] ?? o.indicator_category
    if (!m.has(key)) m.set(key, [])
    m.get(key)!.push(o)
  }
  return Array.from(m.entries()).sort(([a], [b]) => a.localeCompare(b, 'zh-CN'))
})

const timeline = computed(() =>
  [...filteredObservations.value].sort(
    (a, b) => new Date(b.measured_at).getTime() - new Date(a.measured_at).getTime(),
  ),
)

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

function line(o: Observation): string {
  if (o.indicator_is_narrative) {
    return [o.findings_text, o.conclusion_text].filter(Boolean).join('；') || '—'
  }
  const bits = [o.value_text, o.ref_text ? `参考 ${o.ref_text}` : '', o.remarks].filter(
    Boolean,
  )
  return bits.join(' · ') || '—'
}

const showNoAbnormalTip = computed(
  () =>
    props.reportMode === 'all' &&
    !loading.value &&
    abnormalOnly.value &&
    observations.value.length > 0 &&
    filteredObservations.value.length === 0,
)

const heroEyebrow = computed(() =>
  props.reportMode === 'current-abnormal' ? '当前异常项目' : '报告详情',
)

const emptyHint = computed(() =>
  props.reportMode === 'current-abnormal'
    ? '当前没有仍处于异常状态的检查细项。'
    : '暂无记录。',
)
</script>

<template>
  <div v-if="loading && !person" class="loading-text card loading-card">加载中…</div>
  <div v-else-if="!person" class="card obs-fallback-card">
    <p class="detail-back-row">
      <NavBackLink :to="`/persons/${pid}`" label="返回成员档案" />
    </p>
    <div v-if="err" class="err">{{ err }}</div>
    <p v-else class="muted">无法加载该成员，请返回重试。</p>
  </div>
  <div v-else-if="person" class="card obs-report-page">
    <p class="detail-back-row">
      <NavBackLink :to="`/persons/${pid}`" label="返回成员档案" />
    </p>
    <section class="person-profile-hero obs-report-hero" aria-labelledby="obs-report-eyebrow">
      <p id="obs-report-eyebrow" class="person-profile-eyebrow">{{ heroEyebrow }}</p>
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
            <ReportDetailBadgeIcon class="person-hero-page-badge-icon" />
          </span>
        </div>
      </div>
    </section>

    <div class="report-section-head">
      <h3 class="report-section-title">报告明细</h3>
      <hr class="report-section-rule" aria-hidden="true" />
    </div>

    <div class="obs-outbound-actions">
      <RouterLink
        v-if="reportMode === 'current-abnormal'"
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
          <span class="obs-trends-outbound-main">报告详情（完整）</span>
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
      <RouterLink
        class="obs-trends-outbound"
        :to="`/persons/${pid}/trends`"
        title="按时间浏览 · 指标趋势对比"
      >
        <span class="obs-trends-icon-wrap" aria-hidden="true">
          <svg class="obs-trends-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              class="obs-trends-icon-line"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M5 17l5-8 4 5 8-11"
            />
            <circle class="obs-trends-icon-dot" cx="18" cy="8" r="1.5" fill="currentColor" />
          </svg>
        </span>
        <span class="obs-trends-outbound-text">
          <span class="obs-trends-outbound-kicker">趋势图表</span>
          <span class="obs-trends-outbound-main">历年记录与曲线</span>
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

    <p v-if="reportMode === 'current-abnormal'" class="muted mode-hint">
      以下为当前仍为异常的检查细项（自然年覆盖规则：本年已有复查则以本年为准；本年尚无则以最近一次为准）。
    </p>

    <div
      class="obs-filter-tabs-row"
      :class="{ 'obs-filter-tabs-row--solo': reportMode !== 'all' }"
    >
      <label v-if="reportMode === 'all'" class="obs-abnormal-toggle">
        <input v-model="abnormalOnly" type="checkbox" class="obs-abnormal-input" />
        <span class="obs-abnormal-track" aria-hidden="true">
          <span class="obs-abnormal-knob" />
        </span>
        <span class="obs-abnormal-text">只看异常</span>
      </label>
      <div class="tabs obs-report-tabs">
        <button type="button" :class="{ active: tab === 'organ' }" @click="tab = 'organ'">
          按器官
        </button>
        <button type="button" :class="{ active: tab === 'type' }" @click="tab = 'type'">
          按检查类型
        </button>
        <button type="button" :class="{ active: tab === 'time' }" @click="tab = 'time'">
          按时间
        </button>
      </div>
    </div>

    <p v-if="showNoAbnormalTip" class="muted filter-tip">
      当前筛选下没有标记为异常的记录。
    </p>
    <p v-if="tab === 'organ' && reportMode === 'all'" class="muted organ-sort-hint">
      分组顺序依据<strong>当前成员性别适用的器官目录</strong>（性别未填时包含男女特异性器官供排序参考）。
    </p>
    <p
      v-if="tab === 'organ' && reportMode === 'current-abnormal'"
      class="muted organ-sort-hint"
    >
      分组顺序依据<strong>当前成员性别适用的器官目录</strong>。
    </p>

    <p v-if="loading" class="muted obs-inline-loading">刷新中…</p>

    <template v-else-if="tab === 'organ'">
      <section v-for="[organ, rows] in byOrgan" :key="organ" class="block">
        <h3 class="obs-organ-section-title">{{ organ }}</h3>
        <table class="obs-detail-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>项目</th>
              <th>内容</th>
              <th>异常</th>
              <th class="col-trend">历年</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="o in rows"
              :key="o.id"
              :class="{ 'row-abnormal': o.abnormal === true }"
            >
              <td class="session-datetime">{{ fmt(o.measured_at) }}</td>
              <td>
                {{ o.indicator_parent_name ? o.indicator_parent_name + ' › ' : ''
                }}{{ o.indicator_name }}
              </td>
              <td :class="{ 'cell-abnormal': o.abnormal === true }">
                <template v-if="reportMode === 'current-abnormal' && o.basis_label">
                  <span class="basis-note">{{ o.basis_label }}</span>
                  <br />
                </template>
                {{ line(o) }}
              </td>
              <td :class="{ 'cell-abnormal': o.abnormal === true }">
                {{ o.abnormal === true ? '是' : o.abnormal === false ? '否' : '—' }}
              </td>
              <td class="col-trend">
                <RouterLink
                  class="trend-link"
                  :to="{ path: `/persons/${pid}/trends`, query: { indicator: String(o.indicator_id) } }"
                >
                  历年
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>

    <template v-else-if="tab === 'type'">
      <section v-for="[cat, rows] in byType" :key="cat" class="block">
        <h3>{{ cat }}</h3>
        <table class="obs-detail-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>项目</th>
              <th>内容</th>
              <th>异常</th>
              <th class="col-trend">历年</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="o in rows"
              :key="o.id"
              :class="{ 'row-abnormal': o.abnormal === true }"
            >
              <td class="session-datetime">{{ fmt(o.measured_at) }}</td>
              <td>
                {{ o.indicator_parent_name ? o.indicator_parent_name + ' › ' : ''
                }}{{ o.indicator_name }}
              </td>
              <td :class="{ 'cell-abnormal': o.abnormal === true }">
                <template v-if="reportMode === 'current-abnormal' && o.basis_label">
                  <span class="basis-note">{{ o.basis_label }}</span>
                  <br />
                </template>
                {{ line(o) }}
              </td>
              <td :class="{ 'cell-abnormal': o.abnormal === true }">
                {{ o.abnormal === true ? '是' : o.abnormal === false ? '否' : '—' }}
              </td>
              <td class="col-trend">
                <RouterLink
                  class="trend-link"
                  :to="{ path: `/persons/${pid}/trends`, query: { indicator: String(o.indicator_id) } }"
                >
                  历年
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>

    <template v-else>
      <table class="obs-detail-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>项目</th>
            <th>内容</th>
            <th>异常</th>
            <th class="col-trend">历年</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in timeline"
            :key="o.id"
            :class="{ 'row-abnormal': o.abnormal === true }"
          >
            <td class="session-datetime">{{ fmt(o.measured_at) }}</td>
            <td>
              {{ o.indicator_parent_name ? o.indicator_parent_name + ' › ' : ''
              }}{{ o.indicator_name }}
            </td>
            <td :class="{ 'cell-abnormal': o.abnormal === true }">
              <template v-if="reportMode === 'current-abnormal' && o.basis_label">
                <span class="basis-note">{{ o.basis_label }}</span>
                <br />
              </template>
              {{ line(o) }}
            </td>
            <td :class="{ 'cell-abnormal': o.abnormal === true }">
              {{ o.abnormal === true ? '是' : o.abnormal === false ? '否' : '—' }}
            </td>
            <td class="col-trend">
              <RouterLink
                class="trend-link"
                :to="{ path: `/persons/${pid}/trends`, query: { indicator: String(o.indicator_id) } }"
              >
                历年
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </template>

    <p
      v-if="!loading && observations.length === 0 && !showNoAbnormalTip"
      class="muted"
    >
      {{ emptyHint }}
    </p>
  </div>
</template>

<style scoped>
.detail-back-row {
  margin: 0 0 0.85rem;
}
.loading-card {
  text-align: center;
  padding: 2rem;
}
.obs-fallback-card .detail-back-row {
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
.obs-report-hero {
  margin-bottom: 1.05rem;
}
.person-profile-top {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
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
  color: #e0f2fe;
  border-color: rgba(125, 211, 252, 0.38);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 0 20px rgba(56, 189, 248, 0.15);
  transform: scale(1.04);
}
.obs-trends-icon {
  width: 1.35rem;
  height: 1.35rem;
  display: block;
}
.obs-trends-icon-line {
  opacity: 0.95;
}
.obs-trends-icon-dot {
  opacity: 1;
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
.obs-inline-loading {
  margin: 0.45rem 0 0.65rem;
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
  .obs-abnormal-knob {
    transition: none;
  }
  .obs-trends-outbound:hover .obs-trends-icon-wrap {
    transform: none;
  }
  .obs-trends-outbound:hover .obs-trends-outbound-chevron {
    transform: none;
  }
}
h3 {
  margin: 0 0 0.55rem;
  font-size: 1.02rem;
  font-weight: 650;
  letter-spacing: -0.02em;
  color: #cbd5e1;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid rgba(56, 189, 248, 0.22);
}
h3.obs-organ-section-title {
  margin: 0 0 0.72rem;
  padding: 0.55rem 0.9rem 0.58rem 0.78rem;
  font-size: clamp(1.14rem, 2.75vw, 1.38rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.22;
  color: #f8fafc;
  background: linear-gradient(
    105deg,
    rgba(56, 189, 248, 0.15) 0%,
    rgba(129, 140, 248, 0.08) 42%,
    rgba(15, 23, 42, 0.28) 100%
  );
  border-left: 4px solid rgba(56, 189, 248, 0.78);
  border-bottom: 1px solid rgba(56, 189, 248, 0.32);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.05) inset,
    0 8px 26px rgba(0, 0, 0, 0.14);
}
.block {
  margin-bottom: 1.35rem;
}
.mode-hint {
  margin: 0 0 0.85rem;
  font-size: 0.85rem;
  max-width: 44rem;
}
.basis-note {
  display: inline-block;
  font-size: 0.82rem;
  color: #94a3b8;
  margin-bottom: 0.15rem;
  line-height: 1.35;
}
.obs-filter-tabs-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem 1rem;
  margin-bottom: 0.2rem;
}
.obs-filter-tabs-row .obs-report-tabs {
  margin-bottom: 0.55rem;
}
.obs-filter-tabs-row:not(.obs-filter-tabs-row--solo) .obs-report-tabs {
  margin-left: auto;
}
.obs-filter-tabs-row--solo .obs-report-tabs {
  margin-left: 0;
}
@media (max-width: 520px) {
  .obs-filter-tabs-row:not(.obs-filter-tabs-row--solo) .obs-report-tabs {
    margin-left: 0;
    flex: 1 1 100%;
  }
}
.obs-abnormal-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
  padding: 0.35rem 0.55rem 0.35rem 0.45rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(15, 23, 42, 0.45);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  transition: border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}
.obs-abnormal-toggle:hover {
  border-color: rgba(56, 189, 248, 0.28);
  background: rgba(56, 189, 248, 0.06);
}
.obs-abnormal-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.obs-abnormal-input:focus-visible + .obs-abnormal-track {
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.obs-abnormal-input:checked + .obs-abnormal-track {
  background: linear-gradient(
    145deg,
    rgba(14, 165, 233, 0.52) 0%,
    rgba(99, 102, 241, 0.45) 100%
  );
  border-color: rgba(56, 189, 248, 0.55);
}
.obs-abnormal-input:checked + .obs-abnormal-track .obs-abnormal-knob {
  transform: translateX(1.15rem);
  background: #f8fafc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.28);
}
.obs-abnormal-track {
  position: relative;
  display: inline-block;
  width: 2.65rem;
  height: 1.5rem;
  border-radius: 999px;
  flex-shrink: 0;
  background: rgba(51, 65, 85, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.28);
  transition:
    background 0.22s ease,
    border-color 0.22s ease;
}
.obs-abnormal-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 1.14rem;
  height: 1.14rem;
  border-radius: 50%;
  background: #e2e8f0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.35);
  transition: transform 0.22s cubic-bezier(0.34, 1.45, 0.64, 1), background 0.18s ease;
}
.obs-abnormal-text {
  font-size: 0.88rem;
  font-weight: 650;
  letter-spacing: 0.02em;
  color: var(--text-secondary);
}
.obs-abnormal-input:checked ~ .obs-abnormal-text {
  color: #e0f2fe;
}
.filter-tip {
  margin: 0 0 0.55rem;
  font-size: 0.85rem;
}
.organ-sort-hint {
  margin: 0 0 0.65rem;
  font-size: 0.82rem;
}
.col-trend {
  white-space: nowrap;
  width: 4rem;
}
.trend-link {
  font-weight: 650;
  font-size: 0.88rem;
  border-bottom: 1px dashed rgba(56, 189, 248, 0.45);
  padding-bottom: 1px;
}
.trend-link:hover {
  border-bottom-style: solid;
}
</style>
