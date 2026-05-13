<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { http, apiError } from '../api/http'
import type { Person } from '../api/types'
import { resolveMemberAvatarSrc } from '../utils/memberAvatar'
import { GENDER_SELECT_OPTIONS } from '../constants/personForm'
import { username } from '../auth/session'
import { familyNavLabelFromUsername } from '../utils/familyNavLabel'

const genderOptions = GENDER_SELECT_OPTIONS

const listPageHeadline = computed(() => familyNavLabelFromUsername(username.value))
const router = useRouter()
const route = useRoute()
const persons = ref<Person[]>([])
/** 列表加载、删除等 */
const pageErr = ref('')
/** 添加成员表单校验与提交 */
const formErr = ref('')
const loading = ref(false)

const addPanelEl = ref<HTMLElement | null>(null)
const showAddPanel = ref(false)
/** 列表筛选：仅显示当前仍有异常的成员 */
const abnormalOnlyFilter = ref(false)

const form = ref({
  name: '',
  gender: '',
  birth_date: '',
  member_role: '',
})

async function load() {
  loading.value = true
  pageErr.value = ''
  try {
    const { data } = await http.get<Person[]>('/api/persons')
    persons.value = data
  } catch (e) {
    pageErr.value = apiError(e)
  } finally {
    loading.value = false
  }
}

function closeAddPanel() {
  showAddPanel.value = false
  formErr.value = ''
  if (route.hash === '#add-member') {
    void router.replace({ path: route.path, hash: '' })
  }
}

function goToAddForm() {
  showAddPanel.value = true
  formErr.value = ''
}

function onAddModalKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    closeAddPanel()
  }
}

watch(showAddPanel, (open) => {
  if (open) {
    document.addEventListener('keydown', onAddModalKeydown)
    void nextTick(() => {
      addPanelEl.value?.focus({ preventScroll: true })
    })
  } else {
    document.removeEventListener('keydown', onAddModalKeydown)
  }
})

async function createPerson() {
  if (!form.value.name.trim()) {
    formErr.value = '请输入姓名'
    return
  }
  formErr.value = ''
  try {
    await http.post('/api/persons', {
      name: form.value.name.trim(),
      gender: form.value.gender || null,
      birth_date: form.value.birth_date || null,
      member_role: form.value.member_role.trim() || null,
      notes: null,
    })
    form.value = {
      name: '',
      gender: '',
      birth_date: '',
      member_role: '',
    }
    await load()
    showAddPanel.value = false
    if (route.hash === '#add-member') {
      void router.replace({ path: route.path, hash: '' })
    }
  } catch (e) {
    formErr.value = apiError(e)
  }
}

async function remove(id: number) {
  if (!confirm('确定删除该成员及其全部报告数据？')) return
  pageErr.value = ''
  try {
    await http.delete(`/api/persons/${id}`)
    await load()
  } catch (e) {
    pageErr.value = apiError(e)
  }
}

function fmtVitalNum(v: number | null | undefined): string {
  if (v == null || Number.isNaN(Number(v))) return '—'
  const n = Number(v)
  return Number.isInteger(n) ? String(n) : n.toFixed(1)
}

/** 全家概况（基于当前列表数据） */
const listSummary = computed(() => {
  const list = persons.value
  let abnormalItemsSum = 0
  let membersWithAbnormal = 0
  for (const p of list) {
    const n = p.current_abnormal_count ?? 0
    abnormalItemsSum += n
    if (n > 0) membersWithAbnormal += 1
  }
  return {
    memberCount: list.length,
    abnormalItemsSum,
    membersWithAbnormal,
  }
})

const displayedPersons = computed(() => {
  if (!abnormalOnlyFilter.value) return persons.value
  return persons.value.filter((p) => (p.current_abnormal_count ?? 0) > 0)
})

function toggleFollowFilter() {
  abnormalOnlyFilter.value = !abnormalOnlyFilter.value
}

const tipAvatarNameCol =
  '头像：未上传自定义头像时为姓名缩写占位图；可在成员详情页上传。点击姓名进入成员主页。'

