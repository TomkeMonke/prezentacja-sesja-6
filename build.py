"""Builds index.html (standalone slide viewer) from slides/*.html. Run: python build.py"""
import json, re, pathlib
ROOT = pathlib.Path(__file__).parent
deck = json.loads((ROOT / "slides/deck.json").read_text(encoding="utf-8"))
BLOBS = {
    "914f75d159a66e994b866b9005892664": "img/drillr-plan.png",
    "4a8ff09435aa02f2fcb1762d2e8a6fc1": "img/drillr-position.png",
    "f2b45868fc673ebb43244092a0ca1938": "img/drillr-exercise.png",
    "7c1e0b2a9d4f4e6b8a3c5d1f2e9b0a47": "img/qr-linkedin.png",
    "d4f14e91f5f42fd0c2bcc8ca5db09ee7": "img/ja.jpg",
    "abf0a430c55f6d9b15dae38c96bca0c8": "img/tadroid-lyon.jpg",
    "a843a74544b34e00cac06913c378607f": "img/squirrel-killer.png",
    "8285265882f153b2e265f691b2c38173": "img/hackathon-team.jpg",
}
ICONS = {
    "GraduationCap": '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
    "Users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "Wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "Lightning": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
}
def icon(m):
    name, style = m.group(1), m.group(2)
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" style="{style};flex:none">{ICONS[name]}</svg>')
slides, notes = [], []
for sid in deck["order"]:
    html = (ROOT / f"slides/{sid}.html").read_text(encoding="utf-8")
    for blob, path in BLOBS.items():
        html = html.replace(f"/_blob/{blob}", path)
    html = re.sub(r'<x-icon name="(\w+)" style="([^"]*)"></x-icon>', icon, html)
    m = re.search(r"<aside>(.*?)</aside>", html, re.S)
    notes.append(m.group(1).strip() if m else "")
    slides.append(re.sub(r"<aside>.*?</aside>", "", html, flags=re.S))
fonts = "".join(f'<link rel="stylesheet" href="{f["href"]}">' for f in deck["faces"].values())
page = f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{deck["title"]}</title>{fonts}
<style>
*{{box-sizing:border-box}} html,body{{margin:0;height:100%;background:#0b0e13;overflow:hidden;font-family:Rubik,Arial,sans-serif}}
h1,h2,h3,p{{margin:0}} img{{display:block}}
#stage{{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:center}}
#stage>section{{position:absolute;inset:0;width:1920px;height:1080px}}
#stage>section:not(.on){{visibility:hidden}}
#bar{{position:fixed;left:0;right:0;bottom:0;display:flex;gap:12px;align-items:center;justify-content:center;padding:10px;color:#a9b1bd;font-size:14px;background:#0b0e13cc}}
#bar button{{background:#1f2530;color:#f4f1ea;border:0;border-radius:6px;padding:6px 14px;font:inherit;cursor:pointer}}
#notes{{position:fixed;left:0;right:0;bottom:48px;max-height:30%;overflow:auto;padding:16px 24px;background:#12161dee;color:#f4f1ea;font-size:18px;line-height:1.5;display:none}}
</style></head><body>
<div id="stage">{"".join(slides)}</div>
<div id="notes"></div>
<div id="bar"><button id="prev">&larr;</button><span id="count"></span><button id="next">&rarr;</button><button id="nb">Notatki (N)</button><span>Pełny ekran: F</span></div>
<script>
const NOTES={json.dumps(notes, ensure_ascii=False)};
const S=[...document.querySelectorAll('#stage>section')];let i=Math.max(0,Math.min(S.length-1,(parseInt(location.hash.slice(1))||1)-1));
const stage=document.getElementById('stage'),nt=document.getElementById('notes');
function fit(){{const s=Math.min(innerWidth/1920,innerHeight/1080);stage.style.transform=`translate(-50%,-50%) scale(${{s}})`}}
function show(){{S.forEach((s,k)=>s.classList.toggle('on',k===i));document.getElementById('count').textContent=(i+1)+' / '+S.length;nt.textContent=NOTES[i];history.replaceState(null,'','#'+(i+1))}}
function go(d){{i=Math.max(0,Math.min(S.length-1,i+d));show()}}
addEventListener('keydown',e=>{{if(['ArrowRight','PageDown',' '].includes(e.key))go(1);else if(['ArrowLeft','PageUp'].includes(e.key))go(-1);else if(e.key==='n'||e.key==='N')nt.style.display=nt.style.display==='block'?'none':'block';else if(e.key==='f'||e.key==='F')(document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen())}});
document.getElementById('prev').onclick=()=>go(-1);document.getElementById('next').onclick=()=>go(1);
document.getElementById('nb').onclick=()=>nt.style.display=nt.style.display==='block'?'none':'block';
stage.onclick=()=>go(1);addEventListener('resize',fit);fit();show();
</script></body></html>"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
md = ["# Notatki do slajdów\n"]
for k, (sid, n) in enumerate(zip(deck["order"], notes), 1):
    md.append(f"## {k}. {sid}\n\n{n}\n")
(ROOT / "notatki.md").write_text("\n".join(md), encoding="utf-8")
print("ok", len(slides), "slides")
