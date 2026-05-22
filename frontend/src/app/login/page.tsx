"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";
import LanguageSwitcher from "@/components/LanguageSwitcher";

export default function LoginPage() {
  const router = useRouter();
  const { t } = useI18n();
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("demo123");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const { access_token } = await api.login(username, password);
      setToken(access_token);
      try {
        const profile = await api.profile();
        const prof = (profile.profile || {}) as Record<string, string>;
        if (prof.language) {
          localStorage.setItem("vocab_locale", prof.language);
        }
      } catch {
        /* profile sync optional */
      }
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("login.failed"));
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420, marginTop: "4rem" }}>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "0.5rem" }}>
        <LanguageSwitcher />
      </div>
      <div className="card">
        <h1>{t("login.title")}</h1>
        <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
          {t("app.subtitle")}
        </p>
        <form onSubmit={handleSubmit}>
          <label>{t("login.username")}</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
          <label>{t("login.password")}</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn" style={{ width: "100%" }}>
            {t("login.submit")}
          </button>
        </form>
        <p style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
          {t("login.demo")} · <Link href="/register">{t("login.registerLink")}</Link>
        </p>
      </div>
    </div>
  );
}
