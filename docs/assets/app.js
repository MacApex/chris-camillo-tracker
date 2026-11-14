(function () {
  const KEY = "cct-lang";

  function readLang() {
    try {
      const q = new URLSearchParams(location.search).get("lang");
      if (q === "en" || q === "zh") return q;
      const saved = localStorage.getItem(KEY);
      if (saved === "en" || saved === "zh") return saved;
    } catch (e) {}
    return "zh";
  }

  function applyLang(lang, { writeUrl } = {}) {
    if (lang !== "en") lang = "zh";
    const html = document.documentElement;
    html.setAttribute("data-lang", lang);
    html.lang = lang === "zh" ? "zh-Hans" : "en";
    try {
      localStorage.setItem(KEY, lang);
    } catch (e) {}
    const title = document.querySelector("title");
    if (title) {
      const zh = title.getAttribute("data-title-zh");
      const en = title.getAttribute("data-title-en");
      if (zh && en) document.title = lang === "zh" ? zh : en;
    }
    document.querySelectorAll("[data-lang-switch]").forEach((box) => {
      const label = lang === "zh" ? "语言" : "Language";
      box.setAttribute("aria-label", label);
      box.querySelectorAll("button[data-lang]").forEach((b) => {
        const on = b.getAttribute("data-lang") === lang;
        b.classList.toggle("is-on", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
    });
    document.querySelectorAll(".nav-toggle").forEach((btn) => {
      btn.setAttribute("aria-label", lang === "zh" ? "菜单" : "Menu");
    });
    if (writeUrl) {
      try {
        const url = new URL(location.href);
        url.searchParams.set("lang", lang);
        history.replaceState(null, "", url.pathname + url.search + url.hash);
      } catch (e) {}
    }
    document.dispatchEvent(new CustomEvent("cct-lang", { detail: lang }));
  }

  // Re-apply immediately (boot script in <head> already set data-lang; this syncs title and buttons).
  applyLang(readLang(), { writeUrl: false });

  document.querySelectorAll("[data-lang-switch]").forEach((box) => {
    box.addEventListener("click", (e) => {
      const b = e.target.closest("button[data-lang]");
      if (b) applyLang(b.getAttribute("data-lang"), { writeUrl: true });
    });
  });

  window.cctLang = readLang;
  window.cctApplyLang = applyLang;
})();

(function () {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector("nav.primary");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
})();

(function () {
  document.querySelectorAll(".event-study table").forEach((table) => {
    const labels = [...table.querySelectorAll("thead th")].map((th) => th.textContent.trim());
    table.querySelectorAll("tbody tr").forEach((tr) => {
      [...tr.children].forEach((td, i) => {
        if (td.querySelector(".cell-label")) return;
        const label = document.createElement("span");
        label.className = "cell-label";
        label.textContent = labels[i] || "";
        td.insertBefore(label, td.firstChild);
      });
    });
  });
})();

(function () {
  const table = document.querySelector("[data-scanner]");
  if (!table) return;

  const FLAGS = {
    late_or_crowded: { zh: "已晚或拥挤", en: "late or crowded" },
    watch: { zh: "观察", en: "watch" },
    aligned: { zh: "一致", en: "aligned" },
    opportunity: { zh: "机会旗标", en: "opportunity" },
    unknown: { zh: "未知", en: "unknown" },
  };

  function translateNotes(notes, lang) {
    const map = {
      "Reddit unavailable or empty.": { zh: "Reddit 不可用或为空。", en: "Reddit unavailable or empty." },
    };
    return (notes || [])
      .map((n) => (map[n] ? map[n][lang] : n))
      .join(" ");
  }

  function translateInterp(r, lang) {
    const div = r.divergence || {};
    const flag = div.flag || "unknown";
    const social = ((((r.social || {}).composite) || {}).score);
    const street = ((((r.analyst || {}).composite) || {}).score);
    const fmtN = (x) => (typeof x === "number" && isFinite(x) ? x.toFixed(2).replace(/\.00$/, "") : "—");
    const s = fmtN(social);
    const a = fmtN(street);
    const tpl = {
      late_or_crowded: {
        zh: `分析师已经偏多（${a}），而社交动量更弱（${s}）。若有失衡，可能已经在收口。`,
        en: `Analysts are already constructive (${a}) while social momentum is softer (${s}). The imbalance, if any, may already be closing.`,
      },
      watch: {
        zh: `差距中等（社交 ${s} 对分析师 ${a}）。值得观察，不是旗标。`,
        en: `Moderate gap (social ${s} vs analyst ${a}). Worth watching, not a flag.`,
      },
      aligned: {
        zh: "社交与卖方读数大致一致，没有明显背离。",
        en: "Social and Street readings are roughly in line; no clear divergence.",
      },
      opportunity: {
        zh: `社交动量（${s}）明显高于卖方读数（${a}）——机会旗标，仍须独立核实。`,
        en: `Social momentum (${s}) sits clearly above the Street reading (${a}) — an opportunity flag, still to be independently verified.`,
      },
    };
    if (tpl[flag]) return tpl[flag][lang];
    // Fall back to the source English only in English mode; hide raw English in Chinese mode.
    if (lang === "en") return div.interpretation || "";
    return "（该旗标暂无中文释义。）";
  }

  const I18N = {
    zh: {
      meta: (t, n, f) =>
        `实盘扫描生成于 ${t}（UTC）。${n} 个代码，其中 ${f} 个标了机会旗标。`,
      close: "收盘",
      upside: "隐含上行",
      social: "社交",
      street: "卖方",
      fail: "无法加载扫描结果。请查看仓库中的 toolkit/examples/sample_run.json。",
      flag: (f) => (FLAGS[f] || FLAGS.unknown).zh,
    },
    en: {
      meta: (t, n, f) =>
        `Live run generated ${t} (UTC). ${n} tickers. ${f} opportunity flag(s).`,
      close: "close",
      upside: "implied upside",
      social: "Social",
      street: "Street",
      fail: "Scanner results could not be loaded. See toolkit/examples/sample_run.json in the repository.",
      flag: (f) => (FLAGS[f] || FLAGS.unknown).en,
    },
  };

  const fmt = (x, d) => (typeof x === "number" && isFinite(x) ? x.toFixed(d) : "—");
  const money = (x) =>
    typeof x === "number" && isFinite(x)
      ? x.toLocaleString("en-US", { style: "currency", currency: "USD" })
      : "—";

  let cached = null;

  function ui() {
    return I18N[document.documentElement.getAttribute("data-lang") === "en" ? "en" : "zh"];
  }

  function render(bundle) {
    const T = ui();
    const host = document.querySelector("[data-scanner]");
    const meta = document.querySelector("[data-scan-meta]");
    if (meta) {
      meta.textContent = T.meta(bundle.generated_at || "", bundle.n || 0, bundle.n_opportunity_flags || 0);
    }
    const rows = bundle.results || [];
    host.innerHTML = rows
      .map((r) => {
        const social = (((r.social || {}).composite) || {}).score;
        const street = (((r.analyst || {}).composite) || {}).score;
        const div = (r.divergence || {}).score;
        const flag = (r.divergence || {}).flag || "unknown";
        const lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "zh";
        const interp = translateInterp(r, lang);
        const raw = ((r.analyst || {}).raw) || {};
        const close = raw.last_close;
        const up = raw.implied_upside_pct;
        const sPct = typeof social === "number" ? Math.max(0, Math.min(100, social)) : 0;
        const aPct = typeof street === "number" ? Math.max(0, Math.min(100, street)) : 0;
        const notes = translateNotes((((r.social || {}).composite) || {}).notes || [], lang);
        const upS =
          typeof up === "number" ? (up >= 0 ? "+" : "") + up.toFixed(1) + "%" : "—";
        return `<article class="scan-card">
            <div>
              <p class="sym">${r.symbol || ""}</p>
              <p class="meta">${T.close} ${money(close)} · ${T.upside} ${upS}</p>
            </div>
            <div class="meters">
              <div class="meter-row"><span>${T.social}</span><div class="bar"><span class="social" style="width:${typeof social === "number" ? sPct : 0}%"></span></div><span>${fmt(social, 1)}</span></div>
              <div class="meter-row"><span>${T.street}</span><div class="bar"><span class="street" style="width:${typeof street === "number" ? aPct : 0}%"></span></div><span>${fmt(street, 1)}</span></div>
            </div>
            <div class="flag-pill flag-${flag}">
              <span class="div-num">${fmt(div, 1)}</span>
              ${T.flag(flag)}
            </div>
            <p class="interp">${interp}${notes ? " " + notes : ""}</p>
          </article>`;
      })
      .join("");
  }

  fetch("data/scanner-results.json")
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error("no results"))))
    .then((bundle) => {
      cached = bundle;
      render(bundle);
    })
    .catch(() => {
      const host = document.querySelector("[data-scanner]");
      if (host && !host.innerHTML.trim()) {
        host.innerHTML = `<p class="deck">${ui().fail}</p>`;
      }
    });

  document.addEventListener("cct-lang", () => {
    if (cached) render(cached);
  });
})();

