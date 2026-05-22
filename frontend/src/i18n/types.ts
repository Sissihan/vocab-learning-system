export type Locale = "zh-CN" | "en" | "zh-TW";

export const LOCALES: { code: Locale; label: string }[] = [
  { code: "zh-CN", label: "简体中文" },
  { code: "en", label: "English" },
  { code: "zh-TW", label: "繁體中文" },
];

export const DEFAULT_LOCALE: Locale = "zh-CN";

export type Messages = Record<string, string>;
