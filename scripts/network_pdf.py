#!/usr/bin/env python3
"""İlişki ağını kapsamlı bir PDF olarak üretir: reports/iliski-agi.pdf

Kullanım:  pip install networkx scipy matplotlib reportlab pypdf
           python3 scripts/network_pdf.py [çıktı.pdf]

İçerik: kapak ve okuma kılavuzu, kronolojik ağ (A3), tam ağ (A2), her ilişki türü için ayrı ağ,
ilişkilerin tam listesi, kişi bazında bağlantı dizini, merkezîlik ölçüleri, yazar–eser listesi.
"""
import io
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402
from pypdf import PdfReader, PdfWriter  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.pdfgen import canvas as rl_canvas  # noqa: E402
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,  # noqa: E402
                                Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reports" / "iliski-agi.pdf"

# ---------------------------------------------------------------- veri
people = json.loads((ROOT / "data/people.json").read_text(encoding="utf-8"))
works = json.loads((ROOT / "data/works.json").read_text(encoding="utf-8"))
rels = json.loads((ROOT / "data/relations.json").read_text(encoding="utf-8"))
meta = json.loads((ROOT / "data/meta.json").read_text(encoding="utf-8"))
P = {p["id"]: p for p in people}
W = {w["id"]: w for w in works}
works_by = defaultdict(list)
for w in works:
    if w["yazar_id"]:
        works_by[w["yazar_id"]].append(w)
name = lambda i: P[i]["ad"] if i in P else W[i]["ad_sade"]  # noqa: E731

TYPES = [  # (tür, renk, okunuş: kaynak → hedef)
    ("hoca-öğrenci", "#2563eb", "Hoca → öğrenci"),
    ("himaye", "#d97706", "Hami → himaye edilen"),
    ("etkiledi", "#7c3aed", "Etkileyen → etkilenen"),
    ("çağdaş-tartışma", "#dc2626", "Çağdaş / tartışma (yönsüz)"),
    ("tercüme etti", "#059669", "Mütercim → eser"),
    ("şerh yazdı", "#0891b2", "Şârih → şerh edilen eser"),
]
TCOL = {t: c for t, c, _ in TYPES}
TLAB = {t: lab for t, _, lab in TYPES}
AUTH_COL = "#9ca3af"
DYN = {d["ad"]: d for d in meta["devletler"]}
group_of = lambda d: d if d in DYN else meta["grup_eslemesi"].get(d, "Diğer")  # noqa: E731
GCOL = {g: DYN[g]["renk"] if g in DYN else "#8a8478" for g in meta["grup_sirasi"]}
pgroup = lambda p: group_of(p["devletler"][0])  # noqa: E731


def year(v):
    if v is None:
        return None
    if isinstance(v, int):
        return (v, v)
    s = str(v).lstrip("~")
    a, _, b = s.partition("-")
    return (int(a), int(b or a))


def life(p):
    """Arayüzdeki tahmin mantığının aynısı: bilinmeyen uçlar eser/durak yıllarından."""
    d, o = year(p["dogum"]), year(p["olum"])
    lo, hi = (d[0] if d else None), (o[1] if o else None)
    ys = []
    for w in works_by[p["id"]]:
        y = year(w["yil"])
        if y:
            ys += list(y)
    for s in p["duraklar"]:
        ys += [y for y in (s["yil_baslangic"], s["yil_bitis"]) if y]
    if lo is None and hi is not None:
        lo = min([hi - 60] + [y for y in ys if y <= hi])
    elif hi is None and lo is not None:
        hi = max([lo + 60] + ys)
    elif lo is None and hi is None and ys:
        lo, hi = min(ys), max(ys)
    return lo, hi


LIFE = {p["id"]: life(p) for p in people}
yr_txt = lambda v: "?" if v is None else str(v)  # noqa: E731

# Kişi düzeyine indirgenmiş ilişkiler (eser uçları yazarına bağlanır)
person_edges = []
seen = set()
for r in rels:
    a, b = r["kaynak"], r["hedef"]
    via = None
    if a in W:
        via, a = a, W[a]["yazar_id"]
    if b in W:
        via, b = b, W[b]["yazar_id"]
    if not a or not b or a == b:
        continue
    key = (a, b, r["tur"])
    if key in seen:
        continue
    seen.add(key)
    person_edges.append({"a": a, "b": b, "tur": r["tur"], "via": via, "dogrulanamadi": r.get("dogrulanamadi", False)})

# Tam graf (kişi + eser; ilişki + yazarlık)
G = nx.MultiDiGraph()
for p in people:
    G.add_node(p["id"], kind="p")
for w in works:
    G.add_node(w["id"], kind="w")
for r in rels:
    G.add_edge(r["kaynak"], r["hedef"], tur=r["tur"], dog=r.get("dogrulanamadi", False))
for w in works:
    if w["yazar_id"]:
        G.add_edge(w["yazar_id"], w["id"], tur="yazdı", dog=False)

# Kişi grafı (merkezîlik için)
PG = nx.DiGraph()
PG.add_nodes_from(P)
for e in person_edges:
    PG.add_edge(e["a"], e["b"], tur=e["tur"])
