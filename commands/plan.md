# Planning Commands This file outlines the strategic planning and development workflow commands for project execution. Each command serves a specific purpose in the development lifecycle, from initial repository analysis to final testing phases.

  # ─── STRATEGIC PLANNING ─────────────────────────────────
  - [PM1] Scan the entire repo, extract coding conventions, open issues, and
    TODO comments. Summarise them in a markdown table and propose a first‑pass task
    list.
  - [PM2] Independently repeat PM1’s scan, highlighting any conflicting
    conventions or technical‑debt hotspots. Output a prioritised roadmap.

  # ─── ARCHITECTURE GATE ─────────────────────────────────
  - [ARCH] Merge PM1 & PM2 outputs into a single architecture‑plan draft. Ask
    the USER concise yes/no questions where trade‑offs exist (e.g., monolith vs.
    packages, new lib vs. refactor). Pause for answers before finalising.

  # ─── UI / UX (CONDITIONAL) ─────────────────────────────
  - [UIUX] *Run only if files under /app, /components, or /pages
    changed.* Audit style‑guide compliance, accessibility (WCAG AA), and
    mobile‑first breakpoints. Suggest token or variant fixes rather than changing
    palette outright.

  # ─── WEB RESEARCH ─────────────────────────────────────
  - [WEB] When asked, use web search and web fetch tools to gather the latest
    technologies, libraries, best practices, and debugging resources. Provide
    concise summaries with cited sources and actionable recommendations.

  # ─── IMPLEMENTATION ───────────────────────────────────
  - [DEV] *Run only after ARCH is finalised and upon explicit user request.*
    Act as a senior developer: implement the ARCH‑approved plan, simplify code,
    create granular TODOs, and obey every rule in local CLAUDE.md / memories.
    No skipped tests, no console.logs.

  # ─── END‑TO‑END TESTING ───────────────────────────────
  - [TEST] *Run only when the user explicitly requests a Puppeteer test and a UI
    is available.* Connect to the Puppeteer MCP server, launch localhost:3000,
    execute smoke flows (login → main dashboard → critical CRUD). Report pass/fail
    with screenshots and surface regressions to DEV & USER.