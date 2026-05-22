"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";
import type { Locale } from "@/i18n/types";

const DIM_KEYS = [
  "mastery",
  "morph_ability",
  "semantic_density",
  "engagement",
  "cognitive_load",
] as const;

export default function ProfilePage() {
  const router = useRouter();
  const { t, locale, setLocale } = useI18n();
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [form, setForm] = useState({
    level: "intermediate",
    learning_goal: "general",
    cognitive_style: "visual",
    preferred_scene: "focus",
    language: locale as Locale,
  });

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    api.profile().then((p) => {
      setProfile(p);
      const prof = (p.profile || {}) as Record<string, string>;
      setForm({
        level: (p.level as string) || "intermediate",
        learning_goal: (p.learning_goal as string) || "general",
        cognitive_style: (p.cognitive_style as string) || "visual",
        preferred_scene: prof.preferred_scene || "focus",
        language: (prof.language as Locale) || locale,
      });
    });
  }, [locale, router]);

  async function save() {
    setLocale(form.language);
    const updated = await api.updateProfile({
      ...form,
      language: form.language,
    });
    setProfile(updated);
    alert(t("common.saved"));
  }

  if (!profile) return <div className="container">{t("common.loading")}</div>;

  const dims = (profile.dimensions || {}) as Record<string, number>;
  const dimLabels =
    (profile.dimension_labels as Record<string, string>) ||
    Object.fromEntries(DIM_KEYS.map((k) => [k, t(`dim.${k}`)]));

  return (
    <div className="container">
      <h1>{t("profile.title")}</h1>
      <div className="card">
        <h3>
          {t("profile.account")}: {profile.username as string}
        </h3>
        <label>{t("lang.label")}</label>
        <select
          value={form.language}
          onChange={(e) =>
            setForm({ ...form, language: e.target.value as Locale })
          }
        >
          <option value="zh-CN">简体中文</option>
          <option value="en">English</option>
          <option value="zh-TW">繁體中文</option>
        </select>
        <label>{t("profile.level")}</label>
        <select
          value={form.level}
          onChange={(e) => setForm({ ...form, level: e.target.value })}
        >
          <option value="beginner">{t("level.beginner")}</option>
          <option value="intermediate">{t("level.intermediate")}</option>
          <option value="advanced">{t("level.advanced")}</option>
          <option value="expert">{t("level.expert")}</option>
        </select>
        <label>{t("profile.goal")}</label>
        <select
          value={form.learning_goal}
          onChange={(e) => setForm({ ...form, learning_goal: e.target.value })}
        >
          <option value="general">{t("goal.general")}</option>
          <option value="academic">{t("goal.academic")}</option>
          <option value="exam">{t("goal.exam")}</option>
        </select>
        <label>{t("profile.style")}</label>
        <select
          value={form.cognitive_style}
          onChange={(e) => setForm({ ...form, cognitive_style: e.target.value })}
        >
          <option value="visual">{t("style.visual")}</option>
          <option value="auditory">{t("style.auditory")}</option>
          <option value="kinesthetic">{t("style.kinesthetic")}</option>
        </select>
        <label>{t("profile.scene")}</label>
        <select
          value={form.preferred_scene}
          onChange={(e) => setForm({ ...form, preferred_scene: e.target.value })}
        >
          <option value="commute">{t("scene.commute")}</option>
          <option value="focus">{t("scene.focus")}</option>
          <option value="fragment">{t("scene.fragment")}</option>
          <option value="review">{t("scene.review")}</option>
        </select>
        <button className="btn" onClick={save}>
          {t("common.save")}
        </button>
      </div>

      <div className="card">
        <h3>{t("profile.stats")}</h3>
        <div className="grid-2">
          {DIM_KEYS.map((key) => (
            <div key={key}>
              <span>{dimLabels[key] || t(`dim.${key}`)}</span>
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${(dims[key] ?? 0) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
