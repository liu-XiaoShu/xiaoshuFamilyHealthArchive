<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { http, apiError } from '../api/http'
import type { Indicator, Organ } from '../api/types'
import NavBackLink from '../components/NavBackLink.vue'
import CollapseTextToggle from '../components/CollapseTextToggle.vue'
import MessageDialog from '../components/MessageDialog.vue'

const indicators = ref<Indicator[]>([])
const organs = ref<Organ[]>([])
const err = ref('')
const loading = ref(false)

const editingId = ref<number | null>(null)

const form = ref({
  name: '',
  category: 'lab',
  parent_id: '' as string,
  is_narrative: false,
  unit: '',
  ref_range_hint: '',
  organ_ids: [] as number[],
})

const organForm = ref({ name: '' })

/** 在上级下拉之外快速新建「顶层分组」并选为本条上级 */
const newParentGroupName = ref('')

/** 筛选紧邻下方的「关联器官」列表，与勾选区联动 */
const organQuery = ref('')

const tableSearch = ref('')

/** 从表格点「编辑」时滚到表单区并聚焦名称框，避免用户在页底找不到编辑区 */
const editFormScrollTarget = ref<HTMLElement | null>(null)
const indicatorNameInput = ref<HTMLInputElement | null>(null)

/** 操作失败等非页面级错误（如删除被引用）：弹窗确保用户能看见 */
const messageDlgOpen = ref(false)
const messageDlgTitle = ref('提示')
const messageDlgBody = ref('')

function openMessageDlg(title: string, message: string) {
  messageDlgTitle.value = title
  messageDlgBody.value = message
  messageDlgOpen.value = true
}

function closeMessageDlg() {
  messageDlgOpen.value = false
}

/** 关联器官勾选区：条目较多时折叠，避免占满版面 */
const organsPickerExpanded = ref(false)
const ORGANS_COLLAPSE_THRESHOLD = 10

const filteredOrgansForPicker = computed(() => {
  const s = organQuery.value.trim().toLowerCase()
  if (!s) return organs.value
  return organs.value.filter((o) => o.name.toLowerCase().includes(s))
})

const showOrganCollapseToggle = computed(
  () => filteredOrgansForPicker.value.length > ORGANS_COLLAPSE_THRESHOLD,
)
const organsFieldCollapsed = computed(
  () => showOrganCollapseToggle.value && !organsPickerExpanded.value,
)

const filteredIndicators = computed(() => {
  const s = tableSearch.value.trim().toLowerCase()
  if (!s) return indicators.value
  return indicators.value.filter((i) => i.name.toLowerCase().includes(s))
})

/** 已有指标表格：超过条数时折叠，避免列表过长 */
const INDICATORS_TABLE_COLLAPSE_THRESHOLD = 15
const indicatorsTableExpanded = ref(false)

const showIndicatorsTableCollapseToggle = computed(
  () => filteredIndicators.value.length > INDICATORS_TABLE_COLLAPSE_THRESHOLD,
)

const indicatorsTableDisplayRows = computed(() => {
  const list = filteredIndicators.value
  if (!showIndicatorsTableCollapseToggle.value || indicatorsTableExpanded.value) return list
  return list.slice(0, INDICATORS_TABLE_COLLAPSE_THRESHOLD)
})

const indicatorsTableCollapseMeta = computed(() => {
  const n = filteredIndicators.value.length
  if (showIndicatorsTableCollapseToggle.value && !indicatorsTableExpanded.value) {
    return `展示 ${INDICATORS_TABLE_COLLAPSE_THRESHOLD} / ${n}`
  }
  return `${n} 条`
})

watch(showIndicatorsTableCollapseToggle, (show) => {
  if (!show) indicatorsTableExpanded.value = false
})

const idToName = computed(() => {
  const m = new Map<number, string>()
  for (const i of indicators.value) m.set(i.id, i.name)
  return m
})

function parentLabel(ind: Indicator): string {
  if (!ind.parent_id) return '—'
  return idToName.value.get(ind.parent_id) ?? `#${ind.parent_id}`
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const [{ data: ind }, { data: org }] = await Promise.all([
      http.get<Indicator[]>('/api/indicators'),
      http.get<Organ[]>('/api/indicators/organs'),
    ])
    indicators.value = ind
    organs.value = org
  } catch (e) {
    err.value = apiError(e)
  } finally {
    loading.value = false
  }
}

