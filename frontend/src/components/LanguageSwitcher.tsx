"use client";

import { LOCALES } from "@/i18n/types";
import { useI18n } from "@/i18n/context";

export default function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();

  return (
    <label style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
      <span style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
        {t("lang.label")}
      </span>
      <select
        value={locale}
        onChange={(e) => setLocale(e.target.value as typeof locale)}
        style={{ width: "auto", margin: 0, padding: "0.35rem 0.5rem" }}
        aria-label={t("lang.label")}
      >
        {LOCALES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.label}
          </option>
        ))}
      </select>
    </label>
  );
}
