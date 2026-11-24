#!/usr/bin/env python3
"""ManifestAI story-voice reel: Pexels b-roll per beat + Kokoro (af_heart) narration + bold white captions.

Usage:
  python3 tools/build_story.py daily/YYYY-MM-DD/script.json            # fetch footage from Pexels + render
  python3 tools/build_story.py daily/YYYY-MM-DD/script.json --offline  # placeholder footage (layout/voice test)

script.json:
{
  "name": "ManifestAI_2026-11-25",
  "hook":  {"text": "YOUR FIRST MILLION, AS ONE SENTENCE.", "query": "city apartment window morning"},
  "beats": [{"text": "It's one sentence, said the same way...", "query": "clouds over city timelapse"}, ...]
}
Every beat's line is both narrated and shown on screen. "query" describes what is VISIBLE, never the meaning.
Env: PEXELS_API_KEY (or ~/.config/manifestai/pexels_key), KOKORO_DIR (default ~/manifestai-models).
"""
import json, os, sys, subprocess, random, urllib.request, urllib.parse
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
SEMI = "/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf"
if not os.path.exists(SEMI): SEMI = BOLD
KOKORO_DIR = os.environ.get("KOKORO_DIR", os.path.expanduser("~/manifestai-models"))
VOICE, SPEED, PAD = "af_heart", 1.0, 0.45   # PAD = silence after each line (s)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

def sh(*a): subprocess.run(a, check=True)

def ensure_kokoro():
    os.makedirs(KOKORO_DIR, exist_ok=True)
    base = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        p = os.path.join(KOKORO_DIR, f)
        if not os.path.exists(p) or os.path.getsize(p) < 1_000_000:
            sh("curl", "-sL", "-o", p, base + f)
    from kokoro_onnx import Kokoro
    return Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"), os.path.join(KOKORO_DIR, "voices-v1.0.bin"))

def tts_text(s):
    # say "55x5" naturally; strip on-screen-only punctuation
    return s.replace("55x5", "fifty-five by five").replace("ManifestAI", "Manifest A.I.").replace("₹", "rupees ")

def pexels_key():
    k = os.environ.get("PEXELS_API_KEY")
    if not k:
        p = os.path.expanduser("~/.config/manifestai/pexels_key")
        if os.path.exists(p): k = open(p).read().strip()
    if not k: sys.exit("No Pexels key: set PEXELS_API_KEY")
    return k

