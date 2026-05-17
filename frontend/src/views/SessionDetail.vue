<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { http, apiError } from '../api/http'
import type { ExamSession, Indicator, Observation } from '../api/types'
import NavBackLink from '../components/NavBackLink.vue'

const props = defineProps<{ personId: string; sessionId: string }>()

const session = ref<ExamSession | null>(null)
const observations = ref<Observation[]>([])
const indicatorHits = ref<Indicator[]>([])
const pickedIndicator = ref<Indicator | null>(null)

const indicatorSearch = ref('')
const indicatorCat = ref<'all' | 'physical' | 'lab' | 'imaging'>('all')
const loadingIndicators = ref(false)

const err = ref('')
const loading = ref(false)
const editingId = ref<number | null>(null)

const pid = computed(() => Number(props.personId))
const sid = computed(() => Number(props.sessionId))

const form = ref({
  indicator_id: '' as number | '',
  measured_at: '',
  value_text: '',
  ref_text: '',
  abnormal: '' as '' | 'yes' | 'no',
  remarks: '',
  findings_text: '',
  conclusion_text: '',
})

const selectedInd = computed(() => pickedIndicator.value)

const catLabel: Record<string, string> = {
  physical: '体格',
  lab: '检验',
  imaging: '影像',
}

const groupedHits = computed(() => {
  const g: Record<string, Indicator[]> = {}
  for (const i of indicatorHits.value) {
    if (!g[i.category]) g[i.category] = []
    g[i.category].push(i)
  }
  return g
})

async function fetchLeafIndicators() {
  loadingIndicators.value = true
  try {
    const params: Record<string, string | number | boolean> = {
      leaves_only: true,
      limit: 800,
      offset: 0,
    }
    const q = indicatorSearch.value.trim()
    if (q) params.search = q
    if (indicatorCat.value !== 'all') params.category = indicatorCat.value
    const { data } = await http.get<Indicator[]>('/api/indicators', { params })
    indicatorHits.value = data
    if (
      pickedIndicator.value &&
      !data.some((x) => x.id === pickedIndicator.value!.id)
    ) {
      /* 当前选中项不在本次结果集中时保留选中（提交仍有效），仅列表不展示 */
    }
  } catch (e) {
    err.value = apiError(e)
  } finally {
    loadingIndicators.value = false
  }
}

let searchDebounce: number
watch(indicatorSearch, () => {
  window.clearTimeout(searchDebounce)
  searchDebounce = window.setTimeout(() => fetchLeafIndicators(), 280)
})

watch(indicatorCat, () => {
  fetchLeafIndicators()
})

function pickIndicator(i: Indicator) {
  pickedIndicator.value = i
  form.value.indicator_id = i.id
}

function clearPick() {
  if (editingId.value !== null) return
  pickedIndicator.value = null
  form.value.indicator_id = ''
}

function indicatorFromObservation(o: Observation): Indicator {
  return {
    id: o.indicator_id,
    parent_id: o.indicator_parent_id,
    name: o.indicator_name,
    category: o.indicator_category,
    is_narrative: o.indicator_is_narrative,
    unit: o.indicator_unit,
    ref_range_hint: o.indicator_ref_range_hint ?? null,
    organ_ids: o.organ_ids,
  }
}

function resetValueFields() {
  form.value.value_text = ''
  form.value.ref_text = ''
  form.value.abnormal = ''
  form.value.remarks = ''
  form.value.findings_text = ''
  form.value.conclusion_text = ''
}

function cancelEdit() {
  editingId.value = null
  clearPick()
  resetValueFields()
  if (session.value) {
    form.value.measured_at = toLocal(session.value.report_at)
  }
}

function startEdit(o: Observation) {
  editingId.value = o.id
  err.value = ''
  pickedIndicator.value = indicatorFromObservation(o)
  form.value.indicator_id = o.indicator_id
  form.value.measured_at = toLocal(o.measured_at)
  form.value.value_text = o.value_text ?? ''
  form.value.ref_text = o.ref_text ?? ''
  form.value.abnormal =
    o.abnormal === null || o.abnormal === undefined ? '' : o.abnormal ? 'yes' : 'no'
  form.value.remarks = o.remarks ?? ''
  form.value.findings_text = o.findings_text ?? ''
  form.value.conclusion_text = o.conclusion_text ?? ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const [{ data: sess }, { data: obs }] = await Promise.all([
      http.get<ExamSession>(`/api/persons/${pid.value}/sessions/by-id/${sid.value}`),
      http.get<Observation[]>(
        `/api/persons/${pid.value}/sessions/by-id/${sid.value}/observations`,
      ),
    ])
    session.value = sess
    observations.value = obs
    if (!form.value.measured_at && sess) {
      form.value.measured_at = toLocal(sess.report_at)
    }
    await fetchLeafIndicators()
  } catch (e) {
    err.value = apiError(e)
  } finally {
    loading.value = false
  }
}

