#!/usr/bin/env python3
"""ManifestAI Instagram carousel: 1080x1350 slides, Pexels photo backgrounds, dark scrim, bold white text.

Usage: python3 tools/build_carousel.py daily/YYYY-MM-DD/carousel/carousel.json
carousel.json:
{
  "name": "ManifestAI_2026-11-24_Carousel",
  "slides": [
    {"title": "5 affirmations that are secretly lies", "query": "woman journaling by window"},           # slide 1 = hook (big)
    {"title": "\"I am a millionaire\"", "body": "Your brain checks your bank app and says no.", "query": "empty wallet on table"},
    ...
    {"title": "Want yours written for your goal?", "body": "ManifestAI — link in bio", "query": "sunrise", "cta": true}
  ]
}
3–10 slides. "query" describes what is VISIBLE. Writes slide_01.jpg ... and clips.json (Pexels photo credits).
"""
import json, os, sys, urllib.request, urllib.parse, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1080, 1350
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
SEMI = "/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf"
if not os.path.exists(SEMI): SEMI = BOLD
LIGHT = "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def key():
    k = os.environ.get("PEXELS_API_KEY")
    p = os.path.expanduser("~/.config/manifestai/pexels_key")
    if not k and os.path.exists(p): k = open(p).read().strip()
    if not k: sys.exit("No Pexels key: set PEXELS_API_KEY")
    return k

def photo(query, used):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode({"query": query, "orientation": "portrait", "per_page": 15})
    r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": key(), "User-Agent": UA}), timeout=30))
    c = [p for p in r.get("photos", []) if p["id"] not in used] or r.get("photos", [])
    if not c: raise RuntimeError(f"no Pexels photo for '{query}'")
    p = c[0]; used.add(p["id"])
    src = p["src"].get("large2x") or p["src"]["original"]
    data = urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": UA}), timeout=60).read()
    return Image.open(io.BytesIO(data)).convert("RGB"), {"id": p["id"], "url": p["url"], "by": p["photographer"], "query": query}

def fill(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))

def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    if len(lines) > 1 and len(lines[-1].split()) == 1 and len(lines[-2].split()) > 2:
        p = lines[-2].split(); lines[-2] = " ".join(p[:-1]); lines[-1] = p[-1] + " " + lines[-1]
    return lines

def clean(t):
    # the font has no emoji / arrows: keep Latin text and common typography only
    return "".join(ch for ch in t if ord(ch) < 0x2000 or ch in "‘’“”—–…₹").strip()

def slide(bg, s, idx, total, out):
    s = dict(s, title=clean(s["title"]), body=clean(s.get("body", "")))
    im = ImageEnhance.Brightness(fill(bg)).enhance(0.62)
    im = ImageEnhance.Color(im).enhance(0.85).convert("RGBA")
    hook = idx == 0
    tf = ImageFont.truetype(BOLD, 92 if hook else 70)
    bf = ImageFont.truetype(SEMI, 46)
    title = s["title"].upper() if hook else s["title"]
    tl = wrap(title, tf, 900); bl = wrap(s.get("body", ""), bf, 880) if s.get("body") else []
    th, bh = tf.size * 1.18, bf.size * 1.32
    block = len(tl) * th + (40 + len(bl) * bh if bl else 0)
    y = (H - block) / 2 - (30 if hook else 0)
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(scrim).rectangle([0, y - 90, W, y + block + 90], fill=(0, 0, 0, 110))
    im = Image.alpha_composite(im, scrim.filter(ImageFilter.GaussianBlur(60)))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
    shd = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(shd)
    yy = y
    for line in tl:
        x = (W - tf.getlength(line)) / 2
        ds.text((x + 2, yy + 3), line, font=tf, fill=(0, 0, 0, 190)); d.text((x, yy), line, font=tf, fill=(255, 255, 255, 255)); yy += th
    if bl:
        yy += 40
        for line in bl:
            x = (W - bf.getlength(line)) / 2
            ds.text((x + 2, yy + 3), line, font=bf, fill=(0, 0, 0, 190)); d.text((x, yy), line, font=bf, fill=(250, 240, 240, 255)); yy += bh
    im = Image.alpha_composite(im, shd.filter(ImageFilter.GaussianBlur(5))); im = Image.alpha_composite(im, txt)
    d = ImageDraw.Draw(im); sf = ImageFont.truetype(LIGHT, 30)
    if hook:
        lab = "swipe"; lw = sf.getlength(lab); x0 = (W - lw - 50) / 2; yb = H - 110
        d.text((x0, yb), lab, font=sf, fill=(255, 255, 255, 230))
        ax = x0 + lw + 14; ay = yb + 21
        d.line([(ax, ay), (ax + 34, ay)], fill=(255, 255, 255, 230), width=3)
        d.polygon([(ax + 36, ay), (ax + 24, ay - 8), (ax + 24, ay + 8)], fill=(255, 255, 255, 230))
    pg = f"{idx + 1}/{total}"; d.text((W - 60 - sf.getlength(pg), 50), pg, font=sf, fill=(255, 255, 255, 200))
    d.text((60, 50), "ManifestAI", font=sf, fill=(255, 255, 255, 200))
    im.convert("RGB").save(out, quality=92)

def main():
    p = sys.argv[1]; c = json.load(open(p)); wd = os.path.dirname(os.path.abspath(p))
    used = set()
    logp = os.path.join(ROOT, "log.json")
    if os.path.exists(logp):
        for e in json.load(open(logp)): used.update(x["id"] for x in e.get("photos", []))
    credits, outs = [], []
    n = len(c["slides"])
    assert 3 <= n <= 10, "carousel needs 3-10 slides"
    for i, s in enumerate(c["slides"]):
        bg, cr = photo(s["query"], used); credits.append(cr)
        o = os.path.join(wd, f"slide_{i + 1:02d}.jpg"); slide(bg, s, i, n, o); outs.append(o)
    thumbs = [Image.open(o).resize((216, 270)) for o in outs]
    sheet = Image.new("RGB", (216 * min(n, 5), 270 * ((n + 4) // 5)), "white")
    for i, t in enumerate(thumbs): sheet.paste(t, ((i % 5) * 216, (i // 5) * 270))
    os.makedirs(os.path.join(wd, "_build"), exist_ok=True); sheet.save(os.path.join(wd, "_build", "contact.jpg"))
    json.dump({"photos": credits, "slides": [os.path.basename(o) for o in outs]}, open(os.path.join(wd, "clips.json"), "w"), indent=1)
    print(json.dumps({"slides": outs, "photos": credits}, indent=1))

if __name__ == "__main__":
    main()
