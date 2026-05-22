"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getToken } from "@/lib/api";
import { useI18n } from "@/i18n/context";

type Puzzle = {
  root_id: number;
  root: string;
  meaning: string;
  correct_affix: string;
  example_words?: string[];
  options: { affix: string; meaning: string }[];
  hint: string;
};

type TabId = "puzzle" | "match" | "planet";

export default function GamesPage() {
  const router = useRouter();
  const { t, locale } = useI18n();
  const [tab, setTab] = useState<TabId>("puzzle");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [puzzleData, setPuzzleData] = useState<{
    puzzles?: Puzzle[];
    title?: string;
    description?: string;
  } | null>(null);
  const [matchData, setMatchData] = useState<Record<string, unknown> | null>(null);
  const [planetData, setPlanetData] = useState<Record<string, unknown> | null>(null);
  const [selections, setSelections] = useState<Record<number, string>>({});
  const [matchPairs, setMatchPairs] = useState<Record<number, number>>({});
  const [selectedWord, setSelectedWord] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const loadTab = useCallback(
    async (tId: TabId) => {
      setLoading(true);
      setError("");
      try {
        if (tId === "puzzle") {
          setPuzzleData(await api.rootPuzzle());
          setSelections({});
        }
        if (tId === "match") {
          setMatchData(await api.semanticMatch());
          setMatchPairs({});
          setSelectedWord(null);
        }
        if (tId === "planet") {
          setPlanetData(await api.wordPlanet());
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : t("games.error"));
      } finally {
        setLoading(false);
      }
    },
    [t]
  );

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    loadTab(tab);
  }, [tab, locale, router, loadTab]);

  async function submitPuzzle() {
    const puzzles = puzzleData?.puzzles || [];
    const unanswered = puzzles.filter((p) => !selections[p.root_id]);
    if (unanswered.length > 0) {
      alert(t("games.puzzle.incomplete"));
      return;
    }

    setSubmitting(true);
    try {
      const answers = puzzles.map((p) => ({
        root_id: p.root_id,
        selected_affix: selections[p.root_id],
        correct_affix: p.correct_affix,
      }));
      const result = await api.submitPuzzle(answers);
      alert(
        t("games.puzzle.score", {
          score: String(result.score),
          correct: String(result.correct_count),
          total: String(result.total),
        })
      );
    } catch (e) {
      alert(e instanceof Error ? e.message : t("games.error"));
    } finally {
      setSubmitting(false);
    }
  }

  async function submitMatch() {
    const words = (matchData?.words as { id: number }[]) || [];
    if (words.length === 0) return;

    const unpaired = words.filter((w) => matchPairs[w.id] === undefined);
    if (unpaired.length > 0) {
      alert(t("games.puzzle.incomplete"));
      return;
    }

    setSubmitting(true);
    try {
      const pairs = words.map((w) => ({
        word_id: w.id,
        meaning_id: matchPairs[w.id],
      }));
      const result = await api.submitSemanticMatch(pairs);
      alert(
        t("games.match.result", {
          correct: String(result.correct_count),
          total: String(result.total),
        }) + ` (${result.score}%)`
      );
    } catch (e) {
      alert(e instanceof Error ? e.message : t("games.error"));
    } finally {
      setSubmitting(false);
    }
  }

  const network = (planetData?.network || {}) as {
    nodes?: { id: string; label: string; type: string; meaning?: string }[];
    root?: { root: string; meaning: string };
  };
  const nodes = network.nodes || [];

  return (
    <div className="container">
      <h1>{t("games.title")}</h1>
      <div className="scene-tabs">
        {(
          [
            { id: "puzzle" as TabId, label: t("games.puzzle") },
            { id: "match" as TabId, label: t("games.match") },
            { id: "planet" as TabId, label: t("games.planet") },
          ] as const
        ).map((item) => (
          <button
            key={item.id}
            className={`scene-tab ${tab === item.id ? "active" : ""}`}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="card">
          <p>{t("games.loading")}</p>
        </div>
      )}

      {error && !loading && (
        <div className="card">
          <p className="error">{error}</p>
          <button className="btn" onClick={() => loadTab(tab)}>
            {t("games.retry")}
          </button>
        </div>
      )}

      {!loading && !error && tab === "puzzle" && puzzleData && (
        <div className="card">
          <h3>{puzzleData.title || t("games.puzzle")}</h3>
          <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
            {puzzleData.description || t("games.puzzle.instruction")}
          </p>
          {(puzzleData.puzzles || []).map((p) => (
            <div
              key={p.root_id}
              style={{
                marginBottom: "1.2rem",
                padding: "0.8rem",
                borderRadius: "8px",
                border: "1px solid var(--border)",
              }}
            >
              <strong>{p.root}</strong> — {p.meaning}
              {p.example_words && p.example_words.length > 0 && (
                <div style={{ fontSize: "0.85rem", color: "var(--muted)", marginTop: "0.3rem" }}>
                  e.g. {p.example_words.join(", ")}
                </div>
              )}
              <div style={{ fontSize: "0.8rem", color: "var(--accent2)", marginTop: "0.3rem" }}>
                {t("games.puzzle.hintLabel")}: {p.hint}
              </div>
              <div
                style={{
                  display: "flex",
                  gap: "0.5rem",
                  flexWrap: "wrap",
                  marginTop: "0.6rem",
                }}
              >
                {p.options.map((opt) => (
                  <button
                    key={`${p.root_id}-${opt.affix}`}
                    type="button"
                    className={`btn btn-secondary ${
                      selections[p.root_id] === opt.affix ? "btn-success" : ""
                    }`}
                    onClick={() =>
                      setSelections((prev) => ({ ...prev, [p.root_id]: opt.affix }))
                    }
                  >
                    {opt.affix} ({opt.meaning})
                  </button>
                ))}
              </div>
            </div>
          ))}
          <button
            className="btn"
            onClick={submitPuzzle}
            disabled={submitting || !(puzzleData.puzzles || []).length}
          >
            {submitting ? t("games.loading") : t("games.puzzle.submit")}
          </button>
        </div>
      )}

      {!loading && !error && tab === "match" && matchData && (
        <div className="card">
          <h3>{(matchData.title as string) || t("games.match")}</h3>
          <p style={{ color: "var(--muted)" }}>{t("games.match.instruction")}</p>
          <div className="grid-2">
            <div>
              <h4>{t("games.match.words")}</h4>
              {((matchData.words as { id: number; word: string }[]) || []).map((w) => {
                const paired = matchPairs[w.id] !== undefined;
                const isActive = selectedWord === w.id;
                return (
                  <button
                    key={w.id}
                    type="button"
                    className={`btn btn-secondary ${isActive ? "btn-success" : ""}`}
                    style={{
                      margin: "0.3rem",
                      display: "block",
                      opacity: paired && !isActive ? 0.7 : 1,
                    }}
                    onClick={() => setSelectedWord(w.id)}
                  >
                    {w.word}
                    {paired && (
                      <span className="badge" style={{ marginLeft: "0.4rem" }}>
                        {t("games.match.paired")}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
            <div>
              <h4>{t("games.match.meanings")}</h4>
              {((matchData.meanings as { id: number; meaning: string }[]) || []).map((m) => {
                const linkedWordId = Object.entries(matchPairs).find(
                  ([, mid]) => mid === m.id
                )?.[0];
                return (
                  <button
                    key={m.id}
                    type="button"
                    className="btn btn-secondary"
                    style={{
                      margin: "0.3rem",
                      display: "block",
                      borderColor: linkedWordId ? "var(--accent2)" : undefined,
                    }}
                    onClick={() => {
                      if (selectedWord === null) {
                        alert(t("games.match.selectWord"));
                        return;
                      }
                      setMatchPairs((prev) => ({ ...prev, [selectedWord]: m.id }));
                      setSelectedWord(null);
                    }}
                  >
                    {m.meaning}
                  </button>
                );
              })}
            </div>
          </div>
          <button
            className="btn"
            style={{ marginTop: "1rem" }}
            onClick={submitMatch}
            disabled={submitting}
          >
            {submitting ? t("games.loading") : t("games.match.submit")}
          </button>
        </div>
      )}

      {!loading && !error && tab === "planet" && planetData && (
        <div className="card">
          <h3>
            {(planetData.title as string) || t("games.planet")}
            {network.root?.root ? ` — ${network.root.root}` : ""}
          </h3>
          <p style={{ color: "var(--muted)", marginBottom: "0.5rem" }}>
            {planetData.description as string}
          </p>
          {nodes.length === 0 ? (
            <p>{t("games.planet.empty")}</p>
          ) : (
            <>
              <p style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
                {t("games.planet.nodes")}: {nodes.length}
              </p>
              <div className="planet-canvas">
                {nodes.map((node, i) => {
                  const n = Math.max(nodes.length, 1);
                  const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
                  const r = node.type === "root" ? 0 : 38;
                  const cx = 50 + Math.cos(angle) * r;
                  const cy = 50 + Math.sin(angle) * r;
                  return (
                    <div
                      key={node.id}
                      className={`planet-node ${node.type}`}
                      style={{ left: `${cx}%`, top: `${cy}%` }}
                      title={node.meaning || node.label}
                    >
                      {node.label}
                    </div>
                  );
                })}
              </div>
            </>
          )}
          <p style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
            {t("games.planet.switch")}:
          </p>
          <div>
            {(planetData.available_roots as { id: number; root: string }[])?.map((r) => (
              <button
                key={r.id}
                type="button"
                className={`btn btn-secondary ${
                  (planetData as { current_root_id?: number }).current_root_id === r.id
                    ? "btn-success"
                    : ""
                }`}
                style={{ margin: "0.2rem" }}
                onClick={async () => {
                  setLoading(true);
                  try {
                    setPlanetData(await api.wordPlanet(r.id));
                  } catch (e) {
                    setError(e instanceof Error ? e.message : t("games.error"));
                  } finally {
                    setLoading(false);
                  }
                }}
              >
                {r.root}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
