#!/usr/bin/env python3
"""İlişki ağını kapsamlı bir PDF olarak üretir: reports/iliski-agi.pdf

Kullanım:  pip install networkx scipy matplotlib reportlab pypdf
           python3 scripts/network_pdf.py [çıktı.pdf]

İçerik: kapak ve okuma kılavuzu, kronolojik ağ (A2), tam ağ (A2), her ilişki türü için ayrı ağ,
ilişkilerin tam listesi, kişi bazında bağlantı dizini, merkezîlik ölçüleri, yazar–eser listesi.
"""
import io
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import date
from functools import lru_cache
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.text as mtext  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402
from matplotlib.textpath import TextToPath  # noqa: E402
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
    ("yayımladı", "#be185d", "Yayımlayan / basan → eser"),
    ("iş birliği", "#65a30d", "İş birliği (yönsüz)"),
]
UNDIRECTED = {"çağdaş-tartışma", "iş birliği"}
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


# Bütün şekiller milimetre koordinatında çizilir (eksen = sayfanın tamamı, y aşağı doğru artar).
# Etiket genişlikleri yazı tipinden ölçülür; her şekil kaydedilmeden önce metin çakışmaları denetlenir.
_TTP = TextToPath()
PT_MM = 25.4 / 72
FS_P, FS_W = 7.0, 6.2  # kişi ve eser etiketlerinin punto büyüklüğü


@lru_cache(maxsize=None)
def text_mm(s, fs, italic=False, bold=False):
    """Metnin (genişlik, yükseklik) değeri, mm."""
    fp = FontProperties(family="DejaVu Sans", size=fs, style="italic" if italic else "normal",
                        weight="bold" if bold else "normal")
    w, h, d = _TTP.get_text_width_height_descent(s, fp, ismath=False)
    return w * PT_MM, (h + d) * PT_MM


AUDIT = []  # (şekil adı, çakışma sayısı)


