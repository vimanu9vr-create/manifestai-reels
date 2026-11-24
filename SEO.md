# SEO rules — every post

Search on both apps matches the words people type against your caption / title / description, the text on screen,
and what is spoken (both apps transcribe audio). So the keyword must appear in the words AND in the video.

## 1. Pick ONE primary keyword per post (from the bank below) + 1–2 secondary keywords
- Rotate clusters; don't use the same primary keyword two posts running. Log it in `log.json` as `"keyword"`.
- The hook may stay emotional, but the primary keyword must be SPOKEN in the first 2 beats and appear in on-screen text at least once
  (carousel: on slide 1 or 2).

## 2. Instagram caption (reels + carousels)
- First line (first ~125 chars, shown before "more"): contains the primary keyword, written as a natural sentence, not a list.
- Body: 1–2 secondary keywords used naturally. No keyword stuffing, no list of keywords.
- **Exactly 3–5 hashtags, never more** (Instagram capped posts/Reels at 5 in Dec 2025; more can suppress reach).
  Mix: 1 broad (#affirmations / #manifestation), 2–3 niche matching the topic (#moneyaffirmations, #369method …), 1 brand (#manifestai).
  Put them at the end of the caption, not in a comment.

## 3. YouTube Shorts
- Title: primary keyword at the START, ≤ 70 chars, ends with `#shorts`. e.g. `Affirmations That Actually Work (Why Yours Don't) #shorts`
- Description: first sentence repeats the primary keyword; 120–250 words total in plain sentences explaining the idea;
  secondary keywords used naturally; app link; then 2–3 hashtags on the last line (#shorts #affirmations #manifestation).
- Tags: 5–10 — the primary + secondary keywords and close variants/misspellings ("manifest", "manifesting", "affirmation").
  Tags matter little; the title, description and spoken words matter most.

## 4. Keyword bank (refresh with research; seasonal first)
Seasonal now (Dec–Jan): `vision board 2027`, `manifest 2027`, `new year affirmations`, `2027 goals`, `new year manifestation`.

| cluster | primary keywords | niche hashtags |
|---|---|---|
| affirmations (highest volume) | affirmations, daily affirmations, positive affirmations, affirmations that actually work, why affirmations don't work | #affirmations #dailyaffirmations #positiveaffirmations |
| money | money affirmations, abundance affirmations, manifest money, wealth mindset | #moneyaffirmations #abundancemindset #manifestmoney |
| self-love / confidence | self love affirmations, confidence affirmations, mirror affirmations (rising) | #selflove #confidence #mirrorwork |
| love | love affirmations, manifest love, manifest a relationship | #loveaffirmations #manifestlove |
| career | manifest dream job, career affirmations, affirmations for success | #careergoals #successmindset |
| methods | how to manifest, manifestation techniques, 369 method, 55x5 method, scripting manifestation, future self journaling | #369method #scripting #manifestationtips |
| law of attraction | law of attraction, manifestation for beginners, manifesting tips | #lawofattraction #manifestation #manifesting |
| sleep / night | sleep affirmations, night affirmations, affirmations before bed | #sleepaffirmations #nightroutine |
| habits | 21 day challenge, morning routine affirmations, consistency | #21daychallenge #morningroutine |
| app | manifestation app, affirmation app, AI affirmations | #manifestai #manifestationapp |

## 5. Check before posting
`python3 tools/seo_check.py daily/YYYY-MM-DD/<slot>/post.json` must print OK (it checks hashtag count, keyword placement,
title length/#shorts, description length). Fix and re-run until it passes.
post.json must include `"keyword"` and `"secondary_keywords"`.
