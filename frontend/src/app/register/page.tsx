"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";
import LanguageSwitcher from "@/components/LanguageSwitcher";

export default function RegisterPage() {
  const router = useRouter();
  const { t, locale } = useI18n();
  const [form, setForm] = useState({
    username: "",
    password: "",
    level: "beginner",
    learning_goal: "general",
    cognitive_style: "visual",
  });
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const { access_token } = await api.register({ ...form, language: locale });
      setToken(access_token);
      localStorage.setItem("vocab_locale", locale);
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("register.failed"));
    }
  }

  return (
    <div className="container" style={{ maxWidth: 480, marginTop: "3rem" }}>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "0.5rem" }}>
        <LanguageSwitcher />
      </div>
      <div className="card">
        <h1>{t("register.title")}</h1>
        <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
          {t("register.subtitle")}
        </p>
        <form onSubmit={handleSubmit}>
          <label>{t("login.username")}</label>
          <input
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
          />
          <label>{t("login.password")}</label>
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
          <label>{t("register.level")}</label>
          <select
            value={form.level}
            onChange={(e) => setForm({ ...form, level: e.target.value })}
          >
            <option value="beginner">{t("level.beginner")}</option>
            <option value="intermediate">{t("level.intermediate")}</option>
            <option value="advanced">{t("level.advanced")}</option>
          </select>
          <label>{t("register.goal")}</label>
          <select
            value={form.learning_goal}
            onChange={(e) => setForm({ ...form, learning_goal: e.target.value })}
          >
            <option value="general">{t("goal.general")}</option>
            <option value="academic">{t("goal.academic")}</option>
            <option value="exam">{t("goal.exam")}</option>
          </select>
          <label>{t("register.style")}</label>
          <select
            value={form.cognitive_style}
            onChange={(e) =>
              setForm({ ...form, cognitive_style: e.target.value })
            }
          >
            <option value="visual">{t("style.visual")}</option>
            <option value="auditory">{t("style.auditory")}</option>
            <option value="kinesthetic">{t("style.kinesthetic")}</option>
          </select>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn" style={{ width: "100%" }}>
            {t("register.submit")}
          </button>
        </form>
        <p style={{ marginTop: "1rem" }}>
          <Link href="/login">{t("register.loginLink")}</Link>
        </p>
      </div>
    </div>
  );
}