function toggleOrgan(id: number) {
  const i = form.value.organ_ids.indexOf(id)
  if (i >= 0) form.value.organ_ids.splice(i, 1)
  else form.value.organ_ids.push(id)
}

function resetForm() {
  editingId.value = null
  organsPickerExpanded.value = false
  organQuery.value = ''
  newParentGroupName.value = ''
  form.value = {
    name: '',
    category: 'lab',
    parent_id: '',
    is_narrative: false,
    unit: '',
    ref_range_hint: '',
    organ_ids: [],
  }
}

function startEdit(ind: Indicator) {
  editingId.value = ind.id
  organsPickerExpanded.value = false
  organQuery.value = ''
  newParentGroupName.value = ''
  form.value = {
    name: ind.name,
    category: ind.category,
    parent_id: ind.parent_id != null ? String(ind.parent_id) : '',
    is_narrative: ind.is_narrative,
    unit: ind.unit ?? '',
    ref_range_hint: ind.ref_range_hint ?? '',
    organ_ids: [...ind.organ_ids],
  }
  const smoothScroll =
    typeof matchMedia !== 'undefined' && !matchMedia('(prefers-reduced-motion: reduce)').matches
  void nextTick(() => {
    editFormScrollTarget.value?.scrollIntoView({
      behavior: smoothScroll ? 'smooth' : 'auto',
      block: 'start',
    })
    indicatorNameInput.value?.focus({ preventScroll: true })
  })
}

async function addParentGroup() {
  const name = newParentGroupName.value.trim()
  if (!name) {
    openMessageDlg('无法新建', '请先填写新分组名称')
    return
  }
  const cat = form.value.category
  const dupRoot = indicators.value.some(
    (i) => i.category === cat && i.parent_id == null && i.name.trim() === name,
  )
  if (dupRoot) {
    openMessageDlg(
      '分组已存在',
      `在当前大类下已有同名顶层分组「${name}」，请直接在上拉列表中选择，无需重复创建。`,
    )
    return
  }
  err.value = ''
  try {
    const { data } = await http.post<Indicator>('/api/indicators', {
      name,
      category: cat,
      parent_id: null,
      is_narrative: false,
      unit: null,
      ref_range_hint: null,
      organ_ids: [],
    })
    newParentGroupName.value = ''
    await load()
    form.value.parent_id = String(data.id)
  } catch (e) {
    openMessageDlg('新建分组失败', apiError(e))
  }
}

async function save() {
  if (!form.value.name.trim()) {
    openMessageDlg('无法保存', '请填写名称')
    return
  }
  err.value = ''
  const body = {
    name: form.value.name.trim(),
    category: form.value.category,
    parent_id: form.value.parent_id === '' ? null : Number(form.value.parent_id),
    is_narrative: form.value.is_narrative,
    unit: form.value.unit || null,
    ref_range_hint: form.value.ref_range_hint || null,
    organ_ids: form.value.organ_ids,
  }
  try {
    if (editingId.value === null) {
      await http.post('/api/indicators', body)
    } else {
      await http.patch(`/api/indicators/${editingId.value}`, body)
    }
    resetForm()
    await load()
  } catch (e) {
    openMessageDlg('保存失败', apiError(e))
  }
}

async function remove(id: number) {
  if (!confirm('确定删除该指标？若有下级或已有记录则会失败。')) return
  try {
    await http.delete(`/api/indicators/${id}`)
    if (editingId.value === id) resetForm()
    await load()
  } catch (e) {
    openMessageDlg('无法删除指标', apiError(e))
  }
}

async function addOrgan() {
  const n = organForm.value.name.trim()
  if (!n) return
  err.value = ''
  try {
    await http.post('/api/indicators/organs', { name: n })
    organForm.value.name = ''
    await load()
  } catch (e) {
    openMessageDlg('添加器官失败', apiError(e))
  }
}

const catUi: Record<string, string> = {
  physical: '体格',
  lab: '检验',
  imaging: '影像',
}

watch(organQuery, (q) => {
  if (q.trim() && filteredOrgansForPicker.value.length > ORGANS_COLLAPSE_THRESHOLD) {
    organsPickerExpanded.value = true
  }
})

