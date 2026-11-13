#!/usr/bin/env python3
"""
Parametrik Teknik Çizim Motoru (Blueprint Engine)
=================================================

Fotoğraf/raster kullanmadan, yalnız fiziksel ölçülerden (m, mm) 2B vektör teknik çizim üretir.
Çıktı: Streamlit'te doğrudan basılabilen `plotly.graph_objects.Figure`.

    ParametricCADDrawer().draw_munition_blueprint(length_m, diameter_mm, wingspan_m, category, guidance_type)
    ParametricCADDrawer().draw_platform_top_down(platform_name, stations_dict)
    ParametricCADDrawer().draw_target_symbology(target_category, blast_radius_m)
    ParametricCADDrawer().draw_munition_comparison(items)

NEYİN GERÇEK, NEYİN TEMSİLÎ OLDUĞU
----------------------------------
Ölçüye sadık : toplam uzunluk, gövde çapı, kanat açıklığı (verilmişse), platform uzunluğu ve kanat
               açıklığı, istasyonların yanal konumu, patlama/etki yarıçapları. Tüm görünüşler tek bir
               metre koordinat sisteminde ve eşit eksen ölçeğinde çizilir (4 m'lik gövde, 2 m'lik
               gövdenin ekranda tam 2 katıdır).
Temsilî      : burun/kuyruk profili, kanatçık kiriş ve ok açıları, uçak silüetinin ayrıntısı,
               istasyonların boyuna konumu. Bunlar kategoriye göre seçilen parametrik şablonlardır;
               gerçek dış hat (OML) verisi değildir. Kanat açıklığı verisi yoksa kanatçıklar kesik
               çizgiyle "tahmini" çizilir ve ölçülendirilmez.
Semboller    : MIL-STD-2525D / APP-6'dan ESİNLENEN sadeleştirilmiş çizimlerdir (düşman çerçevesi:
               baklava; tesis: üst çubuk; piyade: çapraz; zırhlı: oval; hava savunma: kubbe).
               Standartla birebir uyumlu bir sembol seti değildir.
"""

from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Tema: koyu blueprint
# ---------------------------------------------------------------------------
BG = "#0a1929"
GRID_MAJOR = "#1b3a5c"
GRID_MINOR = "#12283f"
CYAN = "#4dd0e1"
NEON = "#39ff14"
WHITE = "#eaf2f8"
AMBER = "#ffb000"
RED = "#ff3b3b"
MUTED = "#7f97ad"
FONT = "Consolas, 'Courier New', monospace"
LINE_W = 1.5

# Platform dış ölçüleri [m] (açık kaynak, yaklaşık) ve silüet şablonu.
# KAAN ve Kızılelma değerleri duyurulan yaklaşık ölçülerdir.
PLATFORM_GEOMETRY = {
    "F-16C Block 70": (15.03, 9.96, "swept"),
    "F-35A Lightning II": (15.70, 10.70, "swept"),
    "F-15E Strike Eagle": (19.43, 13.05, "swept"),
    "Eurofighter Typhoon": (15.96, 10.95, "delta"),
    "Rafale": (15.27, 10.90, "delta"),
    "Su-35S": (21.90, 15.30, "swept"),
    "KAAN": (21.00, 14.00, "swept"),
    "Bayraktar Kızılelma": (14.70, 10.00, "delta"),
    "Bayraktar Akıncı": (12.20, 20.00, "straight"),
    "Bayraktar TB2": (6.50, 12.00, "straight"),
}
# şablon: (gövde yarı genişliği/L, kök hücum kenarının burundan uzaklığı/L, kök kiriş/L, uç
# kiriş/L, hücum kenarı ok açısı°, kuyruk açıklığı/b)
PLANFORMS = {
    "swept": (0.055, 0.38, 0.34, 0.10, 40.0, 0.50),
    "delta": (0.055, 0.30, 0.50, 0.05, 50.0, 0.0),
    "straight": (0.040, 0.36, 0.13, 0.07, 3.0, 0.28),
}
STATUS_COLOR = {"ok": NEON, "warn": AMBER, "fail": RED, "collision": RED, "empty": MUTED}

SEEKER_DOME = ("IIR", "IR", "EO", "SAL", "Laser_Beam_Riding", "Command_Guidance")
SYMBOL_TEXT = {
    "Hardened_Structure": "HRD",
    "Soft_Structure": "INST",
    "Infrastructure": "INFRA",
    "Soft_Vehicle": "VEH",
    "Radar/Air_Defense": "AD",
    "Naval": "SHIP",
    "Personnel": "INF",
    "Armored_Vehicle": "ARM",
}