UPG = PG.to_undirected()
deg = dict(UPG.degree())
btw = nx.betweenness_centrality(UPG, normalized=True)
isolated = sorted([i for i in P if deg[i] == 0], key=lambda i: LIFE[i][0] or 0)
components = sorted(nx.connected_components(UPG), key=len, reverse=True)
type_counts = Counter(r["tur"] for r in rels)

# ---------------------------------------------------------------- şekiller (matplotlib)
plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "axes.unicode_minus": False})
MM = 1 / 25.4
INK, MUTED, GRID = "#1f2328", "#6b645a", "#e4ded3"


def legend_handles(include_auth=False):
    hs = [Line2D([0], [0], color=c, lw=2, label=lab) for t, c, lab in TYPES]
    if include_auth:
        hs.append(Line2D([0], [0], color=AUTH_COL, lw=1, ls="--", label="Yazar → eser"))
    hs.append(Line2D([0], [0], color=MUTED, lw=1.2, ls=(0, (2, 2)), label="Kesikli: kaynakla teyit edilemedi"))
    return hs


def page_title(fig, title, sub):
    h = fig.get_figheight() / MM
    fig.text(0.02, 1 - 9 / h, title, fontsize=17, fontweight="bold", color=INK, va="top", family="DejaVu Serif")
    fig.text(0.02, 1 - 18 / h, sub, fontsize=9, color=MUTED, va="top")


def fig_chronological(pdf):
    """Şekil 1: x = yıl, y = devlet grubu şeridi; her kişi ömür çizgisi + orta nokta."""
    W_, H_ = 420 * MM, 297 * MM
    fig = plt.figure(figsize=(W_, H_))
    page_title(fig, "Şekil 1 · Kronolojik ilişki ağı",
               f"{len(people)} kişinin tamamı, devlet grubuna göre şeritlerde. Yatay çizgi ömrü, nokta ömrün ortasını gösterir. "
               f"Oklar {len(person_edges)} kişi–kişi ilişkisini gösterir (eser üzerinden kurulan ilişkiler yazarına bağlanmıştır).")
    ax = fig.add_axes([0.105, 0.10, 0.885, 0.82])
    t0, t1 = meta["zaman_araligi"]
    char_years = 4.6  # 6 pt etiket için bir karakterin yıl karşılığı (deneysel)
    rows, y = {}, 0
    lane_spans = []
    for g in meta["grup_sirasi"]:
        members = sorted([p for p in people if pgroup(p) == g], key=lambda p: LIFE[p["id"]][0])
        if not members:
            continue
        ends = []
        top = y
        for p in members:
            lo, hi = LIFE[p["id"]]
            need = hi + 6 + len(p["ad"]) * char_years
            for k, e in enumerate(ends):
                if e < lo - 4:
                    ends[k] = need
                    rows[p["id"]] = top + k
                    break
            else:
                ends.append(need)
                rows[p["id"]] = top + len(ends) - 1
        y = top + len(ends)
        lane_spans.append((g, top, y))
        y += 0.9
    total = y
    for i, (g, a, b) in enumerate(lane_spans):
        ax.axhspan(a - 0.55, b - 0.45, color=GCOL[g], alpha=0.10, lw=0)
        if g in DYN:
            d = DYN[g]
            ax.plot([max(d["baslangic"], t0), min(d["bitis"], t1)], [a - 0.5, a - 0.5], color=GCOL[g], lw=3, alpha=0.8,
                    solid_capstyle="butt")
        ax.text(t0 - 8, (a + b - 1) / 2, f"{g}\n({b - a} sıra)" if False else g, ha="right", va="center", fontsize=8,
                fontweight="bold", color=GCOL[g] if g != "Diğer" else MUTED, family="DejaVu Serif")
    pos = {}
    for p in people:
        lo, hi = LIFE[p["id"]]
        r = rows[p["id"]]
        mid = (lo + hi) / 2
        pos[p["id"]] = (mid, r)
        dashed = p["tarih_kesinligi"] != "kesin" or p["dogum"] is None or p["olum"] is None
        ax.plot([lo, hi], [r, r], color=GCOL[pgroup(p)], lw=2.2, alpha=0.45, solid_capstyle="round",
                ls=(0, (3, 1.5)) if dashed else "-")
        ax.text(hi + 4, r, p["ad"], fontsize=6, va="center", color=INK)
    for e in person_edges:
        (x1, y1), (x2, y2) = pos[e["a"]], pos[e["b"]]
        rad = 0.25 if x2 >= x1 else -0.25
        arrow = FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
                                arrowstyle="-" if e["tur"] == "çağdaş-tartışma" else "-|>", mutation_scale=7,
                                color=TCOL[e["tur"]], lw=0.9, alpha=0.75, ls="--" if e["dogrulanamadi"] or e["via"] else "-",
                                shrinkA=2, shrinkB=2, zorder=3)
        ax.add_patch(arrow)
    for p in people:
        x, r = pos[p["id"]]
        ax.scatter([x], [r], s=10 + 4 * deg[p["id"]], color=GCOL[pgroup(p)], edgecolor="white", lw=0.5, zorder=4)
    ax.set_xlim(t0 - 5, t1 + 40)
    ax.set_ylim(total, -1.2)
    ax.set_yticks([])
    ax.set_xticks(range(800, t1 + 1, 50), [str(t) if t % 100 == 0 else "" for t in range(800, t1 + 1, 50)], fontsize=8, color=MUTED)
    ax.grid(axis="x", color=GRID, lw=0.6)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    leg = fig.legend(handles=legend_handles() + [Line2D([0], [0], color=MUTED, lw=2, ls=(0, (3, 1.5)), alpha=0.6,
                                                        label="Kesikli ömür: yaklaşık/tartışmalı ya da tahmini")],
                     loc="lower left", bbox_to_anchor=(0.105, 0.032), ncol=5, fontsize=7.5, frameon=False)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.text(0.99, 0.045, "Nokta büyüklüğü = kişinin toplam ilişki sayısı (derece)", ha="right", fontsize=7, color=MUTED)
    pdf.savefig(fig)
    plt.close(fig)


