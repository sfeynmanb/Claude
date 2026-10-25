#!/usr/bin/env python3
"""data/*.json ve src/* dosyalarını tek, kendi kendine yeten index.html içinde birleştirir.

Kullanım:  python3 scripts/build.py                      -> index.html
           python3 scripts/build.py --artifact ÇIKTI.html -> claude.ai Artifact (site) sürümü
Leaflet ve vis-network CDN'den yüklenir; veri, stil ve uygulama kodu HTML'e gömülür
(file:// altında fetch çalışmadığı için).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    data = {name: json.loads((ROOT / "data" / f"{name}.json").read_text(encoding="utf-8"))
            for name in ("people", "works", "relations", "meta")}
    data["basemap"] = json.loads((ROOT / "data" / "basemap.geojson").read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # </script> kapanışını ve HTML yorumlarını kırmamak için
    payload = payload.replace("</", "<\\/").replace("<!--", "\\u003c!--")

    html = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
    style = (ROOT / "src" / "style.css").read_text(encoding="utf-8")
    app = (ROOT / "src" / "app.js").read_text(encoding="utf-8")
    for token in ("/*__STYLE__*/", "/*__APP__*/", "__DATA__"):
        assert html.count(token) == 1, f"şablonda {token} tam bir kez bulunmalı"
    html = html.replace("/*__STYLE__*/", style).replace("/*__APP__*/", app).replace("__DATA__", payload)
    out = ROOT / "index.html"
    if "--artifact" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--artifact") + 1])
        html = artifact(html)
    out.write_text(html, encoding="utf-8")
    print(f"{out.name} yazıldı ({out.stat().st_size // 1024} KB): "
          f"{len(data['people'])} kişi, {len(data['works'])} eser, {len(data['relations'])} ilişki")


def artifact(html):
    """claude.ai Artifact sürümü: iskeleti platform ekler; CSP harici stil dosyasına ve
    harita karolarına izin vermediği için Leaflet CSS gömülür, internet altlığı seçeneği kaldırılır."""
    head = re.search(r"<head>(.*)</head>", html, re.S).group(1)
    body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    head = re.sub(r'\s*<meta charset="utf-8">|\s*<meta name="viewport"[^>]*>|\s*<link rel="stylesheet" href="https://cdnjs[^>]*>', "", head)
    leaflet_css = (ROOT / "src" / "vendor" / "leaflet-1.9.4.css").read_text(encoding="utf-8")
    head = head.replace("<style>", f'<meta name="claude:viewport-fit-sides" content="cover">\n<style>{leaflet_css}</style>\n<style>', 1)
    tiles = '<label class="small"><input id="tiles" type="checkbox"> İnternet altlığı (CARTO/OSM)</label>'
    assert tiles in body
    body = body.replace(tiles, "<span></span>")
    return head.strip() + "\n" + body.strip() + "\n"


if __name__ == "__main__":
    main()
