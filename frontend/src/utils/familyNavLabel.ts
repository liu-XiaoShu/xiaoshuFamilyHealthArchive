/** 未登录或未拉取到用户名时的导航/页眉兜底 */
export const DEFAULT_FAMILY_NAV_LABEL = '家庭成员'

/** 与顶栏、成员列表大标题一致：`{账户名}的家` */
export function familyNavLabelFromUsername(account: string | null | undefined): string {
  const s = (account ?? '').trim()
  return s ? `${s}的家` : DEFAULT_FAMILY_NAV_LABEL
}
