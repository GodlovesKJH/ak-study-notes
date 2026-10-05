"""학습노트 빌드: notes/NN.md -> lectures/NN.html, index.html
사용법: python3 build.py   (pip install markdown 필요)"""
import re, glob, os, html, markdown

TOTAL = 12
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;600&display=swap" rel="stylesheet">'
MERMAID = '<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs";mermaid.initialize({startOnLoad:true,theme:matchMedia("(prefers-color-scheme: dark)").matches?"dark":"neutral",fontFamily:"IBM Plex Sans KR, sans-serif"});</script>'
# 강의 계획 (모르는 회차는 '예정'으로 표시)
PLAN = {2: "근육반응검사 심화와 8체질 검사의 기초"}

def head(title, css):
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{html.escape(title)}</title>{FONTS}<link rel="stylesheet" href="{css}"></head><body>'

def track(n):
    cells = "".join(f'<span class="{"done" if i < n else "now" if i == n else ""}"></span>' for i in range(1, TOTAL + 1))
    return f'<div class="track" aria-hidden="true">{cells}</div>'

def parse(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
    meta = dict(l.split(": ", 1) for l in m.group(1).splitlines())
    return meta, raw[m.end():]

def render(md):
    md = re.sub(r"```mermaid\n(.*?)```", lambda m: '<pre class="mermaid">' + html.escape(m.group(1)) + "</pre>", md, flags=re.S)
    body = markdown.markdown(md, extensions=["tables", "attr_list", "toc"])
    body = body.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    # 비판적 검토 섹션 감싸기
    parts = re.split(r"(?=<h2)", body)
    out = []
    for p in parts:
        if 'class="critical"' in p:
            p = '<section class="critical">' + p.replace(' class="critical"', "") + "</section>"
        out.append(p)
    body = "".join(out)
    toc = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    return body, toc

notes = []
for path in sorted(glob.glob("notes/*.md")):
    meta, md = parse(path)
    n = int(meta["num"])
    body, toc = render(md)
    tochtml = "".join(f'<a href="#{i}">{re.sub("<.*?>", "", t)}</a>' for i, t in toc)
    page = (head(f'제{n}강 {meta["title"]} — AK 학습노트', "../assets/style.css")
        + '<div class="wrap"><nav class="top"><a href="../index.html">← AK 자연치유요법 학습노트 전체</a></nav>'
        + f'<header class="hero"><p class="num">제{n}강</p><h1>{meta["title"]}</h1><p>{meta["summary"]}</p>'
        + track(n) + f'<div class="tracklabel">12강 중 {n}강 · 정리 {meta["date"]}</div></header>'
        + f'<div class="layout"><nav class="toc" aria-label="목차">{tochtml}</nav><article>{body}</article></div>'
        + '<footer>고성윤 · AK 자연치유센터 강의 원고와 녹취를 바탕으로 개인 학습용으로 정리했습니다. 의학적 진단·치료를 대신하지 않습니다.</footer></div>'
        + MERMAID + "</body></html>")
    os.makedirs("lectures", exist_ok=True)
    open(f"lectures/{n:02d}.html", "w", encoding="utf-8").write(page)
    notes.append((n, meta))

done = {n: m for n, m in notes}
items = ""
for i in range(1, TOTAL + 1):
    if i in done:
        m = done[i]
        items += f'<li><div class="n">{i}</div><div><div class="t"><a href="lectures/{i:02d}.html">{m["title"]}</a></div><div class="s">{m["summary"]} · {m["date"]}</div></div></li>'
    else:
        items += f'<li class="todo"><div class="n">{i}</div><div><div class="t">{PLAN.get(i, "예정")}</div><div class="s">아직 정리 전</div></div></li>'
index = (head("AK 자연치유요법 학습노트", "assets/style.css")
    + '<div class="wrap"><header class="hero"><p class="num">AK</p><h1>자연치유요법 12주 학습노트</h1>'
    + '<p>고성윤 · AK 자연치유센터 강의를 회차별로 정리합니다.</p>'
    + '<div class="track" aria-hidden="true">' + "".join(f'<span class="{"done" if i in done else ""}"></span>' for i in range(1, TOTAL + 1)) + '</div>'
    + f'<div class="tracklabel">{len(done)} / {TOTAL}강 정리됨</div></header>'
    + f'<ol class="course">{items}</ol>'
    + '<footer>개인 학습용 정리입니다. 의학적 진단·치료를 대신하지 않습니다.</footer></div></body></html>')
open("index.html", "w", encoding="utf-8").write(index)
print("built", [n for n, _ in notes])