CHAR_MM = 1.42  # 7 pt DejaVu Sans için ortalama karakter genişliği (mm)


def label_of(n):
    return P[n]["ad"] if n in P else W[n]["ad_sade"]


def draw_graph(ax, nodes, pos, edges, fs=7.0, rad=0.12):
    """pos: mm cinsinden (x, y); y aşağı doğru artar."""
    k = fs / 7.0
    for (a, b, d) in edges:
        t = d["tur"]
        col = AUTH_COL if t == "yazdı" else TCOL[t]
        ax.add_patch(FancyArrowPatch(pos[a], pos[b], connectionstyle=f"arc3,rad={rad}",
                                     arrowstyle="-" if t in ("çağdaş-tartışma", "yazdı") else "-|>", mutation_scale=8 * k,
                                     color=col, lw=0.5 if t == "yazdı" else 1.1, alpha=0.6 if t == "yazdı" else 0.9,
                                     ls="--" if (t == "yazdı" or d.get("dog")) else "-", shrinkA=3.5 * k, shrinkB=3.5 * k, zorder=2))
    for n in nodes:
        x, y = pos[n]
        if n in P:
            ax.scatter([x], [y], s=(18 + 5 * deg[n]) * k, color=GCOL[pgroup(P[n])], edgecolor="white", lw=0.6, zorder=3)
            ax.text(x, y + 1.6 * k, P[n]["ad"], fontsize=fs, ha="center", va="top", color=INK, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.75))
        else:
            ax.scatter([x], [y], s=14 * k, marker="D", color="#efe9df", edgecolor=MUTED, lw=0.6, zorder=3)
            ax.text(x, y + 1.3 * k, W[n]["ad_sade"], fontsize=fs * 0.82, ha="center", va="top", color=MUTED,
                    style="italic", zorder=4)
    ax.set_axis_off()


def layered(g, fs=7.0):
    """Bir bileşen için katmanlı yerleşim: kaynaklar üstte. Döndürür: (pos_mm, genişlik, yükseklik)."""
    cond = nx.condensation(g)
    depth = {}
    for c in nx.topological_sort(cond):
        preds = list(cond.predecessors(c))
        depth[c] = 1 + max(depth[q] for q in preds) if preds else 0
    nd = {n: depth[cond.graph["mapping"][n]] for n in g.nodes}
    layers = defaultdict(list)
    for n in sorted(g.nodes, key=label_of):
        layers[nd[n]].append(n)
    und = g.to_undirected()
    wid = lambda n: len(label_of(n)) * CHAR_MM * fs / 7.0 + 5  # noqa: E731
    xs = {}

    def place():
        for ns in layers.values():
            x = 0
            for n in ns:
                w = wid(n)
                xs[n] = x + w / 2
                x += w + 2

    place()
    for _ in range(4):  # barisentrik sıralama: kesişmeleri azaltır
        for L in sorted(layers):
            ns = layers[L]
            bc = {n: (sum(xs[m] for m in und.neighbors(n)) / und.degree(n)) if und.degree(n) else xs[n] for n in ns}
            layers[L] = sorted(ns, key=lambda n: bc[n])
        place()
    widths = {L: sum(wid(n) + 2 for n in ns) - 2 for L, ns in layers.items()}
    W_ = max(widths.values())
    row = 15 * fs / 7.0
    pos = {}
    for L, ns in layers.items():
        off = (W_ - widths[L]) / 2
        for n in ns:
            pos[n] = (xs[n] + off, L * row)
    return pos, W_, (max(layers) * row) + 6


def shelf_pack(boxes, width, gap=8.0):
    """boxes: [(id, w, h)] -> ({id: (x, y)}, toplam yükseklik). Satır satır yerleştirir."""
    out, x, y, shelf = {}, 0.0, 0.0, 0.0
    for i, w, h in boxes:
        if x > 0 and x + w > width:
            x, y, shelf = 0.0, y + shelf + gap, 0.0
        out[i] = (x, y)
        x += w + gap
        shelf = max(shelf, h)
    return out, y + shelf