def audit(fig, label):
    """Görünür bütün metinlerin kutularını karşılaştırır; çakışan ve sayfadan taşan metinleri sayar."""
    fig.canvas.draw()
    rnd = fig.canvas.get_renderer()
    page = fig.bbox
    items = []
    for t in fig.findobj(mtext.Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        bb = t.get_window_extent(rnd)
        items.append((t.get_text(), bb))
    bad = []
    for i in range(len(items)):
        a, A = items[i]
        if A.x0 < page.x0 - 0.5 or A.x1 > page.x1 + 0.5 or A.y0 < page.y0 - 0.5 or A.y1 > page.y1 + 0.5:
            bad.append((a, "sayfa dışı"))
        for j in range(i + 1, len(items)):
            b, B = items[j]
            ix = min(A.x1, B.x1) - max(A.x0, B.x0)
            iy = min(A.y1, B.y1) - max(A.y0, B.y0)
            if ix > 0.5 and iy > 0.5:
                bad.append((a, b))
    AUDIT.append((label, len(items), bad))
    return bad


def page_fig(W_, H_):
    fig = plt.figure(figsize=(W_ * MM, H_ * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_)
    ax.set_ylim(H_, 0)
    ax.set_axis_off()
    return fig, ax


def title_block(ax, W_, title, sub, side=12):
    """Başlık ve alt yazı; alt yazı sayfa genişliğine göre satırlara bölünür. Döndürür: içeriğin başlayacağı y (mm)."""
    ax.text(side, 9, title, fontsize=17, fontweight="bold", color=INK, va="top", family="DejaVu Serif")
    lines, cur = [], ""
    for word in sub.split():
        cand = (cur + " " + word).strip()
        if text_mm(cand, 9)[0] > W_ - 2 * side and cur:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    lines.append(cur)
    y = 19
    for ln in lines:
        ax.text(side, y, ln, fontsize=9, color=MUTED, va="top")
        y += 4.4
    return y + 3


HALO = [pe.withStroke(linewidth=2.2, foreground="white")]


def legend_rows(ax, x, y, items, maxw, fs=7.5):
    """Göstergeyi elle çizer (çizgi örneği + metin), satıra sığmayanı alta alır. Döndürür: bitiş y."""
    cx = x
    for col, ls, lw, lab in items:
        w = 9 + text_mm(lab, fs)[0] + 6
        if cx + w > x + maxw and cx > x:
            cx, y = x, y + 4.6
        ax.plot([cx, cx + 7], [y, y], color=col, lw=lw, ls=ls, solid_capstyle="butt")
        ax.text(cx + 9, y, lab, fontsize=fs, va="center", color=INK)
        cx += w
    return y + 3


def type_legend_items(include_auth=False):
    it = [(c, "-", 2, lab) for _, c, lab in TYPES]
    if include_auth:
        it.append((AUTH_COL, "--", 1, "Yazar → eser"))
    it.append((MUTED, (0, (2, 2)), 1.2, "Kesikli: kaynakla teyit edilemedi"))
    return it


# ---------------------------------------------------------------- Şekil 1: dönemlere bölünmüş kronolojik ağ
ERAS = [("1a", "750–1250", -10**6, 1250), ("1b", "1250–1700", 1250, 1700), ("1c", "1700–1920", 1700, 10**6)]


def era_of(pid):
    lo, hi = LIFE[pid]
    m = (lo + hi) / 2
    return next(k for k, _, a, b in ERAS if a <= m < b)


def fig_chronological(pdf, key, span_label):
    members = [p for p in people if era_of(p["id"]) == key]
    ids = {p["id"] for p in members}
    edges = [e for e in person_edges if e["a"] in ids and e["b"] in ids]
    for W_, H_ in ((420, 297), (594, 420), (841, 594)):
        left, right, bottom = 44, 10, 22
        t0 = min(LIFE[i][0] for i in ids) - 8
        t1 = max(LIFE[i][1] for i in ids)
        aw = W_ - left - right
        lab = {i: text_mm(P[i]["ad"], FS_P) for i in ids}
        for _ in range(8):  # ölçek, en sağdaki etiket sayfaya sığana kadar
            s_ = aw / (t1 - t0)
            need = max(LIFE[i][1] + (2 + lab[i][0] + 2) / s_ for i in ids)
            if need <= t1 + 0.5:
                break
            t1 = need
        X = lambda yv: left + (yv - t0) * s_  # noqa: E731
        rows, lanes, nrow = {}, [], 0
        for g in meta["grup_sirasi"]:
            ms = sorted([p for p in members if pgroup(p) == g], key=lambda p: LIFE[p["id"]][0])
            if not ms:
                continue
            ends, top = [], nrow
            for p in ms:
                lo, hi = LIFE[p["id"]]
                a0, a1 = X(lo) - 1.5, X(hi) + 2 + lab[p["id"]][0]
                for k, e in enumerate(ends):
                    if e + 2.5 < a0:
                        ends[k] = a1
                        rows[p["id"]] = top + k
                        break
                else:
                    ends.append(a1)
                    rows[p["id"]] = top + len(ends) - 1
            nrow = top + len(ends)
            lanes.append((g, top, nrow))
        fig, ax = page_fig(W_, H_)
        y0 = title_block(ax, W_, f"Şekil {key} · Kronolojik ilişki ağı, {span_label}",
                         f"Ömrünün ortası bu döneme düşen {len(members)} kişi, devlet grubuna göre şeritlerde. Yatay çizgi ömrü, "
                         f"nokta ömrün ortasını gösterir. Oklar bu sayfadaki kişiler arasındaki {len(edges)} ilişkidir "
                         f"(eser üzerinden kurulanlar yazarına bağlanır ve kesikli çizilir). Başka dönem sayfasındaki kişilere "
                         f"uzanan ilişkiler Tablo 1'de listelenir.") + 6
        lane_gap = 2.6
        pitch = (H_ - y0 - bottom - lane_gap * len(lanes)) / max(nrow, 1)
        if pitch >= 4.2:
            break
        plt.close(fig)
    pitch = min(pitch, 7.0)
    Y, yy = {}, y0
    lane_box = []
    for g, a, b in lanes:
        top = yy
        for pid, r in rows.items():
            if a <= r < b:
                Y[pid] = top + (r - a + 0.5) * pitch
        yy = top + (b - a) * pitch + lane_gap
        lane_box.append((g, top, top + (b - a) * pitch))
    plot_bottom = yy
    # yıl ızgarası
    for t in range(int(math.ceil(t0 / 50) * 50), int(t1) + 1, 50):
        ax.plot([X(t), X(t)], [y0 - 2, plot_bottom], color=GRID, lw=0.6 if t % 100 == 0 else 0.4,
                ls="-" if t % 100 == 0 else (0, (2, 3)), zorder=0)
        if t % 100 == 0:
            ax.text(X(t), y0 - 2.6, str(t), fontsize=7, color=MUTED, ha="center", va="bottom")
    for g, a, b in lane_box:
        ax.add_patch(Rectangle((left - 2, a - 0.8), W_ - right - left + 2, b - a + 1.6, color=GCOL[g], alpha=0.09, lw=0, zorder=0))
        if g in DYN:
            d = DYN[g]
            xa, xb = X(max(d["baslangic"], t0)), X(min(d["bitis"], t1))
            if xb > xa:
                ax.plot([xa, xb], [a - 0.8, a - 0.8], color=GCOL[g], lw=2.4, alpha=0.8, solid_capstyle="butt", zorder=1)
        gl = g if text_mm(g, 8, bold=True)[0] < left - 6 else g.replace(" ", "\n", 1)
        ax.text(left - 4, (a + b) / 2, gl, ha="right", va="center", fontsize=8, fontweight="bold",
                color=GCOL[g] if g != "Diğer" else MUTED, family="DejaVu Sans", linespacing=1.0)
    pos = {}
    for pid in ids:
        lo, hi = LIFE[pid]
        p = P[pid]
        pos[pid] = (X((lo + hi) / 2), Y[pid])
        dashed = p["tarih_kesinligi"] != "kesin" or p["dogum"] is None or p["olum"] is None
        ax.plot([X(lo), X(hi)], [Y[pid], Y[pid]], color=GCOL[pgroup(p)], lw=2.4, alpha=0.5, solid_capstyle="round",
                ls=(0, (3, 1.5)) if dashed else "-", zorder=2)
        ax.text(X(hi) + 2, Y[pid], p["ad"], fontsize=FS_P, va="center", ha="left", color=INK, zorder=6, path_effects=HALO)
    for e in edges:
        (x1, y1), (x2, y2) = pos[e["a"]], pos[e["b"]]
        rad = 0.3 if x2 >= x1 else -0.3
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
                                     arrowstyle="-" if e["tur"] in UNDIRECTED else "-|>", mutation_scale=8,
                                     color=TCOL[e["tur"]], lw=0.9, alpha=0.8, ls="--" if e["dogrulanamadi"] or e["via"] else "-",
                                     shrinkA=2, shrinkB=2, zorder=3))
    for pid in ids:
        x, y = pos[pid]
        ax.scatter([x], [y], s=10 + 4 * deg[pid], color=GCOL[pgroup(P[pid])], edgecolor="white", lw=0.5, zorder=4)
    items = type_legend_items() + [(MUTED, (0, (3, 1.5)), 2, "Kesikli ömür: yaklaşık, tartışmalı ya da tahmini")]
    ly = legend_rows(ax, left, H_ - bottom + 6, items, W_ - left - right - 70)
    ax.text(W_ - right, H_ - bottom + 6, "Nokta büyüklüğü = toplam ilişki sayısı", ha="right", va="center", fontsize=7, color=MUTED)
    del ly
    audit(fig, f"Şekil {key}")
    pdf.savefig(fig)
    plt.close(fig)


