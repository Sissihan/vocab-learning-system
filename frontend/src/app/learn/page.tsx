"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api, getToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";

function LearnContent() {
  const router = useRouter();
  const { t, locale } = useI18n();
  const params = useSearchParams();
  const wordId = Number(params.get("word_id") || 0);
  const scene = params.get("scene") || "focus";

  const [content, setContent] = useState<Record<string, unknown> | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    if (wordId) loadContent(wordId);
  }, [wordId, scene, locale, router]);

  async function loadContent(id: number) {
    const level =
      scene === "fragment"
        ? "beginner"
        : scene === "focus"
          ? "advanced"
          : "intermediate";
    const data = await api.generateContent(id, level, scene);
    setContent(data);
    setRevealed(false);
  }

  async function recordAnswer(correct: boolean) {
    const elapsed = (Date.now() - startTime) / 1000;
    await api.recordLearning({
      word_id: wordId,
      scene_type: scene,
      is_correct: correct,
      response_time: elapsed,
      score: correct ? 1 : 0,
      activity_type: "study",
    });
    alert(correct ? t("learn.correct") : t("learn.incorrect"));
    router.push("/dashboard");
  }

  if (!wordId) {
    return (
      <div className="container">
        <p>{t("learn.pickWord")}</p>
      </div>
    );
  }

  if (!content) return <div className="container">{t("learn.loading")}</div>;

  return (
    <div className="container">
      <h1>{content.word as string}</h1>
      <span className="badge">{t(`scene.${scene}`)}</span>
      <p style={{ color: "var(--muted)" }}>{content.phonetic as string}</p>

      <div className="card" style={{ marginTop: "1rem" }}>
        {!revealed ? (
          <button className="btn" onClick={() => setRevealed(true)}>
            {t("learn.showMeaning")}
          </button>
        ) : (
          <>
            <h3>{content.meaning as string}</h3>
            <p style={{ marginTop: "1rem" }}>{content.sentence as string}</p>
            <ul style={{ marginTop: "0.5rem", paddingLeft: "1.2rem" }}>
              {((content.examples as string[]) || []).map((ex, i) => (
                <li key={i} style={{ marginBottom: "0.3rem" }}>
                  {ex}
                </li>
              ))}
            </ul>
            {content.root_analysis && (
              <div
                style={{
                  marginTop: "1rem",
                  padding: "0.8rem",
                  background: "var(--surface2)",
                  borderRadius: "8px",
                }}
              >
                <strong>{t("learn.rootAnalysis")}</strong>
                <p>
                  {(content.root_analysis as { root: string }).root} ={" "}
                  {(content.root_analysis as { root_meaning: string }).root_meaning}
                </p>
              </div>
            )}
            <p style={{ marginTop: "0.5rem", color: "var(--warn)" }}>
              {content.scene_hint as string}
            </p>
            <p style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
              {t("learn.validate")}:{" "}
              {(content.validated as boolean)
                ? t("learn.validate.pass")
                : t("learn.validate.pending")}{" "}
              — {((content.validation_notes as string[]) || []).join("; ")}
            </p>
          </>
        )}
      </div>

      {revealed && (
        <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
          <button className="btn btn-success" onClick={() => recordAnswer(true)}>
            {t("learn.known")}
          </button>
          <button className="btn btn-secondary" onClick={() => recordAnswer(false)}>
            {t("learn.unknown")}
          </button>
        </div>
      )}
    </div>
  );
}

export default function LearnPage() {
  const { t } = useI18n();
  return (
    <Suspense fallback={<div className="container">{t("common.loading")}</div>}>
      <LearnContent />
    </Suspense>
  );
}