def fig_by_type(pdf, num, tur):
    es = [(r["kaynak"], r["hedef"], {"tur": tur, "dog": r.get("dogrulanamadi", False)}) for r in rels if r["tur"] == tur]
    g = nx.DiGraph()
    for a, b, d in es:
        g.add_edge(a, b, **d)
    comps = sorted(nx.weakly_connected_components(g), key=len, reverse=True)
    fs = 7.0
    laid = []
    for i, c in enumerate(comps):
        pos, w, h = layered(g.subgraph(c), fs)
        laid.append((i, pos, w, h + 4))
    top, side, bottom = 26, 12, 20
    for W_, H_ in ((297, 210), (420, 297), (594, 420), (841, 594)):
        packed, used = shelf_pack([(i, w, h) for i, _, w, h in laid], W_ - 2 * side, gap=12)
        if used <= H_ - top - bottom:
            break
    fig = plt.figure(figsize=(W_ * MM, H_ * MM))
    page_title(fig, f"Şekil {num} · {tur[0].upper() + tur[1:]} ilişkileri",
               f"{len(es)} ilişki, {g.number_of_nodes()} düğüm, {len(comps)} bağlı bileşen. Okuma yönü: {TLAB[tur]} "
               f"(kaynak üstte, hedef altta).")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_)
    ax.set_ylim(H_, 0)
    pos = {}
    for i, p, w, h in laid:
        ox, oy = packed[i]
        for n, (x, y) in p.items():
            pos[n] = (side + ox + x, top + 4 + oy + y)
    draw_graph(ax, g.nodes, pos, [(a, b, d) for a, b, d in g.edges(data=True)], fs=fs, rad=0.0)
    fig.legend(handles=[Line2D([0], [0], color=TCOL[tur], lw=2, label=TLAB[tur]),
                        Line2D([0], [0], color=TCOL[tur], lw=1.2, ls="--", label="Kesikli: teyit edilemedi")],
               loc="lower left", bbox_to_anchor=(side / W_, 11 / H_), ncol=2, fontsize=8, frameon=False)
    pdf.savefig(fig)
    plt.close(fig)


def fig_full(pdf):
    """Şekil 2: tüm kişiler ve eserler; ilişki ve yazarlık kenarları. Bileşenler büyüklüklerine göre paketlenir."""
    W_, H_ = 594, 420
    top, side, bottom = 26, 10, 22
    und = nx.Graph(G.to_undirected())
    comps = sorted(nx.connected_components(und), key=len, reverse=True)
    unit = 21.0  # mm; kutu kenarı ≈ unit·√n
    laid = []
    for i, c in enumerate(comps):
        sub = und.subgraph(c)
        n = len(c)
        if n == 1:
            p = {next(iter(c)): (0.5, 0.5)}
        else:
            p = nx.kamada_kawai_layout(sub)
            p = normalize(nx.spring_layout(sub, pos=p, k=2.0 / math.sqrt(n), iterations=150, seed=7))
        side_len = unit * math.sqrt(n)
        aspect = 1.45 if i == 0 else 1.25
        laid.append((i, p, side_len * aspect, side_len))
    _, big_p, bw, bh = laid[0]
    scale = min(1.0, (H_ - top - bottom) / bh, (W_ - 2 * side) * 0.68 / bw)
    bw, bh = bw * scale, bh * scale
    rest = [(i, w * scale * 0.9 + 18, h * scale * 0.9 + 10) for i, _, w, h in laid[1:]]
    right_w = W_ - 2 * side - bw - 14
    packed, used = shelf_pack(rest, right_w, gap=6)
    shrink = min(1.0, (H_ - top - bottom) / used) if used else 1.0
    fig = plt.figure(figsize=(W_ * MM, H_ * MM))
    page_title(fig, "Şekil 2 · Tam ağ: kişiler, eserler, ilişkiler ve yazarlık",
               f"{len(people)} kişi (daire, renk = devlet grubu), {len(works)} eser (elmas); {len(rels)} ilişki kenarı (renkli) ve "
               f"{sum(1 for w in works if w['yazar_id'])} yazar–eser bağı (gri kesikli). En büyük bileşen solda, "
               f"diğer {len(comps) - 1} bileşen sağda.")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_)
    ax.set_ylim(H_, 0)
    pos = {}
    for n, (x, y) in big_p.items():
        pos[n] = (side + 6 + x * (bw - 12), top + 6 + y * (bh - 12))
    rx = side + bw + 14
    lookup = {i: (p, w, h) for i, p, w, h in laid}
    for i, (ox, oy) in packed.items():
        p, w, h = lookup[i]
        w, h = w * scale * 0.9 * shrink, h * scale * 0.9 * shrink
        for n, (x, y) in p.items():
            pos[n] = (rx + ox * shrink + 9 + x * w, top + 4 + oy * shrink + y * h)
    draw_graph(ax, G.nodes, pos, list(G.edges(data=True)), fs=5.6, rad=0.08)
    ax.plot([rx - 7, rx - 7], [top + 2, H_ - bottom], color=GRID, lw=0.8)
    fig.legend(handles=legend_handles(True), loc="lower left", bbox_to_anchor=(side / W_, 11 / H_), ncol=8, fontsize=9, frameon=False)
    fig.text(1 - side / W_, 13 / H_, f"{len(comps)} bağlı bileşen; en büyüğü {len(comps[0])} düğüm", ha="right", fontsize=8, color=MUTED)
    pdf.savefig(fig)
    plt.close(fig)


