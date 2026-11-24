#!/usr/bin/env python3
"""ManifestAI SEO blog (GitHub Pages from /docs) + Pinterest-ready RSS feed.

Write an article as blog/posts/YYYY-MM-DD-slug.md:
---
title: Affirmations That Actually Work: Why Yours Don't (and How to Fix Them)
description: 150-160 chars, contains the keyword, written for a human.
keyword: affirmations that actually work
query: woman writing affirmations in journal        # Pexels photo for hero + pin
pin_title: Affirmations that actually work            # <= 8 words, goes on the Pinterest image
---
Markdown body (## headings, paragraphs, - lists, **bold**, [links](url)). 900-1400 words.

Then: python3 tools/build_blog.py   -> rebuilds docs/ (posts, index, sitemap.xml, rss.xml, pins/*.jpg)
Site: https://vimanu9vr-create.github.io/manifestai-reels/
"""
import os, re, json, glob, html, io, sys, urllib.request, urllib.parse, datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://vimanu9vr-create.github.io/manifestai-reels"
APP = "https://daily-purpose-pilot.vimanu9-vr.workers.dev/app"
RESET = "https://daily-purpose-pilot.vimanu9-vr.workers.dev/reset/"
DOCS = os.path.join(ROOT, "docs"); POSTS = os.path.join(ROOT, "blog", "posts")
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
LIGHT = "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

CSS = """*{box-sizing:border-box}body{margin:0;font:18px/1.7 Georgia,'Lora',serif;color:#3a1620;background:#fbf4f5}
a{color:#8c2a45}header,footer{font-family:system-ui,-apple-system,'Segoe UI',sans-serif}
header{padding:18px 20px;border-bottom:1px solid #ead6db;background:#fff}header a{text-decoration:none;font-weight:700;color:#5c1f2e}
main{max-width:720px;margin:0 auto;padding:24px 20px 60px}h1{font-size:2.1rem;line-height:1.2;margin:.4em 0}
h2{font-family:system-ui,sans-serif;font-size:1.3rem;margin-top:2em}img.hero{width:100%;border-radius:14px;aspect-ratio:3/2;object-fit:cover}
.meta{font:14px system-ui,sans-serif;color:#8a6b73}.cta{background:#5c1f2e;color:#fff;border-radius:14px;padding:22px;margin:36px 0;font-family:system-ui,sans-serif}
.cta a{display:inline-block;margin-top:10px;background:#fff;color:#5c1f2e;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:700}
.card{display:block;background:#fff;border-radius:14px;padding:18px;margin:14px 0;text-decoration:none;color:inherit;border:1px solid #ead6db}
.card h3{margin:.2em 0;font-family:system-ui,sans-serif}footer{text-align:center;padding:30px;font-size:14px;color:#8a6b73}"""

def key():
    k = os.environ.get("PEXELS_API_KEY"); p = os.path.expanduser("~/.config/manifestai/pexels_key")
    if not k and os.path.exists(p): k = open(p).read().strip()
    return k

def pexels_photo(query):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": query, "orientation": "landscape", "per_page": 5})
    r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": key(), "User-Agent": UA}), timeout=30))
    p = r["photos"][0]
    data = urllib.request.urlopen(urllib.request.Request(p["src"]["large2x"], headers={"User-Agent": UA}), timeout=60).read()
    return Image.open(io.BytesIO(data)).convert("RGB"), {"id": p["id"], "url": p["url"], "by": p["photographer"]}

def fill(im, W, H):
    s = max(W / im.width, H / im.height); im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2; return im.crop((x, y, x + W, y + H))

def wrap(t, f, mw):
    out, cur = [], ""
    for w in t.split():
        c = (cur + " " + w).strip()
        if f.getlength(c) <= mw or not cur: cur = c
        else: out.append(cur); cur = w
    return out + ([cur] if cur else [])

def pin_image(bg, title, out):
    W, H = 1000, 1500
    im = ImageEnhance.Brightness(fill(bg, W, H)).enhance(0.55).convert("RGBA")
    f = ImageFont.truetype(BOLD, 84); lines = wrap(title.upper(), f, 860); lh = 100
    y = (H - lh * len(lines)) / 2 - 60
    sc = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sc).rectangle([0, y - 80, W, y + lh * len(lines) + 80], fill=(0, 0, 0, 110))
    im = Image.alpha_composite(im, sc.filter(ImageFilter.GaussianBlur(50))); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines): d.text(((W - f.getlength(l)) / 2, y + i * lh), l, font=f, fill="white")
    sf = ImageFont.truetype(LIGHT, 36); s = "ManifestAI  ·  read the guide"
    d.text(((W - sf.getlength(s)) / 2, H - 120), s, font=sf, fill=(255, 255, 255, 230))
    im.convert("RGB").save(out, quality=88)

def md(body):
    out, inlist = [], False
    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
        return s
    for line in body.strip().split("\n"):
        l = line.rstrip()
        if l.startswith("- "):
            if not inlist: out.append("<ul>"); inlist = True
            out.append(f"<li>{inline(l[2:])}</li>"); continue
        if inlist: out.append("</ul>"); inlist = False
        if l.startswith("## "): out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("### "): out.append(f"<h3>{inline(l[4:])}</h3>")
        elif l.strip(): out.append(f"<p>{inline(l)}</p>")
    if inlist: out.append("</ul>")
    return "\n".join(out)

