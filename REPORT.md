# Weekly growth report (Mondays)

Goal: tell the owner in 2 minutes what worked last week and change next week's plan accordingly. India-first account.

## Data (last 7 days, plus the 7 before for comparison)
- `log.json`: every post (slot, type, hook, keyword, cta, format, ids), blog posts.
- Instagram (Zapier Instagram for Business, page 17841438571126703): "New Media" for recent posts → like_count, comments_count per post.
  Account info via `_zap_raw_request` GET `https://graph.facebook.com/v21.0/17841438571126703?fields=followers_count,media_count`.
  Reach/views/saves/shares are NOT available (no insights permission) — say so; ask the owner to paste Insights numbers if they want them included.
- YouTube: `_zap_raw_request` GET `https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id=<comma-separated ids>` → views, likes, comments.
  Channel: GET `.../channels?part=statistics&mine=true` → subscribers.
- `replies.json`: comments received/answered, leads.

## Analysis
- Rank posts by YouTube views and by Instagram (likes + 3×comments). Compare to the account's own median, not to viral accounts.
- Group by hook family, keyword cluster, CTA, slot (reel-1 vs reel-2 vs carousel), length. What's consistently above median?
- Read the comments: what goals/affirmations do people share most? That's next week's topics.
- Be honest about small numbers: with low counts, call patterns "early signals", not conclusions.

## Output
1. `reports/YYYY-Www.md` (commit + push) with: headline numbers + change vs last week; top 3 / bottom 3 posts and why;
   what to do more / less; next week's 7 topics + primary keywords; any experiments (e.g. different posting time, shorter reels).
2. Update the "Keyword bank" order in `SEO.md` and add a short "## What's working (updated YYYY-MM-DD)" section at the top of `DAILY.md`
   (≤ 8 bullets, replace the previous one) so the daily agents use the learnings. Commit + push.
3. Send the owner the summary (≤ 12 lines) + the report path.