def normalize(pos):
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return {n: ((x - x0) / ((x1 - x0) or 1), (y - y0) / ((y1 - y0) or 1)) for n, (x, y) in pos.items()}


# ---------------------------------------------------------------- metin ve tablolar (reportlab)
FD = "/usr/share/fonts/truetype/dejavu/"
for n_, f_ in [("Sans", "DejaVuSans.ttf"), ("Sans-B", "DejaVuSans-Bold.ttf"), ("Serif", "DejaVuSerif.ttf"),
               ("Serif-B", "DejaVuSerif-Bold.ttf"), ("Sans-I", "DejaVuSans.ttf")]:
    pdfmetrics.registerFont(TTFont(n_, FD + f_))
# Eğik DejaVu Sans her sistemde yok; <i> düz yazıyla gösterilir.
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-B")
ST = {
    "h1": ParagraphStyle("h1", fontName="Serif-B", fontSize=22, leading=27, spaceAfter=6, textColor=colors.HexColor(INK)),
    "h2": ParagraphStyle("h2", fontName="Serif-B", fontSize=14, leading=18, spaceBefore=12, spaceAfter=6),
    "h3": ParagraphStyle("h3", fontName="Sans-B", fontSize=10, leading=13, spaceBefore=8, spaceAfter=3),
    "p": ParagraphStyle("p", fontName="Sans", fontSize=9, leading=13, spaceAfter=5, alignment=TA_LEFT),
    "small": ParagraphStyle("small", fontName="Sans", fontSize=7.6, leading=10, textColor=colors.HexColor("#3b3833")),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=7.4, leading=9.4),
    "cellb": ParagraphStyle("cellb", fontName="Sans-B", fontSize=7.4, leading=9.4),
    "muted": ParagraphStyle("muted", fontName="Sans", fontSize=8, leading=11, textColor=colors.HexColor(MUTED)),
}
esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731


def tstyle(header_bg="#efe9df"):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#b9b0a2")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#e4ded3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ])


def swatch(col):
    return f'<font color="{col}">■</font>'


def build_rl(path, story, title):
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=16 * mm,
                            bottomMargin=16 * mm, title=title)
    doc.build(story)
    return len(PdfReader(str(path)).pages)


def cover_story(toc):
    s = [Spacer(1, 4 * mm), Paragraph("Türk-İslam Atlası", ST["muted"]),
         Paragraph("İlişki Ağı", ST["h1"]),
         Paragraph("750–1700 yılları arasında Türk-İslam dünyasında kişiler ve eserler arasındaki hoca-öğrenci, himaye, "
                   "etki, tartışma, tercüme ve şerh ilişkilerinin tam dökümü.", ST["p"]),
         Spacer(1, 4 * mm)]
    n_auth = sum(1 for w in works if w["yazar_id"])
    stats = [["Kişi", str(len(people))], ["Eser", str(len(works))], ["İlişki", str(len(rels))],
             ["Yazar–eser bağı", str(n_auth)], ["Kişi düzeyine indirgenmiş ilişki", str(len(person_edges))],
             ["En az bir ilişkisi olan kişi", str(len(people) - len(isolated))],
             ["Teyit edilemeyen ilişki", str(sum(1 for r in rels if r.get("dogrulanamadi")))]]
    t = Table([[Paragraph(a, ST["cell"]), Paragraph(f"<b>{b}</b>", ST["cell"])] for a, b in stats], colWidths=[70 * mm, 25 * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e4ded3")),
                           ("ALIGN", (1, 0), (1, -1), "RIGHT")]))
    s += [t, Spacer(1, 4 * mm), Paragraph("İlişki türleri", ST["h2"])]
    rows = [[Paragraph("<b>Tür</b>", ST["cell"]), Paragraph("<b>Okuma yönü</b>", ST["cell"]), Paragraph("<b>Sayı</b>", ST["cell"])]]
    for tur, col, lab in TYPES:
        rows.append([Paragraph(f"{swatch(col)} {tur}", ST["cell"]), Paragraph(lab, ST["cell"]),
                     Paragraph(str(type_counts[tur]), ST["cell"])])
    tt = Table(rows, colWidths=[45 * mm, 80 * mm, 18 * mm])
    tt.setStyle(tstyle())
    s += [tt, Paragraph("Okuma kılavuzu", ST["h2"]),
          Paragraph("Bir ilişki her zaman <b>kaynak → hedef</b> yönünde okunur: “Kadızâde-i Rûmî → Uluğ Bey (hoca-öğrenci)”, "
                    "Kadızâde'nin Uluğ Bey'in hocası olduğunu söyler. Çağdaş-tartışma ilişkileri yönsüzdür. Bazı ilişkiler bir "
                    "esere bağlanır (örneğin Teftâzânî'nin Akāidü'n-Nesefî'ye şerh yazması). Kronolojik ağda (Şekil 1) bu ilişkiler "
                    "eserin yazarına bağlanarak kesikli çizilir.", ST["p"]),
          Paragraph("Kesikli kenarlar, veri setinde <i>dogrulanamadi</i> olarak işaretlenmiş, yani kaynakla teyit edilemeyen "
                    "ilişkilerdir. Şekiller vektöreldir; PDF görüntüleyicide yakınlaştırarak en küçük etiket de okunabilir.", ST["p"]),
          Paragraph("Kaynak notu: Kişi ve eserler TDV İslâm Ansiklopedisi maddelerine bağlıdır. Her kaydın teyit durumu "
                    "atlasın doğrulama raporunda (reports/validation.md) ayrıntılı olarak verilmiştir.", ST["muted"]),
          Paragraph("İçindekiler", ST["h2"])]
    trow = [[Paragraph(esc(a), ST["cell"]), Paragraph(str(b), ST["cell"])] for a, b in toc]
    ttoc = Table(trow, colWidths=[150 * mm, 18 * mm])
    ttoc.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e4ded3")),
                              ("ALIGN", (1, 0), (1, -1), "RIGHT")]))
    s += [ttoc, Spacer(1, 3 * mm), Paragraph(f"Üretim tarihi: {date.today().isoformat()} · scripts/network_pdf.py", ST["muted"])]
    return s


