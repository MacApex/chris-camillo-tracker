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
