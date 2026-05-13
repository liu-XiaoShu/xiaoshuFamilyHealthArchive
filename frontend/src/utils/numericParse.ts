/** 字符串开头（允许前置比较符号）的数值 */
function parseLeadingNumericToken(cleanedNoSpaces: string): number | null {
  const m = cleanedNoSpaces.match(/^[<>≤≥≈~～]*([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)/i)
  if (!m) return null
  const n = parseFloat(m[1])
  return Number.isFinite(n) ? n : null
}

/**
 * 中文体检常见写法：数字前有「右眼」「视力」等时，严格前缀解析会失败。
 * 依次尝试：关键字捕获 → 分段 → 首个合理数字（跳过 1900–2100 整数年份）。
 */
function parseNumericEmbeddedChinese(raw: string): number | null {
  const tries = [
    /(?:右眼|左眼|双眼)[：:\s，,\uff1a]*([+-]?\d+(?:\.\d+)?)/,
    /(?:矫正视力|裸眼视力|小数视力)[：:\s，,\uff1a]*([+-]?\d+(?:\.\d+)?)/,
    /(?:矫正|裸眼|屈光)[：:\s，,\uff1a]*([+-]?\d+(?:\.\d+)?)/,
    /视力[：:\s，,\uff1a]*([+-]?\d+(?:\.\d+)?)/,
  ]
  for (const re of tries) {
    const m = raw.match(re)
    if (m) {
      const n = parseFloat(m[1])
      if (Number.isFinite(n)) return n
    }
  }

  for (const segment of raw.split(/[/／]/)) {
    const seg = segment.trim().replace(/,/g, '.').replace(/，/g, '.').replace(/\s+/g, '')
    const v = parseLeadingNumericToken(seg)
    if (v !== null) return v
  }

  const numRe = /([+-]?\d+(?:\.\d+)?)/g
  let mm: RegExpExecArray | null
  while ((mm = numRe.exec(raw)) !== null) {
    const n = parseFloat(mm[1])
    if (!Number.isFinite(n)) continue
    const r = Math.round(n)
    const isWhole = Math.abs(n - r) < 1e-9
    if (isWhole && r >= 1900 && r <= 2100) continue
    return n
  }

  return null
}

/** 从报告值字符串中尝试解析数值（用于趋势曲线）；叙述类或非数值返回 null */
export function parseNumericValue(raw: string | null | undefined): number | null {
  if (raw == null) return null
  const s = String(raw).trim()
  if (!s || !/\d/.test(s)) return null

  const cleaned = s.replace(/,/g, '.').replace(/，/g, '.').replace(/\s+/g, '')
  const strict = parseLeadingNumericToken(cleaned)
  if (strict !== null) return strict

  return parseNumericEmbeddedChinese(s)
}

/**
 * 阴性 / 阳性 / 弱阳 / ± 等定性化验用语 → 纵向刻度（用于趋势图）。
 * 需在 parseNumericValue 失败后调用；不与纯数字字符串冲突。
 *
 * - 0：阴性、(-)、negative 等
 * - 0.5：弱阳性、可疑、± 等灰区
 * - 1：阳性、(+)、+++、positive 等
 */
export function parseQualitativeTrendValue(raw: string | null | undefined): number | null {
  if (raw == null) return null
  const s = String(raw).trim()
  if (!s) return null

  const compact = s.replace(/\s+/g, '')
  const word = s.trim().toLowerCase()

  if (/弱阳性|弱阳|±|可疑/.test(compact)) return 0.5

  if (word === 'negative' || word === 'neg') return 0

  if (/阴性/.test(compact) || /\(-/.test(compact) || /−\)/.test(compact)) return 0
  if (/^[-−]\)?$/u.test(compact) || /^\(?[-−]\)?$/u.test(compact)) return 0

  if (word === 'positive' || word === 'pos') return 1

  if (/阳性/.test(compact) || /\(\+/.test(compact)) return 1
  if (/^\+{1,3}$/.test(compact)) return 1

  return null
}

/** 定性曲线纵轴刻度文案（与 parseQualitativeTrendValue 取值对应） */
export function qualitativeOrdinalLabel(y: number): string {
  if (Math.abs(y) < 1e-6) return '阴性'
  if (Math.abs(y - 0.5) < 1e-6) return '弱阳/可疑'
  if (Math.abs(y - 1) < 1e-6) return '阳性'
  return String(y)
}