def tables_story():
    s = [Paragraph("Tablo 1 · İlişkilerin tam listesi", ST["h1"]),
         Paragraph(f"{len(rels)} ilişkinin tamamı, türe göre gruplanmış. Notlar veri setindeki açıklamalardır.", ST["p"])]
    for tur, col, lab in TYPES:
        rs = [r for r in rels if r["tur"] == tur]
        if not rs:
            continue
        rs.sort(key=lambda r: (LIFE.get(r["kaynak"], (None, None))[0] or (year(W[r["kaynak"]]["yil"]) or (9999,))[0]
                               if r["kaynak"] in W else LIFE[r["kaynak"]][0] or 0))
        rows = [[Paragraph(f"<b>{h}</b>", ST["cell"]) for h in ("Kaynak", "Hedef", "Not", "Durum")]]
        for r in rs:
            a, b = r["kaynak"], r["hedef"]
            ka = f"{esc(name(a))}" + (" <i>(eser)</i>" if a in W else f" <font color='{MUTED}'>{yr_txt(P[a]['dogum'])}–{yr_txt(P[a]['olum'])}</font>")
            kb = f"{esc(name(b))}" + (" <i>(eser)</i>" if b in W else f" <font color='{MUTED}'>{yr_txt(P[b]['dogum'])}–{yr_txt(P[b]['olum'])}</font>")
            rows.append([Paragraph(ka, ST["cell"]), Paragraph(kb, ST["cell"]), Paragraph(esc(r.get("not") or "—"), ST["cell"]),
                         Paragraph("<font color='#b3261e'>teyit edilemedi</font>" if r.get("dogrulanamadi") else "kaynaklı", ST["cell"])])
        t = Table(rows, colWidths=[42 * mm, 42 * mm, 74 * mm, 20 * mm], repeatRows=1)
        t.setStyle(tstyle())
        s += [Paragraph(f"{swatch(col)} {tur} · {len(rs)} · <font color='{MUTED}'>{lab}</font>", ST["h2"]), t]
    s.append(PageBreak())

    # Tablo 2: kişi bazında dizin
    s += [Paragraph("Tablo 2 · Kişi bazında bağlantı dizini", ST["h1"]),
          Paragraph("Her kişinin bütün ilişkileri ve eserleri, alfabetik sırayla. Parantez içindeki sayı, kişi düzeyindeki toplam "
                    "ilişki sayısıdır (derece).", ST["p"])]
    labels_out = {"hoca-öğrenci": "Öğrencileri", "himaye": "Himaye ettikleri", "etkiledi": "Etkiledikleri",
                  "çağdaş-tartışma": "Çağdaş/tartışma", "tercüme etti": "Tercüme ettikleri", "şerh yazdı": "Şerh ettikleri"}
    labels_in = {"hoca-öğrenci": "Hocaları", "himaye": "Hamileri", "etkiledi": "Etkilendikleri",
                 "çağdaş-tartışma": "Çağdaş/tartışma", "tercüme etti": "Tercüme edenler", "şerh yazdı": "Şerh edenler"}
    for p in sorted(people, key=lambda p: p["ad"].replace("İ", "I")):
        pid = p["id"]
        parts = defaultdict(list)
        for r in rels:
            note = " (teyitsiz)" if r.get("dogrulanamadi") else ""
            if r["kaynak"] == pid:
                parts[labels_out[r["tur"]]].append(esc(name(r["hedef"])) + note)
            elif r["hedef"] == pid:
                parts[labels_in[r["tur"]]].append(esc(name(r["kaynak"])) + note)
            elif (r["hedef"] in W and W[r["hedef"]]["yazar_id"] == pid) or (r["kaynak"] in W and W[r["kaynak"]]["yazar_id"] == pid):
                parts["Eserleri üzerinden"].append(f"{esc(name(r['kaynak']))} → {esc(name(r['hedef']))} ({r['tur']})" + note)
        ws = works_by[pid]
        lines = [f"<b>{esc(p['ad'])}</b> <font color='{MUTED}'>{yr_txt(p['dogum'])}–{yr_txt(p['olum'])} · "
                 f"{esc(', '.join(p['devletler']))} · ({deg[pid]})</font>"]
        for k in ["Hocaları", "Öğrencileri", "Hamileri", "Himaye ettikleri", "Etkilendikleri", "Etkiledikleri",
                  "Çağdaş/tartışma", "Tercüme ettikleri", "Tercüme edenler", "Şerh ettikleri", "Şerh edenler", "Eserleri üzerinden"]:
            if parts.get(k):
                lines.append(f"<font color='{MUTED}'>{k}:</font> " + "; ".join(dict.fromkeys(parts[k])))
        if ws:
            lines.append(f"<font color='{MUTED}'>Eserleri ({len(ws)}):</font> " + "; ".join(esc(w["ad_sade"]) for w in ws))
        if deg[pid] == 0:
            lines.append(f"<font color='{MUTED}'>Veri setinde başka bir kişiyle kayıtlı ilişkisi yok.</font>")
        s.append(KeepTogether([Paragraph("<br/>".join(lines), ST["small"]), Spacer(1, 2.2 * mm)]))
    s.append(PageBreak())

    # Tablo 3: merkezîlik
    s += [Paragraph("Tablo 3 · Merkezîlik ölçüleri", ST["h1"]),
          Paragraph("Kişi düzeyindeki yönsüz ağda hesaplanmıştır. <b>Derece</b>, kişinin doğrudan bağlantı sayısıdır. <b>Arasındalık</b>, "
                    "kişinin diğer kişiler arasındaki en kısa yollar üzerinde ne sıklıkla bulunduğunu gösterir (0–1). Yüksek arasındalık, "
                    "farklı çevreleri birbirine bağlayan aracı figürleri işaret eder. Değerler yalnızca bu veri setindeki ilişkileri "
                    "yansıtır; tarihî etkinin ölçüsü değildir.", ST["p"])]
    top = sorted(P, key=lambda i: (-deg[i], -btw[i]))[:30]
    rows = [[Paragraph(f"<b>{h}</b>", ST["cell"]) for h in ("#", "Kişi", "Devlet grubu", "Derece", "Arasındalık", "Giden", "Gelen")]]
    for i, pid in enumerate(top, 1):
        rows.append([Paragraph(str(i), ST["cell"]), Paragraph(esc(P[pid]["ad"]), ST["cell"]), Paragraph(pgroup(P[pid]), ST["cell"]),
                     Paragraph(str(deg[pid]), ST["cell"]), Paragraph(f"{btw[pid]:.3f}", ST["cell"]),
                     Paragraph(str(PG.out_degree(pid)), ST["cell"]), Paragraph(str(PG.in_degree(pid)), ST["cell"])])
    t = Table(rows, colWidths=[8 * mm, 52 * mm, 40 * mm, 16 * mm, 22 * mm, 16 * mm, 16 * mm], repeatRows=1)
    t.setStyle(tstyle())
    s += [t, Spacer(1, 4 * mm), Paragraph("Bağlı bileşenler", ST["h2"]),
          Paragraph(f"Kişi düzeyindeki ağ {len([c for c in components if len(c) > 1])} çok üyeli bileşenden ve "
                    f"{len(isolated)} bağlantısız kişiden oluşur.", ST["p"])]
    for i, c in enumerate([c for c in components if len(c) > 1], 1):
        mem = sorted(c, key=lambda x: LIFE[x][0] or 0)
        s.append(Paragraph(f"<b>Bileşen {i}</b> ({len(c)} kişi): " + ", ".join(esc(P[m]["ad"]) for m in mem), ST["small"]))
        s.append(Spacer(1, 1.5 * mm))
    s += [Paragraph("Bağlantısız kişiler", ST["h2"]),
          Paragraph("Bu kişilerin veri setinde başka bir kişiyle kayıtlı ilişkisi yoktur. Bu, tarihte ilişkisiz oldukları anlamına "
                    "gelmez; ilişkileri henüz kaynakla eklenmemiştir.", ST["p"]),
          Paragraph(", ".join(f"{esc(P[i]['ad'])} <font color='{MUTED}'>({yr_txt(P[i]['dogum'])}–{yr_txt(P[i]['olum'])})</font>"
                              for i in isolated), ST["small"]), PageBreak()]

    # Tablo 4: yazar–eser
    s += [Paragraph("Tablo 4 · Yazar–eser bağları", ST["h1"]),
          Paragraph(f"{len(works)} eserin tamamı, yazarların kronolojik sırasıyla.", ST["p"])]
    rows = [[Paragraph(f"<b>{h}</b>", ST["cell"]) for h in ("Yazar", "Eser", "Yıl", "Dil", "Tür")]]
    for p in sorted(people, key=lambda p: LIFE[p["id"]][0] or 0):
        for k, w in enumerate(works_by[p["id"]]):
            rows.append([Paragraph(f"<b>{esc(p['ad'])}</b>" if k == 0 else "", ST["cell"]), Paragraph(esc(w["ad_sade"]), ST["cell"]),
                         Paragraph(esc(yr_txt(w["yil"])), ST["cell"]), Paragraph(esc(w["dil"]), ST["cell"]), Paragraph(esc(w["tur"]), ST["cell"])])
    for w in works:
        if not w["yazar_id"]:
            rows.append([Paragraph("<i>Anonim</i>", ST["cell"]), Paragraph(esc(w["ad_sade"]), ST["cell"]), Paragraph(esc(yr_txt(w["yil"])), ST["cell"]),
                         Paragraph(esc(w["dil"]), ST["cell"]), Paragraph(esc(w["tur"]), ST["cell"])])
    t = Table(rows, colWidths=[36 * mm, 64 * mm, 20 * mm, 26 * mm, 32 * mm], repeatRows=1)
    t.setStyle(tstyle())
    s.append(t)
    return s