function toLocal(iso: string): string {
  const d = new Date(iso)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`
}

function parseAbnormalFromForm(): boolean | null {
  if (form.value.abnormal === '') return null
  return form.value.abnormal === 'yes'
}

function buildObservationBody() {
  const ind = pickedIndicator.value!
  const narrative = ind.is_narrative
  return {
    indicator_id: ind.id,
    measured_at: form.value.measured_at
      ? new Date(form.value.measured_at).toISOString()
      : null,
    value_text: narrative ? null : form.value.value_text || null,
    ref_text: narrative ? null : form.value.ref_text || null,
    abnormal: parseAbnormalFromForm(),
    remarks: form.value.remarks || null,
    findings_text: narrative ? form.value.findings_text || null : null,
    conclusion_text: narrative ? form.value.conclusion_text || null : null,
  }
}

async function submitObservation() {
  if (!session.value) return
  if (!pickedIndicator.value || form.value.indicator_id === '') {
    err.value = '请在下方列表中点选一条检查细项（支持搜索缩小范围）'
    return
  }
  err.value = ''
  const body = buildObservationBody()
  try {
    if (editingId.value !== null) {
      await http.patch(
        `/api/persons/${pid.value}/sessions/by-id/${sid.value}/observations/${editingId.value}`,
        body,
      )
      cancelEdit()
    } else {
      await http.post(
        `/api/persons/${pid.value}/sessions/by-id/${sid.value}/observations`,
        [body],
      )
      clearPick()
      resetValueFields()
    }
    await load()
  } catch (e) {
    err.value = apiError(e)
  }
}

async function deleteObservation(id: number) {
  if (!window.confirm('确定删除这条记录？删除后不可恢复。')) return
  err.value = ''
  try {
    await http.delete(
      `/api/persons/${pid.value}/sessions/by-id/${sid.value}/observations/${id}`,
    )
    if (editingId.value === id) cancelEdit()
    await load()
  } catch (e) {
    err.value = apiError(e)
  }
}

function fmt(iso: string) {
  return new Date(iso).toLocaleString('zh-CN')
}

function dispObs(o: Observation): string {
  if (o.indicator_is_narrative) {
    return [o.findings_text, o.conclusion_text].filter(Boolean).join(' / ') || '—'
  }
  return [o.value_text, o.ref_text ? `参考:${o.ref_text}` : '']
    .filter(Boolean)
    .join(' ')
}

function abnormalLabel(v: boolean | null): string {
  if (v === null || v === undefined) return '—'
  return v ? '异常' : '正常'
}

onMounted(load)
</script>

<template>
  <div v-if="loading && !session" class="loading-text card loading-card">加载中…</div>
  <template v-else-if="session">
    <div class="card">
      <p>
        <NavBackLink :to="`/persons/${pid}`" label="返回成员档案" />
      </p>
      <h2>批次明细</h2>
      <p class="muted">报告时间：{{ fmt(session.report_at) }}</p>
      <div v-if="err" class="err">{{ err }}</div>

      <h4>{{ editingId === null ? '新增一条记录' : `修改记录 #${editingId}` }}</h4>

      <div v-if="editingId !== null && selectedInd" class="edit-banner card-inner">
        <strong>正在修改：</strong>
        {{ selectedInd.name }}
        <span class="muted">（{{ catLabel[selectedInd.category] ?? selectedInd.category }}）</span>
      </div>

      <div
        v-if="editingId !== null && selectedInd && !selectedInd.is_narrative"
        class="edit-values card-inner"
      >
        <div class="row edit-values-row">
          <label class="edit-field"
            >报告值
            <input v-model="form.value_text" class="edit-input"
          /></label>
          <label class="edit-field"
            >标准值
            <input
              v-model="form.ref_text"
              class="edit-input"
              :placeholder="selectedInd.ref_range_hint || '参考范围或报告单标准值'"
            />
          </label>
          <label class="edit-field"
            >是否异常
            <select v-model="form.abnormal" class="edit-input">
              <option value="">未填</option>
              <option value="no">否</option>
              <option value="yes">是</option>
            </select>
          </label>
          <label class="edit-field grow"
            >备注
            <input v-model="form.remarks" class="edit-input"
          /></label>
        </div>
      </div>

      <div v-if="editingId !== null && selectedInd?.is_narrative" class="edit-values card-inner">
        <div class="row">
          <label class="grow"
            >报告显示
            <textarea v-model="form.findings_text" rows="2"
          /></label>
        </div>
        <div class="row">
          <label class="grow"
            >报告结论
            <textarea v-model="form.conclusion_text" rows="2"
          /></label>
        </div>
        <div class="row edit-values-row">
          <label class="edit-field"
            >是否异常
            <select v-model="form.abnormal" class="edit-input">
              <option value="">未填</option>
              <option value="no">否（正常）</option>
              <option value="yes">是（异常）</option>
            </select>
          </label>
          <label class="edit-field grow"
            >备注
            <input v-model="form.remarks" class="edit-input"
          /></label>
        </div>
      </div>

      <div class="row">
        <label
          >测量时间
          <input v-model="form.measured_at" type="datetime-local"
        /></label>
      </div>

      <div v-show="editingId === null" class="picker card-inner">
        <div class="picker-head">
          <strong>检查细项</strong>
          <span class="muted small">（叶子节点才可录入；细项多时请用搜索）</span>
          <RouterLink class="dict-link" to="/indicators">去指标编辑 →</RouterLink>
        </div>

        <div class="cat-tabs">
          <button
            type="button"
            :class="{ active: indicatorCat === 'all' }"
            class="secondary tab-btn"
            @click="indicatorCat = 'all'"
          >
            全部
          </button>
          <button
            type="button"
            :class="{ active: indicatorCat === 'physical' }"
            class="secondary tab-btn"
            @click="indicatorCat = 'physical'"
          >
            体格
          </button>
          <button
            type="button"
            :class="{ active: indicatorCat === 'lab' }"
            class="secondary tab-btn"
            @click="indicatorCat = 'lab'"
          >
            检验
          </button>
          <button
            type="button"
            :class="{ active: indicatorCat === 'imaging' }"
            class="secondary tab-btn"
            @click="indicatorCat = 'imaging'"
          >
            影像
          </button>
        </div>

        <label class="search-row">
          <span class="lbl">名称搜索</span>
          <input
            v-model="indicatorSearch"
            type="search"
            placeholder="输入关键字筛选，例如：胆红素、白细胞…"
            autocomplete="off"
          />
        </label>

        <div v-if="pickedIndicator" class="picked">
          已选：<strong>{{ pickedIndicator.name }}</strong>
          <span class="muted">（{{ catLabel[pickedIndicator.category] ?? pickedIndicator.category }}）</span>
          <button type="button" class="secondary tiny" @click="clearPick">重新选择</button>
        </div>

        <p v-if="loadingIndicators" class="muted">加载细项列表…</p>
        <div v-else class="hit-scroll">
          <template v-if="indicatorHits.length === 0">
            <p class="muted">
              没有匹配的细项。请调整关键字或大类，或在
              <RouterLink to="/indicators">指标编辑</RouterLink>
              中新增后再搜。
            </p>
          </template>
          <template v-else>
            <section
              v-for="cat in ['physical', 'lab', 'imaging']"
              v-show="groupedHits[cat]?.length"
              :key="cat"
              class="hit-section"
            >
              <h5>{{ catLabel[cat] }}</h5>
              <ul class="hit-list">
                <li v-for="i in groupedHits[cat]" :key="i.id">
                  <button
                    type="button"
                    class="hit-item"
                    :class="{ sel: pickedIndicator?.id === i.id }"
                    @click="pickIndicator(i)"
                  >
                    {{ i.name }}
                    <span v-if="i.unit" class="unit">{{ i.unit }}</span>
                  </button>
                </li>
              </ul>
            </section>
            <p class="muted footnote">
              单次最多展示 800 条；若没有你要的项，请用搜索缩小或去指标编辑页新增分组/细项。
            </p>
          </template>
        </div>
      </div>

      <template v-if="editingId === null && selectedInd?.is_narrative">
        <div class="row">
          <label class="grow"
            >报告显示
            <textarea v-model="form.findings_text" rows="2"
          /></label>
        </div>
        <div class="row">
          <label class="grow"
            >报告结论
            <textarea v-model="form.conclusion_text" rows="2"
          /></label>
        </div>
        <div class="row">
          <label
            >是否异常
            <select v-model="form.abnormal">
              <option value="">未填</option>
              <option value="no">否（正常）</option>
              <option value="yes">是（异常）</option>
            </select>
          </label>
          <label class="grow"
            >备注
            <input v-model="form.remarks"
          /></label>
        </div>
      </template>
      <template v-else-if="editingId === null && selectedInd">
        <div class="row">
          <label
            >报告值
            <input v-model="form.value_text"
          /></label>
          <label
            >标准值
            <input v-model="form.ref_text" :placeholder="selectedInd.ref_range_hint ?? ''"
          /></label>
          <label
            >是否异常
            <select v-model="form.abnormal">
              <option value="">未填</option>
              <option value="no">否</option>
              <option value="yes">是</option>
            </select>
          </label>
          <label class="grow"
            >备注
            <input v-model="form.remarks"
          /></label>
        </div>
      </template>

      <p class="form-actions">
        <button type="button" :disabled="!selectedInd" @click="submitObservation">
          {{ editingId === null ? '保存本条' : '保存修改' }}
        </button>
        <button v-if="editingId !== null" type="button" class="secondary" @click="cancelEdit">
          取消修改
        </button>
      </p>

      <h4>本批次已有记录</h4>
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>项目</th>
            <th>结果</th>
            <th>异常</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in observations"
            :key="o.id"
            :class="{
              'row-abnormal': o.abnormal === true,
              'row-editing': editingId === o.id,
            }"
          >
            <td>{{ fmt(o.measured_at) }}</td>
            <td>
              {{ o.indicator_parent_name ? o.indicator_parent_name + ' › ' : ''
              }}{{ o.indicator_name }}
            </td>
            <td :class="{ 'cell-abnormal': o.abnormal === true }">{{ dispObs(o) }}</td>
            <td :class="{ 'cell-abnormal': o.abnormal === true }">
              {{ abnormalLabel(o.abnormal) }}
            </td>
            <td class="obs-actions">
              <button type="button" class="secondary tiny" @click="startEdit(o)">修改</button>
              <button type="button" class="danger tiny" @click="deleteObservation(o.id)">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