const tipOrganSearch =
  '系统已按标准人体解剖与检验习惯内置一批器官名称，并允许您补充库内没有的条目。在此输入关键字可实时筛选下方列表，便于快速勾选关联；清空则显示全部。'
const tipCustomOrgan =
  '若目录中确实没有所需名称，可在此填写后「添加至库」；成功后刷新列表，即可在下方勾选。若与已有器官同名，接口会提示失败。'
const tipIndicatorName =
  '指标在本系统中的正式名称：指标表、录入报告时的下拉框与报告明细中均显示此名称。若为化验/检查细项，请避免与上级分组同名。'
const tipCategory =
  '体格：身高体重等体格检查；检验：血/尿等实验室项目；影像：超声、放射、内镜等影像学或功能检查。大类影响表单归类与录入习惯。'
const tipParent =
  '选「无」表示本条为顶层分组或独立指标；若为细项请先选所属分组。若下拉暂无合适项，可在「新建并入列」卡片中填写名称并点按钮，会在当前大类下并入一条顶层分组并自动选为本条上级。'
const tipUnit =
  '数值类指标的建议单位（如 mmol/L、kU/L、mmHg），录入体检报告时将作为占位提示；叙述类可留空。'
const tipRefHint =
  '与报告单上「参考范围」类的文字描述一致时使用；不参与自动判断是否异常，仅作提示备忘。'
const tipLinkedOrgans =
  '可多选：该指标在临床或报告书写上常归哪些解剖部位或脏器。将影响「按器官」浏览顺序；可先在上框搜索关键字再勾选。已选项目在筛选为空时仍可保留勾选。'
const tipNarrative =
  '勾选后本条为叙述类指标。适用于体检报告中的所见、印象、结论及小结等长文本，不参与带单位的数值录入；与普通数值/分项区分。录入与展示偏重段落描述，单位常可省略。'

type HoverTipState = { text: string; x: number; y: number }

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
  hoverTip.value = { ...cur, x: e.clientX + 14, y: e.clientY + 14 }
}

function tipLeave() {
  hoverTip.value = null
}

const organsPickerMetaLabel = computed(() => {
  const total = organs.value.length
  const shown = filteredOrgansForPicker.value.length
  if (organQuery.value.trim()) return `展示 ${shown} / ${total}`
  return `${total} 项`
})

function organScopeTag(scope: string): string {
  if (scope === 'male') return '男'
  if (scope === 'female') return '女'
  return ''
}

onMounted(load)
</script>

