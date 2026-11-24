#!/usr/bin/env python3
"""Validate a post.json against SEO.md. Exit 1 with reasons if it fails.
post.json keys: keyword, secondary_keywords, instagram_caption, [youtube_title, youtube_description, youtube_tags] (reels only)
Optional: pass the script.json / carousel.json as 2nd arg to check the keyword is spoken/shown."""
import json, re, sys

def norm(s): return re.sub(r"[^a-z0-9 ]+", " ", s.lower())

def main():
    p = json.load(open(sys.argv[1])); errs = []
    kw = p.get("keyword", "").strip()
    if not kw: errs.append("missing 'keyword'")
    cap = p.get("instagram_caption", "")
    tags = re.findall(r"#\w+", cap)
    if not 3 <= len(tags) <= 5: errs.append(f"instagram caption has {len(tags)} hashtags (need 3-5)")
    if kw and norm(kw) not in norm(cap[:140]): errs.append(f"keyword '{kw}' not in first ~125 chars of the caption")
    if len(cap) > 2200: errs.append("caption over 2200 chars")
    if "youtube_title" in p:
        t = p["youtube_title"]
        if len(t) > 100: errs.append("youtube title over 100 chars")
        if "#shorts" not in t.lower(): errs.append("youtube title missing #shorts")
        if kw and norm(kw) not in norm(t[:len(kw) + 25]): errs.append(f"keyword '{kw}' not at the start of the youtube title")
        d = p.get("youtube_description", "")
        if kw and norm(kw) not in norm(d.split("\n")[0]): errs.append("keyword not in first line of youtube description")
        if len(d.split()) < 100: errs.append(f"youtube description only {len(d.split())} words (need 120+)")
        if not 5 <= len(p.get("youtube_tags", [])) <= 15: errs.append("need 5-15 youtube tags")
    if len(sys.argv) > 2 and kw:
        s = json.load(open(sys.argv[2]))
        if "beats" in s:
            early = " ".join([s["hook"]["text"]] + [b["text"] for b in s["beats"][:2]])
            if norm(kw) not in norm(early): errs.append(f"keyword '{kw}' not spoken in hook or first 2 beats")
        elif "slides" in s:
            early = " ".join(x.get("title", "") + " " + x.get("body", "") for x in s["slides"][:2])
            if norm(kw) not in norm(early): errs.append(f"keyword '{kw}' not on slide 1 or 2")
    if errs:
        print("SEO FAIL:\n- " + "\n- ".join(errs)); sys.exit(1)
    print("SEO OK", kw, f"({len(tags)} hashtags)")

if __name__ == "__main__":
    main()
