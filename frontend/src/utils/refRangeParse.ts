/** 从参考范围文案解析数值区间（用于趋势图背景带）；解析失败返回 null */

export interface ParsedRefBand {
  low?: number
  high?: number
  /** 原始参考文案（展示用） */
  rawLabel: string
}

export function parseRefRange(ref: string | null | undefined): ParsedRefBand | null {
  if (ref == null) return null
  const rawLabel = String(ref).trim()
  if (!rawLabel || !/\d/.test(rawLabel)) return null

  let s = rawLabel.replace(/\s+/g, '')
  s = s.replace(
    /μmol\/l|μmol\/L|mmol\/l|mmol\/L|ng\/ml|ng\/mL|NG\/ML|U\/mL|u\/ml|IU\/ml|%|×10⁹\/L|×10\^9\/L/gi,
    '',
  )

  const between = s.match(/^([\d.]+)[-–~～]([\d.]+)$/)
  if (between) {
    const a = parseFloat(between[1])
    const b = parseFloat(between[2])
    if (Number.isFinite(a) && Number.isFinite(b)) {
      return { low: Math.min(a, b), high: Math.max(a, b), rawLabel }
    }
  }

  const le = s.match(/^[≤<]([\d.]+)$/)
  if (le) {
    const high = parseFloat(le[1])
    if (Number.isFinite(high)) return { high, rawLabel }
  }

  const ge = s.match(/^[≥>]([\d.]+)$/)
  if (ge) {
    const low = parseFloat(ge[1])
    if (Number.isFinite(low)) return { low, rawLabel }
  }

  return null
}

/** 取时间上「最后一次」能解析出数值区间的参考说明（与表格最后一行一致） */
export function mergeRefBandFromLatestPoint(points: { refText: string | null }[]): ParsedRefBand | null {
  for (let i = points.length - 1; i >= 0; i--) {
    const p = parseRefRange(points[i].refText)
    if (p && (p.low != null || p.high != null)) return p
  }
  return null
}
