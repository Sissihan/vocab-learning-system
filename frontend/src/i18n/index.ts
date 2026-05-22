import type { Locale, Messages } from "./types";
import zhCN from "./locales/zh-CN";
import en from "./locales/en";
import zhTW from "./locales/zh-TW";

export * from "./types";

const catalogs: Record<Locale, Messages> = {
  "zh-CN": zhCN,
  en,
  "zh-TW": zhTW,
};

export function getMessages(locale: Locale): Messages {
  return catalogs[locale] || catalogs["zh-CN"];
}

export function translate(
  locale: Locale,
  key: string,
  params?: Record<string, string | number>
): string {
  const msg = getMessages(locale)[key] ?? catalogs["zh-CN"][key] ?? key;
  if (!params) return msg;
  return Object.entries(params).reduce(
    (text, [k, v]) => text.replace(new RegExp(`\\{${k}\\}`, "g"), String(v)),
    msg
  );
}

export function normalizeLocale(input: string | null): Locale {
  if (!input) return "zh-CN";
  const lower = input.toLowerCase().replace("_", "-");
  if (lower === "zh-tw" || lower === "zh-hant" || lower === "tw") return "zh-TW";
  if (lower.startsWith("en")) return "en";
  if (lower.startsWith("zh")) return "zh-CN";
  return "zh-CN";
}
