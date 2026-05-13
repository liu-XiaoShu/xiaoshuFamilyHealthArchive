/** 成员占位头像：DiceBear「initials」（缩写 + 素雅纯色底）；可上传自定义头像覆盖 */

import type { Person } from '../api/types'

export interface MemberAvatarInput {
  id: number
  name: string
  gender: string | null
  birth_date: string | null
}

/** 蓝灰阶底色，由 seed 稳定映射其一 */
const BACKGROUND_PALETTE_SLATE =
  '475569,64748b,526583,334155,3d4f6f,4b5e7a,5c6b88,6b7280,4a5568'

/**
 * 同一成员固定不变；缩写由姓名推导，后缀 id 降低同名同色概率。
 */
export function memberAvatarUrl(p: MemberAvatarInput): string {
  const base = (p.name || '').trim() || `成员${p.id}`
  const seed = `${base}-${p.id}`
  const q = new URLSearchParams({
    seed,
    radius: '50',
    scale: '86',
    backgroundType: 'solid',
    backgroundColor: BACKGROUND_PALETTE_SLATE,
    textColor: 'f8fafc',
    clip: 'true',
  })
  return `https://api.dicebear.com/9.x/initials/svg?${q.toString()}`
}

/** 有自定义头像时用同源接口 URL；可选 bust 绕过浏览器缓存（上传/删除后递增）。 */
export function resolveMemberAvatarSrc(p: Person, bust?: number): string {
  const url = p.avatar_url
  if (url) {
    return bust != null && bust > 0 ? `${url}?v=${bust}` : url
  }
  return memberAvatarUrl(p)
}