<template>
  <div class="card indicators-page">
    <p class="detail-back-row">
      <NavBackLink to="/" label="返回家庭成员页" variant="home" />
    </p>

    <section class="person-profile-hero indicators-hero" aria-labelledby="indicators-hero-eyebrow">
      <p id="indicators-hero-eyebrow" class="person-profile-eyebrow">指标编辑</p>
      <div class="person-profile-top indicators-hero-top">
        <div class="person-profile-title-block">
          <h2 class="person-profile-name">检查项目与器官</h2>
          <p class="muted ind-hero-hint">
            维护器官、检查分组（上级）与细项（下级）；录入报告时请选<strong>叶子节点</strong>。
            器官库已按<strong>标准人体解剖/检验习惯</strong>预置并区分性别适用范围；条目含「男」「女」标签的仅在该性别成员的「按器官」视图中参与排序。
          </p>
        </div>
      </div>
    </section>

    <div v-if="err" class="err">{{ err }}</div>

    <div class="report-section-head">
      <h3 class="report-section-title">新建与编辑</h3>
      <hr class="report-section-rule" aria-hidden="true" />
    </div>

    <div class="ind-form-shell">
      <p ref="editFormScrollTarget" class="ind-block-kicker ind-block-kicker-spaced ind-edit-scroll-target">
        {{ editingId === null ? '新建指标' : `编辑指标 #${editingId}` }}
      </p>
      <div class="row ind-edit-row ind-basic-row">
        <label class="ind-field-label ind-field-grow ind-name-field">
          <span
            class="ind-field-caption ind-caption-tier"
            @mouseenter="(e) => tipEnter(e, tipIndicatorName)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >名称 *</span>
          <input
            ref="indicatorNameInput"
            v-model="form.name"
            class="ind-form-control"
            type="text"
            placeholder="指标正式名称"
          />
        </label>
        <label class="ind-field-label ind-category-field">
          <span
            class="ind-field-caption ind-caption-tier"
            @mouseenter="(e) => tipEnter(e, tipCategory)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >大类 *</span>
          <select v-model="form.category" class="ind-form-control">
            <option value="physical">体格</option>
            <option value="lab">检验</option>
            <option value="imaging">影像</option>
          </select>
        </label>
        <div
          class="ind-field-label ind-narrative-field ind-narrative-in-row"
          @mouseover="(e) => tipEnter(e, tipNarrative)"
          @mousemove="tipMove"
          @mouseleave="tipLeave"
        >
          <span class="ind-field-caption ind-caption-tier">叙述类</span>
          <label class="ind-narrative-toggle">
            <input v-model="form.is_narrative" type="checkbox" class="ind-narrative-input" />
            <span class="ind-narrative-track" aria-hidden="true">
              <span class="ind-narrative-knob" />
            </span>
          </label>
        </div>
      </div>

      <div class="ind-parent-field">
        <div class="ind-parent-caption-block">
          <span
            class="ind-field-caption ind-caption-tier"
            @mouseenter="(e) => tipEnter(e, tipParent)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >上级分组</span>
          <span class="ind-parent-caption-note muted">可选；化验/影像等细项一般挂在分组下。</span>
        </div>
        <div class="ind-parent-panel">
          <div class="ind-parent-panel-body">
          <label class="ind-parent-select-wrap">
            <span class="ind-sr-only">选择上级分组</span>
            <select v-model="form.parent_id" class="ind-form-control">
              <option value="">无 — 本条为顶层分组或为独立指标</option>
              <option
                v-for="i in indicators.filter((x) => x.id !== editingId)"
                :key="i.id"
                :value="String(i.id)"
              >
                {{ i.name }}
              </option>
            </select>
          </label>
          <div class="ind-parent-create-card">
            <p class="ind-parent-create-heading">没找到合适的分组？</p>
            <p class="ind-parent-create-desc muted">
              按左侧「大类」新建一个<strong>顶层</strong>分组，并可立即设为本条的上级。
            </p>
            <div class="ind-parent-create-actions">
              <input
                v-model="newParentGroupName"
                class="ind-form-control"
                type="text"
                placeholder="新顶层分组名称"
                autocomplete="off"
                @keydown.enter.prevent="addParentGroup"
              />
              <button type="button" class="secondary ind-form-btn ind-parent-create-btn" @click="addParentGroup">
                新建并入列并选为上级
              </button>
            </div>
          </div>
          </div>
        </div>
      </div>

      <div class="row ind-edit-row">
        <label class="ind-field-label">
          <span
            class="ind-field-caption"
            @mouseenter="(e) => tipEnter(e, tipUnit)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >单位</span>
          <input v-model="form.unit" class="ind-form-control" type="text" placeholder="如 mmol/L、kU/L" />
        </label>
        <label class="ind-field-label ind-field-grow">
          <span
            class="ind-field-caption"
            @mouseenter="(e) => tipEnter(e, tipRefHint)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >参考范围说明</span>
          <input v-model="form.ref_range_hint" class="ind-form-control" type="text" placeholder="对照报告单备注" />
        </label>
      </div>

      <p class="ind-block-kicker ind-block-kicker-spaced">器官与关联</p>
      <div class="row ind-edit-row">
        <label class="ind-field-label ind-field-grow">
          <span
            class="ind-field-caption ind-caption-tier"
            @mouseenter="(e) => tipEnter(e, tipOrganSearch)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >搜索关联器官</span>
          <input
            v-model="organQuery"
            type="search"
            class="ind-form-control"
            placeholder="关键字筛选下方列表，便于勾选"
            autocomplete="off"
          />
        </label>
        <label class="ind-field-label ind-custom-organ-field">
          <span
            class="ind-field-caption ind-caption-tier"
            @mouseenter="(e) => tipEnter(e, tipCustomOrgan)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >自定义器官（可选）</span>
          <div class="ind-inline-input-btn">
            <input v-model="organForm.name" class="ind-form-control" type="text" placeholder="库中尚无的名称" />
            <button type="button" class="secondary ind-form-btn" @click="addOrgan">添加至库</button>
          </div>
        </label>
      </div>

      <fieldset class="org-field" :class="{ 'org-field--collapsed': organsFieldCollapsed }">
        <legend>
          <span
            class="ind-field-caption ind-legend-caption ind-caption-tier"
            @mouseenter="(e) => tipEnter(e, tipLinkedOrgans)"
            @mousemove="tipMove"
            @mouseleave="tipLeave"
            >关联器官</span>
        </legend>
        <div class="org-field-inner">
          <div class="org-chips" aria-label="勾选关联器官">
            <template v-if="filteredOrgansForPicker.length > 0">
              <label v-for="o in filteredOrgansForPicker" :key="o.id" class="chk">
                <input
                  type="checkbox"
                  :checked="form.organ_ids.includes(o.id)"
                  @change="toggleOrgan(o.id)"
                />
                {{ o.name
                }}<span v-if="organScopeTag(o.gender_scope)" class="organ-scope">{{
                  organScopeTag(o.gender_scope)
                }}</span>
              </label>
            </template>
            <p v-else-if="organQuery.trim()" class="ind-organ-filter-empty muted">
              无匹配项，请调整关键字或清空搜索。
            </p>
            <p v-else-if="organs.length === 0" class="ind-organ-filter-empty muted">
              器官库为空，可在下方「自定义器官」添加。
            </p>
          </div>
          <CollapseTextToggle
            v-if="showOrganCollapseToggle"
            variant="inline"
            :expanded="organsPickerExpanded"
            label-collapsed="展开全部"
            label-expanded="收起"
            :meta="organsPickerMetaLabel"
            @toggle="organsPickerExpanded = !organsPickerExpanded"
          />
        </div>
      </fieldset>

      <div class="ind-form-actions-wrap ind-form-actions-in-shell">
        <p class="cell-actions ind-form-actions">
          <button type="button" class="ind-form-btn-primary" @click="save">
            {{ editingId === null ? '创建' : '保存修改' }}
          </button>
          <button v-if="editingId !== null" type="button" class="secondary ind-form-btn" @click="resetForm">
            取消编辑
          </button>
        </p>
      </div>
    </div>

    <div class="report-section-head ind-table-section-head">
      <h3 class="report-section-title">已有指标</h3>
      <hr class="report-section-rule" aria-hidden="true" />
    </div>

    <div class="ind-table-toolbar">
      <label class="ind-search-field">
        <span class="ind-search-kicker">筛选名称</span>
        <input
          v-model="tableSearch"
          class="ind-search-input"
          type="search"
          placeholder="输入关键字，本地过滤下方表格…"
          autocomplete="off"
        />
      </label>
    </div>
    <p v-if="loading" class="loading-text ind-loading">加载中…</p>
    <div v-else class="indicators-panel">
      <div class="ind-table-panel-inner">
        <table class="obs-detail-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>上级</th>
              <th>名称</th>
              <th>大类</th>
              <th>类型</th>
              <th>器官</th>
              <th class="ind-th-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="i in indicatorsTableDisplayRows" :key="i.id">
              <td>{{ i.id }}</td>
              <td>{{ parentLabel(i) }}</td>
              <td>{{ i.name }}</td>
              <td>{{ catUi[i.category] ?? i.category }}</td>
              <td>{{ i.is_narrative ? '叙述' : '数值/文本' }}</td>
              <td class="ind-organ-cell">
                {{
                  i.organ_ids
                    .map((oid) => organs.find((x) => x.id === oid)?.name ?? oid)
                    .join('、') || '—'
                }}
              </td>
              <td class="ind-actions-cell">
                <div class="cell-actions ind-row-actions">
                  <button type="button" class="secondary" @click.stop="startEdit(i)">编辑</button>
                  <button type="button" class="danger" @click.stop="remove(i.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <CollapseTextToggle
          v-if="showIndicatorsTableCollapseToggle"
          variant="inline"
          :expanded="indicatorsTableExpanded"
          label-collapsed="展开全部"
          label-expanded="收起"
          :meta="indicatorsTableCollapseMeta"
          class="ind-table-collapse-toggle"
          @toggle="indicatorsTableExpanded = !indicatorsTableExpanded"
        />
      </div>
      <p
        v-if="indicators.length > 0 && filteredIndicators.length === 0"
        class="muted ind-panel-empty"
      >
        无匹配项，请调整筛选关键字。
      </p>
      <p v-if="indicators.length === 0" class="muted ind-panel-empty">暂无指标，请在上方新建。</p>
    </div>
    </div>

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

    <MessageDialog
    :open="messageDlgOpen"
    :title="messageDlgTitle"
    :message="messageDlgBody"
    @close="closeMessageDlg"
  />