const tipVitalsCols =
  '血型、身高、体重来自体检报告指标（与本年复查覆盖规则一致：本年内有记录则取本年最新一条有值记录，否则取更早的最近一条）。'

const tipAbnormalCol =
  '「当前异常」按本年是否复查覆盖统计（详见进入列表后的页面说明）。点击数字进入异常列表。'

const tipEnterHome = '进入成员主页'

type HoverTipState = { text: string; x: number; y: number }

/** 原生 title 在部分环境下不可靠；用跟随鼠标的浮动层展示说明 */
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

onMounted(async () => {
  await load()
  await nextTick()
  if (route.hash === '#add-member') {
    goToAddForm()
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', onAddModalKeydown)
})
</script>

<template>
  <div class="card">
    <div class="list-head list-page-topbar">
      <div class="list-intro">
        <h2 class="list-page-title">{{ listPageHeadline }}</h2>
      </div>
      <button type="button" class="secondary btn-profile-edit" @click="goToAddForm">
        添加成员
      </button>
    </div>
    <div v-if="!loading" class="summary-strip">
      <div class="summary-strip-inner">
        <header class="summary-heading">
          <p class="person-profile-eyebrow summary-eyebrow">家庭概览</p>
          <p class="summary-lede">
            <span class="summary-lede-strong">{{ listSummary.memberCount }}</span>
            <span class="summary-lede-rest">位成员 · </span>
            <span
              class="summary-lede-strong summary-lede-accent"
              :class="{ 'summary-lede-zero': listSummary.abnormalItemsSum === 0 }"
              >{{ listSummary.abnormalItemsSum }}</span
            >
            <span class="summary-lede-rest"> 项异常合计</span>
          </p>
          <p class="summary-microcopy">
            {{ listSummary.membersWithAbnormal }} 人仍有待跟进 · 点击「跟进」只看仍有异常成员
          </p>
        </header>
        <div class="person-profile-stats summary-stats-grid">
          <div
            class="profile-stat-tile profile-stat-tile-data profile-stat-tile-age summary-tile-static"
            aria-hidden="true"
          >
            <span class="profile-stat-kicker">档案</span>
            <span class="profile-stat-value profile-stat-num">{{ listSummary.memberCount }}</span>
            <span class="profile-stat-caption">成员总数</span>
          </div>
          <div
            class="profile-stat-tile profile-stat-tile-data profile-stat-tile-vitals summary-tile-static"
            aria-hidden="true"
          >
            <span class="profile-stat-kicker">健康提醒</span>
            <span
              class="profile-stat-value profile-stat-num summary-num-accent"
              :class="{ 'summary-num-calm': listSummary.abnormalItemsSum === 0 }"
              >{{ listSummary.abnormalItemsSum }}</span
            >
            <span class="profile-stat-caption">当前异常（项）</span>
          </div>
          <button
            type="button"
            class="profile-stat-tile profile-stat-tile-link profile-stat-tile-reports summary-tile-follow"
            :class="{ 'summary-follow-pressed': abnormalOnlyFilter }"
            :aria-pressed="abnormalOnlyFilter"
            :aria-label="
              abnormalOnlyFilter
                ? '跟进筛选已开启，点击恢复显示全部成员'
                : '跟进：点击后列表仅显示仍有异常的成员'
            "
            @click="toggleFollowFilter"
          >
            <span class="profile-stat-kicker">跟进</span>
            <span
              class="profile-stat-value profile-stat-num summary-follow-count"
              :class="{ 'summary-follow-count-zero': listSummary.membersWithAbnormal === 0 }"
              >{{ listSummary.membersWithAbnormal }}</span
            >
            <span class="profile-stat-caption">{{
              abnormalOnlyFilter ? '筛选中 · 再点恢复全部' : '点击只看仍有异常'
            }}</span>
          </button>
        </div>
      </div>
    </div>
    <div v-if="pageErr" class="err">{{ pageErr }}</div>
    <div class="person-list-panel">
      <p v-if="loading" class="loading-text person-list-panel-loading">加载中…</p>
      <table v-else class="person-table">
      <thead>
        <tr>
          <th
            class="col-name th-hint"
            @mouseenter="(e) => tipEnter(e, tipAvatarNameCol)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
          >
            头像 · 姓名
          </th>
          <th>成员属性</th>
          <th>性别</th>
          <th>出生日期</th>
          <th
            class="th-hint"
            @mouseenter="(e) => tipEnter(e, tipVitalsCols)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
          >
            血型
          </th>
          <th
            class="th-hint"
            @mouseenter="(e) => tipEnter(e, tipVitalsCols)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
          >
            身高
          </th>
          <th
            class="th-hint"
            @mouseenter="(e) => tipEnter(e, tipVitalsCols)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
          >
            体重
          </th>
          <th
            class="col-abnorm th-hint"
            @mouseenter="(e) => tipEnter(e, tipAbnormalCol)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
          >
            当前异常
          </th>
          <th />
        </tr>
      </thead>
      <tbody>
        <tr v-if="persons.length > 0 && displayedPersons.length === 0">
          <td colspan="9" class="muted filter-empty-cell">
            当前筛选下没有仍有异常的成员。
          </td>
        </tr>
        <template v-for="p in displayedPersons" :key="p.id">
          <tr>
          <td class="cell-with-avatar">
            <img
              class="avatar-img th-hint"
              :src="resolveMemberAvatarSrc(p)"
              width="44"
              height="44"
              alt=""
              loading="lazy"
              decoding="async"
              @mouseenter="(e) => tipEnter(e, tipAvatarNameCol)"
              @mousemove="tipMove"
              @mouseleave="tipLeave"
            />
            <a
              href="#"
              class="table-link"
              @click.prevent="router.push(`/persons/${p.id}`)"
              >{{ p.name }}</a
            >
          </td>
          <td>{{ p.member_role?.trim() ? p.member_role : '—' }}</td>
          <td>{{ p.gender ?? '—' }}</td>
          <td>{{ p.birth_date ?? '—' }}</td>
          <td>{{ p.blood_type ?? '—' }}</td>
          <td>{{ fmtVitalNum(p.height_cm) }}</td>
          <td>{{ fmtVitalNum(p.weight_kg) }}</td>
          <td class="col-abnorm">
            <RouterLink
              class="abnorm-link"
              :class="
                (p.current_abnormal_count ?? 0) > 0 ? 'abnorm-positive' : 'abnorm-zero'
              "
              :to="`/persons/${p.id}/current-abnormals`"
              @mouseenter="(e) => tipEnter(e, tipAbnormalCol)"
              @mousemove="tipMove"
              @mouseleave="tipLeave"
            >
              {{ p.current_abnormal_count ?? 0 }} 项
            </RouterLink>
          </td>
          <td>
            <div class="cell-actions">
              <button
                type="button"
                class="secondary"
                @mouseenter="(e) => tipEnter(e, tipEnterHome)"
                @mousemove="tipMove"
                @mouseleave="tipLeave"
                @click="router.push(`/persons/${p.id}`)"
              >
                详情
              </button>
              <button type="button" class="danger" @click="remove(p.id)">删除</button>
            </div>
          </td>
        </tr>
        </template>
      </tbody>
    </table>
      <p v-if="!loading && persons.length === 0" class="muted person-list-panel-empty">
        暂无成员。请点击「添加成员」填写资料。
      </p>
    </div>
  </div>

  <Teleport to="body">
    <div
      v-if="showAddPanel"
      class="profile-edit-overlay"
      role="presentation"
      @click.self="closeAddPanel"
    >
      <div
        id="add-member"
        ref="addPanelEl"
        class="profile-edit-dialog card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-member-title"
        tabindex="-1"
      >
        <div class="profile-edit-head">
          <h3 id="add-member-title">添加新成员</h3>
          <button type="button" class="secondary" @click="closeAddPanel">关闭</button>
        </div>
        <p class="muted add-hint">
          仅需填写档案字段；血型、身高、体重请在录入<strong>体检报告</strong>时填写对应指标（列表中会按规则自动汇总）。
        </p>
        <div v-if="formErr" class="err">{{ formErr }}</div>
        <div class="row profile-edit-fields">
          <label
            >姓名 *
            <input v-model="form.name" placeholder="姓名"
          /></label>
          <label
            >成员属性
            <input v-model="form.member_role" placeholder="如：父亲、儿子、女儿"
          /></label>
          <label
            >性别（选填）
            <select v-model="form.gender">
              <option v-for="opt in genderOptions" :key="'g-' + (opt.value || 'unset')" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </label>
          <label
            >出生日期
            <input v-model="form.birth_date" type="date"
          /></label>
          <button type="button" :disabled="loading" @click="createPerson">保存新成员</button>
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

<style scoped>
.list-page-topbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}
.list-intro {
  min-width: 0;
}
.list-page-title {
  margin: 0 0 0.25rem;
  font-size: clamp(1.45rem, 3.2vw, 1.85rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.2;
  color: var(--text-primary);
}
.list-page-topbar .btn-profile-edit {
  flex-shrink: 0;
  align-self: center;
}
h3 {
  margin: 0 0 0.35rem;
  font-size: 1.15rem;
}
.th-hint {
  cursor: default;
  text-decoration: underline;
  text-decoration-style: dotted;
  text-decoration-color: rgba(148, 163, 184, 0.55);
  text-underline-offset: 3px;
}
.person-table thead .th-hint {
  text-decoration-thickness: 1px;
}
.person-list-panel {
  margin-top: 0.15rem;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(148, 163, 184, 0.16);
  background:
    linear-gradient(180deg, rgba(56, 189, 248, 0.045) 0%, transparent 42%),
    rgba(15, 23, 42, 0.48);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.055),
    0 10px 32px rgba(0, 0, 0, 0.18);
  overflow-x: auto;
  overflow-y: visible;
  -webkit-overflow-scrolling: touch;
}
.person-list-panel-loading {
  margin: 0;
  padding: 1.35rem 1.25rem;
}
.person-list-panel-empty {
  margin: 0;
  padding: 1.35rem 1.25rem 1.5rem;
}
.person-table {
  font-size: 1rem;
  width: 100%;
}
.person-list-panel .person-table thead {
  background: rgba(10, 16, 34, 0.92);
}
.person-list-panel .person-table thead th {
  border-bottom-color: rgba(56, 189, 248, 0.14);
}
.person-list-panel .person-table tbody tr:last-child td {
  border-bottom-color: transparent;
}
.person-table th {
  font-size: 0.9rem;
  letter-spacing: 0.03em;
  padding: 0.72rem 0.8rem;
}
.person-table td {
  padding: 0.78rem 0.85rem;
  vertical-align: middle;
}
.person-list-panel .person-table tbody tr:hover {
  background: rgba(56, 189, 248, 0.06);
}
.col-name {
  min-width: 11rem;
}
.cell-with-avatar {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.avatar-img {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
  background: rgba(148, 163, 184, 0.14);
  border: 1px solid rgba(148, 163, 184, 0.22);
}
.avatar-img.th-hint {
  cursor: default;
}
.col-abnorm {
  white-space: nowrap;
  width: 6.25rem;
}
.abnorm-link {
  font-weight: 650;
  font-size: inherit;
  cursor: pointer;
}
.abnorm-positive {
  color: #fb7185;
  border-bottom: 1px dashed rgba(251, 113, 133, 0.65);
  padding-bottom: 2px;
}
.abnorm-positive:hover {
  color: #fda4af;
  border-bottom-style: solid;
}
.abnorm-zero {
  color: #4ade80;
  font-weight: 600;
}
.abnorm-zero:hover {
  color: #86efac;
}
.table-link {
  font-weight: 650;
  font-size: inherit;
  border-bottom: 1px dashed rgba(56, 189, 248, 0.45);
  padding-bottom: 1px;
}
.table-link:hover {
  border-bottom-style: solid;
}
.summary-strip {
  --summary-pad: 1.15rem 1.25rem;
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  justify-content: space-between;
  gap: 1.15rem;
  margin-bottom: 1.15rem;
  padding: var(--summary-pad);
  border-radius: calc(var(--radius-lg) + 2px);
  border: 1px solid rgba(148, 163, 184, 0.18);
  background:
    linear-gradient(
      145deg,
      rgba(56, 189, 248, 0.09) 0%,
      rgba(129, 140, 248, 0.06) 42%,
      rgba(15, 23, 42, 0.35) 100%
    ),
    var(--surface-inner);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.06) inset,
    0 14px 36px rgba(0, 0, 0, 0.22);
}
.summary-strip-inner {
  flex: 1 1 14rem;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.summary-eyebrow {
  margin: 0 0 0.35rem;
}

.summary-heading {
  margin: 0;
}
.summary-lede {
  margin: 0 0 0.45rem;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.15rem 0.55rem;
  font-size: 0.9375rem;
  font-weight: 500;
  line-height: 1.45;
  letter-spacing: 0.02em;
  color: var(--text-secondary);
}
.summary-lede-strong {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}
.summary-lede-accent {
  background: linear-gradient(115deg, #f472b6 0%, #fb923c 52%, #fbbf24 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.summary-lede-zero {
  background: none;
  -webkit-background-clip: unset;
  background-clip: unset;
  color: #6ee7b7;
}
.summary-lede-rest {
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}
.summary-microcopy {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  color: rgba(148, 163, 184, 0.82);
}
.summary-stats-grid {
  grid-template-columns: repeat(3, minmax(min(100%, 5.75rem), 1fr));
  gap: 0.75rem 0.82rem;
}

.summary-tile-static {
  justify-content: center;
}

.summary-stats-grid .profile-stat-caption {
  text-align: left;
  width: 100%;
}

button.summary-tile-follow {
  appearance: none;
  margin: 0;
  width: 100%;
  cursor: pointer;
  text-align: left;
  font: inherit;
  color: inherit;
}

button.summary-tile-follow:focus-visible {
  outline: none;
}

.summary-stats-grid .summary-num-accent:not(.summary-num-calm) {
  background: linear-gradient(108deg, #fca5a5 0%, #fb923c 50%, #fcd34d 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.summary-stats-grid .summary-num-calm {
  background: linear-gradient(125deg, #34d399 0%, #22d3ee 55%, #7dd3fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.summary-follow-count {
  background: linear-gradient(108deg, #fda4af 0%, #f87171 48%, #fb923c 100%) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
  color: transparent !important;
  filter: drop-shadow(0 0 16px rgba(248, 113, 113, 0.35));
}

.summary-follow-count.summary-follow-count-zero {
  background: none !important;
  -webkit-background-clip: unset !important;
  background-clip: unset !important;
  color: rgba(148, 163, 184, 0.95) !important;
  filter: none;
}

.summary-tile-follow.summary-follow-pressed {
  border-color: rgba(125, 211, 252, 0.42) !important;
  border-left-color: rgba(192, 181, 253, 0.95) !important;
  background:
    linear-gradient(
      165deg,
      rgba(99, 102, 241, 0.16) 0%,
      rgba(30, 41, 72, 0.45) 100%
    ),
    rgba(15, 23, 42, 0.35) !important;
  box-shadow:
    0 1px 0 rgba(129, 140, 248, 0.08) inset,
    0 0 0 1px rgba(129, 140, 248, 0.22),
    0 10px 28px rgba(0, 0, 0, 0.22) !important;
}

.summary-tile-follow.summary-follow-pressed:hover {
  border-left-color: rgba(221, 214, 254, 1) !important;
}
.filter-empty-cell {
  text-align: center;
  padding: 1.25rem !important;
}
@media (max-width: 720px) {
  .summary-strip {
    flex-direction: column;
    align-items: stretch;
  }
  .summary-stats-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 540px) {
  .list-page-topbar {
    flex-direction: column;
    align-items: stretch;
  }
  .list-page-topbar .btn-profile-edit {
    width: 100%;
    align-self: stretch;
  }
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
  outline: none;
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
.profile-edit-fields {
  margin-top: 0.35rem;
}
@media (max-width: 540px) {
  .profile-edit-head {
    flex-direction: column;
    align-items: stretch;
  }
  .profile-edit-head .secondary {
    width: 100%;
  }
}
.add-hint {
  margin: 0 0 0.85rem;
}
.member-list-tooltip {
  position: fixed;
  z-index: 10050;
  max-width: min(22rem, calc(100vw - 1.5rem));
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
</style>