def pexels_clip(query, need_s, used, out):
    key = pexels_key()
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "orientation": "portrait", "per_page": 15, "size": "medium"})
    req = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": UA})
    vids = json.load(urllib.request.urlopen(req, timeout=30)).get("videos", [])
    cands = [v for v in vids if v["id"] not in used and v["duration"] >= min(need_s, 6) and v["height"] > v["width"]]
    if not cands: cands = [v for v in vids if v["id"] not in used]
    if not cands: raise RuntimeError(f"no Pexels result for '{query}'")
    v = cands[0]
    files = sorted([f for f in v["video_files"] if f.get("height") and f["height"] >= 1280 and f["height"] > f["width"]],
                   key=lambda f: abs(f["height"] - 1920)) or sorted(v["video_files"], key=lambda f: -(f.get("height") or 0))
    req = urllib.request.Request(files[0]["link"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as fh: fh.write(r.read())
    used.add(v["id"])
    return {"id": v["id"], "url": v["url"], "by": v["user"]["name"], "query": query}

def placeholder_clip(i, out, dur):
    hues = ["0x2b2a33", "0x3a3029", "0x1f2a30", "0x332629", "0x2d3326", "0x2a2433"]
    sh("ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
       f"color=c={hues[i % len(hues)]}:s={W}x{H}:d={dur + 1}:r={FPS},noise=alls=12:allf=t", "-c:v", "libx264", "-pix_fmt", "yuv420p", out)

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

def caption_png(text, hook, out):
    """White bold text with soft shadow. Hook: uppercase, bigger, upper third. Lines: centred mid-frame."""
    size = 78 if hook else 50
    f = ImageFont.truetype(BOLD if hook else SEMI, size)
    t = text.upper() if hook else text
    lines = wrap(t, f, 860 if hook else 840)
    lh = size * 1.2
    cy = 640 if hook else 860            # inside the safe band, clear of IG UI
    y0 = cy - lh * len(lines) / 2
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
    for k, s in enumerate(lines):
        x = (W - f.getlength(s)) / 2
        d.text((x, y0 + k * lh), s, font=f, fill=(255, 255, 255, 255))
    sh_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh_)
    for k, s in enumerate(lines):
        x = (W - f.getlength(s)) / 2
        ds.text((x + 2, y0 + k * lh + 3), s, font=f, fill=(0, 0, 0, 200))
    sh_ = sh_.filter(ImageFilter.GaussianBlur(6))
    Image.alpha_composite(sh_, txt).save(out)

def main():
    spath = sys.argv[1]; offline = "--offline" in sys.argv
    sc = json.load(open(spath)); wd = os.path.dirname(os.path.abspath(spath))
    tmp = os.path.join(wd, "_build"); os.makedirs(tmp, exist_ok=True)
    beats = [dict(sc["hook"], hook=True)] + [dict(b, hook=False) for b in sc["beats"]]
    k = ensure_kokoro()
    used = set()
    logp = os.path.join(ROOT, "log.json")
    if os.path.exists(logp):
        for e in json.load(open(logp)): used.update(c["id"] for c in e.get("clips", []))
    credits, segs, voice = [], [], []
    for i, b in enumerate(beats):
        a, sr = k.create(tts_text(b["text"]), voice=VOICE, speed=SPEED, lang="en-us")
        a = np.concatenate([np.zeros(int(0.12 * sr)), a, np.zeros(int(PAD * sr))])
        dur = len(a) / sr; voice.append(a)
        raw = os.path.join(tmp, f"raw{i:02d}.mp4")
        if offline: placeholder_clip(i, raw, dur)
        else: credits.append(pexels_clip(b["query"], dur, used, raw))
        png = os.path.join(tmp, f"cap{i:02d}.png"); caption_png(b["text"], b["hook"], png)
        seg = os.path.join(tmp, f"seg{i:02d}.mp4")
        # fill 9:16, slow push-in so frame 0 is already moving, slight darken for text legibility
        # fill 9:16 with 10% headroom and drift slowly so frame 0 is already moving; slight darken for legibility
        vf = (f"[0:v]fps={FPS},scale={int(W*1.1)}:{int(H*1.1)}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H}:x='(iw-ow)/2':y='(ih-oh)*(0.15+0.7*t/{dur:.2f})',"
              f"eq=brightness=-0.06:saturation=0.9[v];[v][1:v]overlay=0:0,format=yuv420p")
        sh("ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-loop", "1", "-i", png, "-filter_complex", vf,
           "-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", seg)
        segs.append(seg)
    sr = 24000
    sf.write(os.path.join(tmp, "voice.wav"), np.concatenate(voice), sr)
    with open(os.path.join(tmp, "list.txt"), "w") as fh:
        for s in segs: fh.write(f"file '{s}'\n")
    out = os.path.join(wd, sc["name"] + ".mp4")
    sh("ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "list.txt"),
       "-i", os.path.join(tmp, "voice.wav"), "-map", "0:v", "-map", "1:a",
       "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "veryfast", "-profile:v", "main",
       "-level", "4.0", "-pix_fmt", "yuv420p", "-g", "60", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
       "-shortest", "-movflags", "+faststart", out)
    # cover from the hook beat, contact sheet for QC
    sh("ffmpeg", "-loglevel", "error", "-y", "-ss", "1.0", "-i", out, "-frames:v", "1", "-q:v", "2",
       os.path.join(wd, sc["name"] + "_Cover.jpg"))
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
    sh("ffmpeg", "-loglevel", "error", "-y", "-i", out, "-vf", f"fps=12/{dur:.2f},scale=270:480,tile=6x2",
       "-frames:v", "1", os.path.join(tmp, "contact.jpg"))
    json.dump({"clips": credits, "duration": round(dur, 2)}, open(os.path.join(wd, "clips.json"), "w"), indent=1)
    print(json.dumps({"video": out, "duration": round(dur, 2), "clips": credits}, indent=1))

if __name__ == "__main__":
    main()