def cross_era_edges():
    out = []
    for e in person_edges:
        ea, eb = era_of(e["a"]), era_of(e["b"])
        if ea != eb:
            out.append((e, ea, eb))
    return out


# ---------------------------------------------------------------- düğüm-etiket kutuları ve çakışma giderme
def node_box(n):
    """Düğüm noktasına göre etiket kutusu: (x0, x1, y0, y1) mm. Etiket düğümün altına ortalanır."""
    if n in P:
        w, h = text_mm(P[n]["ad"], FS_P)
        r = 1.6
    else:
        w, h = text_mm(W[n]["ad_sade"], FS_W, italic=True)
        r = 1.2
    hw = max(w / 2, r) + 0.8
    return (-hw, hw, -r - 0.4, r + 0.8 + h + 0.6)


def declutter(pos, margin=1.4, iters=4000):
    """Kutular çakışmayana kadar düğümleri en kısa eksende iter (eksenlere hizalı dikdörtgen itmesi)."""
    ids = list(pos)
    if len(ids) < 2:
        return pos
    xy = np.array([pos[i] for i in ids], dtype=float)
    bx = np.array([node_box(i) for i in ids])
    rng = np.random.default_rng(3)
    for _ in range(iters):
        x0, x1 = xy[:, 0] + bx[:, 0], xy[:, 0] + bx[:, 1]
        y0, y1 = xy[:, 1] + bx[:, 2], xy[:, 1] + bx[:, 3]
        ox = np.minimum(x1[:, None], x1[None, :]) - np.maximum(x0[:, None], x0[None, :]) + margin
        oy = np.minimum(y1[:, None], y1[None, :]) - np.maximum(y0[:, None], y0[None, :]) + margin
        hit = (ox > 0) & (oy > 0)
        np.fill_diagonal(hit, False)
        if not hit.any():
            break
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        dx = cx[:, None] - cx[None, :]
        dy = cy[:, None] - cy[None, :]
        dx[dx == 0] = rng.uniform(-0.1, 0.1, size=(dx == 0).sum())
        dy[dy == 0] = rng.uniform(-0.1, 0.1, size=(dy == 0).sum())
        alongx = ox < oy * 1.6  # yatay itme tercih edilir (etiketler geniş, alçak)
        mx = np.where(hit & alongx, np.sign(dx) * ox / 2, 0).sum(axis=1)
        my = np.where(hit & ~alongx, np.sign(dy) * oy / 2, 0).sum(axis=1)
        xy[:, 0] += np.clip(mx, -6, 6) * 0.6
        xy[:, 1] += np.clip(my, -6, 6) * 0.6
    return {i: tuple(xy[k]) for k, i in enumerate(ids)}


