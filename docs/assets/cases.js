/* Documented-case timelines. Real series only; missing stays missing. */
(function () {
  "use strict";

  const T = {
    zh: {
      price: "股价（复权收盘，美元）",
      trends: "Google Trends（窗口内 0–100）",
      wiki: "维基百科日浏览",
      jeffree: "Jeffree Star 维基浏览",
      upgrades: "卖方上调",
      downgrades: "卖方下调",
      ptRaise: "目标价上调",
      ptLower: "目标价下调",
      otherStreet: "其他卖方动作",
      earningsBeat: "财报超预期",
      earningsMiss: "财报不及预期",
      earnings: "财报",
      entry: "记录的买入窗口",
      entry2: "第二次买入窗口",
      exit: "退出 / 仍持有标记",
      exitPartial: "分批卖出",
      lead: "时差",
      leadDays: "日",
      leadUnavailable: "时差不可用",
      daysUnit: "个日历日",
      fromPlaceholder: "自月精度占位",
      summaryTitle: "各案例时差与远期回报",
      ret1: "1 个月",
      ret3: "3 个月",
      ret6: "6 个月",
      retDir: "按所标方向",
      retEq: "标的路径（不是期权损益）",
      retFwd: "远期回报（事件研究，不是他的个人损益）",
      noRet: "没有从一个有日期的进场起算的已发表远期回报。",
      worked: "已取到",
      missing: "缺失",
      partial: "部分",
      prices: "股价",
      street: "卖方评级",
      earn: "财报日",
      wikiPill: "维基浏览",
      trendsPill: "Google Trends",
      zoom: "拖动或捏合以缩放",
      firm: "机构",
      action: "动作",
      to: "调至",
      frm: "来自",
      pt: "目标价",
      date: "日期",
      loadErr: "无法加载案例数据。",
      putNote: "标的路径，不是看跌期权损益。",
      mentionNote: "这是提及日，不是建仓日。",
      mentionMark: "发表 / 提及",
      stageTitle: "把时钟分开",
      returnsWithdrawn: "不展示。旧路径用的日期不是成交日。",
      signalNotValue: "社会或搜索观察不是利润、现金流或价值。",
      stillLong: "「仍在持有」标记，不是退出。",
      eraNote: "只有年代，不是精确进场日。",
      monthNote: "月精度：中间日只是占位，不是核实过的成交日。",
      dayNote: "有具体日期的记录。",
      summaryLead: "时差（日）",
      summaryRet6: "6 个月远期回报（%）",
      summaryRet1: "1 个月（%）",
      summaryRet3: "3 个月（%）",
      na: "不可用",
      beat: "超预期",
      miss: "不及预期",
      surprise: "惊喜",
      sourceYahoo: "Yahoo Finance（yfinance）",
      sourceTrends: "Google Trends（pytrends，自定义时间窗，美国）",
      sourceWiki: "Wikimedia 页面浏览（英文维基）",
      underlyingShort: "空头方向上的标的回报",
      comparisonHint: "只有在有真实、有日期的卖方事件时才给出时差。没有时差的案例画成回报柱，时差标记为「不可用」，不记作零。回报来自既有事件研究，不是他的个人损益。",
      clickLegend: "点击图例可显示或隐藏序列。缺失的序列不会画成零。",
    },
    en: {
      price: "Share price (adjusted close, USD)",
      trends: "Google Trends (0–100 in this window)",
      wiki: "Wikipedia daily pageviews",
      jeffree: "Jeffree Star Wikipedia pageviews",
      upgrades: "Street upgrades",
      downgrades: "Street downgrades",
      ptRaise: "Target raised",
      ptLower: "Target lowered",
      otherStreet: "Other Street actions",
      earningsBeat: "Earnings beat",
      earningsMiss: "Earnings miss",
      earnings: "Earnings",
      entry: "Documented entry window",
      entry2: "Second purchase window",
      exit: "Exit / still-long marker",
      exitPartial: "Partial selling",
      lead: "Lead time",
      leadDays: "days",
      leadUnavailable: "Lead time unavailable",
      daysUnit: "calendar days",
      fromPlaceholder: "from a month-precision placeholder",
      summaryTitle: "Lead time and forward returns across cases",
      ret1: "1 month",
      ret3: "3 months",
      ret6: "6 months",
      retDir: "in the stated direction",
      retEq: "underlying path (not options P&L)",
      retFwd: "Forward returns (event study, not his personal P&L)",
      noRet: "No published forward return from a dated entry.",
      worked: "collected",
      missing: "missing",
      partial: "partial",
      prices: "Price",
      street: "Street ratings",
      earn: "Earnings dates",
      wikiPill: "Wikipedia",
      trendsPill: "Google Trends",
      zoom: "Drag or pinch to zoom",
      firm: "Firm",
      action: "Action",
      to: "To",
      frm: "From",
      pt: "Target",
      date: "Date",
      loadErr: "Could not load the case data.",
      putNote: "Underlying path, not put P&L.",
      mentionNote: "This is a mention date, not an entry.",
      mentionMark: "Publication / mention",
      stageTitle: "Separate the clocks",
      returnsWithdrawn: "Not shown. The old path used a date that is not an execution.",
      signalNotValue: "A social or search observation is not earnings, cash flow, or value.",
      stillLong: "A still-long marker, not an exit.",
      eraNote: "Era only, not an exact entry day.",
      monthNote: "Month precision: the mid-month day is a placeholder, not a verified trade date.",
      dayNote: "Documented to the day.",
      summaryLead: "Lead time (days)",
      summaryRet6: "6-month forward return (%)",
      summaryRet1: "1 month (%)",
      summaryRet3: "3 months (%)",
      na: "n/a",
      beat: "beat",
      miss: "miss",
      surprise: "surprise",
      sourceYahoo: "Yahoo Finance (yfinance)",
      sourceTrends: "Google Trends (pytrends, custom timeframe, US)",
      sourceWiki: "Wikimedia pageviews (English Wikipedia)",
      underlyingShort: "underlying return in the short direction",
      comparisonHint: "Lead time is shown only when a real, dated Street event exists. Cases without one are drawn as return bars with lead marked unavailable — not zero. Returns come from the existing event study, not his personal P&L.",
      clickLegend: "Click the legend to show or hide a series. Missing series are not drawn as zero.",
    },
  };

  let DATA = null;
  let currentId = "elf-2019";
  let timeline = null;
  let summary = null;

  function lang() {
    return document.documentElement.getAttribute("data-lang") === "en" ? "en" : "zh";
  }
  function t(k) {
    return T[lang()][k] || k;
  }
  function cases() {
    return (DATA && DATA.cases) || [];
  }
  function current() {
    return cases().find((c) => c.id === currentId) || cases()[0];
  }
  function fmtDay(s) {
    if (!s) return "";
    const d = String(s).slice(0, 10);
    if (lang() === "zh") {
      const m = d.match(/^(\d{4})-(\d{2})-(\d{2})$/);
      return m ? `${m[1]} 年 ${Number(m[2])} 月 ${Number(m[3])} 日` : d;
    }
    return d;
  }
  function fmtPct(x) {
    if (x == null || x === "") return t("na");
    const n = Number(x);
    const sign = n > 0 ? "+" : "";
    return sign + n.toFixed(Math.abs(n) >= 10 ? 1 : 2) + "%";
  }
  function nearestPrice(series, date) {
    if (!series || !series.length) return null;
    let prev = null;
    for (const p of series) {
      if (p.date === date) return p.close;
      if (p.date > date) return prev != null ? prev : p.close;
      prev = p.close;
    }
    return prev;
  }

  function buildPicker() {
    const el = document.getElementById("case-picker");
    if (!el) return;
    const aria = el.getAttribute(lang() === "en" ? "data-aria-en" : "data-aria-zh");
    if (aria) el.setAttribute("aria-label", aria);
    el.innerHTML = "";
    cases().forEach((c) => {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("data-id", c.id);
      const L = c.labels || {};
      b.textContent = lang() === "zh" ? L.short_zh || c.ticker : L.short_en || c.ticker;
      if (c.id === currentId) b.classList.add("is-on");
      if (c.role === "loss") b.classList.add("is-loss");
      if (c.role === "exit") b.classList.add("is-exit");
      b.addEventListener("click", () => {
        currentId = c.id;
        const u = new URL(location.href);
        u.searchParams.set("case", c.id);
        history.replaceState({}, "", u);
        renderAll();
      });
      el.appendChild(b);
    });
  }

  function pill(label, status) {
    const cls = status === "worked" ? "worked" : status === "partial" ? "partial" : "missing";
    const word =
      status === "worked" ? t("worked") : status === "partial" ? t("partial") : t("missing");
    return `<span class="${cls}">${label} · ${word}</span>`;
  }

  function renderMeta() {
    const c = current();
    if (!c) return;
    const L = c.labels || {};
    const title = document.getElementById("case-title");
    const sub = document.getElementById("case-sub");
    if (title) title.textContent = (lang() === "zh" ? L.zh : L.en) + "  ·  " + c.ticker;
    if (sub) {
      const bits = [];
      bits.push(c.ticker);
      bits.push(c.window[0] + " – " + c.window[1]);
      if (c.side) bits.push(c.side);
      sub.textContent = bits.join("  ·  ");
    }

    const pills = document.getElementById("series-pills");
    if (pills) {
      const st = c.series_status || {};
      const wikiStatus =
        (c.missing_notes || []).some((n) => n.series === "wikipedia" && n.partial) && st.wikipedia === "worked"
          ? "partial"
          : st.wikipedia;
      pills.innerHTML =
        pill(t("prices"), st.prices) +
        pill(t("trendsPill"), st.trends) +
        pill(t("wikiPill"), wikiStatus) +
        pill(t("street"), st.grades === "worked" && c.street && c.street.n > 0 ? "worked" : st.grades === "worked" && c.street && c.street.n === 0 ? "missing" : st.grades) +
        pill(t("earn"), st.earnings);
    }

    const leadEl = document.getElementById("lead-card");
    if (leadEl) {
      const ld = c.lead || {};
      leadEl.className = "lead-card" + (ld.ok ? "" : " unavailable");
      const num = leadEl.querySelector(".num");
      const body = leadEl.querySelector(".lead-body");
      const text = lang() === "zh" ? ld.zh : ld.en;
      if (ld.ok && ld.days != null) {
        num.innerHTML = ld.days + `<small>${t("daysUnit")}${ld.from_precision === "month" ? " · " + t("fromPlaceholder") : ""}</small>`;
      } else {
        num.innerHTML = t("leadUnavailable");
      }
      body.innerHTML = `<p>${escapeHtml(text || ld.reason || "")}</p>`;
    }
    const stages = document.getElementById("stage-ledger");
    if (stages) {
      const rows = c.stages || [];
      if (!rows.length) {
        stages.innerHTML = "";
      } else {
        const cap = t("stageTitle");
        const clock = {
          social_observation: { zh: "社会观察", en: "Social observation" },
          verified_signal_timestamp: { zh: "已核实的信号时间", en: "Verified signal time" },
          documented_entry: { zh: "有记录的进场", en: "Documented entry" },
          first_street_response: { zh: "第一次卖方反应", en: "First Street response" },
          earnings_confirmation: { zh: "财报确认", en: "Earnings confirmation" },
          investment_outcome: { zh: "投资结果", en: "Investment outcome" },
        };
        const body = rows
          .map((s) => {
            const name = (clock[s.id] && clock[s.id][lang()]) || s.id;
            return `<tr><th scope="row">${escapeHtml(name)}</th><td>${escapeHtml(lang() === "zh" ? s.status_zh : s.status_en)}</td><td>${escapeHtml(lang() === "zh" ? s.zh : s.en)}</td></tr>`;
          })
          .join("");
        stages.innerHTML = `<h3>${escapeHtml(cap)}</h3><p class="small">${escapeHtml(t("signalNotValue"))}</p><div class="table-wrap"><table><thead><tr><th>${lang() === "zh" ? "时钟" : "Clock"}</th><th>${lang() === "zh" ? "状态" : "Status"}</th><th>${lang() === "zh" ? "依据" : "What is actually known"}</th></tr></thead><tbody>${body}</tbody></table></div>`;
      }
    }

    const ret = document.getElementById("returns-row");
    if (ret) {
      const es = c.event_study || {};
      const keys = Object.keys(es);
      const firstPeek = keys.length ? es[keys[0]] : null;
      if (!keys.length || (firstPeek && firstPeek.display_returns === false)) {
        ret.innerHTML = `<p class="small">${t("returnsWithdrawn")}</p>`;
      } else {
        const first = es[keys[0]];
        const r = first.returns || {};
        const isPut = c.side === "short";
        const dir = first.direction || {};
        function cell(h, label) {
          const item = r[h] || {};
          const raw = item.pct;
          const shown = isPut && dir[h] != null ? dir[h] : raw;
          const cls = shown == null ? "" : shown >= 0 ? "pos" : "neg";
          const sub = isPut ? t("underlyingShort") : "";
          const px =
            item.start_px != null
              ? `${item.start_date} ${item.start_px} → ${item.end_date} ${item.end_px}`
              : "";
          return `<div class="ret"><div class="h">${label}</div><div class="v ${cls}">${fmtPct(shown)}</div><div class="sub">${escapeHtml(sub || px)}</div></div>`;
        }
        let extra = "";
        if (keys.length > 1) {
          extra = keys
            .slice(1)
            .map((k) => {
              const r2 = es[k].returns || {};
              return `<div class="ret"><div class="h">${k}</div><div class="v ${((r2["6m"] || {}).pct || 0) >= 0 ? "pos" : "neg"}">${fmtPct((r2["6m"] || {}).pct)} <span style="font-size:12px;color:var(--muted)">6m</span></div></div>`;
            })
            .join("");
        }
        ret.innerHTML = cell("1m", t("ret1")) + cell("3m", t("ret3")) + cell("6m", t("ret6")) + extra;
      }
    }

    const notes = document.getElementById("chart-notes");
    if (notes) {
      const lis = [];
      (c.missing_notes || []).forEach((n) => {
        lis.push(`<li>${escapeHtml(lang() === "zh" && n.reason_zh ? n.reason_zh : n.reason)}</li>`);
      });
      (c.price_notes || []).forEach((n) => {
        lis.push(`<li>${escapeHtml(lang() === "zh" ? n.zh : n.en)}</li>`);
      });
      if (lang() === "en" && c.wikipedia && c.wikipedia.interpretive_note) {
        lis.push(`<li>${escapeHtml(c.wikipedia.interpretive_note)}</li>`);
      }
      if (c.wikipedia_jeffree_star) {
        lis.push(
          `<li>${escapeHtml(lang() === "zh" ? c.wikipedia_jeffree_star.note_zh : c.wikipedia_jeffree_star.note_en)}</li>`
        );
      }
      if (c.trends && c.trends.ok && c.trends.peak) {
        const pk = c.trends.peak;
        lis.push(
          lang() === "zh"
            ? `<li>Google Trends 关键词「${escapeHtml(c.trends.keyword)}」，自定义窗口 ${c.trends.timeframe}（美国）。窗口峰值 ${fmtDay(pk.date)} = ${pk.value}。</li>`
            : `<li>Google Trends keyword “${escapeHtml(c.trends.keyword)}”, custom window ${c.trends.timeframe} (US). Window peak ${pk.date} = ${pk.value}.</li>`
        );
      }
      if (c.note) lis.push(`<li>${escapeHtml(c.note)}</li>`);
      notes.innerHTML = lis.length ? `<ul class="chart-notes">${lis.join("")}</ul>` : "";
    }

    renderActions(c);
  }

  function renderActions(c) {
    const wrap = document.getElementById("actions-wrap");
    if (!wrap) return;
    const actions = (c.street && c.street.actions) || [];
    const earns = (c.earnings && c.earnings.earnings) || [];
    if (!actions.length && !earns.length) {
      wrap.innerHTML =
        `<p class="small">${lang() === "zh" ? "此窗口内没有 Yahoo 评级或财报日期（缺失，不是零活动）。" : "No Yahoo ratings or earnings dates in this window (missing, not zero activity)."}</p>`;
      return;
    }
    const rows = [];
    actions.forEach((a) => {
      const act = (a.action || "").toLowerCase();
      const cls = act === "up" ? "tag-up" : act === "down" ? "tag-down" : "";
      const pt =
        a.pt != null && a.pt !== 0
          ? (a.prior_pt ? `${a.prior_pt} → ${a.pt}` : String(a.pt)) + (a.pt_action ? ` (${a.pt_action})` : "")
          : a.pt_action || "";
      rows.push({
        date: a.date,
        html: `<tr><td>${a.date}</td><td>${escapeHtml(a.firm || "")}</td><td class="${cls}">${escapeHtml(a.action || "")}</td><td>${escapeHtml((a.frm || "") + (a.to ? " → " + a.to : ""))}</td><td>${escapeHtml(pt)}</td></tr>`,
      });
    });
    earns.forEach((e) => {
      const s = e["Surprise(%)"];
      const cls = s != null && Number(s) > 2 ? "tag-up" : s != null && Number(s) < -2 ? "tag-down" : "tag-earn";
      const word = s != null && Number(s) > 2 ? t("beat") : s != null && Number(s) < -2 ? t("miss") : t("earnings");
      rows.push({
        date: e.date,
        html: `<tr><td>${e.date}</td><td>${t("earnings")}</td><td class="${cls}">${word}</td><td>est. ${e["EPS Estimate"]} / rpt. ${e["Reported EPS"]}</td><td>${s != null ? fmtPct(s) : ""}</td></tr>`,
      });
    });
    rows.sort((a, b) => (a.date < b.date ? -1 : 1));
    wrap.innerHTML = `<div class="table-wrap actions-wrap"><table><thead><tr><th>${t("date")}</th><th>${t("firm")}</th><th>${t("action")}</th><th>${t("frm")} → ${t("to")}</th><th>${t("pt")}</th></tr></thead><tbody>${rows.map((r) => r.html).join("")}</tbody></table></div>`;
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function markerLines(c) {
    const data = [];
    const labelColor = "#e4c88a";
    function add(date, name, color, precision) {
      if (!date) return;
      let extra = "";
      if (precision === "month") extra = "  (" + t("monthNote") + ")";
      else if (precision === "era" || precision === "multi-year") extra = "  (" + t("eraNote") + ")";
      else if (precision === "mention") extra = "  (" + t("mentionNote") + ")";
      else if (precision === "day") extra = "";
      data.push({
        xAxis: date,
        label: {
          formatter: name + "\n" + date + extra,
          color: labelColor,
          fontSize: 10,
          width: 180,
          overflow: "break",
        },
        lineStyle: { color: color, type: "solid", width: 1.5 },
      });
    }
    if (c.entry) {
      const name = c.entry.precision === "mention" ? t("mentionMark") : t("entry");
      add(c.entry.date, name, "#6ee7a8", c.entry.precision);
    }
    if (c.entry2) add(c.entry2.date, t("entry2"), "#86efac", c.entry2.precision);
    if (c.exit_partial) add(c.exit_partial.date, t("exitPartial"), "#f0b429", c.exit_partial.precision);
    if (c.exit) {
      const isStill = (c.exit.label || "").toLowerCase().includes("still long");
      add(c.exit.date, isStill ? t("stillLong") : t("exit"), "#f0b429", c.exit.precision);
    }
    return data;
  }

  function leadArea(c) {
    const ld = c.lead || {};
    if (!ld.ok || !ld.from || !ld.to || ld.days == null) return null;
    if (ld.from_precision === "month" || ld.from_precision === "era") return null;
    const label =
      lang() === "zh"
        ? `时差 ${ld.days} 日${ld.from_precision === "month" ? "（月精度占位）" : ""}\n${ld.from} → ${ld.to}${ld.kind === "earnings_beat" ? "（首次财报超预期）" : "（首次卖方上调）"}`
        : `Lead ${ld.days} days${ld.from_precision === "month" ? " (month-precision placeholder)" : ""}\n${ld.from} → ${ld.to}${ld.kind === "earnings_beat" ? " (first earnings beat)" : " (first Street upgrade)"}`;
    return {
      silent: true,
      itemStyle: { color: "rgba(201,166,107,0.16)" },
      label: {
        show: true,
        position: "insideTop",
        formatter: label,
        color: "#e4c88a",
        fontSize: 11,
        fontFamily: "Outfit, sans-serif",
        lineHeight: 16,
      },
      data: [[{ xAxis: ld.from }, { xAxis: ld.to }]],
    };
  }

  function streetScatters(c) {
    const prices = (c.prices && c.prices.series) || [];
    const groups = {
      up: [],
      down: [],
      raise: [],
      lower: [],
      other: [],
      beat: [],
      miss: [],
      earn: [],
    };
    ((c.street && c.street.actions) || []).forEach((a) => {
      const y = nearestPrice(prices, a.date);
      if (y == null) return;
      const act = (a.action || "").toLowerCase();
      const pt = (a.pt_action || "").toLowerCase();
      const tip = [
        a.date,
        a.firm || "",
        [a.frm, a.to].filter(Boolean).join(" → "),
        a.action || "",
        a.pt ? `${a.prior_pt || ""} → ${a.pt} (${a.pt_action || ""})` : a.pt_action || "",
      ]
        .filter(Boolean)
        .join("\n");
      const ptObj = { value: [a.date, y], tooltip: { formatter: () => tip } };
      if (act === "up") groups.up.push(ptObj);
      else if (act === "down") groups.down.push(ptObj);
      else if (pt === "raises") groups.raise.push(ptObj);
      else if (pt === "lowers") groups.lower.push(ptObj);
      else groups.other.push(ptObj);
    });
    ((c.earnings && c.earnings.earnings) || []).forEach((e) => {
      const y = nearestPrice(prices, e.date);
      if (y == null) return;
      const s = e["Surprise(%)"];
      const tip = `${e.date}\n${t("earnings")}\nest. ${e["EPS Estimate"]} / rpt. ${e["Reported EPS"]}\n${t("surprise")} ${s != null ? fmtPct(s) : t("na")}`;
      const ptObj = { value: [e.date, y], tooltip: { formatter: () => tip } };
      if (s != null && Number(s) > 2) groups.beat.push(ptObj);
      else if (s != null && Number(s) < -2) groups.miss.push(ptObj);
      else groups.earn.push(ptObj);
    });
    return groups;
  }

  function renderTimeline() {
    const c = current();
    const el = document.getElementById("timeline-chart");
    if (!c || !el || typeof echarts === "undefined") return;
    if (!timeline) timeline = echarts.init(el, null, { renderer: "canvas" });
    const L = lang();
    const prices = (c.prices && c.prices.ok && c.prices.series) || [];
    const trends = (c.trends && c.trends.ok && c.trends.series) || [];
    const wiki = (c.wikipedia && c.wikipedia.ok && c.wikipedia.series) || [];
    const jeffree = (c.wikipedia_jeffree_star && c.wikipedia_jeffree_star.series) || [];
    const scat = streetScatters(c);
    const area = leadArea(c);
    const lines = markerLines(c);

    const axisPtr = { type: "cross", label: { backgroundColor: "#1a1e28" } };
    const textColor = "#c8c3b8";
    const muted = "#8a8578";
    const axisLine = { lineStyle: { color: "#2a2e38" } };
    const splitLine = { lineStyle: { color: "#1c2028", type: "dashed" } };

    const series = [];
    if (prices.length) {
      series.push({
        name: t("price"),
        type: "line",
        yAxisIndex: 0,
        showSymbol: false,
        sampling: "lttb",
        lineStyle: { width: 2.2, color: "#e4c88a" },
        itemStyle: { color: "#e4c88a" },
        data: prices.map((p) => [p.date, p.close]),
        markLine: lines.length
          ? { symbol: "none", animation: false, data: lines, label: { fontSize: 10 } }
          : undefined,
        markArea: area || undefined,
        z: 3,
      });
    }
    if (trends.length) {
      series.push({
        name: t("trends") + (c.trends.keyword ? ` · ${c.trends.keyword}` : ""),
        type: "line",
        yAxisIndex: 1,
        showSymbol: false,
        lineStyle: { width: 1.8, color: "#5ec8c5" },
        itemStyle: { color: "#5ec8c5" },
        areaStyle: { color: "rgba(94,200,197,0.08)" },
        data: trends.map((p) => [p.date, p.value]),
        z: 2,
      });
    }
    if (jeffree.length) {
      series.push({
        name: t("jeffree"),
        type: "line",
        yAxisIndex: 2,
        showSymbol: false,
        sampling: "lttb",
        lineStyle: { width: 1.3, color: "#f09a6a" },
        itemStyle: { color: "#f09a6a" },
        data: jeffree.map((p) => [p.date, p.views]),
        z: 1,
      });
    }
    // Brand wiki: skip default display when dwarfed by Jeffree, but still offer it
    if (wiki.length) {
      const maxW = Math.max.apply(null, wiki.map((p) => p.views));
      const maxJ = jeffree.length ? Math.max.apply(null, jeffree.map((p) => p.views)) : 0;
      const hidden = jeffree.length && maxJ > maxW * 20;
      series.push({
        name: t("wiki") + (c.wikipedia.article ? ` · ${c.wikipedia.article}` : ""),
        type: "line",
        yAxisIndex: jeffree.length && !hidden ? 3 : 2,
        showSymbol: false,
        sampling: "lttb",
        lineStyle: { width: 1.3, color: "#a78bfa" },
        itemStyle: { color: "#a78bfa" },
        data: wiki.map((p) => [p.date, p.views]),
        z: 1,
      });
    }

    function scatter(name, data, symbol, color, size, defaultShow) {
      if (!data.length) return;
      series.push({
        name,
        type: "scatter",
        yAxisIndex: 0,
        data,
        symbol,
        symbolSize: size || 10,
        itemStyle: { color, borderColor: "#090a0d", borderWidth: 1 },
        z: 5,
      });
    }
    scatter(t("upgrades"), scat.up, "triangle", "#6ee7a8", 12);
    scatter(t("downgrades"), scat.down, "triangle", "#f07178", 12);
    // rotate downgrade? echarts symbolRotate
    if (series.length && scat.down.length) {
      const last = series[series.length - 1];
      if (last.name === t("downgrades")) last.symbolRotate = 180;
    }
    scatter(t("ptRaise"), scat.raise, "diamond", "#c9a66b", 9);
    scatter(t("ptLower"), scat.lower, "diamond", "#d9846a", 9);
    scatter(t("otherStreet"), scat.other, "circle", "#8a8578", 7);
    scatter(t("earningsBeat"), scat.beat, "star", "#7dd3fc", 13);
    scatter(t("earningsMiss"), scat.miss, "star", "#f5b4b8", 13);
    scatter(t("earnings"), scat.earn, "star", "#94a3b8", 10);

    const yAxis = [
      {
        type: "value",
        name: t("price"),
        nameTextStyle: { color: "#e4c88a", fontSize: 11 },
        axisLabel: { color: textColor, fontSize: 10 },
        axisLine,
        splitLine,
        scale: true,
      },
      {
        type: "value",
        name: t("trends"),
        nameTextStyle: { color: "#5ec8c5", fontSize: 11 },
        min: 0,
        max: 100,
        axisLabel: { color: textColor, fontSize: 10 },
        axisLine,
        splitLine: { show: false },
      },
      {
        type: "value",
        name: t("wiki"),
        nameTextStyle: { color: "#a78bfa", fontSize: 11 },
        axisLabel: { color: textColor, fontSize: 10, formatter: compactNum },
        axisLine,
        splitLine: { show: false },
        scale: true,
        offset: 0,
      },
    ];
    // If both jeffree and brand wiki, a 4th axis gets crowded on mobile — share axis 2
    // (already assigned). Fine.

    const opt = {
      backgroundColor: "transparent",
      textStyle: { fontFamily: "Outfit, IBM Plex Mono, sans-serif", color: textColor },
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(16,18,24,0.94)",
        borderColor: "#2a2e38",
        textStyle: { color: "#e8e6e0", fontSize: 12 },
        axisPointer: axisPtr,
      },
      legend: {
        type: "scroll",
        top: 4,
        textStyle: { color: textColor, fontSize: 11 },
        pageIconColor: "#c9a66b",
        pageTextStyle: { color: muted },
      },
      grid: { left: 56, right: 56, top: 72, bottom: 72 },
      dataZoom: [
        { type: "inside", filterMode: "none" },
        { type: "slider", height: 18, bottom: 12, borderColor: "#2a2e38", fillerColor: "rgba(201,166,107,0.18)", textStyle: { color: muted }, handleStyle: { color: "#c9a66b" }, moveHandleStyle: { color: "#c9a66b" } },
      ],
      xAxis: {
        type: "time",
        axisLabel: { color: textColor, fontSize: 10, hideOverlap: true },
        axisLine,
        splitLine: { show: false },
      },
      yAxis,
      series,
    };
    timeline.setOption(opt, { notMerge: true });
  }

  function compactNum(n) {
    n = Number(n);
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
    if (n >= 1e3) return (n / 1e3).toFixed(n >= 1e4 ? 0 : 1) + "k";
    return String(n);
  }

  function renderSummary() {
    const el = document.getElementById("summary-chart");
    if (!el || typeof echarts === "undefined") return;
    if (!summary) summary = echarts.init(el, null, { renderer: "canvas" });
    const names = [];
    const lead = [];
    const r1 = [];
    const r3 = [];
    const r6 = [];
    const leadLabels = [];
    cases().forEach((c) => {
      const L = c.labels || {};
      names.push(lang() === "zh" ? L.short_zh : L.short_en);
      const ld = c.lead || {};
      lead.push(ld.ok ? ld.days : null);
      leadLabels.push(ld.ok ? ld.days : t("na"));
      const es = c.event_study || {};
      const keys = Object.keys(es);
      const first = keys.length ? es[keys[0]] : null;
      const dir = (first && first.direction) || {};
      const ret = (first && first.returns) || {};
      // For shorts, use direction-of-side so a correct short shows as positive
      function pick(h) {
        if (!first || first.display_returns === false) return null;
        if (c.side === "short" && dir[h] != null) return dir[h];
        return (ret[h] && ret[h].ok ? ret[h].pct : null) ?? null;
      }
      // RBI: use April window as the first key (rbi-2019-apr)
      r1.push(pick("1m"));
      r3.push(pick("3m"));
      r6.push(pick("6m"));
    });
    const textColor = "#c8c3b8";
    const muted = "#8a8578";
    summary.setOption(
      {
        backgroundColor: "transparent",
        textStyle: { fontFamily: "Outfit, sans-serif", color: textColor },
        tooltip: {
          trigger: "axis",
          backgroundColor: "rgba(16,18,24,0.94)",
          borderColor: "#2a2e38",
          textStyle: { color: "#e8e6e0" },
          formatter: function (params) {
            if (!params || !params.length) return "";
            const i = params[0].dataIndex;
            const lines = [names[i]];
            lines.push(t("summaryLead") + ": " + leadLabels[i] + (lead[i] != null ? " " + t("leadDays") : ""));
            lines.push(t("summaryRet1") + ": " + fmtPct(r1[i]));
            lines.push(t("summaryRet3") + ": " + fmtPct(r3[i]));
            lines.push(t("summaryRet6") + ": " + fmtPct(r6[i]));
            return lines.join("<br>");
          },
        },
        legend: { top: 4, textStyle: { color: textColor, fontSize: 11 } },
        grid: { left: 48, right: 48, top: 56, bottom: 80 },
        xAxis: {
          type: "category",
          data: names,
          axisLabel: { color: textColor, fontSize: 10, rotate: 30, interval: 0 },
          axisLine: { lineStyle: { color: "#2a2e38" } },
        },
        yAxis: [
          {
            type: "value",
            name: t("summaryRet6").replace("（%）", "").replace(" (%)", ""),
            nameTextStyle: { color: textColor, fontSize: 11 },
            axisLabel: { color: textColor, formatter: "{value}%" },
            splitLine: { lineStyle: { color: "#1c2028", type: "dashed" } },
            axisLine: { lineStyle: { color: "#2a2e38" } },
          },
          {
            type: "value",
            name: t("summaryLead"),
            nameTextStyle: { color: "#c9a66b", fontSize: 11 },
            axisLabel: { color: "#c9a66b" },
            splitLine: { show: false },
            min: 0,
          },
        ],
        series: [
          {
            name: t("ret1"),
            type: "bar",
            data: r1,
            itemStyle: { color: "rgba(94,200,197,0.7)" },
            barMaxWidth: 16,
          },
          {
            name: t("ret3"),
            type: "bar",
            data: r3,
            itemStyle: { color: "rgba(167,139,250,0.75)" },
            barMaxWidth: 16,
          },
          {
            name: t("ret6"),
            type: "bar",
            data: r6,
            itemStyle: { color: "rgba(228,200,138,0.9)" },
            barMaxWidth: 16,
          },
          {
            name: t("summaryLead"),
            type: "scatter",
            yAxisIndex: 1,
            data: lead.map((v, i) => (v == null ? null : v)),
            symbolSize: 16,
            itemStyle: { color: "#c9a66b", borderColor: "#090a0d", borderWidth: 1 },
            label: {
              show: true,
              formatter: (p) => (p.value != null ? p.value + (lang() === "zh" ? "日" : "d") : ""),
              color: "#e4c88a",
              fontSize: 10,
              position: "top",
            },
            z: 5,
          },
        ],
      },
      { notMerge: true }
    );

    const tbl = document.getElementById("summary-table");
    if (tbl) {
      const head =
        lang() === "zh"
          ? `<tr><th>案例</th><th>时差</th><th>种类</th><th>1 个月</th><th>3 个月</th><th>6 个月</th><th>说明</th></tr>`
          : `<tr><th>Case</th><th>Lead</th><th>Kind</th><th>1m</th><th>3m</th><th>6m</th><th>Note</th></tr>`;
      const body = cases()
        .map((c, i) => {
          const L = c.labels || {};
          const ld = c.lead || {};
          const leadCell = ld.ok
            ? `${ld.days} ${lang() === "zh" ? "日" : "d"}`
            : t("na");
          const kind =
            ld.kind === "street_upgrade"
              ? lang() === "zh"
                ? "卖方上调"
                : "Street upgrade"
              : ld.kind === "earnings_beat"
              ? lang() === "zh"
                ? "财报超预期"
                : "Earnings beat"
              : t("na");
          const note = lang() === "zh" ? ld.zh : ld.en;
          return `<tr><td>${escapeHtml(lang() === "zh" ? L.zh : L.en)} <span class="mono">${c.ticker}</span></td><td>${leadCell}</td><td>${kind}</td><td>${fmtPct(r1[i])}</td><td>${fmtPct(r3[i])}</td><td>${fmtPct(r6[i])}</td><td style="font-size:12.5px;color:var(--muted)">${escapeHtml(note || "")}</td></tr>`;
        })
        .join("");
      tbl.innerHTML = `<div class="table-wrap"><table><thead>${head}</thead><tbody>${body}</tbody></table></div>`;
    }
  }

  function renderAll() {
    buildPicker();
    renderMeta();
    renderTimeline();
    renderSummary();
  }

  function resize() {
    if (timeline) timeline.resize();
    if (summary) summary.resize();
  }

  function boot() {
    const params = new URLSearchParams(location.search);
    const want = params.get("case");
    fetch("data/cases-charts.json")
      .then((r) => {
        if (!r.ok) throw new Error("http " + r.status);
        return r.json();
      })
      .then((d) => {
        DATA = d;
        if (want && d.cases.some((c) => c.id === want)) currentId = want;
        renderAll();
      })
      .catch((err) => {
        const el = document.getElementById("case-title");
        if (el) el.textContent = t("loadErr") + " " + err;
      });
    document.addEventListener("cct-lang", renderAll);
    window.addEventListener("resize", resize);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
