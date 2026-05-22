"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";

const SCENE_IDS = ["commute", "focus", "fragment", "review"] as const;

type RecommendItem = {
  word_id: number;
  word: string;
  meaning: string;
  score: number;
  r_sim: number;
  s_sim: number;
  alpha: number;
  explanation: string;
};

const DIM_KEYS = [
  "mastery",
  "morph_ability",
  "semantic_density",
  "engagement",
  "cognitive_load",
] as const;

export default function DashboardPage() {
  const router = useRouter();
  const { t, locale } = useI18n();
  const [scene, setScene] = useState("fragment");
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);
  const [knowledge, setKnowledge] = useState<Record<string, unknown> | null>(null);
  const [recommend, setRecommend] = useState<{
    items?: RecommendItem[];
    alpha?: number;
    alpha_explanation?: Record<string, string>;
    scene_adaptation?: Record<string, string>;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scene, locale]);

  async function load() {
    setLoading(true);
    try {
      const [p, k, r] = await Promise.all([
        api.profile(),
        api.knowledgeStatus(),
        api.recommend(scene),
      ]);
      setProfile(p);
      setKnowledge(k);
      setRecommend(r as typeof recommend);
    } catch {
      router.replace("/login");
    } finally {
      setLoading(false);
    }
  }

  const dims = (profile?.dimensions || {}) as Record<string, number>;
  const dimLabels =
    (knowledge?.dimension_labels as Record<string, string>) ||
    (profile?.dimension_labels as Record<string, string>) ||
    Object.fromEntries(DIM_KEYS.map((k) => [k, t(`dim.${k}`)]));

  if (loading) return <div className="container">{t("common.loading")}</div>;

  const sceneAdapt = recommend?.scene_adaptation || {};

  return (
    <div className="container">
      <h1>{t("dashboard.title")}</h1>
      <p style={{ color: "var(--muted)", marginBottom: "1.5rem" }}>
        {t("dashboard.formula")}
      </p>

      <div className="scene-tabs">
        {SCENE_IDS.map((id) => (
          <button
            key={id}
            className={`scene-tab ${scene === id ? "active" : ""}`}
            onClick={() => setScene(id)}
          >
            {t(`scene.${id}`)}{" "}
            <small>({t(`scene.${id}.desc`)})</small>
          </button>
        ))}
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>{t("dashboard.dimensions")}</h3>
          {DIM_KEYS.map((key) => (
            <div key={key} style={{ marginBottom: "0.8rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>{dimLabels[key] || t(`dim.${key}`)}</span>
                <span>{((dims[key] ?? 0) * 100).toFixed(0)}%</span>
              </div>
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${(dims[key] ?? 0) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <h3>
            {t("dashboard.alpha")} = {recommend?.alpha?.toFixed(2)}
          </h3>
          {recommend?.alpha_explanation && (
            <div style={{ fontSize: "0.9rem", color: "var(--muted)" }}>
              <p>{recommend.alpha_explanation.strategy}</p>
              <p>
                {t("dashboard.morphSemantic", {
                  morph: recommend.alpha_explanation.morph_weight,
                  semantic: recommend.alpha_explanation.semantic_weight,
                })}
              </p>
            </div>
          )}
          {sceneAdapt.presentation_label && (
            <p style={{ marginTop: "0.5rem" }}>
              <span className="badge">{sceneAdapt.presentation_label}</span>{" "}
              {t("dashboard.duration")} {sceneAdapt.duration_minutes} ·{" "}
              {t("dashboard.game")} {sceneAdapt.gamification_label}
            </p>
          )}
        </div>
      </div>

      <div className="card">
        <h3>{t("dashboard.recommendations")}</h3>
        <ul style={{ listStyle: "none" }}>
          {(recommend?.items || []).map((item) => (
            <li
              key={item.word_id}
              style={{
                padding: "0.8rem 0",
                borderBottom: "1px solid var(--border)",
              }}
            >
              <strong>{item.word}</strong> — {item.meaning}
              <div
                style={{
                  fontSize: "0.85rem",
                  color: "var(--muted)",
                  marginTop: "0.3rem",
                }}
              >
                {t("dashboard.score")} {item.score} · R_sim={item.r_sim} ·
                S_sim={item.s_sim} · α={item.alpha}
              </div>
              <div
                style={{
                  fontSize: "0.8rem",
                  color: "var(--accent2)",
                  marginTop: "0.2rem",
                }}
              >
                {item.explanation}
              </div>
              <a
                href={`/learn?word_id=${item.word_id}&scene=${scene}`}
                style={{ fontSize: "0.85rem" }}
              >
                {t("dashboard.startLearn")}
              </a>
            </li>
          ))}
        </ul>
      </div>

      <div className="card">
        <h3>
          {t("dashboard.knowledge")} (
          {((knowledge?.words as unknown[]) || []).length}{" "}
          {t("dashboard.words")})
        </h3>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {((knowledge?.words as { word: string; mastery: number }[]) || []).map(
            (w) => (
              <span
                key={w.word}
                className="badge"
                title={`${((w.mastery * 100).toFixed(0))}%`}
              >
                {w.word} {(w.mastery * 100).toFixed(0)}%
              </span>
            )
          )}
        </div>
      </div>
    </div>
  );
}
