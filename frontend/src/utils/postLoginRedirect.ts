/**
 * 登录成功后的跳转目标：
 * - 默认：家庭成员列表 /
 * - 若曾去往成员详情、报告等相关路径（以 /persons 开头），则恢复原 URL
 */
export function postLoginTarget(raw: unknown): string {
  if (typeof raw !== 'string') {
    if (Array.isArray(raw) && typeof raw[0] === 'string') {
      return postLoginTarget(raw[0])
    }
    return '/'
  }
  const p = decodeURIComponent(raw).trim()
  if (!p.startsWith('/')) return '/'
  if (p === '/login') return '/'
  if (p.startsWith('/persons')) return p
  return '/'
}