def _nan(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _nice_step(span: float) -> float:
    """Izgara aralığı: 1-2-5 dizisinden, görünen açıklığın yaklaşık onda biri."""
    raw = max(span, 1e-6) / 10.0
    power = 10 ** math.floor(math.log10(raw))
    for mult in (1, 2, 5, 10):
        if raw <= mult * power:
            return mult * power
    return 10 * power


def _fmt_len(metres: float) -> str:
    return f"{metres * 1000:.0f} mm" if metres < 1.0 else f"{metres:.2f} m"


# ---------------------------------------------------------------------------
# Parametrik mühimmat şablonu
# ---------------------------------------------------------------------------
def munition_style(category: str, guidance_type: str = "", propulsion: str = "") -> dict:
    """Kategori / güdüm / itki bilgisinden çizim şablonu seçer (temsilî profil parametreleri)."""
    category, guidance = str(category), str(guidance_type)
    dome = any(tok in SEEKER_DOME for tok in guidance.replace("+", "/").split("/"))
    if category == "Bunker_Buster" or "Penetrator" in category:
        return dict(
            key="penetrator",
            nose="cone",
            nose_len=("D", 2.4),
            tail_len=0.16,
            base=0.72,
            wing="cruciform_tail",
            label="delici: sivri burun konisi",
        )
    if category in ("GP_Bomb",) or guidance == "Unguided":
        return dict(
            key="gp_bomb",
            nose="ogive",
            nose_len=("L", 0.30),
            tail_len=0.34,
            base=0.38,
            wing="cruciform_tail",
            label="GP bomba formu",
        )
    if category in ("ALCM", "AShM") or propulsion in ("Turbojet", "Turbofan"):
        return dict(
            key="cruise",
            nose="ellipse",
            nose_len=("D", 0.9),
            tail_len=0.10,
            base=0.62,
            wing="planar_swept",
            label="seyir füzesi: küt burun, açılır ok kanat",
        )
    if category in ("PGM_Glide", "Micro_PGM", "Loitering"):
        return dict(
            key="glide",
            nose="ellipse" if dome else "ogive",
            nose_len=("D", 1.0 if dome else 2.0),
            tail_len=0.10,
            base=0.70,
            wing="planar_straight",
            label="süzülen mühimmat: açılır düz kanat",
        )
    if category == "PGM_Laser_INS":
        return dict(
            key="guided_bomb",
            nose="ellipse" if dome else "ogive",
            nose_len=("L", 0.22),
            tail_len=0.26,
            base=0.45,
            wing="cruciform_tail",
            label="güdüm kitli bomba",
        )
    return dict(
        key="missile",
        nose="ellipse" if dome else "ogive",
        nose_len=("D", 0.7 if dome else 2.6),
        tail_len=0.0,
        base=1.0,
        wing="cruciform_tail",
        label="füze: " + ("arayıcı kubbesi" if dome else "ojiv radom"),
    )


def body_profile(length: float, diameter: float, style: dict, n: int = 40) -> tuple[np.ndarray, np.ndarray]:
    """Burun ucundan (x=0) kuyruğa (x=L) gövde yarıçapı r(x). Uzunluk ve azami çap veriye sadıktır."""
    radius = diameter / 2.0
    kind, value = style["nose_len"]
    nose = min(value * (length if kind == "L" else diameter), 0.45 * length)
    tail = style["tail_len"] * length
    t = np.linspace(0.0, 1.0, n)
    if style["nose"] == "cone":
        r_nose = radius * t
    elif style["nose"] == "ellipse":
        r_nose = radius * np.sqrt(1.0 - (1.0 - t) ** 2)
    else:  # ojiv (parabolik yaklaşım)
        r_nose = radius * (1.0 - (1.0 - t) ** 2)
    xs = list(nose * t)
    rs = list(r_nose)
    xs.append(length - tail)
    rs.append(radius)
    if tail > 0:
        xs.append(length)
        rs.append(radius * style["base"])
    return np.array(xs), np.array(rs)


def _radius_at(xs: np.ndarray, rs: np.ndarray, x: float) -> float:
    return float(np.interp(x, xs, rs))


def fin_sets(length: float, diameter: float, wingspan: float | None, style: dict) -> list[dict]:
    """Kanat/kanatçık takımları. 'estimated' = açıklık verisi yok, temsilî (kesik çizgi)."""
    known = not _nan(wingspan) and wingspan > diameter
    span = float(wingspan) if known else 1.5 * diameter
    wing = style["wing"]
    sets: list[dict] = []
    if wing == "cruciform_tail":
        root = 0.16 * length
        sets.append(
            dict(
                name="kuyruk kanatçıkları",
                x0=length - root - 0.01 * length,
                root=root,
                tip=0.45 * root,
                sweep=0.45 * root,
                span=span,
                cruciform=True,
                estimated=not known,
            )
        )
    else:
        swept = wing == "planar_swept"
        root = (0.13 if swept else 0.10) * length
        sweep = math.tan(math.radians(25.0 if swept else 0.0)) * (span - diameter) / 2.0
        sets.append(
            dict(
                name="ana kanat",
                x0=0.42 * length,
                root=root,
                tip=0.6 * root,
                sweep=sweep,
                span=span,
                cruciform=False,
                estimated=not known,
            )
        )
        tail_root = 0.09 * length
        sets.append(
            dict(
                name="kuyruk kanatçıkları",
                x0=length - tail_root - 0.01 * length,
                root=tail_root,
                tip=0.5 * tail_root,
                sweep=0.4 * tail_root,
                span=min(1.7 * diameter, span),
                cruciform=True,
                estimated=True,
            )
        )
    return sets


def munition_geometry(
    length_m: float,
    diameter_mm: float,
    wingspan_m: float | None,
    category: str,
    guidance_type: str = "",
    propulsion: str = "",
) -> dict:
    """Çizimden bağımsız geometri: gövde profili, kanat poligonları ve sınır kutuları (metre)."""
    if _nan(length_m) or _nan(diameter_mm) or length_m <= 0 or diameter_mm <= 0:
        raise ValueError("Teknik çizim için uzunluk ve çap gerekli (NA olamaz)")
    length, diameter = float(length_m), float(diameter_mm) / 1000.0
    style = munition_style(category, guidance_type, propulsion)
    xs, rs = body_profile(length, diameter, style)
    fins = fin_sets(length, diameter, wingspan_m, style)
    polys = []
    for fin in fins:
        r_front, r_back = _radius_at(xs, rs, fin["x0"]), _radius_at(xs, rs, fin["x0"] + fin["root"])
        half = fin["span"] / 2.0
        tip_x0 = fin["x0"] + fin["sweep"]
        poly = np.array(
            [
                [fin["x0"], r_front],
                [tip_x0, half],
                [min(tip_x0 + fin["tip"], length), half],
                [fin["x0"] + fin["root"], r_back],
            ]
        )
        polys.append((fin, poly))
    top_half = max([diameter / 2.0] + [f["span"] / 2.0 for f in fins])
    side_half = max([diameter / 2.0] + [f["span"] / 2.0 for f in fins if f["cruciform"]])
    span_known = [f["span"] for f in fins if not f["estimated"]]
    return dict(
        length=length,
        diameter=diameter,
        style=style,
        xs=xs,
        rs=rs,
        fins=polys,
        top_half=top_half,
        side_half=side_half,
        span=max(span_known) if span_known else None,
    )


# ---------------------------------------------------------------------------
# Çizim sınıfı
# ---------------------------------------------------------------------------
class ParametricCADDrawer:
    """Koyu blueprint temalı 2B ortografik çizim üreticisi (Plotly)."""

    def __init__(self, height: int = 620):
        self.height = height

    # -- temel yardımcılar ---------------------------------------------------
    def _figure(
        self, x_range: tuple[float, float], y_range: tuple[float, float], zoom: float = 1.0, height: int | None = None
    ) -> go.Figure:
        cx, cy = sum(x_range) / 2.0, sum(y_range) / 2.0
        half_x, half_y = (x_range[1] - x_range[0]) / 2.0 / zoom, (y_range[1] - y_range[0]) / 2.0 / zoom
        step = _nice_step(2 * max(half_x, half_y))
        axis = dict(
            showgrid=True,
            gridcolor=GRID_MAJOR,
            gridwidth=1,
            dtick=step,
            zeroline=False,
            minor=dict(showgrid=True, gridcolor=GRID_MINOR, dtick=step / 5.0),
            tickfont=dict(family=FONT, size=10, color=MUTED),
            ticksuffix=" m",
            showline=True,
            linecolor=GRID_MAJOR,
            mirror=True,
        )
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            height=height or self.height,
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family=FONT, color=WHITE, size=12),
            dragmode="pan",
            xaxis=dict(range=[cx - half_x, cx + half_x], constrain="domain", **axis),
            yaxis=dict(range=[cy - half_y, cy + half_y], scaleanchor="x", scaleratio=1, constrain="domain", **axis),
        )
        return fig

    @staticmethod
    def _line(fig: go.Figure, x, y, color=CYAN, width=LINE_W, dash=None, fill=None, name=None) -> None:
        fig.add_trace(
            go.Scatter(
                x=list(x),
                y=list(y),
                mode="lines",
                line=dict(color=color, width=width, dash=dash),
                fill="toself" if fill else None,
                fillcolor=fill,
                hoverinfo="name" if name else "skip",
                name=name or "",
            )
        )

    @staticmethod
    def _text(
        fig: go.Figure,
        x: float,
        y: float,
        text: str,
        color=WHITE,
        size=11,
        anchor="center",
        yanchor="middle",
        angle=0,
        bg=BG,
    ) -> None:
        fig.add_annotation(
            x=x,
            y=y,
            text=text,
            showarrow=False,
            font=dict(family=FONT, size=size, color=color),
            xanchor=anchor,
            yanchor=yanchor,
            textangle=angle,
            bgcolor=bg,
            borderpad=2,
        )

    def _dimension(
        self, fig: go.Figure, p1: tuple[float, float], p2: tuple[float, float], offset: float, text: str, color=AMBER
    ) -> None:
        """Mühendislik ölçü çizgisi: uzatma çizgileri + çift oklu ölçü çizgisi + |<-- değer -->| etiketi."""
        (x1, y1), (x2, y2) = p1, p2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        ux, uy = dx / dist, dy / dist
        nx, ny = -uy, ux
        a = (x1 + nx * offset, y1 + ny * offset)
        b = (x2 + nx * offset, y2 + ny * offset)
        over = 0.12 * abs(offset) * (1 if offset >= 0 else -1)
        xs = [x1, a[0] + nx * over, None, x2, b[0] + nx * over, None, a[0], b[0]]
        ys = [y1, a[1] + ny * over, None, y2, b[1] + ny * over, None, a[1], b[1]]
        self._line(fig, xs, ys, color=color, width=1.0)
        head = min(0.05 * dist, 0.35 * abs(offset))
        for (px, py), sign in ((a, 1), (b, -1)):
            tip = (px, py)
            base = (px + sign * ux * head, py + sign * uy * head)
            wing = 0.28 * head
            self._line(
                fig,
                [tip[0], base[0] + nx * wing, base[0] - nx * wing, tip[0]],
                [tip[1], base[1] + ny * wing, base[1] - ny * wing, tip[1]],
                color=color,
                width=1.0,
                fill=color,
            )
        self._text(
            fig,
            (a[0] + b[0]) / 2,
            (a[1] + b[1]) / 2,
            f"|&lt;— {text} —&gt;|",
            color=color,
            size=11,
            angle=-90 if abs(ux) < 0.5 else 0,
        )

    # -- mühimmat görünüşleri ------------------------------------------------
    def _draw_longitudinal(
        self,
        fig: go.Figure,
        geo: dict,
        x0: float,
        y0: float,
        view: str,
        color=CYAN,
        along_y: bool = False,
        show_centerline: bool = True,
    ) -> None:
        """Yan ('side') ya da üst ('top') görünüş. along_y=True → burun +y yönünde (platform üstten görünüşü)."""
        xs, rs, length = geo["xs"], geo["rs"], geo["length"]

        def place(px, py):
            px, py = np.asarray(px, dtype=float), np.asarray(py, dtype=float)
            return (x0 + py, y0 - px) if along_y else (x0 + px, y0 + py)

        outline_x = np.concatenate([xs, xs[::-1], xs[:1]])
        outline_y = np.concatenate([rs, -rs[::-1], rs[:1]])
        self._line(fig, *place(outline_x, outline_y), color=color, fill="rgba(77,208,225,.06)")
        for fin, poly in geo["fins"]:
            visible = view == "top" or fin["cruciform"]
            dash = "dot" if fin["estimated"] else None
            if visible:
                for sign in (1, -1):
                    px = np.append(poly[:, 0], poly[0, 0])
                    py = sign * np.append(poly[:, 1], poly[0, 1])
                    self._line(fig, *place(px, py), color=NEON, dash=dash, fill="rgba(57,255,20,.07)")
            else:  # düzlem kanat yandan: kenardan görünüş
                self._line(fig, *place([fin["x0"], fin["x0"] + fin["root"]], [0, 0]), color=NEON, width=2.5, dash=dash)
        if geo["style"]["nose"] == "ellipse":  # arayıcı kubbesi ayrım çizgisi
            xn = xs[len(xs) - (3 if geo["style"]["tail_len"] > 0 else 2)]
            rn = _radius_at(xs, rs, xn)
            self._line(fig, *place([xn, xn], [-rn, rn]), color=color, width=1.0)
        if show_centerline:
            ext = 0.04 * length
            self._line(fig, *place([-ext, length + ext], [0, 0]), color=WHITE, width=0.8, dash="dashdot")

    def _draw_front(self, fig: go.Figure, geo: dict, x0: float, y0: float) -> None:
        theta = np.linspace(0, 2 * math.pi, 73)
        radius = geo["diameter"] / 2.0
        self._line(fig, x0 + radius * np.cos(theta), y0 + radius * np.sin(theta), fill="rgba(77,208,225,.06)")
        for fin, _ in geo["fins"]:
            half, dash = fin["span"] / 2.0, "dot" if fin["estimated"] else None
            self._line(
                fig,
                [x0 - half, x0 - radius, None, x0 + radius, x0 + half],
                [y0, y0, None, y0, y0],
                color=NEON,
                dash=dash,
            )
            if fin["cruciform"]:
                self._line(
                    fig,
                    [x0, x0, None, x0, x0],
                    [y0 - half, y0 - radius, None, y0 + radius, y0 + half],
                    color=NEON,
                    dash=dash,
                )
        ext = 1.25 * max(geo["top_half"], radius)
        self._line(
            fig,
            [x0 - ext, x0 + ext, None, x0, x0],
            [y0, y0, None, y0 - ext, y0 + ext],
            color=WHITE,
            width=0.8,
            dash="dashdot",
        )

    def draw_munition_blueprint(
        self,
        length_m: float,
        diameter_mm: float,
        wingspan_m: float | None,
        category: str,
        guidance_type: str = "",
        name: str = "",
        propulsion: str = "",
        show_dimensions: bool = True,
        zoom: float = 1.0,
    ) -> go.Figure:
        """Yan, üst ve ön görünüş; tek ölçekte (eksenler eşit), ölçü çizgileriyle."""
        geo = munition_geometry(length_m, diameter_mm, wingspan_m, category, guidance_type, propulsion)
        length, dia = geo["length"], geo["diameter"]
        gap = 0.10 * length + 0.25
        y_side = geo["side_half"] + gap / 2.0
        y_top = -(geo["top_half"] + gap / 2.0)
        x_front = length + gap + geo["top_half"]
        pad = 0.04 * length + 0.1
        fig = self._figure(
            (-pad - gap * 0.6, x_front + geo["top_half"] + pad + gap * 0.5),
            (
                y_top - geo["top_half"] - pad - gap * 0.3,
                y_side + max(geo["side_half"], 1.25 * geo["top_half"]) + 0.9 * gap,
            ),
            zoom,
        )
        self._draw_longitudinal(fig, geo, 0.0, y_side, "side")
        self._draw_longitudinal(fig, geo, 0.0, y_top, "top")
        self._draw_front(fig, geo, x_front, y_side)
        label_dy = 0.5 * gap
        self._text(fig, 0, y_side + geo["side_half"] + label_dy, "YAN GÖRÜNÜŞ", MUTED, 11, "left")
        self._text(fig, 0, y_top + geo["top_half"] + label_dy * 0.55, "ÜST GÖRÜNÜŞ", MUTED, 11, "left")
        self._text(fig, x_front, y_side + 1.25 * geo["top_half"] + 0.5 * label_dy, "ÖN GÖRÜNÜŞ", MUTED, 11)
        if show_dimensions:
            off = geo["side_half"] + 0.28 * gap
            self._dimension(fig, (0, y_side), (length, y_side), -off, _fmt_len(length))
            self._dimension(
                fig,
                (x_front + geo["top_half"], y_side - dia / 2),
                (x_front + geo["top_half"], y_side + dia / 2),
                -0.45 * gap,
                f"Ø {dia * 1000:.0f} mm",
            )
            if geo["span"]:
                self._dimension(
                    fig, (0, y_top - geo["span"] / 2), (0, y_top + geo["span"] / 2), 0.45 * gap, _fmt_len(geo["span"])
                )
        span_txt = _fmt_len(geo["span"]) if geo["span"] else "NA (kanatçık tahmini, kesik çizgi)"
        block = (
            f"<b>{name or 'MÜHİMMAT'}</b><br>L = {_fmt_len(length)} · Ø = {dia * 1000:.0f} mm<br>"
            f"KANAT AÇIKLIĞI = {span_txt}<br>{category} · {guidance_type or '-'}<br>"
            f"ŞABLON: {geo['style']['label']}<br>ÖLÇEK: eksenler eşit (1:1 oran)"
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.995,
            y=0.01,
            xanchor="right",
            yanchor="bottom",
            text=block,
            showarrow=False,
            align="left",
            font=dict(family=FONT, size=11, color=WHITE),
            bordercolor=CYAN,
            borderwidth=1,
            borderpad=6,
            bgcolor="rgba(10,25,41,.9)",
        )
        return fig

    def draw_munition_comparison(self, items: list[dict], show_dimensions: bool = True, zoom: float = 1.0) -> go.Figure:
        """Birden çok mühimmatın yan görünüşü, ortak ölçekte alt alta (oran doğrulaması için)."""
        geos = [
            (
                it.get("name", ""),
                munition_geometry(
                    it["length_m"],
                    it["diameter_mm"],
                    it.get("wingspan_m"),
                    it.get("category", ""),
                    it.get("guidance_type", ""),
                    it.get("propulsion", ""),
                ),
            )
            for it in items
        ]
        longest = max(g["length"] for _, g in geos)
        gap = 0.08 * longest + 0.3
        y, rows = 0.0, []
        for name, geo in geos:
            y -= geo["side_half"]
            rows.append((name, geo, y))
            y -= geo["side_half"] + gap
        pad = 0.08 * longest + 0.2
        fig = self._figure(
            (-pad, longest + pad), (y - pad * 0.2, gap + pad * 0.3), zoom, height=max(260, int(150 * len(geos) + 80))
        )
        for name, geo, yc in rows:
            self._draw_longitudinal(fig, geo, 0.0, yc, "side")
            self._text(fig, 0, yc + geo["side_half"] + 0.3 * gap, name, WHITE, 11, "left")
            if show_dimensions:
                self._dimension(
                    fig, (0, yc), (geo["length"], yc), -(geo["side_half"] + 0.3 * gap), _fmt_len(geo["length"])
                )
        return fig

    # -- platform üstten görünüş --------------------------------------------
    @staticmethod
    def platform_planform(platform_name: str, geometry: tuple | None = None) -> dict:
        """Silüet poligonları ve kanat kiriş fonksiyonu. x: yanal [m], y: boyuna [m] (burun +y)."""
        length, span, kind = geometry or PLATFORM_GEOMETRY.get(platform_name, (15.0, 10.0, "swept"))
        fus, le_root, c_root, c_tip, sweep, tail_span = PLANFORMS[kind]
        half, w = span / 2.0, fus * length
        nose_y, tail_y = length / 2.0, -length / 2.0
        fuselage = np.array(
            [
                [0, nose_y],
                [0.45 * w, nose_y - 0.10 * length],
                [w, nose_y - 0.28 * length],
                [w, tail_y + 0.08 * length],
                [0.7 * w, tail_y],
                [-0.7 * w, tail_y],
                [-w, tail_y + 0.08 * length],
                [-w, nose_y - 0.28 * length],
                [-0.45 * w, nose_y - 0.10 * length],
                [0, nose_y],
            ]
        )
        y_le_root = nose_y - le_root * length
        y_le_tip = y_le_root - math.tan(math.radians(sweep)) * (half - w)
        y_te_root, y_te_tip = y_le_root - c_root * length, y_le_tip - c_tip * length
        if kind == "delta":
            y_te_tip = max(y_te_tip, y_te_root)
        wing = np.array([[w, y_le_root], [half, y_le_tip], [half, y_te_tip], [w, y_te_root]])
        polys = [fuselage, wing, wing * [-1, 1]]
        if tail_span > 0:
            th, yt = tail_span * half, tail_y + 0.16 * length
            tail = np.array(
                [[0.7 * w, yt], [th, yt - 0.06 * length], [th, yt - 0.10 * length], [0.7 * w, tail_y + 0.03 * length]]
            )
            polys += [tail, tail * [-1, 1]]
        if kind == "delta":
            yc = nose_y - 0.24 * length
            canard = np.array(
                [
                    [w * 0.9, yc],
                    [0.30 * half, yc - 0.05 * length],
                    [0.30 * half, yc - 0.08 * length],
                    [w * 0.9, yc - 0.07 * length],
                ]
            )
            polys += [canard, canard * [-1, 1]]

        def chord_at(x_abs: float) -> tuple[float, float]:
            """Yanal konumda (hücum kenarı y, firar kenarı y)."""
            t = float(np.clip((abs(x_abs) - w) / max(half - w, 1e-6), 0.0, 1.0))
            return y_le_root + t * (y_le_tip - y_le_root), y_te_root + t * (y_te_tip - y_te_root)

        return dict(length=length, span=span, kind=kind, polys=polys, chord_at=chord_at, fus_half=w)

    def draw_platform_top_down(
        self,
        platform_name: str,
        stations_dict: dict,
        show_dimensions: bool = True,
        zoom: float = 1.0,
        geometry: tuple | None = None,
        height: int | None = None,
    ) -> go.Figure:
        """Üstten yükleme planı. Mühimmatlar istasyonlara GERÇEK boyutlarıyla, aynı ölçekte yerleştirilir.

        stations_dict: {istasyon_id: {"x_norm": -1..1 (yanal konum / yarı açıklık), "kind": "wing|wingtip|
                        fuselage|internal", "label": str, "status": "ok|warn|fail|empty",
                        "munition": None | {"name", "length_m", "diameter_mm", "wingspan_m", "category",
                                            "guidance_type", "propulsion"}}}
        Bitişik istasyonlardaki mühimmatların üstten izleri kesişirse "collision" olarak kırmızı çizilir.
        Dönen figürün `layout.meta` alanında {"collisions": [...], "undrawn": [...]} bulunur.
        """
        plan = self.platform_planform(platform_name, geometry)
        half, length = plan["span"] / 2.0, plan["length"]
        pad = 0.10 * max(plan["span"], length)
        fig = self._figure((-half - pad, half + pad), (-length / 2 - pad, length / 2 + pad), zoom, height)
        for poly in plan["polys"]:
            self._line(fig, poly[:, 0], poly[:, 1], color=WHITE, width=1.2, fill="rgba(234,242,248,.04)")
        self._line(
            fig, [0, 0], [-length / 2 - 0.4 * pad, length / 2 + 0.4 * pad], color=WHITE, width=0.8, dash="dashdot"
        )

        placed, undrawn = [], []
        for sid, stn in stations_dict.items():
            x = float(stn["x_norm"]) * half
            y_le, y_te = plan["chord_at"](x)
            y_ref = y_le - 0.35 * (y_le - y_te)
            if stn.get("kind") in ("fuselage", "internal"):
                x = float(np.clip(x, -plan["fus_half"] * 2.2, plan["fus_half"] * 2.2))
            mun, geo = stn.get("munition"), None
            if mun:
                try:
                    geo = munition_geometry(
                        mun.get("length_m"),
                        mun.get("diameter_mm"),
                        mun.get("wingspan_m"),
                        mun.get("category", ""),
                        mun.get("guidance_type", ""),
                        mun.get("propulsion", ""),
                    )
                except ValueError:
                    undrawn.append(f"{sid}: {mun.get('name', '?')} (uzunluk/çap verisi yok)")
            placed.append(dict(sid=sid, x=x, y_ref=y_ref, stn=stn, geo=geo, status=stn.get("status", "empty")))

        collisions = []
        loaded = sorted([p for p in placed if p["geo"]], key=lambda p: p["x"])
        for a, b in zip(loaded, loaded[1:]):
            if abs(a["x"] - b["x"]) < 1e-6 and {a["stn"].get("kind"), b["stn"].get("kind")} == {"internal"}:
                continue
            overlap = a["geo"]["top_half"] + b["geo"]["top_half"] - (b["x"] - a["x"])
            y_a = (a["y_ref"] + 0.45 * a["geo"]["length"], a["y_ref"] - 0.55 * a["geo"]["length"])
            y_b = (b["y_ref"] + 0.45 * b["geo"]["length"], b["y_ref"] - 0.55 * b["geo"]["length"])
            if overlap > 0 and min(y_a[0], y_b[0]) > max(y_a[1], y_b[1]):
                collisions.append(f"{a['sid']} - {b['sid']}: {overlap * 1000:.0f} mm kesişme")
                a["status"] = b["status"] = "collision"

        for p in placed:
            color = STATUS_COLOR.get(p["status"], MUTED)
            internal = p["stn"].get("kind") == "internal"
            fig.add_trace(
                go.Scatter(
                    x=[p["x"]],
                    y=[p["y_ref"]],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=color,
                        symbol="diamond-open" if internal else "circle-open",
                        line=dict(width=1.5, color=color),
                    ),
                    hovertemplate=f"<b>{p['sid']}</b> · {p['stn'].get('label', '')}<br>"
                    f"{(p['stn'].get('munition') or {}).get('name', 'boş')}<extra></extra>",
                )
            )
            if p["geo"]:
                nose_y = p["y_ref"] + 0.45 * p["geo"]["length"]
                self._draw_longitudinal(
                    fig, p["geo"], p["x"], nose_y, "top", color=color, along_y=True, show_centerline=False
                )
            self._text(
                fig,
                p["x"],
                p["y_ref"] + (0.45 * p["geo"]["length"] if p["geo"] else 0) + 0.035 * length,
                p["sid"],
                color,
                10,
                yanchor="bottom",
                bg="rgba(10,25,41,.6)",
            )
        if show_dimensions:
            self._dimension(fig, (-half, -length / 2), (half, -length / 2), -0.55 * pad, _fmt_len(plan["span"]))
            self._dimension(fig, (-half, -length / 2), (-half, length / 2), 0.55 * pad, _fmt_len(length))
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.995,
            y=0.99,
            xanchor="right",
            yanchor="top",
            showarrow=False,
            align="left",
            font=dict(family=FONT, size=10, color=WHITE),
            bordercolor=CYAN,
            borderwidth=1,
            borderpad=5,
            bgcolor="rgba(10,25,41,.9)",
            text=f"<b>{platform_name}</b><br>L {length:.2f} m · b {plan['span']:.2f} m<br>"
            f"silüet temsilî · mühimmatlar ölçekli",
        )
        fig.update_layout(meta=dict(collisions=collisions, undrawn=undrawn))
        return fig

    # -- hedef sembolojisi ---------------------------------------------------
    def _symbol(self, fig: go.Figure, category: str, size: float, label: str) -> None:
        """Düşman (baklava) çerçeveli, 2525D/APP-6'dan esinlenen sadeleştirilmiş hedef sembolü."""
        s = size
        diamond_x, diamond_y = [0, s, 0, -s, 0], [s, 0, -s, 0, s]
        self._line(fig, diamond_x, diamond_y, color=RED, width=2.0, fill="rgba(255,59,59,.12)")
        installation = category in ("Hardened_Structure", "Soft_Structure", "Infrastructure")
        if installation:  # tesis: çerçeve üstünde dolu çubuk
            self._line(
                fig,
                [-0.45 * s, 0.45 * s, 0.45 * s, -0.45 * s, -0.45 * s],
                [1.02 * s, 1.02 * s, 1.16 * s, 1.16 * s, 1.02 * s],
                color=RED,
                fill=RED,
            )
        if category == "Hardened_Structure":  # sertleştirilmiş: iç çerçeve (standart dışı vurgu)
            self._line(fig, [0, 0.8 * s, 0, -0.8 * s, 0], [0.8 * s, 0, -0.8 * s, 0, 0.8 * s], color=RED, width=1.0)
        if category == "Personnel":  # piyade: çapraz çizgiler
            self._line(
                fig,
                [-0.5 * s, 0.5 * s, None, -0.5 * s, 0.5 * s],
                [-0.5 * s, 0.5 * s, None, 0.5 * s, -0.5 * s],
                color=RED,
            )
        elif category == "Armored_Vehicle":  # zırhlı: oval
            t = np.linspace(0, 2 * math.pi, 49)
            self._line(fig, 0.5 * s * np.cos(t), 0.25 * s * np.sin(t), color=RED)
        elif category == "Radar/Air_Defense":  # hava savunma: kubbe
            t = np.linspace(0, math.pi, 37)
            self._line(fig, 0.6 * s * np.cos(t), -0.4 * s + 0.45 * s * np.sin(t), color=RED)
        elif category == "Soft_Vehicle":  # tekerlekli araç: çerçeve altında tekerlekler
            t = np.linspace(0, 2 * math.pi, 25)
            for cx in (-0.25 * s, 0.25 * s):
                self._line(fig, cx + 0.09 * s * np.cos(t), -1.12 * s + 0.09 * s * np.sin(t), color=RED)
        elif category == "Naval":  # su üstü: gövde silüeti
            self._line(
                fig,
                [-0.55 * s, 0.55 * s, 0.38 * s, -0.38 * s, -0.55 * s],
                [0.05 * s, 0.05 * s, -0.2 * s, -0.2 * s, 0.05 * s],
                color=RED,
            )
        self._text(
            fig,
            0,
            -0.42 * s if category in ("Personnel", "Armored_Vehicle") else 0.3 * s,
            label or SYMBOL_TEXT.get(category, "TGT"),
            RED,
            12,
            bg="rgba(0,0,0,0)",
        )

    def draw_target_symbology(
        self,
        target_category: str,
        blast_radius_m: float,
        required_radius_m: float | None = None,
        collateral_radius_m: float | None = None,
        label: str = "",
        show_dimensions: bool = True,
        zoom: float = 1.0,
        height: int | None = None,
    ) -> go.Figure:
        """Hedef sembolü + gerçek alan ölçeğinde ölümcül yarıçap (ve varsa hedef izi / tali hasar) halkaları."""
        radii = [r for r in (blast_radius_m, required_radius_m, collateral_radius_m) if not _nan(r) and r > 0]
        if not radii:
            raise ValueError("En az bir yarıçap gerekli")
        extent = 1.2 * max(radii)
        fig = self._figure((-extent, extent), (-extent, extent), zoom, height)
        theta = np.linspace(0, 2 * math.pi, 181)
        rings = [
            (collateral_radius_m, CYAN, "longdash", None, "TALİ HASAR (1 psi)"),
            (blast_radius_m, NEON, None, "rgba(57,255,20,.08)", "ÖLÜMCÜL YARIÇAP"),
            (required_radius_m, AMBER, "dot", None, "HEDEF İZİ"),
        ]
        for i, (radius, color, dash, fill, name) in enumerate(rings):
            if _nan(radius) or radius <= 0:
                continue
            self._line(
                fig, radius * np.cos(theta), radius * np.sin(theta), color=color, dash=dash, fill=fill, name=name
            )
            ang = math.radians(50 + 35 * i)
            self._text(fig, radius * math.cos(ang), radius * math.sin(ang), f"{name} R={radius:.1f} m", color, 10)
        self._symbol(fig, target_category, 0.16 * extent, label)
        if show_dimensions and not _nan(blast_radius_m) and blast_radius_m > 0:
            self._dimension(fig, (0, 0), (blast_radius_m, 0), -0.10 * extent, f"R {blast_radius_m:.1f} m", NEON)
        bar = _nice_step(2 * extent) * 2
        x0, y0 = -extent * 0.94, -extent * 0.92
        self._line(
            fig,
            [x0, x0 + bar, None, x0, x0, None, x0 + bar, x0 + bar],
            [y0, y0, None, y0 - 0.015 * extent, y0 + 0.015 * extent, None, y0 - 0.015 * extent, y0 + 0.015 * extent],
            color=WHITE,
            width=2,
        )
        self._text(fig, x0 + bar / 2, y0 + 0.04 * extent, f"{bar:g} m", WHITE, 10)
        return fig
