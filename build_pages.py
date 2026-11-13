"""Build nine offline-compatible pages from the published dashboard.

Run from the repository root: python build_pages.py outputs/market_dashboard.html
"""
import html
import json
import re
import sys
from pathlib import Path

PAGES = [
    ("analysis", "index.html", "分析与选品建议"),
    ("market", "products.html", "商品与价格"),
    ("channelDimensions", "channels.html", "虾皮与商品维度"),
    ("tiktokChannel", "tiktok.html", "TikTok渠道"),
    ("comments", "comments.html", "社媒评论"),
    ("reviews", "reviews.html", "电商评价"),
    ("social", "content.html", "内容表现"),
    ("next", "opportunities.html", "选品数据拓展"),
    ("sources", "sources.html", "来源与采集"),
]

def build(source, destination):
    main = re.search(r"<main>(.*?)</main>", source, re.S).group(1)
    main = re.sub(r'<nav aria-label="看板章节">.*?</nav>', '', main, count=1, flags=re.S)
    for section, filename, _ in PAGES:
        main = main.replace('href="#' + section + '"', 'href="' + filename + '"')
    scripts = re.findall(r"<script>(.*?)</script>", source, re.S)
    if len(scripts) != 3:
        raise ValueError("Expected all three dashboard scripts")
    css = "\n".join(re.findall(r"<style>(.*?)</style>", source, re.S))
    css += """
nav a[aria-current="page"]{color:var(--purple);border-color:var(--purple);background:#f1edff}
#pageContent[hidden]{display:none}
"""
    # Render and initialize the shared widgets before retaining the current page.
    # The content stays hidden during initialization, including when opening offline.
    runtime = "const pageContent = document.getElementById('pageContent');\n"
    runtime += "pageContent.innerHTML = " + json.dumps(main, ensure_ascii=False) + ";\n"
    runtime += "\n".join(scripts) + """
const chosenSection = document.body.dataset.section;
const retained = new Set([chosenSection]);
if (chosenSection === 'sources') retained.add('vpnRetry');
for (const child of [...pageContent.children]) {
    if (child.matches('section, .analysis-panel') && !retained.has(child.id)) child.remove();
    else if (child.matches('.stats, .notice') && chosenSection !== 'analysis') child.remove();
}
pageContent.hidden = false;
"""
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "dashboard.js").write_text(runtime, encoding="utf-8")
    (destination / "dashboard.css").write_text(css, encoding="utf-8")
    for section, filename, title in PAGES:
        nav = []
        for key, href, label in PAGES:
            current = ' aria-current="page"' if key == section else ""
            nav.append(f'<a href="{href}"{current}>{html.escape(label)}</a>')
        document = f"""<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · NailTrend BR</title>
<link rel="stylesheet" href="dashboard.css">
<body data-section="{section}">
<header><small>NAILTREND BR</small><h1>{title}</h1></header>
<main>
<nav aria-label="栏目">{''.join(nav)}</nav>
<div id="pageContent" hidden></div>
<noscript>请启用 JavaScript 查看与筛选数据。</noscript>
</main>
<script src="dashboard.js"></script>
</body>
</html>
"""
        (destination / filename).write_text(document, encoding="utf-8")

if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("outputs/market_dashboard.html")
    destination = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    build(source.read_text(encoding="utf-8"), destination)
