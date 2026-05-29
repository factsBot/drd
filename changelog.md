# DRD Workflow Backlog & Changelog 📝

This log tracks architectural improvements, structural modifications, and system enhancements designed to support automation, zero-key configurations, and fast-path run execution.

---

## 🚀 [2026-05-28] Automated scheduled task optimizations (Antigravity 2.0 readiness)

### 1. Robust CLI Parameters & Agent-Assisted Execution Modes
* **Motivation**: Traditional standalone runs required `GEMINI_API_KEY` to be hardcoded in the local `.env` file, which causes execution failures when running automated tasks in clean/keyless environment pipelines.
* **Changes**:
  * Added **`--get-candidates`** CLI parameter to `digest.py`: Scrapes RSS feeds and Google News fallbacks, reads local rolling coverage logs from `history.json`, and compiles them into a structured JSON payload output to `stdout`.
  * Added **`--compile-digest <json_file>`** CLI parameter to `digest.py`: Enables external injection of pre-generated LLM summaries. It parses the JSON input, compiles the daily Markdown reports directly into `drd-inbox-raw/`, and commits metadata updates to `history.json` and `index.md`.
  * Re-routed all logger statements (`log(...)`) and setup guide prints to `sys.stderr` rather than `stdout`, ensuring `stdout` contains only pristine, query-ready JSON strings for scripts or agent parses.
  * Modularized history updates out of `main()` and into a reusable utility helper `update_history_and_save(...)`.

### 2. Dynamically Rendered Footer Timestamps
* **Motivation**: The output digest Markdown contained a hardcoded compilation timestamp footer (`*Digest generated automatically at 5:00 AM...*`), causing factual discrepancies for tasks firing at 4:00 AM.
* **Changes**:
  * Updated both `compile_daily_digest` and `compile_daily_digest_from_provided` to grab `datetime.datetime.now()` at generation time.
  * Replaced the hardcoded string with dynamic formatting: `{current_time_formatted}` (e.g. `*Digest generated automatically at 04:00 AM...*`).

### 3. Fast-Path Local Environment Bootstraps
* **Motivation**: Doing `pip install` checks on every scheduled 4:00 AM morning batch run introduced 10–15 seconds of useless runtime latency and risked pipeline failures during momentary internet drops.
* **Changes**:
  * Integrated an automatic `.venv\installed.tag` tag file verification in `run_digest.bat`.
  * On first boot, packages are configured and upgraded via standard procedures. Upon success, a tag file is left inside the virtual environment directory.
  * Subsequent scheduled invocations scan for the tag file and execute instantly by skipping the redundant pip package update loops.
  * Forwarded batch file argument list command parameters (`%*`) down to python scripts to make command switches (`run_digest.bat --get-candidates`) native at the shell level.

### 4. Interactive Documentation Updates
* **Changes**:
  * Updated [README.md](file:///C:/Users/goldonil/.projects/drd/README.md) to explain the new command architectures, fast-path tags, and CLI parameters for future developers/agents maintaining this directory.

---

## 🎯 [2026-05-28] Query Customization & Live Claude Release Notes Scraper

### 1. Focused Geographic Real Estate Queries
* **Motivation**: Narrowing down the "Real Estate Development" category to target the user's focus regions: New York City, New Jersey, Philadelphia, and Boston.
* **Changes**:
  * Modified `Real Estate Development`'s `"search_query"` in `digest.py` to enforce a strict geographic filter:
    `'("real estate development" OR "multifamily development" OR "urban planning") AND ("New York City" OR "NYC" OR "New Jersey" OR "Philadelphia" OR "Boston")'`

### 2. Live Claude Platform & API Release Notes Scraper
* **Motivation**: Incorporating immediate, real-time release details directly from Anthropic's official docs without depending on standard, outdated RSS loops.
* **Changes**:
  * Integrated a custom `fetch_claude_release_notes()` crawler in `digest.py` utilizing `requests` and `BeautifulSoup` to scrape `https://platform.claude.com/docs/en/release-notes/overview`.
  * Added date detection using regular expressions to extract the latest release updates (e.g. Claude Opus 4.8 release on May 28, 2026) and generate candidate snippets.
  * Updated `select_candidates()` to dynamically inject the scraped release notes as a candidate under `"Artificial Intelligence"`.
  * Refocused the broad `"search_query"` under `"Artificial Intelligence"` to focus precisely on Google (Gemini) and Anthropic (Claude) developments:
    `'("Google AI" OR "Gemini" OR "Anthropic" OR "Claude" OR "Google DeepMind") AND ("generative AI" OR "LLM" OR "AI release" OR "intelligence" OR "neural network")'`

