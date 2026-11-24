#!/usr/bin/env python3
"""Hook scorer + first-3-seconds / retention check for ManifestAI reels and carousels.

  python3 tools/hook_check.py hooks daily/.../hooks.txt          # score candidate hooks (one per line), best first
  python3 tools/hook_check.py script daily/.../script.json        # check a reel script (+ hook audio length if built)
  python3 tools/hook_check.py carousel daily/.../carousel.json    # check a carousel's cover slide

Rubric (0-100), calibrated on this account's known hooks (see manifestai-hooks skill):
  claim-first 20 · stakes/cost 20 · specificity 20 · pattern-interrupt 15 · "you"-addressed 10 · length 15
Dealbreakers (score capped at 40): opens with "stop scrolling"/"POV"/"hey"/"did you know"/"in this video",
  a question with no stakes, or a promise of guaranteed results.
A hook must score >= 75 to be used. Write more from different formulas instead of polishing a weak one.
"""
import json, os, re, sys

BANNED_OPENERS = ("stop scrolling", "pov", "hey", "did you know", "in this video", "today i", "welcome", "watch till")
GUARANTEE = ("guaranteed", "will make you rich", "100% works", "instantly manifest", "overnight")
STAKES = ("quit", "fail", "lie", "lying", "broke", "wrong", "never", "waste", "lose", "losing", "stuck", "again",
          "every time", "nobody", "no one", "won't", "doesn't", "don't", "isn't", "not working", "behind", "rejecting",
          "ignored", "starting over", "restart", "numb", "fake", "forget", "gave up", "give up", "said no", "lasted",
          "costs", "still", "only", "screenshot", "knows", "doesn't believe", "rejected")
INTERRUPT = ("stop", "not", "never", "wrong", "lie", "nobody", "no one", "actually", "secretly", "quietly", "the real",
             "unpopular", "truth", "worst", "mistake", "why your", "don't")
WEAK_START = ("so ", "and ", "but ", "i think", "maybe", "here are", "here's how", "let me", "want to", "do you want")
NUM = re.compile(r"(\d|₹|\bone\b|\btwo\b|\bthree\b|\bfour\b|\bfive\b|\bseven\b|\bten\b|\b21\b|monday|friday|sunday|morning|night|day \d|weeks?|days?|lakh|crore)", re.I)

def score(h):
    t = h.strip(); low = t.lower(); words = re.findall(r"[\w'₹]+", low); n = len(words)
    notes = []; s = 0
    # claim-first: starts with a statement, not filler / a soft question
    if not low.startswith(WEAK_START) and not low.endswith("?"): s += 20
    elif low.endswith("?") and any(k in low for k in STAKES): s += 12; notes.append("question hook (ok only with stakes)")
    else: notes.append("not claim-first")
    st = sum(k in low for k in STAKES)
    s += 20 if st >= 2 else 13 if st == 1 else 0
    if st == 0: notes.append("no stakes/cost in the hook")
    sp = len(NUM.findall(low)) + (1 if ('"' in t or "“" in t or re.search(r"\bi am a?\b", low)) else 0)
    s += 20 if sp >= 2 else 14 if sp == 1 else 0
    if sp == 0: notes.append("no number/date/quote (specificity)")
    s += 15 if any(k in low for k in INTERRUPT) else 0
    s += 10 if re.search(r"\byou(r|'re|rs)?\b", low) else 0
    s += 15 if 5 <= n <= 12 else 8 if n <= 16 else 0
    if n > 12: notes.append(f"{n} words: too long to read in <2s (split: first clause on screen, rest = beat 1)")
    if low.startswith(BANNED_OPENERS): s = min(s, 40); notes.append("dealbreaker opener")
    if any(g in low for g in GUARANTEE): s = min(s, 40); notes.append("guarantee claim — not allowed")
    return min(100, s), notes

def hooks(path):
    hs = [l.strip() for l in open(path) if l.strip() and not l.startswith("#")]
    res = sorted(((score(h), h) for h in hs), key=lambda x: -x[0][0])
    for (sc, notes), h in res: print(f"{sc:5.1f}  {h}" + (f"   <- {'; '.join(notes)}" if notes else ""))
    best = res[0][0][0] if res else 0
    if len(hs) < 8: print(f"FAIL: only {len(hs)} hooks, write at least 8 from different formulas"); sys.exit(1)
    if best < 75: print("FAIL: best hook < 75 — write another round from different formulas"); sys.exit(1)
    print("HOOK OK")

def script(path):
    s = json.load(open(path)); errs = []
    hook = s["hook"]["text"]; sc, notes = score(hook)
    if sc < 75: errs.append(f"hook scores {sc} (<75): {'; '.join(notes)}")
    hw = len(hook.split())
    if hw > 12: errs.append(f"on-screen hook is {hw} words; must be readable in ~2s (<=12)")
    beats = s["beats"]
    if not 5 <= len(beats) <= 9: errs.append(f"{len(beats)} beats (want 5-9)")
    for i, b in enumerate(beats, 1):
        w = len(b["text"].split())
        if w > 24: errs.append(f"beat {i} is {w} words (<=24: one idea per shot, ~5s)")
    first = beats[0]["text"].lower()
    if any(first.startswith(x) for x in ("so ", "today", "hi", "hey", "in this")): errs.append("beat 1 wastes time — it must escalate the hook")
    allt = " ".join(b["text"].lower() for b in beats[:4])
    if not re.search(r"\b(but|and every time|that's why|here's the thing|the problem|it wasn't|not because|actually)\b", allt):
        errs.append("no turn/open loop in beats 1-4 (a 'but…'/'the problem…' that makes them stay)")
    last = beats[-1]["text"].lower()
    if not re.search(r"(comment|save|send|share|follow|link in bio|try|write|tag)", last): errs.append("last beat has no CTA / comment trigger")
    # measured audio: hook must be fully spoken inside 3 s
    cj = os.path.join(os.path.dirname(path), "clips.json")
    if os.path.exists(cj):
        c = json.load(open(cj)); hs = c.get("hook_seconds")
        if hs is not None and hs > 3.2: errs.append(f"hook takes {hs:.1f}s to say (must finish within ~3s: shorten it)")
        d = c.get("duration", 0)
        if d and not 20 <= d <= 50: errs.append(f"duration {d}s (want 20-50s)")
    if errs: print("SCRIPT FAIL:\n- " + "\n- ".join(errs)); sys.exit(1)
    print(f"SCRIPT OK  hook={sc}")

def carousel(path):
    c = json.load(open(path)); t = c["slides"][0]["title"]; sc, notes = score(t); errs = []
    if sc < 70: errs.append(f"cover slide scores {sc} (<70): {'; '.join(notes)}")
    if len(t.split()) > 9: errs.append("cover title > 9 words")
    if errs: print("CAROUSEL FAIL:\n- " + "\n- ".join(errs)); sys.exit(1)
    print(f"CAROUSEL OK  cover={sc}")

if __name__ == "__main__":
    {"hooks": hooks, "script": script, "carousel": carousel}[sys.argv[1]](sys.argv[2])