# ---------------------------------------------------------------- birleştirme
def stamp_numbers(writer, start_title):
    total = len(writer.pages)
    for i, page in enumerate(writer.pages):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(w, h))
        c.setFont("Sans", 7)
        c.setFillColor(colors.HexColor(MUTED))
        c.drawRightString(w - 12 * mm, 7 * mm, f"{i + 1} / {total}")
        c.drawString(12 * mm, 7 * mm, start_title)
        c.save()
        buf.seek(0)
        page.merge_page(PdfReader(buf).pages[0])


def main():
    tmp = OUT.parent / ".network_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    with PdfPages(tmp / "fig1.pdf") as pdf:
        fig_chronological(pdf)
    with PdfPages(tmp / "fig2.pdf") as pdf:
        fig_full(pdf)
    with PdfPages(tmp / "figt.pdf") as pdf:
        for i, (tur, _, _) in enumerate(TYPES, start=3):
            fig_by_type(pdf, i, tur)
    n_tab = build_rl(tmp / "tables.pdf", tables_story(), "İlişki Ağı – Tablolar")
    tab_reader = PdfReader(str(tmp / "tables.pdf"))
    # tablo başlangıç sayfalarını metinden bul
    starts = {}
    for i, pg in enumerate(tab_reader.pages):
        txt = pg.extract_text() or ""
        for k in ("Tablo 1", "Tablo 2", "Tablo 3", "Tablo 4"):
            if k not in starts and txt.lstrip().startswith(k):
                starts[k] = i

    def toc_for(cover_pages):
        base = cover_pages
        toc = [("Şekil 1 · Kronolojik ilişki ağı (A3)", base + 1),
               ("Şekil 2 · Tam ağ: kişiler, eserler, ilişkiler ve yazarlık (A2)", base + 2)]
        toc += [(f"Şekil {i} · {t} ilişkileri", base + i) for i, (t, _, _) in enumerate(TYPES, start=3)]
        tb = base + 2 + len(TYPES)
        names = {"Tablo 1": "Tablo 1 · İlişkilerin tam listesi", "Tablo 2": "Tablo 2 · Kişi bazında bağlantı dizini",
                 "Tablo 3": "Tablo 3 · Merkezîlik ölçüleri ve bileşenler", "Tablo 4": "Tablo 4 · Yazar–eser bağları"}
        toc += [(names[k], tb + v + 1) for k, v in sorted(starts.items(), key=lambda x: x[1])]
        return toc

    n_cover = build_rl(tmp / "cover.pdf", cover_story(toc_for(1)), "İlişki Ağı")
    n_cover = build_rl(tmp / "cover.pdf", cover_story(toc_for(n_cover)), "İlişki Ağı")
    toc = toc_for(n_cover)

    writer = PdfWriter()
    for f in ("cover.pdf", "fig1.pdf", "fig2.pdf", "figt.pdf", "tables.pdf"):
        for pg in PdfReader(str(tmp / f)).pages:
            writer.add_page(pg)
    stamp_numbers(writer, "Türk-İslam Atlası · İlişki Ağı")
    for title, page in toc:
        writer.add_outline_item(title, page - 1)
    writer.add_metadata({"/Title": "Türk-İslam Atlası – İlişki Ağı", "/Author": "Türk-İslam Atlası",
                         "/Subject": "750–1700 arası kişi ve eser ilişkileri"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "wb") as f:
        writer.write(f)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    print(f"{OUT.relative_to(ROOT) if OUT.is_relative_to(ROOT) else OUT}: {len(writer.pages)} sayfa, "
          f"{OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