def boxes_extent(pos):
    xs0 = [pos[n][0] + node_box(n)[0] for n in pos]
    xs1 = [pos[n][0] + node_box(n)[1] for n in pos]
    ys0 = [pos[n][1] + node_box(n)[2] for n in pos]
    ys1 = [pos[n][1] + node_box(n)[3] for n in pos]
    return min(xs0), max(xs1), min(ys0), max(ys1)


def shift_to_origin(pos):
    x0, x1, y0, y1 = boxes_extent(pos)
    return {n: (x - x0, y - y0) for n, (x, y) in pos.items()}, x1 - x0, y1 - y0


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


def draw_graph(ax, nodes, pos, edges, rad=0.1):
    """pos: mm; etiketler düğümün altında, beyaz zeminli; kenarlar altta kalır."""
    for (a, b, d) in edges:
        t = d["tur"]
        col = AUTH_COL if t == "yazdı" else TCOL[t]
        ax.add_patch(FancyArrowPatch(pos[a], pos[b], connectionstyle=f"arc3,rad={rad}",
                                     arrowstyle="-" if t in UNDIRECTED or t == "yazdı" else "-|>", mutation_scale=8,
                                     color=col, lw=0.5 if t == "yazdı" else 1.0, alpha=0.6 if t == "yazdı" else 0.9,
                                     ls="--" if (t == "yazdı" or d.get("dog")) else "-", shrinkA=2.4, shrinkB=2.4, zorder=2))
    for n in nodes:
        x, y = pos[n]
        if n in P:
            ax.scatter([x], [y], s=16 + 3 * deg[n], color=GCOL[pgroup(P[n])], edgecolor="white", lw=0.6, zorder=3)
            ax.text(x, y + 2.0, P[n]["ad"], fontsize=FS_P, ha="center", va="top", color=INK, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none", alpha=0.85))
        else:
            ax.scatter([x], [y], s=13, marker="D", color="#efe9df", edgecolor=MUTED, lw=0.6, zorder=3)
            ax.text(x, y + 1.6, W[n]["ad_sade"], fontsize=FS_W, ha="center", va="top", color=MUTED, style="italic", zorder=5,
                    bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85))


def fill_page(pos, x0, y0, avail_w, avail_h, cap=1.8):
    """Paketlenmiş yerleşimi kullanılabilir alanı dolduracak biçimde büyütür. Yalnızca konumlar ölçeklenir,
    yazı boyutu sabit kalır; düğümler birbirinden uzaklaştığı için yeni çakışma oluşmaz."""
    ex = boxes_extent(pos)
    w, h = ex[1] - x0, ex[3] - y0
    f = max(1.0, min(cap, avail_w / max(w, 1), avail_h / max(h, 1)))
    return {n: (x0 + (x - x0) * f, y0 + (y - y0) * f) for n, (x, y) in pos.items()}


def tr_cap(s_):
    return ("İ" if s_[0] == "i" else s_[0].upper()) + s_[1:]


def choose_page(laid, top, side, bottom, gap):
    for W_, H_ in ((420, 297), (594, 420), (841, 594), (1189, 841)):
        packed, used = shelf_pack([(i, w, h) for i, _, w, h in laid], W_ - 2 * side, gap=gap)
        if used <= H_ - top - bottom and max(w for _, _, w, _ in laid) <= W_ - 2 * side:
            return W_, H_, packed
    return W_, H_, packed