(function tradesTable() {
  const host = document.querySelector("[data-trades]");
  if (!host) return;
  const roleFilter = document.querySelector("[data-filter-role]");
  const verFilter = document.querySelector("[data-filter-ver]");
  const q = document.querySelector("[data-filter-q]");
  const meta = document.querySelector("[data-trades-meta]");

  const ROLE_ZH = {
    win: "盈利",
    loss: "亏损",
    miss: "错过",
    theme: "主题",
    exit: "退出",
    signal_note: "信号举例，不是持仓",
    named_no_pnl: "仅点名，无盈亏",
    open_or_unspecified: "未了结 / 未说明",
    third_party: "第三方",
    unconfirmed: "未证实",
    rejected: "排除",
  };
  const VER_ZH = {
    screenshots_viewed_by_journalist: "记者看过截图",
    self_reported_and_market_fact: "自述 + 市场事实",
    self_reported: "自述",
    third_party_mention: "第三方提及",
    unconfirmed_ticker: "代码未证实",
    missed_opportunity: "错过的机会",
    rejected_no_source: "排除（无来源）",
    independently_reviewed: "独立审阅",
  };

  const PREC_ZH = {
    month: "月",
    day: "日",
    year: "年",
    era: "时代",
    "n/a": "不适用",
    unknown: "未知",
    "year-uncertain": "年份不确定",
    "multi-year": "跨年",
    "day-approx": "约至日",
    mention: "提及",
  };

  const I18N = {
    zh: {
      showing: (a, b, c) => `显示 ${a} / ${b} 条。编制于 ${c}。`,
      fail: "无法加载 trades.json。",
      role: (v) => ROLE_ZH[v] || (v || "").replace(/_/g, " "),
      ver: (v) => VER_ZH[v] || (v || "").replace(/_/g, " "),
      prec: (v) => PREC_ZH[v] || v || "",
      allRoles: "全部角色",
      allVer: "全部核实等级",
    },
    en: {
      showing: (a, b, c) => `Showing ${a} of ${b} records. Compiled ${c}.`,
      fail: "Could not load trades.json.",
      role: (v) => (v || "").replace(/_/g, " "),
      ver: (v) => (v || "").replace(/_/g, " "),
      prec: (v) => (v || "").replace(/_/g, " "),
      allRoles: "All roles",
      allVer: "All verification",
    },
  };

  function ui() {
    return I18N[document.documentElement.getAttribute("data-lang") === "en" ? "en" : "zh"];
  }

  let rows = [];
  let compiled = "";

  const badge = (v, label) =>
    `<span class="badge badge-${v}">${label}</span>`;

  const fillFilters = () => {
    const T = ui();
    const lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "zh";
    if (q) {
      const ph = q.getAttribute(lang === "en" ? "data-ph-en" : "data-ph-zh");
      if (ph) q.placeholder = ph;
    }
    const fill = (sel, vals, labelFn, allLabel) => {
      if (!sel) return;
      const cur = sel.value || "all";
      const unique = ["all", ...vals];
      sel.innerHTML = unique
        .map((v) => `<option value="${v}">${v === "all" ? allLabel : labelFn(v)}</option>`)
        .join("");
      if (unique.includes(cur)) sel.value = cur;
    };
    const roles = [...new Set(rows.map((r) => r.role).filter(Boolean))];
    const vers = [...new Set(rows.map((r) => r.verification).filter(Boolean))];
    fill(roleFilter, roles, T.role, T.allRoles);
    fill(verFilter, vers, T.ver, T.allVer);
  };

  const render = () => {
    const T = ui();
    const lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "zh";
    fillFilters();
    const role = roleFilter ? roleFilter.value : "all";
    const ver = verFilter ? verFilter.value : "all";
    const query = (q && q.value ? q.value : "").toLowerCase();
    const shown = rows.filter((t) => {
      if (role !== "all" && t.role !== role) return false;
      if (ver !== "all" && t.verification !== ver) return false;
      if (query) {
        const blob = [t.id, t.name, t.ticker, t.thesis, t.thesis_zh, t.source, t.outcome, t.outcome_zh].join(" ").toLowerCase();
        if (!blob.includes(query)) return false;
      }
      return true;
    });
    if (meta) meta.textContent = T.showing(shown.length, rows.length, compiled);
    host.innerHTML = shown
      .map(
        (t) => `<tr>
            <td>${t.date || "—"}<br><span class="small">${T.prec(t.date_precision)}</span></td>
            <td>${t.ticker || "—"}</td>
            <td><strong>${t.name || ""}</strong><br><span class="small">${(lang === "zh" ? t.thesis_zh || "（中文译文缺失）" : t.thesis || "").slice(0, 220)}</span></td>
            <td>${lang === "zh" ? t.instrument_zh || "—" : t.instrument || "—"}</td>
            <td>${badge(t.role, T.role(t.role))}${badge(t.verification, T.ver(t.verification))}</td>
            <td class="small">${(lang === "zh" ? t.outcome_zh || "（中文译文缺失）" : t.outcome || "").slice(0, 260)}</span></td>
            <td class="small">${t.source || ""}</td>
          </tr>`
      )
      .join("");
  };

  fetch("data/trades.json")
    .then((r) => r.json())
    .then((bundle) => {
      rows = bundle.trades || [];
      compiled = bundle.compiled_at_asia_shanghai || "";
      [roleFilter, verFilter, q].forEach((el) => el && el.addEventListener("input", render));
      document.addEventListener("cct-lang", render);
      render();
    })
    .catch(() => {
      host.innerHTML = `<tr><td colspan=7>${ui().fail}</td></tr>`;
    });
})();

(function platformStatus() {
  const host = document.querySelector("[data-platforms]");
  if (!host) return;
  // Static bilingual tables should not be overwritten.
  if (host.hasAttribute("data-platforms-static")) return;
  fetch("data/platform_status.json")
    .then((r) => r.json())
    .then((bundle) => {
      const plats = bundle.platforms || {};
      host.innerHTML = Object.entries(plats)
        .map(
          ([name, v]) => `<tr>
          <td>${name}</td>
          <td><span class="badge badge-${v.status}">${v.status}</span></td>
          <td class="small">${v.reason || ""}</td>
          <td class="small">${(v.tried || []).join(" · ")}</td>
        </tr>`
        )
        .join("");
    })
    .catch(() => {});
})();