</template>

<style scoped>
.loading-card {
  text-align: center;
  padding: 2rem;
}
h4 {
  margin: 1rem 0 0.5rem;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}
h5 {
  margin: 0.5rem 0 0.35rem;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #64748b;
}
.grow {
  flex: 1;
  min-width: 200px;
}
textarea {
  width: 100%;
}
.small {
  font-size: 0.8rem;
}
.card-inner {
  background: var(--surface-inner);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
.picker-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
}
.dict-link {
  margin-left: auto;
  font-size: 0.88rem;
  font-weight: 650;
}
.cat-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.65rem;
}
.tab-btn {
  padding: 0.32rem 0.72rem;
  font-size: 0.82rem;
}
.tab-btn.active {
  background: linear-gradient(145deg, #0ea5e9 0%, #6366f1 100%);
  color: #fff;
  border-color: transparent;
}
.search-row {
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
  margin-bottom: 0.65rem;
}
.search-row input {
  width: 100%;
  max-width: 520px;
}
.lbl {
  font-size: var(--font-form-label);
  font-weight: 650;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.picked {
  margin-bottom: 0.55rem;
  font-size: var(--font-form-control);
  padding: 0.45rem 0.65rem;
  border-radius: var(--radius-sm);
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.22);
}
.tiny {
  margin-left: 0.5rem;
  padding: 0.22rem 0.52rem;
  font-size: 0.76rem;
}
.hit-scroll {
  max-height: 340px;
  overflow: auto;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 0.65rem;
  background: rgba(6, 10, 18, 0.45);
}
.hit-section {
  margin-bottom: 0.55rem;
}
.hit-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.38rem;
}
.hit-item {
  background: rgba(51, 65, 85, 0.45);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  padding: 0.38rem 0.62rem;
  font-size: 0.84rem;
  border: 1px solid transparent;
  cursor: pointer;
  text-align: left;
  transition:
    background 0.12s ease,
    border-color 0.12s ease;
}
.hit-item:hover {
  background: rgba(71, 85, 105, 0.55);
  border-color: rgba(148, 163, 184, 0.25);
}
.hit-item.sel {
  background: rgba(56, 189, 248, 0.16);
  border-color: rgba(56, 189, 248, 0.55);
  color: #e0f2fe;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.12);
}
.unit {
  margin-left: 0.35rem;
  font-size: 0.76rem;
  color: var(--text-muted);
}
.footnote {
  margin: 0.55rem 0 0;
  font-size: 0.76rem;
}
.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.obs-actions {
  white-space: nowrap;
}
.obs-actions .tiny + .tiny {
  margin-left: 0.35rem;
}
.row-editing {
  background: rgba(56, 189, 248, 0.1);
}
.edit-banner {
  margin-bottom: 0.75rem;
  padding: 0.65rem 0.85rem;
  background: rgba(56, 189, 248, 0.1);
  border-color: rgba(56, 189, 248, 0.28);
}
.edit-values {
  margin-bottom: 0.85rem;
}
.edit-values-row {
  align-items: flex-start;
}
.edit-field {
  min-width: 8.5rem;
  flex: 1 1 10rem;
}
.edit-input {
  width: 100%;
  min-width: 0;
}
</style>