# ---------------------------------------------------------------- Şekil 3–10: ilişki türleri, katmanlı
def layered(g):
    """Bir bileşen için katmanlı yerleşim: kaynaklar üstte; etiket genişlikleri ölçülür. Döndürür: pos (mm)."""
    cond = nx.condensation(g)
    depth = {}
    for c in nx.topological_sort(cond):
        preds = list(cond.predecessors(c))
        depth[c] = 1 + max(depth[q] for q in preds) if preds else 0
    nd = {n: depth[cond.graph["mapping"][n]] for n in g.nodes}
    layers = defaultdict(list)
    for n in sorted(g.nodes, key=lambda n: name(n)):
        layers[nd[n]].append(n)
    und = g.to_undirected()
    wid = lambda n: node_box(n)[1] - node_box(n)[0]  # noqa: E731
    xs = {}

    def place():
        for ns in layers.values():
            x = 0
            for n in ns:
                w = wid(n)
                xs[n] = x + w / 2
                x += w + 3

    place()
    for _ in range(6):  # barisentrik sıralama: kesişmeleri azaltır
        for L in sorted(layers):
            ns = layers[L]
            bc = {n: (sum(xs[m] for m in und.neighbors(n)) / und.degree(n)) if und.degree(n) else xs[n] for n in ns}
            layers[L] = sorted(ns, key=lambda n: bc[n])
        place()
    widths = {L: sum(wid(n) + 3 for n in ns) - 3 for L, ns in layers.items()}
    Wm = max(widths.values())
    pos = {}
    for L, ns in layers.items():
        off = (Wm - widths[L]) / 2
        for n in ns:
            pos[n] = (xs[n] + off, L * 16.0)
    return pos


def fig_by_type(pdf, num, tur):
    es = [(r["kaynak"], r["hedef"], {"tur": tur, "dog": r.get("dogrulanamadi", False)}) for r in rels if r["tur"] == tur]
    g = nx.DiGraph()
    for a, b, d in es:
        g.add_edge(a, b, **d)
    comps = sorted(nx.weakly_connected_components(g), key=len, reverse=True)
    laid = []
    for i, c in enumerate(comps):
        p, w, h = shift_to_origin(layered(g.subgraph(c)))
        laid.append((i, p, w, h))
    side, bottom, gap = 12, 18, 10
    top = 36
    W_, H_, packed = choose_page(laid, top, side, bottom, gap)
    fig, ax = page_fig(W_, H_)
    top = title_block(ax, W_, f"Şekil {num} · {tr_cap(tur)} ilişkileri",
                      f"{len(es)} ilişki, {g.number_of_nodes()} düğüm, {len(comps)} bağlı bileşen. Okuma yönü: {TLAB[tur]} "
                      f"(kaynak üstte, hedef altta). Daire kişi, elmas eserdir.")
    pos = {}
    for i, p, w, h in laid:
        ox, oy = packed[i]
        for n, (x, y) in p.items():
            pos[n] = (side + ox + x, top + oy + y)
    pos = fill_page(pos, side, top, W_ - 2 * side, H_ - top - bottom, cap=1.5)
    draw_graph(ax, g.nodes, pos, [(a, b, d) for a, b, d in g.edges(data=True)], rad=0.0)
    legend_rows(ax, side, H_ - 12, [(TCOL[tur], "-", 2, TLAB[tur]), (TCOL[tur], "--", 1.2, "Kesikli: teyit edilemedi")], W_ - 2 * side)
    audit(fig, f"Şekil {num}")
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------- Şekil 2: ilişki ağı (kişiler + ilişkili eserler)
def full_graph():
    H = nx.MultiDiGraph()
    rel_works = {n for r in rels for n in (r["kaynak"], r["hedef"]) if n in W}
    for r in rels:
        H.add_edge(r["kaynak"], r["hedef"], tur=r["tur"], dog=r.get("dogrulanamadi", False))
    for wid_ in rel_works:
        a = W[wid_]["yazar_id"]
        if a:
            H.add_edge(a, wid_, tur="yazdı", dog=False)
    return H, rel_works


