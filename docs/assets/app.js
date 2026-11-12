(function () {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector("nav.primary");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  const table = document.querySelector("[data-scanner]");
  if (!table) return;

  const fmt = (x, d) => (typeof x === "number" && isFinite(x) ? x.toFixed(d) : "—");
  const money = (x) =>
    typeof x === "number" && isFinite(x)
      ? x.toLocaleString("en-US", { style: "currency", currency: "USD" })
      : "—";

  fetch("data/scanner-results.json")
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error("no results"))))
    .then((bundle) => {
      const host = document.querySelector("[data-scanner]");
      const meta = document.querySelector("[data-scan-meta]");
      if (meta) {
        const t = bundle.generated_at || "";
        meta.textContent =
          "Live run generated " +
          t +
          " (UTC). " +
          (bundle.n || 0) +
          " tickers. " +
          (bundle.n_opportunity_flags || 0) +
          " opportunity flag(s).";
      }
      const rows = bundle.results || [];
      host.innerHTML = rows
        .map((r) => {
          const social = (((r.social || {}).composite) || {}).score;
          const street = (((r.analyst || {}).composite) || {}).score;
          const div = (r.divergence || {}).score;
          const flag = (r.divergence || {}).flag || "unknown";
          const interp = (r.divergence || {}).interpretation || "";
          const raw = ((r.analyst || {}).raw) || {};
          const close = raw.last_close;
          const up = raw.implied_upside_pct;
          const sPct = typeof social === "number" ? Math.max(0, Math.min(100, social)) : 0;
          const aPct = typeof street === "number" ? Math.max(0, Math.min(100, street)) : 0;
          const notes = ((((r.social || {}).composite) || {}).notes || []).join(" ");
          return `<article class="scan-card">
            <div>
              <p class="sym">${r.symbol || ""}</p>
              <p class="meta">close ${money(close)} · implied upside ${typeof up === "number" ? (up >= 0 ? "+" : "") + up.toFixed(1) + "%" : "—"}</p>
            </div>
            <div class="meters">
              <div class="meter-row"><span>Social</span><div class="bar"><span class="social" style="width:${typeof social === "number" ? sPct : 0}%"></span></div><span>${fmt(social, 1)}</span></div>
              <div class="meter-row"><span>Street</span><div class="bar"><span class="street" style="width:${typeof street === "number" ? aPct : 0}%"></span></div><span>${fmt(street, 1)}</span></div>
            </div>
            <div class="flag-pill flag-${flag}">
              <span class="div-num">${fmt(div, 1)}</span>
              ${flag.replace(/_/g, " ")}
            </div>
            <p class="interp">${interp}${notes ? " " + notes : ""}</p>
          </article>`;
        })
        .join("");
    })
    .catch(() => {
      const host = document.querySelector("[data-scanner]");
      if (host && !host.innerHTML.trim()) {
        host.innerHTML =
          '<p class="deck">Scanner results could not be loaded. See <a href="../toolkit/examples/sample_run.json">sample_run.json</a> in the repository.</p>';
      }
    });
})();

(function langToggle() {
  const root = document.body;
  const box = document.querySelector("[data-lang-toggle]");
  if (!box) return;
  const saved = localStorage.getItem("cct-lang") || "zh";
  const apply = (lang) => {
    root.setAttribute("data-lang", lang);
    localStorage.setItem("cct-lang", lang);
    box.querySelectorAll("button").forEach((b) => {
      b.classList.toggle("is-on", b.getAttribute("data-lang") === lang);
    });
  };
  apply(saved);
  box.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-lang]");
    if (b) apply(b.getAttribute("data-lang"));
  });
})();

(function tradesTable() {
  const host = document.querySelector("[data-trades]");
  if (!host) return;
  const roleFilter = document.querySelector("[data-filter-role]");
  const verFilter = document.querySelector("[data-filter-ver]");
  const q = document.querySelector("[data-filter-q]");
  const meta = document.querySelector("[data-trades-meta]");

  const badge = (v) => `<span class="badge badge-${v}">${(v || "").replace(/_/g, " ")}</span>`;

  fetch("data/trades.json")
    .then((r) => r.json())
    .then((bundle) => {
      let rows = bundle.trades || [];
      const render = () => {
        const role = roleFilter ? roleFilter.value : "all";
        const ver = verFilter ? verFilter.value : "all";
        const query = (q && q.value ? q.value : "").toLowerCase();
        const shown = rows.filter((t) => {
          if (role !== "all" && t.role !== role) return false;
          if (ver !== "all" && t.verification !== ver) return false;
          if (query) {
            const blob = [t.id, t.name, t.ticker, t.thesis, t.source, t.outcome].join(" ").toLowerCase();
            if (!blob.includes(query)) return false;
          }
          return true;
        });
        if (meta) meta.textContent = `Showing ${shown.length} of ${rows.length} records. Compiled ${bundle.compiled_at_asia_shanghai || ""}.`;
        host.innerHTML = shown
          .map((t) => `<tr>
            <td>${t.date || "—"}<br><span class="small">${t.date_precision || ""}</span></td>
            <td>${t.ticker || "—"}</td>
            <td><strong>${t.name || ""}</strong><br><span class="small">${(t.thesis || "").slice(0, 180)}${(t.thesis || "").length > 180 ? "…" : ""}</span></td>
            <td>${t.instrument || "—"}</td>
            <td>${badge(t.role)}${badge(t.verification)}</td>
            <td class="small">${(t.outcome || "").slice(0, 220)}${(t.outcome || "").length > 220 ? "…" : ""}</td>
            <td class="small">${t.source || ""}</td>
          </tr>`)
          .join("");
      };
      [roleFilter, verFilter, q].forEach((el) => el && el.addEventListener("input", render));
      render();
    })
    .catch(() => {
      host.innerHTML = "<tr><td colspan=7>Could not load trades.json.</td></tr>";
    });
})();

(function platformStatus() {
  const host = document.querySelector("[data-platforms]");
  if (!host) return;
  fetch("data/platform_status.json")
    .then((r) => r.json())
    .then((bundle) => {
      const plats = bundle.platforms || {};
      host.innerHTML = Object.entries(plats)
        .map(([name, v]) => `<tr>
          <td>${name}</td>
          <td><span class="badge badge-${v.status}">${v.status}</span></td>
          <td class="small">${v.reason || ""}</td>
          <td class="small">${(v.tried || []).join(" · ")}</td>
        </tr>`)
        .join("");
    })
    .catch(() => {});
})();
