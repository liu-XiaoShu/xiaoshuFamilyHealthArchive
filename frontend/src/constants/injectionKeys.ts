import type { InjectionKey } from 'vue'

export type OpenAboutFn = () => void

/** 全局打开「关于」对话框（由 App 提供） */
export const openAboutKey: InjectionKey<OpenAboutFn> = Symbol('openAbout')