def fig_full(pdf):
    H, rel_works = full_graph()
    und = nx.Graph(H.to_undirected())
    comps = sorted(nx.connected_components(und), key=len, reverse=True)
    laid = []
    for i, c in enumerate(comps):
        sub = und.subgraph(c)
        n = len(c)
        if n <= 3:
            p = {k: (j * 30.0, 0.0) for j, k in enumerate(sorted(c, key=lambda x: (x in W, name(x))))}
        else:
            p = nx.kamada_kawai_layout(sub)
            area = sum((node_box(k)[1] - node_box(k)[0]) * (node_box(k)[3] - node_box(k)[2]) for k in c) * 3.2
            xs = [v[0] for v in p.values()]
            ys = [v[1] for v in p.values()]
            sc = math.sqrt(area / max((max(xs) - min(xs)) * (max(ys) - min(ys)), 1e-6))
            p = {k: (v[0] * sc * 1.25, v[1] * sc) for k, v in p.items()}
        p = declutter(p)
        p, w, h = shift_to_origin(p)
        laid.append((i, p, w, h))
    side, bottom, gap = 12, 24, 10
    W_, H_, packed = choose_page(laid, 40, side, bottom, gap)
    fig, ax = page_fig(W_, H_)
    n_people = sum(1 for k in H.nodes if k in P)
    top = title_block(ax, W_, "Şekil 2 · İlişki ağı: kişiler ve ilişkili eserler",
                      f"En az bir ilişkisi olan {n_people} kişi (daire, renk = devlet grubu) ve bir ilişkiye konu olan "
                      f"{len(rel_works)} eser (elmas); {len(rels)} ilişki kenarı (renkli) ve bu eserlerin yazar bağları (gri kesikli). "
                      f"{len(comps)} bağlı bileşen, büyükten küçüğe. İlişkisi olmayan kişiler Tablo 4'te, bütün eserler Tablo 5'te listelenir.")
    pos = {}
    for i, p, w, h in laid:
        ox, oy = packed[i]
        for k, (x, y) in p.items():
            pos[k] = (side + ox + x, top + oy + y)
    pos = fill_page(pos, side, top, W_ - 2 * side, H_ - top - bottom)
    draw_graph(ax, H.nodes, pos, list(H.edges(data=True)), rad=0.08)
    legend_rows(ax, side, H_ - 16, type_legend_items(True), W_ - 2 * side)
    audit(fig, "Şekil 2")
    pdf.savefig(fig)
    plt.close(fig)


# ---------------------------------------------------------------- metin ve tablolar (reportlab)
FD = "/usr/share/fonts/truetype/dejavu/"
for n_, f_ in [("Sans", "DejaVuSans.ttf"), ("Sans-B", "DejaVuSans-Bold.ttf"), ("Serif", "DejaVuSerif.ttf"),
               ("Serif-B", "DejaVuSerif-Bold.ttf"), ("Sans-I", "DejaVuSans.ttf")]:
    pdfmetrics.registerFont(TTFont(n_, FD + f_))
# Eğik DejaVu Sans her sistemde yok; <i> düz yazıyla gösterilir.
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-B")
ST = {
    "h1": ParagraphStyle("h1", fontName="Serif-B", fontSize=22, leading=27, spaceAfter=6, textColor=colors.HexColor(INK)),
    "h2": ParagraphStyle("h2", fontName="Serif-B", fontSize=14, leading=18, spaceBefore=9, spaceAfter=5),
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
         Paragraph(f"{meta['zaman_araligi'][0]}–1900 yılları arasında Türk-İslam dünyasında kişiler ve eserler arasındaki hoca-öğrenci, "
                   "himaye, etki, tartışma, tercüme, şerh, yayın ve iş birliği ilişkilerinin tam dökümü.", ST["p"]),
         Spacer(1, 4 * mm)]
    n_auth = sum(1 for w in works if w["yazar_id"])
    stats = [["Kişi", str(len(people))], ["Eser", str(len(works))], ["İlişki", str(len(rels))],
             ["Yazar–eser bağı", str(n_auth)], ["Kişi düzeyine indirgenmiş ilişki", str(len(person_edges))],
             ["En az bir ilişkisi olan kişi", str(len(people) - len(isolated))],
             ["Teyit edilemeyen ilişki", str(sum(1 for r in rels if r.get("dogrulanamadi")))]]
    stats.append(["", ""])
    pairs = [stats[i] + stats[i + 1] for i in range(0, len(stats), 2)]
    t = Table([[Paragraph(a, ST["cell"]), Paragraph(f"<b>{b}</b>", ST["cell"]), Paragraph(c, ST["cell"]),
                Paragraph(f"<b>{d}</b>", ST["cell"])] for a, b, c, d in pairs], colWidths=[58 * mm, 18 * mm, 58 * mm, 18 * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e4ded3")),
                           ("ALIGN", (1, 0), (1, -1), "RIGHT"), ("ALIGN", (3, 0), (3, -1), "RIGHT")]))
    s += [t, Paragraph("İlişki türleri", ST["h2"])]
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
                    "eserin yazarına bağlanarak kesikli çizilir. Şekil 1 okunurluk için üç dönem sayfasına (750–1250, 1250–1700, "
                    "1700–1920) bölünmüştür; sayfalar arasında kalan ilişkiler Tablo 1'dedir.", ST["p"]),
          Paragraph("Kesikli kenarlar, veri setinde <i>dogrulanamadi</i> olarak işaretlenmiş, yani kaynakla teyit edilemeyen "
                    "ilişkilerdir. Etiket genişlikleri yazı tipinden ölçülerek yerleştirilmiştir; hiçbir şekilde yazılar üst üste "
                    "binmez. Şekiller vektöreldir; büyük sayfalar (A2–A1) yakınlaştırılarak okunur.", ST["p"]),
          Paragraph("Kaynak notu: Kişi ve eserler TDV İslâm Ansiklopedisi maddelerine bağlıdır. Her kaydın teyit durumu "
                    "atlasın doğrulama raporunda (reports/validation.md) ayrıntılı olarak verilmiştir.", ST["muted"]),
          Paragraph("İçindekiler", ST["h2"])]
    trow = [[Paragraph(esc(a), ST["cell"]), Paragraph(str(b), ST["cell"])] for a, b in toc]
    ttoc = Table(trow, colWidths=[150 * mm, 18 * mm])
    ttoc.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e4ded3")),
                              ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                              ("TOPPADDING", (0, 0), (-1, -1), 1.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2)]))
    s += [ttoc, Spacer(1, 3 * mm), Paragraph(f"Üretim tarihi: {date.today().isoformat()} · scripts/network_pdf.py", ST["muted"])]
    return s


