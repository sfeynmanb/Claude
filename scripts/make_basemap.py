#!/usr/bin/env python3
"""Çevrimdışı altlık haritasını üretir: Natural Earth 1:50m kara poligonları -> data/basemap.geojson.

Kaynak: npm paketi world-atlas@2.0.2 (land-50m.json, TopoJSON; Natural Earth, kamu malı).
Kullanım:  npm pack world-atlas@2.0.2 && tar xzf world-atlas-2.0.2.tgz
           python3 scripts/make_basemap.py package/land-50m.json
Bu dosya yalnızca altlığı yeniden üretmek için gerekir; data/basemap.geojson depoda hazırdır.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KUTU = (-20.0, -2.0, 95.0, 60.0)  # batı, güney, doğu, kuzey


def decode_arcs(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def ring_from(arc_ids, arcs):
    ring = []
    for i in arc_ids:
        pts = arcs[i] if i >= 0 else list(reversed(arcs[~i]))
        ring.extend(pts if not ring else pts[1:])
    return ring


def clip(ring, kutu):
    """Sutherland–Hodgman: halkayı dikdörtgene kırpar."""
    w, s, e, n = kutu
    kenarlar = [
        (lambda p: p[0] >= w, lambda a, b: (w, a[1] + (b[1] - a[1]) * (w - a[0]) / (b[0] - a[0]))),
        (lambda p: p[0] <= e, lambda a, b: (e, a[1] + (b[1] - a[1]) * (e - a[0]) / (b[0] - a[0]))),
        (lambda p: p[1] >= s, lambda a, b: (a[0] + (b[0] - a[0]) * (s - a[1]) / (b[1] - a[1]), s)),
        (lambda p: p[1] <= n, lambda a, b: (a[0] + (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]), n)),
    ]
    pts = ring
    for icerde, kesisim in kenarlar:
        if not pts:
            break
        yeni = []
        onceki = pts[-1]
        for p in pts:
            if icerde(p):
                if not icerde(onceki):
                    yeni.append(kesisim(onceki, p))
                yeni.append(p)
            elif icerde(onceki):
                yeni.append(kesisim(onceki, p))
            onceki = p
        pts = yeni
    return pts


def sadelestir(ring, basamak=2):
    out = []
    for x, y in ring:
        q = [round(x, basamak), round(y, basamak)]
        if not out or out[-1] != q:
            out.append(q)
    if len(out) >= 3 and out[0] != out[-1]:
        out.append(out[0])
    return out if len(out) >= 4 else None


def main(src):
    topo = json.loads(Path(src).read_text())
    arcs = decode_arcs(topo)
    polys = []
    for geom in topo["objects"]["land"]["geometries"]:
        parts = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
        for poly in parts:
            rings = []
            for ring_ids in poly:
                r = sadelestir(clip(ring_from(ring_ids, arcs), KUTU))
                if r:
                    rings.append(r)
            if rings:
                polys.append(rings)
    gj = {"type": "Feature", "properties": {"kaynak": "Natural Earth 1:50m (world-atlas@2.0.2)"},
          "geometry": {"type": "MultiPolygon", "coordinates": polys}}
    hedef = ROOT / "data" / "basemap.geojson"
    hedef.write_text(json.dumps(gj, separators=(",", ":")), encoding="utf-8")
    print(f"{len(polys)} poligon, {hedef.stat().st_size // 1024} KB -> {hedef.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1])