</template>

<style scoped>
.detail-back-row {
  margin: 0 0 0.85rem;
}

.indicators-page {
  margin-bottom: 1.35rem;
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

.indicators-hero {
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

.indicators-hero-top {
  margin-bottom: 0;
}

.person-profile-title-block {
  flex: 1;
  min-width: min(100%, 12rem);
}

.person-profile-name {
  margin: 0 0 0.65rem;
  font-size: clamp(1.22rem, 2.85vw, 1.62rem);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.15;
  color: var(--text-primary);
}

.ind-hero-hint {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.55;
  max-width: 48rem;
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
  margin: 0.72rem 0 0.95rem;
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

.ind-table-section-head {
  margin-top: 1.25rem;
}

.ind-table-section-head .report-section-rule {
  margin-bottom: 0.85rem;
}

.ind-block-kicker {
  margin: 0 0 0.55rem;
  padding: 0.18rem 0 0.12rem 0.65rem;
  border-left: 3px solid rgba(56, 189, 248, 0.65);
  font-size: 0.9375rem;
  font-weight: 700;
  letter-spacing: 0.025em;
  line-height: 1.42;
  color: #cbd5e1;
}

.ind-block-kicker-spaced {
  margin-top: 1.15rem;
}

/* 对齐 App 顶部 sticky，避免滚到表单时被顶栏压住 */
.ind-edit-scroll-target {
  scroll-margin-top: 5.5rem;
}

.ind-form-shell {
  margin: 0 0 1.05rem;
  padding: 0.75rem 1rem 0.95rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(56, 189, 248, 0.14);
  background:
    linear-gradient(165deg, rgba(15, 23, 42, 0.62) 0%, rgba(30, 41, 72, 0.34) 100%),
    rgba(12, 18, 34, 0.38);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.045),
    0 6px 24px rgba(0, 0, 0, 0.12);
}

.ind-parent-field {
  margin: 0 0 0.95rem;
}

.ind-parent-caption-block {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem 0.75rem;
  margin-bottom: 0.45rem;
}

.ind-parent-caption-note {
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: none;
  text-decoration: none;
  color: #94a3b8;
}

.ind-form-shell .ind-edit-row {
  margin-bottom: 0.9rem;
  align-items: flex-end;
}

.ind-form-shell .ind-field-label {
  display: flex;
  flex-direction: column;
  gap: 0.36rem;
  flex: 1 1 10rem;
  min-width: 8.75rem;
  margin: 0;
  font-size: inherit;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: none;
  color: var(--text-muted);
}

.ind-field-grow {
  flex: 2 1 14rem;
  min-width: min(100%, 12rem);
}

.ind-sr-only {
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

.ind-basic-row.ind-edit-row {
  align-items: flex-end;
}

.ind-name-field {
  flex: 2 1 16rem;
  min-width: min(100%, 11rem);
}

.ind-category-field {
  flex: 0 1 9rem;
  min-width: 6.75rem;
}

.ind-narrative-in-row {
  align-self: flex-end;
}

.ind-parent-panel {
  margin: 0;
  padding: 0.75rem 1rem 0.88rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(6, 12, 24, 0.42);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.ind-parent-panel-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ind-parent-select-wrap {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.ind-parent-create-card {
  padding: 0.62rem 0.75rem;
  border-radius: 10px;
  border: 1px dashed rgba(56, 189, 248, 0.28);
  background: rgba(15, 23, 42, 0.45);
}

.ind-parent-create-heading {
  margin: 0 0 0.35rem;
  font-size: 0.8125rem;
  font-weight: 700;
  color: #e2e8f0;
}

.ind-parent-create-desc {
  margin: 0 0 0.62rem;
  font-size: 0.765rem;
  line-height: 1.52;
}

.ind-parent-create-desc strong {
  color: #93c5fd;
  font-weight: 650;
}

.ind-parent-create-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: stretch;
}

.ind-parent-create-actions .ind-form-control {
  flex: 1 1 12rem;
  min-width: min(100%, 9rem);
}

.ind-parent-create-btn {
  flex: 0 1 auto;
  min-width: fit-content;
}

@media (min-width: 720px) {
  .ind-parent-panel-body {
    flex-direction: row;
    align-items: stretch;
    gap: 1rem;
  }

  .ind-parent-select-wrap {
    flex: 1 1 40%;
  }

  .ind-parent-create-card {
    flex: 1 1 58%;
  }
}

.ind-custom-organ-field {
  flex: 1.35 1 16rem;
  min-width: min(100%, 14rem);
}

/* 与成员列表表头 .th-hint 一致：默认指针 + 灰点下划线，不用 help 问号光标 */
.ind-field-caption {
  display: inline-block;
  width: fit-content;
  max-width: 100%;
  font-size: var(--font-form-label);
  font-weight: 650;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.97);
  cursor: default;
  text-decoration: underline;
  text-decoration-style: dotted;
  text-decoration-color: rgba(148, 163, 184, 0.55);
  text-underline-offset: 3px;
  text-decoration-thickness: 1px;
}

.ind-field-caption.ind-legend-caption:not(.ind-caption-tier) {
  font-size: 0.72rem;
  letter-spacing: 0.09em;
}

.ind-form-shell .ind-field-caption.ind-caption-tier {
  font-size: clamp(0.8725rem, 0.8rem + 0.35vw, 0.95rem);
  letter-spacing: 0.08em;
}

.ind-form-shell .ind-form-control {
  width: 100%;
  min-height: 2.35rem;
  box-sizing: border-box;
}

.ind-inline-input-btn {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  align-items: stretch;
}

.ind-inline-input-btn .ind-form-control {
  flex: 1;
  min-width: 9.5rem;
}

.ind-inline-input-btn .ind-form-btn {
  flex-shrink: 0;
}

.ind-form-shell .row.ind-edit-row .ind-form-btn,
.ind-form-btn-primary {
  min-height: 2.35rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.ind-form-shell .ind-edit-row .ind-form-btn {
  padding: 0.45rem 0.92rem;
  font-size: 0.8rem;
}

.ind-form-shell .ind-form-btn-primary {
  padding: 0.48rem 1.05rem;
  font-size: 0.86rem;
}

.ind-organ-filter-empty {
  margin: 0;
  padding: 0.25rem 0 0.1rem;
  font-size: 0.8125rem;
}

.ind-form-actions-in-shell.ind-form-actions-wrap {
  margin-top: 1rem;
  padding-bottom: 0;
  border-bottom: none;
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

.ind-form-shell fieldset.org-field legend {
  padding-left: 0;
  padding-right: 0.35rem;
}

/* 叙述类：标签在上；选中态沿用全站 cyan / indigo accent，控件宽度随开关收紧 */

.ind-field-label.ind-narrative-field {
  flex: 0 0 auto;
  width: fit-content;
  max-width: 100%;
  min-width: 0;
}

.ind-field-label.ind-narrative-field > .ind-field-caption {
  margin-bottom: 0.02rem;
}

.ind-narrative-field .ind-narrative-toggle {
  position: relative;
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: fit-content;
  box-sizing: border-box;
  min-height: 2.35rem;
  margin: 0;
  padding: 0.32rem 0.45rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  background: var(--surface-2);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  font-size: inherit;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: none;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.ind-narrative-field .ind-narrative-toggle:hover {
  border-color: rgba(56, 189, 248, 0.38);
  background: rgba(15, 23, 42, 0.55);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 0 0 1px rgba(56, 189, 248, 0.08);
}

.ind-narrative-field .ind-narrative-toggle:has(.ind-narrative-input:checked) {
  border-color: rgba(56, 189, 248, 0.52);
  background:
    linear-gradient(
      165deg,
      rgba(14, 165, 233, 0.16) 0%,
      rgba(99, 102, 241, 0.12) 100%
    ),
    rgba(15, 23, 42, 0.72);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 0 0 1px rgba(56, 189, 248, 0.12),
    0 2px 14px rgba(14, 165, 233, 0.12);
}

.ind-narrative-input {
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

.ind-narrative-input:focus-visible + .ind-narrative-track {
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.24);
}

.ind-narrative-input:checked + .ind-narrative-track {
  background: linear-gradient(145deg, rgba(14, 165, 233, 0.85) 0%, rgba(99, 102, 241, 0.78) 100%);
  border-color: rgba(125, 211, 252, 0.45);
}

.ind-narrative-input:checked + .ind-narrative-track .ind-narrative-knob {
  transform: translateX(1.15rem);
  background: #f0f9ff;
  box-shadow: 0 1px 6px rgba(14, 165, 233, 0.35);
}

.ind-narrative-track {
  position: relative;
  display: inline-block;
  width: 2.65rem;
  height: 1.5rem;
  border-radius: 999px;
  flex-shrink: 0;
  background: rgba(51, 65, 85, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.32);
  transition:
    background 0.22s ease,
    border-color 0.22s ease;
}

.ind-narrative-knob {
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

@media (prefers-reduced-motion: reduce) {
  .ind-narrative-knob {
    transition: none;
  }
}

.ind-form-actions-wrap {
  margin-top: 0.85rem;
  margin-bottom: 0;
  padding-bottom: 1.35rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.ind-form-actions {
  margin: 0;
}

.org-field {
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  margin: 0.55rem 0 0.25rem;
}

.org-field-inner {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.org-chips {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.42rem 0.92rem;
  position: relative;
}

.org-field--collapsed .org-chips {
  max-height: 5.75rem;
  overflow: hidden;
}

.org-field--collapsed .org-chips::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1.9rem;
  background: linear-gradient(to bottom, transparent, rgba(15, 23, 42, 0.93));
  pointer-events: none;
}

.chk {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.organ-scope {
  margin-left: 0.15rem;
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 700;
  opacity: 0.85;
}

.ind-table-toolbar {
  margin: 0 0 0.85rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(56, 189, 248, 0.14);
  background:
    linear-gradient(165deg, rgba(15, 23, 42, 0.55) 0%, rgba(30, 41, 72, 0.28) 100%),
    rgba(12, 18, 34, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.ind-search-field {
  display: flex;
  flex-direction: column;
  gap: 0.42rem;
  margin: 0;
}

@media (min-width: 520px) {
  .ind-search-field {
    flex-direction: row;
    align-items: center;
    gap: 0.75rem 1rem;
  }

  .ind-search-kicker {
    flex-shrink: 0;
    min-width: 4.75rem;
  }

  .ind-search-input {
    flex: 1;
    min-width: 0;
    max-width: 28rem;
  }
}

.ind-search-kicker {
  font-size: var(--font-form-label);
  font-weight: 650;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.95);
}

.ind-search-input {
  width: 100%;
}

.ind-actions-cell {
  white-space: nowrap;
  vertical-align: middle;
  text-align: center;
}

.ind-th-actions {
  text-align: center;
  white-space: nowrap;
}

.ind-row-actions {
  justify-content: center;
}

.indicators-panel .ind-row-actions button {
  font-size: 0.74rem;
  padding: 0.32rem 0.58rem;
}

.ind-loading {
  margin: 0.35rem 0 0.85rem;
}

.indicators-panel {
  margin-top: 0;
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

.ind-table-panel-inner {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.08rem;
  min-width: min-content;
}

.ind-table-collapse-toggle {
  align-self: center;
  margin: 0.15rem 0.85rem 0.55rem;
  flex-shrink: 0;
}

.indicators-panel .obs-detail-table {
  font-size: inherit;
}

.indicators-panel .obs-detail-table thead {
  background: rgba(10, 16, 34, 0.92);
}

.indicators-panel .obs-detail-table thead th {
  font-size: 0.92rem;
  border-bottom-color: rgba(56, 189, 248, 0.14);
}

.indicators-panel .obs-detail-table tbody td {
  font-size: 0.8125rem;
  line-height: 1.45;
  color: #cbd5e1;
}

.indicators-panel .obs-detail-table tbody td:first-child {
  font-variant-numeric: tabular-nums;
  color: #94a3b8;
}

.indicators-panel .obs-detail-table tbody tr:last-child td {
  border-bottom-color: transparent;
}

.indicators-panel .obs-detail-table tbody tr:hover {
  background: rgba(56, 189, 248, 0.06);
}

.ind-organ-cell {
  font-size: 0.75rem;
  max-width: 220px;
  color: #94a3b8;
}

.ind-panel-empty {
  margin: 0;
  padding: 1.2rem 1.25rem 1.35rem;
}

</style>
