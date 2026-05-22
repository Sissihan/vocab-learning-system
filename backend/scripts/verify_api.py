"""Quick API smoke test. Run: python scripts/verify_api.py"""
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def req(path, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    checks = []
    try:
        h = req("/health")
        checks.append(("health", h.get("status") == "healthy"))

        tok = req("/api/auth/login/json", "POST", {"username": "demo", "password": "demo123"})
        token = tok["access_token"]
        checks.append(("login", bool(token)))

        rec = req("/api/recommend?scene_type=focus&limit=3", token=token)
        checks.append(("recommend", len(rec.get("items", [])) > 0 and "alpha" in rec))

        kn = req("/api/knowledge/status", token=token)
        checks.append(("knowledge", "mastery" in kn))

        puzzle = req("/api/games/root-puzzle", token=token)
        checks.append(("root-puzzle", len(puzzle.get("puzzles", [])) > 0))

        match = req("/api/games/semantic-match", token=token)
        checks.append(("semantic-match", "words" in match))

        planet = req("/api/games/word-planet", token=token)
        checks.append(("word-planet", "network" in planet and len(planet["network"].get("nodes", [])) > 0))

        puzzle_submit = req(
            "/api/games/root-puzzle/result",
            "POST",
            {
                "answers": [
                    {
                        "root_id": p["root_id"],
                        "selected_affix": p["correct_affix"],
                        "correct_affix": p["correct_affix"],
                    }
                    for p in puzzle["puzzles"][:2]
                ],
            },
            token=token,
        )
        checks.append(
            ("puzzle-submit", puzzle_submit.get("score", 0) == 100.0)
        )

        match_pairs = [
            {"word_id": w["id"], "meaning_id": w["id"]}
            for w in match["words"][:4]
        ]
        match_submit = req(
            "/api/games/semantic-match/result",
            "POST",
            {"pairs": match_pairs},
            token=token,
        )
        checks.append(
            ("match-submit", match_submit.get("correct_count", 0) == len(match_pairs))
        )

        content = req("/api/content/generate?word_id=1&level=intermediate", token=token)
        checks.append(("content", content.get("word") is not None))

        scenes = req("/api/context/scenes", token=token)
        checks.append(("scenes", len(scenes) == 4))

        rec_en = req("/api/recommend?scene_type=focus&limit=1&lang=en", token=token)
        checks.append(
            ("i18n-en", "Score =" in rec_en["items"][0]["explanation"])
        )
        rec_tw = req("/api/recommend?scene_type=focus&limit=1&lang=zh-TW", token=token)
        checks.append(
            ("i18n-zh-TW", "；" in rec_tw["items"][0]["explanation"])
        )

    except urllib.error.URLError as e:
        print(f"FAIL: Cannot reach backend at {BASE} — {e}")
        print("Start backend: cd backend && venv\\Scripts\\python run.py")
        sys.exit(1)

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  [{'OK' if ok else 'FAIL'}] {name}")

    if failed:
        print(f"\nFailed: {failed}")
        sys.exit(1)
    print("\nAll API checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
