# SEO blog + Pinterest agent (daily)

Site: https://vimanu9vr-create.github.io/manifestai-reels/ (GitHub Pages from `/docs` on main).
Pinterest: the owner connects `https://vimanu9vr-create.github.io/manifestai-reels/rss.xml` in Pinterest → Settings → Bulk create Pins
→ Auto-publish (RSS). Every new article's 1000×1500 pin image is published automatically. Nothing else to do for Pinterest.
Audience: India first (Indian English, ₹ amounts, Indian examples — salary in lakh, exams, family, Bengaluru/Mumbai jobs) while staying readable worldwide.

## Each run
1. Read `SEO.md` (keyword bank) and `blog/posts/` (what's already written). Pick ONE primary keyword not yet covered, seasonal first
   (Dec–Jan: vision board 2027, new year affirmations, manifest 2027). Prefer long-tail, question-style keywords people actually type
   ("how to manifest a job", "affirmations for exam success", "369 method explained", "money affirmations that work").
2. Web research (3–6 searches): what currently ranks for it, what questions people ask (People Also Ask, Reddit), what's missing.
   Write something better and more honest. Never copy text. Never invent studies, statistics, quotes or testimonials;
   if you cite research, describe it generally or link a real source you opened.
3. Write `blog/posts/YYYY-MM-DD-<slug>.md` (format in the header of tools/build_blog.py):
   - title ≤ 65 chars with the keyword near the start; description 140–160 chars with the keyword; slug = keyword-ish, short.
   - 900–1400 words: intro that names the reader's problem, 4–6 `##` sections, a before→after or step list, a "How ManifestAI helps"
     section (honest, brand facts only — see manifestai-daily-reel skill / DAILY.md), and `## Frequently asked questions` with 3 `###` questions.
   - keyword in the first 100 words, one `##` heading, and naturally 3–6 times total; 2–3 secondary keywords.
   - Link to 1–2 earlier posts (internal links) when relevant.
   - No guaranteed outcomes, no medical/financial promises.
4. `python3 tools/build_blog.py` (needs PEXELS_API_KEY) → rebuilds docs/, sitemap.xml, rss.xml, pin image. Open the new pin jpg and check it.
5. Commit + push. Log to `log.json`: `{date, slot:"blog", type:"blog", keyword, url}`.
6. Summary to owner: title, keyword, URL.