def person_cell(i):
    return f"{esc(P[i]['ad'])} <font color='{MUTED}'>{yr_txt(P[i]['dogum'])}–{yr_txt(P[i]['olum'])}</font>"


def tables_story():
    cross = cross_era_edges()
    era_name = {k: f"Şekil {k} ({lab})" for k, lab, _, _ in ERAS}
    s = [Paragraph("Tablo 1 · Dönem sayfaları arasındaki ilişkiler", ST["h1"]),
         Paragraph(f"Şekil 1 okunur kalsın diye üç dönem sayfasına bölündü; her kişi ömrünün ortasının düştüğü sayfada yer alır. "
                   f"Uçları farklı sayfalarda kalan {len(cross)} kişi düzeyindeki ilişki burada listelenir (Şekil 2'de ise hepsi birlikte "
                   f"görünür).", ST["p"])]
    rows = [[Paragraph(f"<b>{h}</b>", ST["cell"]) for h in ("Kaynak", "Sayfa", "Hedef", "Sayfa", "Tür")]]
    for e, ea, eb in sorted(cross, key=lambda x: (x[1], LIFE[x[0]["a"]][0])):
        tur = e["tur"] + (f" (eser: {esc(W[e['via']]['ad_sade'])})" if e["via"] else "") + (" · teyitsiz" if e["dogrulanamadi"] else "")
        rows.append([Paragraph(person_cell(e["a"]), ST["cell"]), Paragraph(era_name[ea], ST["cell"]),
                     Paragraph(person_cell(e["b"]), ST["cell"]), Paragraph(era_name[eb], ST["cell"]),
                     Paragraph(f"{swatch(TCOL[e['tur']])} {tur}", ST["cell"])])
    t = Table(rows, colWidths=[42 * mm, 26 * mm, 42 * mm, 26 * mm, 42 * mm], repeatRows=1)
    t.setStyle(tstyle())
    s += [t, PageBreak(),
          Paragraph("Tablo 2 · İlişkilerin tam listesi", ST["h1"]),
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

    # Tablo 3: kişi bazında dizin
    s += [Paragraph("Tablo 3 · Kişi bazında bağlantı dizini", ST["h1"]),
          Paragraph("Her kişinin bütün ilişkileri ve eserleri, alfabetik sırayla. Parantez içindeki sayı, kişi düzeyindeki toplam "
                    "ilişki sayısıdır (derece).", ST["p"])]
    labels_out = {"hoca-öğrenci": "Öğrencileri", "himaye": "Himaye ettikleri", "etkiledi": "Etkiledikleri",
                  "çağdaş-tartışma": "Çağdaş/tartışma", "tercüme etti": "Tercüme ettikleri", "şerh yazdı": "Şerh ettikleri",
                  "yayımladı": "Yayımladıkları", "iş birliği": "Birlikte çalıştıkları"}
    labels_in = {"hoca-öğrenci": "Hocaları", "himaye": "Hamileri", "etkiledi": "Etkilendikleri",
                 "çağdaş-tartışma": "Çağdaş/tartışma", "tercüme etti": "Tercüme edenler", "şerh yazdı": "Şerh edenler",
                 "yayımladı": "Yayımlayanlar", "iş birliği": "Birlikte çalıştıkları"}
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
                  "Çağdaş/tartışma", "Birlikte çalıştıkları", "Tercüme ettikleri", "Tercüme edenler", "Şerh ettikleri",
                  "Şerh edenler", "Yayımladıkları", "Yayımlayanlar", "Eserleri üzerinden"]:
            if parts.get(k):
                lines.append(f"<font color='{MUTED}'>{k}:</font> " + "; ".join(dict.fromkeys(parts[k])))
        if ws:
            lines.append(f"<font color='{MUTED}'>Eserleri ({len(ws)}):</font> " + "; ".join(esc(w["ad_sade"]) for w in ws))
        if deg[pid] == 0:
            lines.append(f"<font color='{MUTED}'>Veri setinde başka bir kişiyle kayıtlı ilişkisi yok.</font>")
        s.append(KeepTogether([Paragraph("<br/>".join(lines), ST["small"]), Spacer(1, 2.2 * mm)]))
    s.append(PageBreak())

    # Tablo 4: merkezîlik
    s += [Paragraph("Tablo 4 · Merkezîlik ölçüleri", ST["h1"]),
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

    # Tablo 5: yazar–eser
    s += [Paragraph("Tablo 5 · Yazar–eser bağları", ST["h1"]),
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
        for key, lab, _, _ in ERAS:
            fig_chronological(pdf, key, lab)
    with PdfPages(tmp / "fig2.pdf") as pdf:
        fig_full(pdf)
    with PdfPages(tmp / "figt.pdf") as pdf:
        for i, (tur, _, _) in enumerate(TYPES, start=3):
            fig_by_type(pdf, i, tur)
    build_rl(tmp / "tables.pdf", tables_story(), "İlişki Ağı – Tablolar")
    tab_reader = PdfReader(str(tmp / "tables.pdf"))
    starts = {}  # tablo başlangıç sayfaları
    for i, pg in enumerate(tab_reader.pages):
        txt = (pg.extract_text() or "").lstrip()
        for k in ("Tablo 1 ", "Tablo 2 ", "Tablo 3 ", "Tablo 4 ", "Tablo 5 "):
            if k not in starts and txt.startswith(k):
                starts[k] = i
    sizes = {f: len(PdfReader(str(tmp / f)).pages) for f in ("fig1.pdf", "fig2.pdf", "figt.pdf")}

    def toc_for(cover_pages):
        pg = cover_pages + 1
        toc = []
        for key, lab, _, _ in ERAS:
            toc.append((f"Şekil {key} · Kronolojik ilişki ağı, {lab}", pg))
            pg += 1
        toc.append(("Şekil 2 · İlişki ağı: kişiler ve ilişkili eserler", pg))
        pg += sizes["fig2.pdf"]
        for i, (t, _, _) in enumerate(TYPES, start=3):
            toc.append((f"Şekil {i} · {tr_cap(t)} ilişkileri", pg))
            pg += 1
        names = {"Tablo 1 ": "Tablo 1 · Dönem sayfaları arasındaki ilişkiler", "Tablo 2 ": "Tablo 2 · İlişkilerin tam listesi",
                 "Tablo 3 ": "Tablo 3 · Kişi bazında bağlantı dizini", "Tablo 4 ": "Tablo 4 · Merkezîlik ölçüleri ve bileşenler",
                 "Tablo 5 ": "Tablo 5 · Yazar–eser bağları"}
        toc += [(names[k], pg + v) for k, v in sorted(starts.items(), key=lambda x: x[1])]
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
                         "/Subject": "750–1900 arası kişi ve eser ilişkileri"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "wb") as f:
        writer.write(f)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    print(f"{OUT.relative_to(ROOT) if OUT.is_relative_to(ROOT) else OUT}: {len(writer.pages)} sayfa, "
          f"{OUT.stat().st_size // 1024} KB")
    total = 0
    for label, n, bad in AUDIT:
        total += len(bad)
        print(f"  {label}: {n} metin, {len(bad)} çakışma" + (f" {bad[:3]}" if bad else ""))
    if total:
        sys.exit(f"{total} metin çakışması var")


if __name__ == "__main__":
    main()
