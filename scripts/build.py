#!/usr/bin/env python3
"""data/*.json ve src/* dosyalarını tek, kendi kendine yeten index.html içinde birleştirir.

Kullanım:  python3 scripts/build.py
Leaflet ve vis-network CDN'den yüklenir; veri, stil ve uygulama kodu HTML'e gömülür
(file:// altında fetch çalışmadığı için).
"""
import json
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
    out.write_text(html, encoding="utf-8")
    print(f"index.html yazıldı ({out.stat().st_size // 1024} KB): "
          f"{len(data['people'])} kişi, {len(data['works'])} eser, {len(data['relations'])} ilişki")


if __name__ == "__main__":
    main()
