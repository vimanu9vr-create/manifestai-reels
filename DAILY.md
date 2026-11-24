# Daily ManifestAI content — runbook

Three posts a day, each made by its own scheduled run. Every run is told its SLOT:

| slot | goes live (IST) | what | where | folder |
|---|---|---|---|---|
| `reel-1` | ~8:30 AM | story-voice reel | Instagram Reels + YouTube Shorts | `daily/YYYY-MM-DD/reel-1/` |
| `carousel` | ~1:00 PM | 6–10 slide carousel | Instagram only | `daily/YYYY-MM-DD/carousel/` |
| `reel-2` | ~7:30 PM | story-voice reel, DIFFERENT angle | Instagram Reels + YouTube Shorts | `daily/YYYY-MM-DD/reel-2/` |

Instagram account: @try_manifestation, page id 17841438571126703 ("ManifestAI | Manifestation App" — never the personal account).
If `log.json` already has an entry with today's date AND this slot, stop: it is already posted.
Variety rule: read today's and yesterday's log entries first. Never reuse a hook family, topic or CTA from the last 3 posts.
Reel 2 must differ from reel 1 in angle (e.g. reel 1 = generic-affirmation problem, reel 2 = a specific goal like a job, money in ₹, confidence, consistency/day-4 quitting, a 55x5 / scripting / future-self technique done properly).
The carousel should be save-worthy: a list, a framework, a before→after rewrite, a "5 X that…" — teach something, end with the app.
Style: matches the user's "story-voice" reels — one Pexels clip per line, bold uppercase white hook, one white caption
sentence per shot, Kokoro `af_heart` narration reading every line, ~35–50 s.

## 0. Setup (fresh machine)
```
pip install --break-system-packages -q kokoro-onnx soundfile
git config user.name "ManifestAI reels bot"; git config user.email "reels-bot@users.noreply.github.com"
```
`tools/build_story.py` downloads the Kokoro model from GitHub releases on first run. It needs `PEXELS_API_KEY` in the env.

## 1. Learn from what already ran
- Read `log.json` (every past post, its hook, format, CTA, clips).
- Pull the last 7 Instagram posts (Zapier "Instagram for Business → New Media", account above): likes + comments per post.
- Pull YouTube stats for the logged `youtube_id`s (Zapier YouTube find_video / get_report) where available.
- Note which hook family / CTA / topic did best. **Early on ignore raw views; compare against the account's own median.**
- Never repeat yesterday's CTA. Never reuse a Pexels clip id already in `log.json` (the builder enforces this).

## 2. Research (mandatory, web search, last 7 → 30 days first)
Several varied queries: Reels/Shorts ranking signals now; manifestation / affirmation / future-self formats trending;
what manifestation audiences complain about (Reddit, comments); saturated angles; one adjacent viral format worth adapting.
Honesty: you cannot see other accounts' view counts. Never state a view count, trend name or statistic you didn't verify.

## 3. Write
- 6–10 hooks, score them (claim-first, stakes in the hook, a concrete number/date/thing), pick the winner.
  Never open with "stop scrolling". Hook on screen ≤ ~9 words.
- Script = hook + 5–8 beats, each one or two short sentences (≤ ~20 words). Every line is narrated AND shown.
- The emotion must BE the app's argument: build the problem (generic affirmations aren't yours → you quit by day 2–4),
  and the app is the answer (ManifestAI writes your affirmations from the one sentence you type about your own goal).
- Each beat's `query` describes what is VISIBLE (e.g. "hand writing in notebook close up"), never the meaning.
- Brand facts only: personalised affirmations from one typed goal, 5-minute daily practice (breathe · intention · one action),
  21-day journey, vision boards, sleep tracks, meditations, journal, habits & streaks, AI coach.
  India prices if mentioned: ₹99/week, ₹249/month, ₹999/year. Never claim affirmations cause money/jobs/houses.
  No fake testimonials, user counts, results or guarantees. No URL on screen ("link in bio").
- Write `daily/YYYY-MM-DD/<slot>/script.json` and `daily/YYYY-MM-DD/<slot>/post.json`
  (`instagram_caption` ≤2200 chars with 8–12 hashtags, `youtube_title` ≤100 chars incl. #shorts, `youtube_description`, `youtube_tags`).

## 4. Build + QC
```
python3 tools/build_story.py daily/YYYY-MM-DD/<slot>/script.json
```
Open `daily/YYYY-MM-DD/<slot>/_build/contact.jpg` and LOOK at it: captions readable on every shot, footage matches the line,
nothing off-topic (wrong gender/age is fine, wrong mood or weird content is not), hook frame works with sound off.
If a clip is wrong, change that beat's `query`, delete `_build/raw0N.mp4` and its entry in `clips.json`, rebuild.
ffprobe: 1080x1920, 30 fps, h264 + aac, 20–60 s. If QC fails twice, do NOT post — report instead.

## 5. Publish
1. Commit + push the day folder. Video URL = `https://raw.githubusercontent.com/vimanu9vr-create/manifestai-reels/<commit sha>/daily/YYYY-MM-DD/<slot>/<name>.mp4` — curl -I it, expect 200.
2. Instagram: Zapier `instagram_for_business_publish_video` with instagramPageId 17841438571126703, video URL, caption.
   If it returns "Video is still processing", wait 3 min, then check "New Media" — only retry if today's post is NOT there (no duplicates).
3. YouTube: Zapier `youtube_upload_video`, privacy_status public, made_for_kids false, notify_subscribers true, tags, default_language en.
4. Append to `log.json` (date, slot, type, folder, hook, format, cta, duration, instagram_media_id, youtube_id, clips) and push.

## 5b. Carousel slot (instead of steps 4–5)
Write `daily/YYYY-MM-DD/carousel/carousel.json` (see header of `tools/build_carousel.py`): slide 1 = hook (≤8 words),
middle slides = one idea each (title ≤6 words + body ≤25 words), last slide = app CTA. No emoji in slide text (the font can't draw them; captions can have emoji).
`python3 tools/build_carousel.py daily/YYYY-MM-DD/carousel/carousel.json` → look at `_build/contact.jpg` (readable? photo fits the line?).
Commit, push, then Zapier `instagram_for_business_publish_photo_s` with `media` = list of raw.githubusercontent URLs (pinned to the commit SHA, in slide order) and the caption.
Log it with `"slot": "carousel"`, `"type": "carousel"`, and `"photos"` from clips.json (the builder avoids reusing photo ids).

## 6. Report
Send the user a short summary: hook, what yesterday's numbers suggested, links to both posts, anything that failed.
Remind them (once a week, not daily) that adding a trending sound in the Instagram app boosts reach.
