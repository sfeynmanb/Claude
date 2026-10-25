/* Türk-İslam Atlası — tek dosyalık arayüz. Veri, build sırasında #atlas-data içine gömülür. */
(function () {
  "use strict";

  const DATA = JSON.parse(document.getElementById("atlas-data").textContent);
  const { people, works, relations, meta, basemap } = DATA;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---------- Güvenli depolama ----------
  const store = {
    get(k, def) { try { const v = localStorage.getItem(k); return v == null ? def : JSON.parse(v); } catch (e) { return def; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* özel pencere vb. */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* yok say */ } },
  };

  // ---------- Yardımcılar ----------
  function parseYear(v) {
    if (v == null) return null;
    if (typeof v === "number") return { lo: v, hi: v, approx: false };
    const s = String(v).trim();
    const approx = s.startsWith("~");
    const m = s.replace(/^~/, "").match(/^(\d{3,4})(?:-(\d{3,4}))?$/);
    if (!m) return null;
    const lo = +m[1], hi = m[2] ? +m[2] : lo;
    return { lo, hi, approx };
  }
  const yearText = (v) => (v == null ? "?" : String(v));
  const fold = (s) => String(s || "")
    .toLocaleLowerCase("tr")
    .replace(/ı/g, "i")
    .normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/[’'‘`ʿʾ´]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();

  const P = new Map(people.map((p) => [p.id, p]));
  const W = new Map(works.map((w) => [w.id, w]));
  const worksBy = new Map();
  works.forEach((w) => { if (w.yazar_id) { if (!worksBy.has(w.yazar_id)) worksBy.set(w.yazar_id, []); worksBy.get(w.yazar_id).push(w); } });
  worksBy.forEach((l) => l.sort((a, b) => (workYear(a)?.lo ?? 9999) - (workYear(b)?.lo ?? 9999)));
  const relsOf = new Map();
  relations.forEach((r) => {
    [r.kaynak, r.hedef].forEach((id) => { if (!relsOf.has(id)) relsOf.set(id, []); relsOf.get(id).push(r); });
  });
  const dynasty = new Map(meta.devletler.map((d) => [d.ad, d]));
  const groupOf = (d) => (dynasty.has(d) ? d : meta.grup_eslemesi[d] || "Diğer");
  const groupColor = (g) => (dynasty.get(g)?.renk) || "#8a8478";
  const primaryGroup = (p) => groupOf(p.devletler[0]);
  function workYear(w) { return parseYear(w.yil); }
  const nameOf = (id) => (P.get(id)?.ad) || (W.get(id)?.ad_sade) || id;
  const isPerson = (id) => P.has(id);

  // Ömür: bilinmeyen uçlar eser ve durak yıllarından tahmin edilir.
  function life(p) {
    if (p._life) return p._life;
    const d = parseYear(p.dogum), o = parseYear(p.olum);
    let lo = d ? d.lo : null, hi = o ? o.hi : null, guessed = false;
    if (lo == null || hi == null) {
      const ys = [];
      (worksBy.get(p.id) || []).forEach((w) => { const y = workYear(w); if (y) ys.push(y.lo, y.hi); });
      p.duraklar.forEach((s) => { if (s.yil_baslangic) ys.push(s.yil_baslangic); if (s.yil_bitis) ys.push(s.yil_bitis); });
      if (lo == null && hi != null) lo = Math.min(hi - 60, ...ys.filter((y) => y <= hi));
      else if (hi == null && lo != null) hi = Math.max(lo + 60, ...ys);
      else if (ys.length) { lo = Math.min(...ys); hi = Math.max(...ys); guessed = true; }
      if (lo != null && hi != null) guessed = guessed || true;
    }
    p._life = { lo, hi, guessed, approx: p.tarih_kesinligi !== "kesin" };
    return p._life;
  }
  const aliveIn = (p, y) => { const l = life(p); return l.lo != null && l.lo <= y && y <= l.hi; };

  const DIL_BATI = "Avrupa dilleri (Latince, Fransızca, Rusça)", DIL_YOK = "Dil yok (mimari, müzik, resim, kurum)";
  function dilKeys(w) {
    const s = w.dil || "";
    if (/^Yok/.test(s)) return [DIL_YOK]; // "Yok (müzik eseri; Arapça güfte)" Arapça sayılmaz
    const out = [];
    if (/Türkçe/.test(s)) out.push("Türkçe");
    if (/Arapça/.test(s)) out.push("Arapça");
    if (/Farsça/.test(s)) out.push("Farsça");
    if (/Latince|Fransızca|Rusça/.test(s)) out.push(DIL_BATI);
    if (!out.length) out.push(DIL_YOK);
    return out;
  }
  // Eser türü kategorileri (filtre): serbest metin "tur" alanından ilk eşleşen kategori seçilir.
  const TUR_KAT = [
    ["Gazete ve dergi", /gazete|dergi/],
    ["Kurum (okul, matbaa, kütüphane)", /^kurum/],
    ["Belge (ferman, kanun, anayasa)", /^ferman|^kanun|^anayasa/],
    ["Sanat (mimari, müzik, resim)", /^mimari eser|^beste|^nota sistemi|^tablo/],
    ["Edebî eser", /divan|mesnevi|şiir|roman|tiyatro|destan|hikâye|antoloji|nasihatname|hiciv|hamse|mersiye|maktel|mevlid|manzum|tezkire|münşeat|hatırat|otobiyografi|düşünce yazıları/],
  ];
  const TUR_DIGER = "İlmî ve fikrî eser";
  const turKat = (w) => (TUR_KAT.find(([, re]) => re.test(w.tur || "")) || [TUR_DIGER])[0];
  const centuryLabel = (c) => `${c}. yüzyıl (${(c - 1) * 100 + 1}–${c * 100})`;
  const yksRank = { "yüksek": 3, "orta": 2, "düşük": 1 };
  // YKS modu (meta.yks_modu): kapalıysa vurgu, rozet ve Sınav sekmesi gizlenir.
  const YKS = meta.yks_modu !== false;
  const isHigh = (x) => YKS && x.yks_onemi === "yüksek";

  // ---------- Durum ----------
  const state = {
    tab: "harita",
    f: { alan: "", devlet: "", dil: "", tur: "", yuzyil: "", yks: "" },
    year: null,
    sel: null, // {type:'p'|'w', id}
  };

  // ---------- Filtreler ----------
  function centuryOverlap(lo, hi, c) {
    if (lo == null) return false;
    const a = (c - 1) * 100 + 1, b = c * 100;
    return lo <= b && hi >= a;
  }
  function yksOk(v) {
    if (!YKS || !state.f.yks) return true;
    if (state.f.yks === "yüksek") return v === "yüksek";
    return v === "yüksek" || v === "orta";
  }
  function personOk(p) {
    const f = state.f;
    if (f.alan && !p.alanlar.includes(f.alan)) return false;
    if (f.devlet && !p.devletler.some((d) => d === f.devlet || groupOf(d) === f.devlet)) return false;
    if (f.dil && !(worksBy.get(p.id) || []).some((w) => dilKeys(w).includes(f.dil))) return false;
    if (f.tur && !(worksBy.get(p.id) || []).some((w) => turKat(w) === f.tur)) return false;
    if (f.yuzyil) { const l = life(p); if (!centuryOverlap(l.lo, l.hi, +f.yuzyil)) return false; }
    return yksOk(p.yks_onemi);
  }
  function workOk(w) {
    const f = state.f;
    const a = P.get(w.yazar_id);
    if (f.alan && !(a && a.alanlar.includes(f.alan))) return false;
    if (f.devlet && !(w.devlet === f.devlet || groupOf(w.devlet) === f.devlet)) return false;
    if (f.dil && !dilKeys(w).includes(f.dil)) return false;
    if (f.tur && turKat(w) !== f.tur) return false;
    if (f.yuzyil) { const y = workYear(w); if (!y || !centuryOverlap(y.lo, y.hi, +f.yuzyil)) return false; }
    return yksOk(w.yks_onemi);
  }
  const filtersActive = () => Object.values(state.f).some(Boolean);

  function initFilters() {
    const count = (arr) => arr.reduce((m, x) => m.set(x, (m.get(x) || 0) + 1), new Map());
    const alanlar = count(people.flatMap((p) => p.alanlar));
    const alanSel = $("#f-alan");
    [...alanlar.keys()].sort((a, b) => a.localeCompare(b, "tr")).forEach((a) => alanSel.add(new Option(`${a} (${alanlar.get(a)})`, a)));
    const devSel = $("#f-devlet");
    meta.grup_sirasi.filter((g) => g !== "Diğer").forEach((g) => devSel.add(new Option(g, g)));
    const diger = [...new Set(people.flatMap((p) => p.devletler).concat(works.map((w) => w.devlet)))]
      .filter((d) => d && !dynasty.has(d)).sort((a, b) => a.localeCompare(b, "tr"));
    if (diger.length) {
      const og = document.createElement("optgroup"); og.label = "Diğer devlet ve beylikler";
      diger.forEach((d) => og.appendChild(new Option(d, d))); devSel.appendChild(og);
    }
    ["Türkçe", "Arapça", "Farsça", DIL_BATI, DIL_YOK].forEach((d) => $("#f-dil").add(new Option(d, d)));
    const turlar = count(works.map(turKat));
    TUR_KAT.map(([k]) => k).concat(TUR_DIGER).forEach((k) => $("#f-tur").add(new Option(`${k} (${turlar.get(k) || 0})`, k)));
    const [y0, y1] = meta.zaman_araligi;
    for (let c = Math.floor(y0 / 100) + 1; c <= Math.ceil(y1 / 100); c++) $("#f-yuzyil").add(new Option(centuryLabel(c), c));
    const map = { alan: "#f-alan", devlet: "#f-devlet", dil: "#f-dil", tur: "#f-tur", yuzyil: "#f-yuzyil", yks: "#f-yks" };
    Object.entries(map).forEach(([k, s]) => $(s).addEventListener("change", (e) => { state.f[k] = e.target.value; onFilter(); }));
    $("#f-reset").addEventListener("click", () => {
      Object.keys(state.f).forEach((k) => { state.f[k] = ""; $(map[k]).value = ""; });
      onFilter();
    });
    if (window.matchMedia("(min-width: 900px)").matches) $("#filters").open = true;
  }
  function onFilter() {
    const n = Object.values(state.f).filter(Boolean).length;
    const pill = $("#filter-count"); pill.hidden = !n; pill.textContent = n;
    const pc = people.filter(personOk).length, wc = works.filter(workOk).length;
    $("#filter-summary").textContent = filtersActive() ? `Filtreye uyan: ${pc} kişi, ${wc} eser.` : "";
    renderAll();
  }

  // ---------- Arama ----------
  const index = [
    ...people.map((p) => ({ t: "p", id: p.id, label: p.ad, sub: p.lakap || p.ad_akademik, yks: p.yks_onemi,
      hay: fold([p.ad, p.ad_akademik, p.tam_ad, p.lakap, p.id].join(" ")) })),
    ...works.map((w) => ({ t: "w", id: w.id, label: w.ad_sade, sub: w.ad, yks: w.yks_onemi,
      hay: fold([w.ad, w.ad_sade, w.id].join(" ")) })),
  ].map((e) => Object.assign(e, { compact: e.hay.replace(/ /g, "") }));
  function search(q) {
    const f = fold(q);
    if (!f) return [];
    const toks = f.split(" ");
    const fc = f.replace(/ /g, "");
    return index
      .filter((e) => toks.every((t) => e.hay.includes(t) || e.compact.includes(t)))
      .map((e) => ({ e, s: (e.hay.startsWith(f) || e.compact.startsWith(fc) ? 10 : 0) + (YKS ? yksRank[e.yks] || 0 : 0) + (e.t === "p" ? 1 : 0) }))
      .sort((a, b) => b.s - a.s || a.e.label.localeCompare(b.e.label, "tr"))
      .slice(0, 12).map((x) => x.e);
  }
  function initSearch() {
    const inp = $("#q"), list = $("#q-results");
    let items = [], active = -1;
    const close = () => { list.hidden = true; inp.setAttribute("aria-expanded", "false"); active = -1; };
    const draw = () => {
      list.innerHTML = items.length ? items.map((e, i) => {
        const extra = e.t === "p" ? (() => { const p = P.get(e.id); return `${yearText(p.dogum)}–${yearText(p.olum)}`; })()
          : esc(nameOf(W.get(e.id).yazar_id) || "Anonim");
        return `<li role="option" id="qr-${i}" data-i="${i}" aria-selected="${i === active}"><span class="kind">${e.t === "p" ? "Kişi" : "Eser"}</span><span>${esc(e.label)}${YKS && e.yks === "yüksek" ? ' <span class="badge yks-yuksek">YKS</span>' : ""}<br><span class="small muted">${esc(e.sub || "")}</span></span><span class="meta">${extra}</span></li>`;
      }).join("") : `<li class="muted">Sonuç yok</li>`;
      list.hidden = false; inp.setAttribute("aria-expanded", "true");
      if (active >= 0) inp.setAttribute("aria-activedescendant", `qr-${active}`);
    };
    const pick = (i) => { const e = items[i]; if (!e) return; close(); inp.value = ""; select(e.t, e.id, { open: true }); };
    inp.addEventListener("input", () => { items = search(inp.value); active = items.length ? 0 : -1; inp.value.trim() ? draw() : close(); });
    inp.addEventListener("keydown", (ev) => {
      if (list.hidden) return;
      if (ev.key === "ArrowDown") { active = Math.min(items.length - 1, active + 1); draw(); ev.preventDefault(); }
      else if (ev.key === "ArrowUp") { active = Math.max(0, active - 1); draw(); ev.preventDefault(); }
      else if (ev.key === "Enter") { pick(active); ev.preventDefault(); }
      else if (ev.key === "Escape") close();
    });
    list.addEventListener("mousedown", (ev) => { const li = ev.target.closest("li[data-i]"); if (li) { ev.preventDefault(); pick(+li.dataset.i); } });
    inp.addEventListener("blur", () => setTimeout(close, 120));
  }

  // ---------- Sekmeler ----------
  function showTab(tab) {
    state.tab = tab;
    $$(".tabs [role=tab]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
    $$(".view").forEach((v) => { v.hidden = v.id !== `view-${tab}`; });
    renderTab(tab);
    updateHash();
  }
  function initTabs() {
    $$(".tabs [role=tab]").forEach((b) => b.addEventListener("click", () => showTab(b.dataset.tab)));
    $(".tabs").addEventListener("keydown", (e) => {
      if (!["ArrowRight", "ArrowLeft"].includes(e.key)) return;
      const tabs = $$(".tabs [role=tab]").filter((t) => !t.hidden); const i = tabs.findIndex((t) => t.getAttribute("aria-selected") === "true");
      const n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length]; n.focus(); showTab(n.dataset.tab);
    });
  }
  function renderTab(tab) {
    if (tab === "harita") renderMap();
    else if (tab === "zaman") renderTimeline();
    else if (tab === "ag") renderNetwork();
    else if (tab === "sinav") renderExam();
  }
  function renderAll() { renderTab(state.tab); }

  function updateHash() {
    const h = state.sel ? `#${state.tab}/${state.sel.type === "p" ? "kisi" : "eser"}/${state.sel.id}` : `#${state.tab}`;
    try { history.replaceState(null, "", h); } catch (e) { /* file:// bazı tarayıcılarda */ }
  }
  function readHash() {
    const m = location.hash.slice(1).split("/");
    if (["harita", "zaman", "ag", "sinav"].includes(m[0])) state.tab = m[0];
    if (m[1] && m[2]) {
      const id = decodeURIComponent(m[2]);
      if (m[1] === "kisi" && P.has(id)) state.sel = { type: "p", id };
      if (m[1] === "eser" && W.has(id)) state.sel = { type: "w", id };
    }
  }

  // ---------- Seçim ve detay paneli ----------
  function select(type, id, opt = {}) {
    state.sel = { type, id };
    if (opt.open !== false) openDetail();
    if (opt.tab) showTab(opt.tab);
    else { renderAll(); updateHash(); }
  }
  function badgeKesinlik(k) {
    const cls = { "kesin": "kesin", "yaklaşık": "yaklasik", "tartışmalı": "tartismali" }[k] || "";
    return `<span class="badge ${cls}" title="Tarih kesinliği">${esc(k)}</span>`;
  }
  const badgeYks = (v) => !YKS ? "" : v === "yüksek" ? '<span class="badge yks-yuksek">YKS: yüksek</span>' : v === "orta" ? '<span class="badge yks-orta">YKS: orta</span>' : '<span class="badge">YKS: düşük</span>';
  const relLabel = { "hoca-öğrenci": ["hocası", "öğrencisi"], "himaye": ["hamisi", "himaye ettiği"], "etkiledi": ["etkilendiği", "etkilediği"],
    "çağdaş-tartışma": ["çağdaş / tartışma", "çağdaş / tartışma"], "tercüme etti": ["tercüme eden", "tercüme ettiği"], "şerh yazdı": ["şerh eden", "şerh ettiği"],
    "yayımladı": ["yayımlayan / basan", "yayımladığı / bastığı"], "iş birliği": ["birlikte çalıştığı", "birlikte çalıştığı"] };
  const rolLabel = (w) => (w.rol ? w.rol[0].toLocaleUpperCase("tr") + w.rol.slice(1) : "Yazar");
  // Sık karıştırılan eser çiftleri (meta.karistirilanlar) eser detayında da gösterilir.
  function confusedHtml(id) {
    const ps = meta.karistirilanlar.filter((c) => c.a === id || c.b === id);
    return ps.length ? `<h3>Sık karıştırılan</h3><ul>${ps.map((c) => `<li>${linkTo(c.a === id ? c.b : c.a)}<br><span class="small muted">${esc(c.fark)}</span></li>`).join("")}</ul>` : "";
  }
  const linkTo = (id) => `<button type="button" class="linklike" data-go="${esc(id)}">${esc(nameOf(id))}</button>`;
  function relationsHtml(id) {
    const rs = relsOf.get(id) || [];
    if (!rs.length) return '<p class="muted small">Kayıtlı ilişki yok.</p>';
    return `<ul class="rel-list">${rs.map((r) => {
      const out = r.kaynak === id; const other = out ? r.hedef : r.kaynak;
      const lab = relLabel[r.tur] ? relLabel[r.tur][out ? 1 : 0] : r.tur;
      return `<li><span class="rel-type">${esc(lab)}:</span> ${linkTo(other)}${r.not ? ` <span class="small muted">— ${esc(r.not)}</span>` : ""}${r.dogrulanamadi ? ' <span class="badge warn">doğrulanamadı</span>' : ""}</li>`;
    }).join("")}</ul>`;
  }
  const sourcesHtml = (ks) => `<ul>${ks.map((k) => `<li><a href="${esc(k.url)}" target="_blank" rel="noopener">${esc(k.ad || k.url)}</a></li>`).join("")}</ul>`;
  const teyitHtml = (x) => (x.teyitsiz_alanlar && x.teyitsiz_alanlar.length)
    ? `<p class="note small">Kaynakla teyit edilmemiş alanlar: <b>${x.teyitsiz_alanlar.map(esc).join(", ")}</b>. Bu alanlar genel bilgiye dayanır; TDV maddesiyle karşılaştırın.</p>` : "";
  const navButtons = (type, id) => `<div class="links">
      <button type="button" class="btn small" data-nav="harita" data-t="${type}" data-id="${esc(id)}">Haritada göster</button>
      <button type="button" class="btn small" data-nav="zaman" data-t="${type}" data-id="${esc(id)}">Zaman çizelgesinde göster</button>
      <button type="button" class="btn small" data-nav="ag" data-t="${type}" data-id="${esc(id)}">Ağda göster</button></div>`;

  function personHtml(p) {
    const l = life(p);
    const ws = worksBy.get(p.id) || [];
    return `<h2>${esc(p.ad)}</h2>
      <p class="alt">${esc(p.ad_akademik)}${p.lakap ? ` · <i>${esc(p.lakap)}</i>` : ""}</p>
      <div class="badges">${badgeYks(p.yks_onemi)}${badgeKesinlik(p.tarih_kesinligi)}${p.koken_tartismali ? '<span class="badge tartismali">köken tartışmalı</span>' : ""}${l.guessed && (p.dogum == null || p.olum == null) ? '<span class="badge warn">ömür eser/durak yıllarından tahmini</span>' : ""}</div>
      <dl>
        <dt>Tam adı</dt><dd>${esc(p.tam_ad)}</dd>
        <dt>Yaşamı</dt><dd>${yearText(p.dogum)} – ${yearText(p.olum)}</dd>
        <dt>Köken</dt><dd>${esc(p.koken)}</dd>
        <dt>Devletler</dt><dd>${p.devletler.map(esc).join(", ")}</dd>
        ${p.hami.length ? `<dt>Hami</dt><dd>${p.hami.map(esc).join("; ")}</dd>` : ""}
        <dt>Alanlar</dt><dd>${p.alanlar.map(esc).join(", ")}</dd>
      </dl>
      ${p.tarih_notu ? `<p class="note small"><b>Tarih notu:</b> ${esc(p.tarih_notu)}</p>` : ""}
      ${navButtons("p", p.id)}
      <p>${esc(p.ozet)}</p>
      <h3>Katkıları</h3><ul>${p.katkilar.map((k) => `<li>${esc(k)}</li>`).join("")}</ul>
      <h3>Eserleri (${ws.length})</h3>${ws.length ? `<ul>${ws.map((w) => `<li>${linkTo(w.id)} <span class="small muted">${esc(yearText(w.yil))} · ${esc(w.dil)}${w.rol ? ` · ${esc(w.rol)}` : ""}</span></li>`).join("")}</ul>` : '<p class="muted small">Veri setinde eseri yok.</p>'}
      <h3>Güzergâh</h3>${p.duraklar.length ? `<ol>${p.duraklar.map((d) => `<li><b>${esc(d.sehir)}</b> <span class="small muted">${yearText(d.yil_baslangic)}–${yearText(d.yil_bitis)}</span> — ${esc(d.ne_yapti)}</li>`).join("")}</ol>` : '<p class="muted small">Bilinen durak yok.</p>'}
      <h3>İlişkiler</h3>${relationsHtml(p.id)}
      <h3>Kaynaklar</h3>${sourcesHtml(p.kaynaklar)}${teyitHtml(p)}`;
  }
  function workHtml(w) {
    const a = P.get(w.yazar_id);
    return `<h2>${esc(w.ad_sade)}</h2>
      <p class="alt">${esc(w.ad)}</p>
      <div class="badges">${badgeYks(w.yks_onemi)}${w.dogrulanamadi ? '<span class="badge warn">doğrulanamadı</span>' : ""}${w.ilk_olma ? `<span class="badge">İlk: ${esc(w.ilk_olma)}</span>` : ""}${w.olum_sonrasi_tamamlandi ? '<span class="badge">ölümünden sonra tamamlandı</span>' : ""}</div>
      <dl>
        <dt>${esc(rolLabel(w))}</dt><dd>${a ? linkTo(a.id) : "Anonim"}</dd>
        <dt>Yıl</dt><dd>${esc(yearText(w.yil))}${w.yil_notu ? ` <span class="small muted">— ${esc(w.yil_notu)}</span>` : ""}</dd>
        <dt>Dil</dt><dd>${esc(w.dil)}</dd>
        <dt>Tür</dt><dd>${esc(w.tur)} <span class="small muted">(${esc(turKat(w))})</span></dd>
        ${w.sunuldugu_kisi ? `<dt>Sunulduğu kişi</dt><dd>${esc(w.sunuldugu_kisi)}</dd>` : ""}
        ${w.yazildigi_yer ? `<dt>Yazıldığı yer</dt><dd>${esc(w.yazildigi_yer)}</dd>` : ""}
        <dt>Devlet</dt><dd>${esc(w.devlet)}${w.devlet_notu ? ` <span class="small muted">— ${esc(w.devlet_notu)}</span>` : ""}</dd>
      </dl>
      ${navButtons("w", w.id)}
      <h3>Konusu</h3><p>${esc(w.konu)}</p>
      <h3>Önemi</h3><p>${esc(w.onemi)}</p>
      ${confusedHtml(w.id)}
      <h3>İlişkiler</h3>${relationsHtml(w.id)}
      <h3>Kaynaklar</h3>${sourcesHtml(w.kaynaklar)}${teyitHtml(w)}`;
  }
  function openDetail() {
    const s = state.sel; if (!s) return;
    const body = $("#detail-body");
    body.innerHTML = s.type === "p" ? personHtml(P.get(s.id)) : workHtml(W.get(s.id));
    const d = $("#detail"); d.hidden = false; d.scrollTop = 0;
    document.body.classList.add("detail-open");
    relayout();
  }
  function closeDetail() { $("#detail").hidden = true; document.body.classList.remove("detail-open"); relayout(); }
  // Panel açılıp kapanınca içerik genişliği değişir; harita ve ağ yeniden boyutlanmalı.
  function relayout() {
    document.documentElement.style.setProperty("--top-h", `${$(".topbar").offsetHeight}px`);
    if (map) map.invalidateSize();
    if (net) net.redraw();
  }
  function initDetail() {
    $("#detail-close").addEventListener("click", closeDetail);
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("#detail").hidden) closeDetail(); });
    document.addEventListener("click", (e) => {
      const go = e.target.closest("[data-go]");
      if (go) { const id = go.dataset.go; select(isPerson(id) ? "p" : "w", id); return; }
      const nav = e.target.closest("[data-nav]");
      if (nav) {
        state.sel = { type: nav.dataset.t, id: nav.dataset.id };
        if (window.matchMedia("(max-width: 640px)").matches) closeDetail();
        showTab(nav.dataset.nav);
        if (nav.dataset.nav === "zaman") scrollTimelineTo(state.sel);
      }
    });
  }

  // ---------- Harita ----------
  let map = null, landLayer = null, tileLayer = null, cityLayer = null, routeLayer = null, playTimer = null;
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  function initMap() {
    if (map || typeof L === "undefined") return !!map;
    map = L.map("map", { zoomSnap: 0.5, minZoom: 2, maxZoom: 9, worldCopyJump: false, preferCanvas: false });
    map.fitBounds([[18, -10], [56, 80]]);
    landLayer = L.geoJSON(basemap, { interactive: false, style: landStyle }).addTo(map);
    map.attributionControl.setPrefix(false);
    map.attributionControl.addAttribution("Kıyılar: Natural Earth");
    cityLayer = L.layerGroup().addTo(map);
    routeLayer = L.layerGroup().addTo(map);
    const tiles = $("#tiles"); // site sürümünde yok (karolar CSP ile engelli)
    if (tiles) {
      tiles.addEventListener("change", (e) => { setTiles(e.target.checked); store.set("atlas.tiles", e.target.checked); });
      if (store.get("atlas.tiles", false)) { tiles.checked = true; setTiles(true); }
    }
    return true;
  }
  const landStyle = () => ({ fillColor: css("--land"), fillOpacity: 1, color: css("--coast"), weight: 0.7 });
  function setTiles(on) {
    if (tileLayer) { map.removeLayer(tileLayer); tileLayer = null; }
    if (!on) return;
    const dark = document.documentElement.dataset.resolved === "dark";
    tileLayer = L.tileLayer(`https://{s}.basemaps.cartocdn.com/${dark ? "dark_all" : "light_all"}/{z}/{x}/{y}{r}.png`, {
      subdomains: "abcd", maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> katkıcıları &copy; <a href="https://carto.com/">CARTO</a>',
    }).addTo(map);
    tileLayer.bringToBack();
  }
  function stopAt(p, y) {
    const ds = p.duraklar.filter((d) => d.enlem != null);
    if (!ds.length) return null;
    const cover = ds.filter((d) => d.yil_baslangic != null && d.yil_bitis != null && d.yil_baslangic <= y && y <= d.yil_bitis);
    if (cover.length) return cover[cover.length - 1];
    let best = ds[0], bd = Infinity;
    ds.forEach((d) => {
      const a = d.yil_baslangic ?? d.yil_bitis, b = d.yil_bitis ?? d.yil_baslangic;
      const dist = a == null ? 500 : (y < a ? a - y : y > b ? y - b : 0);
      if (dist < bd) { bd = dist; best = d; }
    });
    return best;
  }
  function renderMap() {
    if (!initMap()) { $("#map-fallback").hidden = false; $("#map").hidden = true; renderAlive(visiblePeople()); return; }
    map.invalidateSize();
    cityLayer.clearLayers(); routeLayer.clearLayers();
    const vis = visiblePeople();
    const cities = new Map();
    vis.forEach((p) => {
      const ds = state.year == null ? p.duraklar : [stopAt(p, state.year)].filter(Boolean);
      ds.forEach((d) => {
        if (!cities.has(d.sehir)) cities.set(d.sehir, { d, ids: new Set(), high: false });
        const c = cities.get(d.sehir); c.ids.add(p.id); if (isHigh(p)) c.high = true;
      });
    });
    const accent = css("--accent"), gold = css("--gold");
    cities.forEach((c, name) => {
      const n = c.ids.size;
      const m = L.circleMarker([c.d.enlem, c.d.boylam], {
        radius: 4 + 3.2 * Math.sqrt(n), color: c.high ? gold : accent, weight: c.high ? 2.5 : 1,
        fillColor: accent, fillOpacity: 0.55,
      });
      m.bindTooltip(`${esc(name)} · ${n} kişi`, { direction: "top" });
      const list = [...c.ids].map((id) => P.get(id)).sort((a, b) => (life(a).lo ?? 0) - (life(b).lo ?? 0));
      m.bindPopup(`<b>${esc(name)}</b><ul class="popup-list">${list.map((p) => `<li><button type="button" data-go="${p.id}">${isHigh(p) ? "★ " : ""}${esc(p.ad)}</button> <span class="small muted">${yearText(p.dogum)}–${yearText(p.olum)}</span></li>`).join("")}</ul>`);
      m.addTo(cityLayer);
    });
    drawRoute();
    renderAlive(vis);
  }
  function drawRoute() {
    const info = $("#route-info"); info.textContent = "";
    const s = state.sel; if (!s) return;
    const p = s.type === "p" ? P.get(s.id) : P.get(W.get(s.id).yazar_id);
    if (!p) { info.textContent = "Anonim eserin güzergâhı yok."; return; }
    const ds = p.duraklar.filter((d) => d.enlem != null);
    if (!ds.length) { info.textContent = `${p.ad}: bilinen durak yok.`; return; }
    const pts = ds.map((d) => [d.enlem, d.boylam]);
    const col = css("--accent-2");
    if (pts.length > 1) L.polyline(pts, { color: col, weight: 3, opacity: 0.9, dashArray: "6 6" }).addTo(routeLayer);
    ds.forEach((d, i) => {
      L.marker([d.enlem, d.boylam], { icon: L.divIcon({ className: "route-num", html: String(i + 1) }), keyboard: false })
        .bindTooltip(esc(d.sehir), { permanent: true, direction: "right", offset: [10, 0], className: "route-label" }).addTo(routeLayer);
    });
    if (pts.length > 1) map.fitBounds(pts, { padding: [40, 40], maxZoom: 6 }); else map.setView(pts[0], 5);
    info.textContent = `${p.ad} güzergâhı: ${ds.map((d) => d.sehir).join(" → ")}`;
  }
  function visiblePeople() {
    return people.filter((p) => personOk(p) && (state.year == null || aliveIn(p, state.year)));
  }
  function renderAlive(vis) {
    const box = $("#alive");
    const head = state.year == null ? `${vis.length} kişi gösteriliyor` : `${state.year} yılında hayatta: ${vis.length} kişi`;
    const rank = (p) => (YKS ? yksRank[p.yks_onemi] : 0);
    const list = vis.slice().sort((a, b) => (rank(b) - rank(a)) || (life(a).lo ?? 0) - (life(b).lo ?? 0));
    box.innerHTML = `<span class="small muted" style="align-self:center">${head}:</span>` + list.map((p) =>
      `<button type="button" class="chip${isHigh(p) ? " high" : ""}${state.sel && state.sel.id === p.id ? " sel" : ""}" data-go="${p.id}">${esc(p.ad)}</button>`).join("");
  }
  function setYear(y) {
    state.year = y;
    $("#year-out").textContent = y == null ? "Tüm dönem" : String(y);
    if (y != null) $("#year").value = y;
    $("#year").disabled = y == null;
    $("#year-all").checked = y == null;
    if (state.tab === "harita") renderMap();
  }
  function initYear() {
    $("#year").min = meta.zaman_araligi[0]; $("#year").max = meta.zaman_araligi[1];
    $("#year").addEventListener("input", (e) => setYear(+e.target.value));
    $("#year-all").addEventListener("change", (e) => setYear(e.target.checked ? null : +$("#year").value));
    $("#play").addEventListener("click", () => {
      if (playTimer) { stopPlay(); return; }
      let y = state.year == null || state.year >= T1 ? T0 : state.year;
      setYear(y);
      $("#play").textContent = "⏸ Durdur";
      playTimer = setInterval(() => { y += 5; if (y > T1) { stopPlay(); return; } setYear(y); }, 220);
    });
  }
  function stopPlay() { clearInterval(playTimer); playTimer = null; $("#play").textContent = "▶ Oynat"; }

  // ---------- Zaman çizelgesi ----------
  let ppy = 1.35; // yıl başına piksel
  const T0 = meta.zaman_araligi[0], T1 = meta.zaman_araligi[1];
  function renderTimeline() {
    const box = $("#timeline");
    const vis = people.filter(personOk);
    const groups = new Map(meta.grup_sirasi.map((g) => [g, []]));
    vis.forEach((p) => { const l = life(p); if (l.lo != null) groups.get(primaryGroup(p)).push(p); });
    const left = 10, width = Math.round((T1 - T0) * ppy) + left + 160;
    const X = (y) => left + (Math.max(T0, Math.min(T1, y)) - T0) * ppy;
    const rowH = 22, gHead = 24;
    let svg = "", y = 0;
    // Eksen
    let axis = '<g class="axis">';
    for (let t = 800; t <= T1; t += 50) {
      axis += `<line x1="${X(t)}" x2="${X(t)}" y1="0" y2="__H__" stroke-dasharray="${t % 100 ? "2 4" : ""}"/>`;
      if (t % 100 === 0) axis += `<text x="${X(t) + 3}" y="14">${t}</text>`;
    }
    axis += "</g>";
    y = 24;
    // Devlet dönemleri şeridi (şerit içi yerleştirme)
    const lanes = [];
    const dyn = meta.devletler.slice().sort((a, b) => a.baslangic - b.baslangic).map((d) => {
      let lane = lanes.findIndex((end) => end <= d.baslangic); if (lane < 0) { lanes.push(0); lane = lanes.length - 1; }
      lanes[lane] = d.bitis + 30; return { d, lane };
    });
    let strip = '<g class="dyn">';
    dyn.forEach(({ d, lane }) => {
      const x1 = X(d.baslangic), x2 = X(d.bitis), yy = y + lane * 16;
      strip += `<rect x="${x1}" y="${yy}" width="${Math.max(2, x2 - x1)}" height="13" rx="3" fill="${d.renk}" opacity="0.85"><title>${esc(d.ad)} (${d.baslangic}–${d.bitis})</title></rect>`;
      if (x2 - x1 > d.ad.length * 6.4) strip += `<text x="${x1 + 4}" y="${yy + 10}" style="fill:#fff;font-size:10.5px;font-weight:600">${esc(d.ad)}</text>`;
    });
    strip += "</g>";
    y += lanes.length * 16 + 10;
    let body = "";
    groups.forEach((list, g) => {
      if (!list.length) return;
      list.sort((a, b) => life(a).lo - life(b).lo);
      const top = y, h = gHead + list.length * rowH + 6;
      const dd = dynasty.get(g);
      body += `<g class="grp"><rect x="0" y="${top}" width="${width}" height="${h}" fill="var(--surface-2)" opacity="0.35"/>`;
      if (dd) body += `<rect x="${X(dd.baslangic)}" y="${top}" width="${X(dd.bitis) - X(dd.baslangic)}" height="${h}" fill="${dd.renk}" opacity="0.13"/>`;
      body += `<text x="${left}" y="${top + 16}">${esc(g)}${dd ? ` (${dd.baslangic}–${dd.bitis})` : ""} · ${list.length}</text></g>`;
      y += gHead;
      list.forEach((p) => {
        const l = life(p), col = groupColor(g);
        const x1 = X(l.lo), x2 = Math.max(X(l.hi), x1 + 4), cy = y + rowH / 2;
        const high = isHigh(p);
        const sel = state.sel && (state.sel.id === p.id || (state.sel.type === "w" && W.get(state.sel.id)?.yazar_id === p.id));
        body += `<g class="bar${sel ? " sel" : ""}" data-pid="${p.id}" tabindex="0" role="button" aria-label="${esc(p.ad)} ${yearText(p.dogum)}–${yearText(p.olum)}">`;
        body += `<rect class="life" x="${x1}" y="${y + 4}" width="${x2 - x1}" height="${rowH - 8}" rx="4" fill="${col}" fill-opacity="${l.approx || l.guessed ? 0.55 : 0.9}" ${l.approx || l.guessed ? `stroke="${col}" stroke-dasharray="3 2"` : ""}><title>${esc(p.ad)}: ${yearText(p.dogum)}–${yearText(p.olum)} (${esc(p.tarih_kesinligi)})</title></rect>`;
        const label = `${high ? "★ " : ""}${p.ad}`;
        body += `<text x="${x2 + 6}" y="${cy + 4}" style="${high ? "font-weight:700;" : ""}">${esc(label)}</text>`;
        (worksBy.get(p.id) || []).filter(workOk).forEach((w) => {
          const wy = workYear(w); if (!wy) return;
          const wx = X((wy.lo + wy.hi) / 2);
          body += `<rect class="work${isHigh(w) ? " high" : ""}" data-wid="${w.id}" x="${wx - 4}" y="${cy - 4}" width="8" height="8" transform="rotate(45 ${wx} ${cy})"><title>${esc(w.ad_sade)} (${esc(yearText(w.yil))})</title></rect>`;
        });
        body += "</g>";
        y += rowH;
      });
      y += 6;
    });
    const H = y + 10;
    if (!body) body = `<text x="${left}" y="${y + 20}">Filtreye uyan kişi yok.</text>`;
    svg = `<svg width="${width}" height="${Math.max(H, 120)}" xmlns="http://www.w3.org/2000/svg">${axis.replace(/__H__/g, H)}${strip}${body}</svg>`;
    box.innerHTML = svg;
  }
  function scrollTimelineTo(sel) {
    const pid = sel.type === "p" ? sel.id : W.get(sel.id)?.yazar_id;
    if (!pid) return;
    requestAnimationFrame(() => {
      const g = $(`#timeline .bar[data-pid="${CSS.escape(pid)}"]`); if (!g) return;
      const box = $("#timeline"), r = g.getBoundingClientRect(), br = box.getBoundingClientRect();
      box.scrollTop += r.top - br.top - box.clientHeight / 3;
      box.scrollLeft += r.left - br.left - 40;
      g.classList.add("flash"); setTimeout(() => g.classList.remove("flash"), 2600);
    });
  }
  function initTimeline() {
    const box = $("#timeline");
    box.addEventListener("click", (e) => {
      const w = e.target.closest("[data-wid]"); if (w) { select("w", w.dataset.wid); return; }
      const b = e.target.closest("[data-pid]"); if (b) select("p", b.dataset.pid);
    });
    box.addEventListener("keydown", (e) => { const b = e.target.closest("[data-pid]"); if (b && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); select("p", b.dataset.pid); } });
    const zoom = (k) => { const c = box.scrollLeft / ppy; ppy = Math.max(0.6, Math.min(4, ppy * k)); renderTimeline(); box.scrollLeft = c * ppy; };
    $("#tl-in").addEventListener("click", () => zoom(1.25));
    $("#tl-out").addEventListener("click", () => zoom(0.8));
  }

  // ---------- İlişki ağı ----------
  const EDGE = {
    "hoca-öğrenci": { c: "#2563eb", t: "Hoca → öğrenci" },
    "himaye": { c: "#d97706", t: "Hami → himaye edilen" },
    "etkiledi": { c: "#7c3aed", t: "Etkiledi" },
    "çağdaş-tartışma": { c: "#dc2626", t: "Çağdaş / tartışma" },
    "tercüme etti": { c: "#059669", t: "Tercüme etti" },
    "şerh yazdı": { c: "#0891b2", t: "Şerh yazdı" },
    "yayımladı": { c: "#be185d", t: "Yayımladı / bastı" },
    "iş birliği": { c: "#65a30d", t: "İş birliği" },
    "yazdı": { c: "#9ca3af", t: "Yazar → eser", dash: true },
  };
  const UNDIRECTED = new Set(["çağdaş-tartışma", "iş birliği"]);
  let net = null, nodesDS = null, edgesDS = null, netKey = "";
  function renderLegend() {
    $("#legend").innerHTML = Object.values(EDGE).map((e) => `<li><i class="${e.dash ? "dash" : ""}" style="border-top-color:${e.c}"></i>${esc(e.t)}</li>`).join("")
      + '<li><i class="dot"></i>Kişi (renk: devlet grubu)</li><li><i class="sq"></i>Eser</li>'
      + (YKS ? '<li><i class="dot" style="background:var(--gold)"></i>YKS önemi yüksek (altın kenar)</li>' : "");
  }
  function renderNetwork() {
    if (typeof vis === "undefined") { $("#net-fallback").hidden = false; $("#network").hidden = true; return; }
    const allWorks = $("#net-allworks").checked, auth = $("#net-authorship").checked;
    const key = JSON.stringify([state.f, allWorks, auth, document.documentElement.dataset.resolved]);
    if (net && key === netKey) { focusSel(); return; }
    netKey = key;
    const txt = css("--text"), surf = css("--surface"), gold = css("--gold");
    const vp = people.filter(personOk), vpSet = new Set(vp.map((p) => p.id));
    const relWorkIds = new Set(relations.flatMap((r) => [r.kaynak, r.hedef]).filter((id) => W.has(id)));
    const vw = works.filter((w) => workOk(w) && (allWorks || relWorkIds.has(w.id)) && (!w.yazar_id || vpSet.has(w.yazar_id) || relWorkIds.has(w.id)));
    const ids = new Set([...vpSet, ...vw.map((w) => w.id)]);
    const nodes = vp.map((p) => {
      const g = primaryGroup(p), high = isHigh(p);
      return { id: p.id, label: p.ad, shape: "dot", size: high ? 15 : 10, title: `${p.ad} (${yearText(p.dogum)}–${yearText(p.olum)})`,
        color: { background: groupColor(g), border: high ? gold : groupColor(g), highlight: { background: groupColor(g), border: txt } },
        borderWidth: high ? 3 : 1, font: { color: txt, size: high ? 15 : 13, strokeWidth: 3, strokeColor: surf } };
    }).concat(vw.map((w) => ({
      id: w.id, label: w.ad_sade.length > 30 ? w.ad_sade.slice(0, 28) + "…" : w.ad_sade, shape: "diamond", size: isHigh(w) ? 10 : 7,
      title: `${w.ad_sade} (${yearText(w.yil)})`, color: { background: css("--surface-2"), border: isHigh(w) ? gold : css("--muted") },
      borderWidth: isHigh(w) ? 2.5 : 1, font: { color: css("--muted"), size: 11, strokeWidth: 3, strokeColor: surf },
    })));
    const edges = relations.filter((r) => ids.has(r.kaynak) && ids.has(r.hedef)).map((r, i) => ({
      id: `r${i}`, from: r.kaynak, to: r.hedef, color: { color: EDGE[r.tur].c, opacity: 0.85 }, width: 1.8,
      arrows: UNDIRECTED.has(r.tur) ? "" : "to", dashes: !!r.dogrulanamadi, title: `${r.tur}${r.not ? ": " + r.not : ""}`,
    }));
    if (auth) vw.forEach((w) => { if (w.yazar_id && ids.has(w.yazar_id)) edges.push({ id: `a-${w.id}`, from: w.yazar_id, to: w.id, color: { color: EDGE["yazdı"].c, opacity: 0.6 }, width: 1, dashes: true, arrows: "" }); });
    nodesDS = new vis.DataSet(nodes); edgesDS = new vis.DataSet(edges);
    const opts = {
      interaction: { hover: true, tooltipDelay: 120, navigationButtons: false, keyboard: false },
      physics: { solver: "barnesHut", barnesHut: { gravitationalConstant: -5200, springLength: 105, springConstant: 0.03, avoidOverlap: 0.2 }, stabilization: { iterations: 300, fit: true } },
      edges: { smooth: { type: "continuous" }, arrows: { to: { scaleFactor: 0.55 } } },
    };
    if (net) net.destroy();
    net = new vis.Network($("#network"), { nodes: nodesDS, edges: edgesDS }, opts);
    net.once("stabilizationIterationsDone", () => { net.setOptions({ physics: false }); focusSel(); });
    net.on("click", (e) => {
      if (e.nodes.length) { const id = e.nodes[0]; highlight(id); select(isPerson(id) ? "p" : "w", id); }
      else { highlight(null); }
    });
  }
  function highlight(id) {
    if (!net) return;
    if (!id || !nodesDS.get(id)) {
      nodesDS.update(nodesDS.getIds().map((n) => ({ id: n, opacity: 1 })));
      edgesDS.update(edgesDS.get().map((e) => ({ id: e.id, hidden: false })));
      return;
    }
    const nb = new Set(net.getConnectedNodes(id)); nb.add(id);
    nodesDS.update(nodesDS.getIds().map((n) => ({ id: n, opacity: nb.has(n) ? 1 : 0.12 })));
    const ce = new Set(net.getConnectedEdges(id));
    edgesDS.update(edgesDS.get().map((e) => ({ id: e.id, hidden: !ce.has(e.id) })));
  }
  function focusSel() {
    if (!net || !state.sel || state.tab !== "ag") return;
    const id = state.sel.id;
    if (!nodesDS.get(id)) return;
    net.selectNodes([id]); highlight(id);
    net.focus(id, { scale: 1.1, animation: { duration: 500 } });
  }
  function initNetwork() {
    renderLegend();
    ["#net-allworks", "#net-authorship"].forEach((s) => $(s).addEventListener("change", () => renderNetwork()));
    $("#net-fit").addEventListener("click", () => { if (net) { highlight(null); net.fit({ animation: true }); } });
  }

  // ---------- Sınav kartları ----------
  let examSub = "kartlar";
  const hukumdar = (w) => w.sunuldugu_kisi || (P.get(w.yazar_id)?.hami || []).join("; ") || "—";
  function renderExam() {
    $$(".subtabs button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.sub === examSub)));
    $$("#view-sinav .sub").forEach((s) => { s.hidden = s.id !== `sub-${examSub}`; });
    if (examSub === "kartlar") renderCards();
    else if (examSub === "karistirilanlar") renderPairs();
    else renderQuiz();
  }
  function renderCards() {
    const list = works.filter(workOk).sort((a, b) => (yksRank[b.yks_onemi] - yksRank[a.yks_onemi]) || ((workYear(a)?.lo ?? 9999) - (workYear(b)?.lo ?? 9999)));
    $("#cards").innerHTML = list.map((w) => {
      const a = P.get(w.yazar_id);
      return `<button type="button" class="card${isHigh(w) ? " high" : ""}" data-card="${w.id}" aria-label="${esc(w.ad_sade)} kartı, çevirmek için basın">
        <span class="inner">
          <span class="face front">${isHigh(w) ? '<span class="star">★ YKS</span>' : ""}<span class="t">${esc(w.ad_sade)}</span><span class="s">${esc(w.ad)}</span></span>
          <span class="face back">
            <span><b>Eser:</b> ${esc(w.ad_sade)}</span>
            <span><b>Yazar:</b> ${esc(a ? a.ad : "Anonim")}</span>
            <span><b>Devlet:</b> ${esc(w.devlet)}</span>
            <span><b>Hükümdar / sunulduğu:</b> ${esc(hukumdar(w))}</span>
            <span><b>Dil:</b> ${esc(w.dil)}</span>
            <span><b>Tür:</b> ${esc(w.tur)}</span>
            <span><b>Yıl:</b> ${esc(yearText(w.yil))}</span>
            ${w.ilk_olma ? `<span><b>İlk:</b> ${esc(w.ilk_olma)}</span>` : ""}
          </span>
        </span></button>`;
    }).join("") || '<p class="muted">Filtreye uyan eser yok.</p>';
  }
  function renderPairs() {
    $("#pairs").innerHTML = meta.karistirilanlar.map((c) => {
      const side = (id) => { const w = W.get(id), a = P.get(w.yazar_id); return `<div class="side"><h4>${linkTo(id)}</h4><p>${esc(a ? a.ad : "Anonim")} · ${esc(w.devlet)} · ${esc(w.dil)} · ${esc(yearText(w.yil))}</p><p class="muted">${esc(w.tur)}</p></div>`; };
      return `<article class="pair"><div class="two">${side(c.a)}${side(c.b)}</div><p class="diff">${esc(c.fark)}</p></article>`;
    }).join("");
  }

  // Test: yanlış yapılan eserler sonraki sorularda daha sık gelir; ilerleme localStorage'da.
  const QKEY = "atlas.quiz.v1";
  let quiz = store.get(QKEY, { stats: {}, dogru: 0, yanlis: 0 });
  let current = null;
  const saveQuiz = () => store.set(QKEY, quiz);
  const QTYPES = [
    { key: "yazar", q: (w) => `“${w.ad_sade}” kime aittir?`, ans: (w) => P.get(w.yazar_id)?.ad, pool: () => [...new Set(works.filter((x) => x.yazar_id).map((x) => P.get(x.yazar_id).ad))] },
    { key: "devlet", q: (w) => `“${w.ad_sade}” hangi devlet döneminde yazıldı?`, ans: (w) => w.devlet, pool: () => [...new Set(works.map((x) => x.devlet))] },
    { key: "dil", q: (w) => `“${w.ad_sade}” hangi dilde yazıldı?`, ans: (w) => dilKeys(w)[0], pool: () => ["Türkçe", "Arapça", "Farsça", DIL_BATI],
      uygun: (w) => dilKeys(w).length === 1 },
  ];
  function quizPool() {
    const onlyHigh = $("#quiz-high").checked;
    return works.filter((w) => w.yazar_id && w.dil && !/^Yok/.test(w.dil) && (onlyHigh ? w.yks_onemi === "yüksek" : w.yks_onemi !== "düşük"));
  }
  function weight(w) {
    const s = quiz.stats[w.id] || { d: 0, y: 0 };
    return Math.max(0.25, 1 + 2.5 * s.y - 0.6 * s.d);
  }
  function pickWeighted(list) {
    const ws = list.map(weight), sum = ws.reduce((a, b) => a + b, 0);
    let r = Math.random() * sum;
    for (let i = 0; i < list.length; i++) { r -= ws[i]; if (r <= 0) return list[i]; }
    return list[list.length - 1];
  }
  const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  function nextQuestion() {
    const pool = quizPool();
    if (!pool.length) { current = null; return; }
    let w = pickWeighted(pool);
    if (current && pool.length > 1 && w.id === current.w.id) w = pickWeighted(pool);
    const types = QTYPES.filter((t) => !t.uygun || t.uygun(w));
    const qt = types[Math.floor(Math.random() * types.length)];
    const right = qt.ans(w);
    const wrong = shuffle(qt.pool().filter((x) => x && x !== right)).slice(0, 3);
    current = { w, qt, right, opts: shuffle([right, ...wrong]), answered: false };
  }
  function renderQuiz() {
    if (!current) nextQuestion();
    const box = $("#quiz");
    const total = quiz.dogru + quiz.yanlis;
    $("#quiz-score").textContent = total ? `Doğru: ${quiz.dogru} · Yanlış: ${quiz.yanlis} · Başarı: %${Math.round(100 * quiz.dogru / total)}` : "Henüz soru çözülmedi.";
    if (!current) { box.innerHTML = '<p class="muted">Soru havuzu boş.</p>'; return; }
    const hard = Object.entries(quiz.stats).filter(([, s]) => s.y > s.d).length;
    box.innerHTML = `<p class="q">${esc(current.qt.q(current.w))}</p>
      <div class="opts">${current.opts.map((o, i) => `<button type="button" data-opt="${i}">${String.fromCharCode(65 + i)}) ${esc(o)}</button>`).join("")}</div>
      <p class="fb" id="quiz-fb"></p>
      <div class="row"><span class="small muted">${hard ? `Tekrar listesinde ${hard} eser var; bunlar daha sık sorulur.` : "Yanlış yaptığınız eserler sonraki sorularda daha sık gelir."}</span>
      <button type="button" class="btn" id="quiz-next">Sonraki soru →</button></div>`;
  }
  function answer(i) {
    if (!current || current.answered) return;
    current.answered = true;
    const pick = current.opts[i], ok = pick === current.right;
    const s = quiz.stats[current.w.id] || { d: 0, y: 0 };
    ok ? (s.d++, quiz.dogru++) : (s.y++, quiz.yanlis++);
    quiz.stats[current.w.id] = s; saveQuiz();
    $$("#quiz .opts button").forEach((b, j) => {
      b.disabled = true;
      if (current.opts[j] === current.right) b.classList.add("right");
      else if (j === i) b.classList.add("wrong");
    });
    const w = current.w, a = P.get(w.yazar_id);
    $("#quiz-fb").innerHTML = `${ok ? "✓ Doğru." : `✗ Yanlış. Doğru cevap: <b>${esc(current.right)}</b>.`} <span class="small muted">${esc(w.ad_sade)} — ${esc(a ? a.ad : "")}, ${esc(w.devlet)}, ${esc(w.dil)}${w.ilk_olma ? `; ilk: ${esc(w.ilk_olma)}` : ""}.</span> ${linkTo(w.id)}`;
    const total = quiz.dogru + quiz.yanlis;
    $("#quiz-score").textContent = `Doğru: ${quiz.dogru} · Yanlış: ${quiz.yanlis} · Başarı: %${Math.round(100 * quiz.dogru / total)}`;
  }
  function initExam() {
    $$(".subtabs button").forEach((b) => b.addEventListener("click", () => { examSub = b.dataset.sub; renderExam(); }));
    $("#cards").addEventListener("click", (e) => { const c = e.target.closest("[data-card]"); if (c) c.classList.toggle("flipped"); });
    $("#quiz").addEventListener("click", (e) => {
      const o = e.target.closest("[data-opt]"); if (o) { answer(+o.dataset.opt); return; }
      if (e.target.closest("#quiz-next")) { nextQuestion(); renderQuiz(); }
    });
    $("#quiz-high").addEventListener("change", () => { nextQuestion(); renderQuiz(); });
    $("#quiz-reset").addEventListener("click", () => { quiz = { stats: {}, dogru: 0, yanlis: 0 }; store.del(QKEY); nextQuestion(); renderQuiz(); });
  }

  // ---------- Tema ----------
  // "auto" modunda sayfayı barındıran ortamın (ör. claude.ai görüntüleyicisi) koyduğu data-theme korunur.
  const THEMES = ["auto", "light", "dark"];
  const root = document.documentElement;
  let hostTheme = root.dataset.theme || null;
  let theme = "auto";
  const resolve = () => {
    const eff = theme === "auto" ? hostTheme : theme;
    return eff === "dark" || (!eff && window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
  };
  function setThemeAttrs() {
    if (theme === "auto") { if (hostTheme) root.dataset.theme = hostTheme; else delete root.dataset.theme; }
    else root.dataset.theme = theme;
    root.dataset.resolved = resolve();
    $("#theme-btn").title = `Tema: ${{ auto: "otomatik", light: "açık", dark: "koyu" }[theme]}`;
  }
  function applyTheme() {
    setThemeAttrs();
    if (landLayer) landLayer.setStyle(landStyle());
    if (tileLayer) setTiles(true);
    netKey = "";
    renderAll();
  }
  function initTheme() {
    theme = store.get("atlas.theme", "auto");
    if (!THEMES.includes(theme)) theme = "auto";
    $("#theme-btn").addEventListener("click", () => { theme = THEMES[(THEMES.indexOf(theme) + 1) % 3]; store.set("atlas.theme", theme); applyTheme(); });
    try { window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (theme === "auto") applyTheme(); }); } catch (e) { /* eski tarayıcı */ }
    new MutationObserver(() => {
      // Yalnızca dışarıdan yapılan değişikliği izle (kendi yazdığımız değeri değil).
      if (theme !== "auto" || root.dataset.theme === (hostTheme || undefined)) return;
      hostTheme = root.dataset.theme || null;
      applyTheme();
    }).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    setThemeAttrs();
  }

  // ---------- Başlat ----------
  function init() {
    if (!YKS) {
      document.body.classList.add("no-yks");
      $("#tab-sinav").hidden = true; $(".yks-badge").hidden = true; $("#f-yks").closest("label").hidden = true;
    }
    $("#counts").textContent = `· ${people.length} kişi, ${works.length} eser, ${relations.length} ilişki`;
    initTheme(); initFilters(); initSearch(); initTabs(); initDetail(); initYear(); initTimeline(); initNetwork(); initExam();
    readHash();
    if (!YKS && state.tab === "sinav") state.tab = "harita";
    showTab(state.tab);
    if (state.sel) openDetail();
    window.addEventListener("resize", relayout);
    relayout();
  }
  init();
})();