def parse(path):
    raw = open(path).read(); m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M)); meta["body"] = m.group(2)
    base = os.path.basename(path)[:-3]; meta["date"] = base[:10]; meta["slug"] = base[11:]
    return meta

def page(title, desc, canon, body, img=None, jsonld=None):
    og = f'<meta property="og:image" content="{img}">' if img else ""
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"""<!DOCTYPE html><html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="p:domain_verify" content="a835aaa98f7c3bfddc9791f908876ead"/>
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canon}">{og}
<meta name="twitter:card" content="summary_large_image"><link rel="alternate" type="application/rss+xml" href="{SITE}/rss.xml">{ld}<style>{CSS}</style></head>
<body><header><a href="{SITE}/">ManifestAI Journal</a></header><main>{body}</main>
<footer>ManifestAI · <a href="{APP}">Try the app</a> · <a href="{SITE}/rss.xml">RSS</a></footer></body></html>"""

def build():
    os.makedirs(os.path.join(DOCS, "posts"), exist_ok=True); os.makedirs(os.path.join(DOCS, "img"), exist_ok=True)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    credits_p = os.path.join(ROOT, "blog", "images.json")
    credits = json.load(open(credits_p)) if os.path.exists(credits_p) else {}
    posts = sorted((parse(p) for p in glob.glob(os.path.join(POSTS, "*.md"))), key=lambda m: m["date"], reverse=True)
    for m in posts:
        sid = f'{m["date"]}-{m["slug"]}'; hero = os.path.join(DOCS, "img", sid + ".jpg"); pin = os.path.join(DOCS, "img", sid + "-pin.jpg")
        if not (os.path.exists(hero) and os.path.exists(pin)):
            bg, cr = pexels_photo(m.get("query", m["keyword"])); credits[sid] = cr
            fill(bg, 1200, 800).save(hero, quality=85); pin_image(bg, m.get("pin_title", m["title"]), pin)
        url = f"{SITE}/posts/{m['slug']}.html"; m["url"] = url; m["pin"] = f"{SITE}/img/{sid}-pin.jpg"
        cr = credits.get(sid, {})
        words = len(re.sub(r"[#*\-\[\]()]", " ", m["body"]).split())
        body = f"""<article><p class="meta">{m['date']} · {max(1, words // 220)} min read</p><h1>{html.escape(m['title'])}</h1>
<img class="hero" src="{SITE}/img/{sid}.jpg" alt="{html.escape(m['keyword'])}">
{md(m['body'])}
<div class="cta"><strong>Want affirmations written for your goal, not someone else's?</strong><br>
ManifestAI turns one sentence about what you want into affirmations that sound like you, plus a 5-minute daily practice.<br>
<a href="{APP}">Try ManifestAI free</a> &nbsp; <a href="{RESET}">The Seven-Day Reset workbook</a></div>
<p class="meta">Photo: <a href="{cr.get('url', 'https://www.pexels.com')}">{html.escape(cr.get('by', 'Pexels'))} on Pexels</a></p></article>"""
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": m["title"], "description": m["description"],
              "datePublished": m["date"], "image": f"{SITE}/img/{sid}.jpg", "mainEntityOfPage": url,
              "author": {"@type": "Organization", "name": "ManifestAI"}, "keywords": m["keyword"]}
        open(os.path.join(DOCS, "posts", m["slug"] + ".html"), "w").write(page(m["title"], m["description"], url, body, f"{SITE}/img/{sid}.jpg", ld))
    json.dump(credits, open(credits_p, "w"), indent=1)
    cards = "".join(f'<a class="card" href="{m["url"]}"><span class="meta">{m["date"]}</span><h3>{html.escape(m["title"])}</h3><p>{html.escape(m["description"])}</p></a>' for m in posts)
    idx = f"<h1>ManifestAI Journal</h1><p>Affirmations that sound like you, manifestation methods explained honestly, and small daily practices that actually stick.</p>{cards}"
    open(os.path.join(DOCS, "index.html"), "w").write(page("ManifestAI Journal: affirmations and manifestation, explained honestly",
        "Affirmations that actually work, manifestation techniques explained honestly, and 5-minute daily practices from ManifestAI.", SITE + "/", idx))
    sm = "".join(f"<url><loc>{m['url']}</loc><lastmod>{m['date']}</lastmod></url>" for m in posts)
    open(os.path.join(DOCS, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}/</loc></url>{sm}</urlset>')
    open(os.path.join(DOCS, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    def rfc(d): return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 06:00:00 +0530")
    items = "".join(f"""<item><title>{html.escape(m['title'])}</title><link>{m['url']}</link><guid>{m['url']}</guid><pubDate>{rfc(m['date'])}</pubDate>
<description>{html.escape(m['description'])}</description><enclosure url="{m['pin']}" type="image/jpeg" length="0"/><media:content url="{m['pin']}" medium="image"/></item>""" for m in posts[:30])
    open(os.path.join(DOCS, "rss.xml"), "w").write(f"""<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel>
<title>ManifestAI Journal</title><link>{SITE}/</link><description>Affirmations and manifestation, explained honestly.</description><language>en-in</language>{items}</channel></rss>""")
    print(json.dumps([{"title": m["title"], "url": m["url"], "pin": m["pin"]} for m in posts[:5]], indent=1))

if __name__ == "__main__":
    build()
