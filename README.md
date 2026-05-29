# Daily Industry News Digest 🚀

A highly customized daily intelligence aggregator that tracks, filters, and analyzes news from **Commercial Real Estate**, **Real Estate Development**, **Artificial Intelligence**, and **Engineering Principles**.

This project has been modernized to utilize the latest **Google GenAI SDK** and patched to ensure robust local scraping across restricted corporate environments (with global SSL unverified context overrides).

---

## 📂 Project Structure

* `digest.py`: The core Python engine that handles news scraping, candidate selection, and digest compilation.
* `run_digest.bat`: A lightweight batch file that boots up the Python virtual environment and synchronizes package updates.
* `register_task.ps1`: A PowerShell script to register automated daily runs at 5:00 AM via Windows Task Scheduler.
* `requirements.txt`: Project package dependencies.
* `drd-inbox-raw/`: The designated inbox where your compiled daily digests are stored:
  * `index.md`: A central markdown dashboard archive compiling all past daily digests.
  * `YYYY-MM-DD_digest.md`: The daily customized digest file containing deep industry-specific impact analyses.
  * `history.json`: Log file preserving 7-day selection variety counts to maintain a balanced coverage matrix.

---

## 🧠 Zero-Setup & Zero-Key Workflow (Highly Recommended)

Because running cloud-based LLM cognitive processes typically requires dedicated API keys and active Google Cloud Platform billing, this project supports a **completely free, zero-setup, zero-key collaborative workflow** powered by **Antigravity** (your AI coding copilot).

You do **not** need to set up any API keys or enter any credit card information. 

### How to get your Daily Digest:
1. Open this workspace in your IDE or terminal.
2. In the **Antigravity** chat window, simply say:
   > *"Run my daily digest"* (or just type `/drd`)
3. The AI agent will immediately:
   * Boot the local scraper on your machine (100% free) to pull fresh articles via the new `python digest.py --get-candidates` CLI mode.
   * Apply its own cognitive intelligence to filter the best 3 variety-balanced candidates and generate deep impact summaries.
   * Call `python digest.py --compile-digest [JSON_FILE]` to write your custom, multi-paragraph industry impact analyses directly to your [drd-inbox-raw](file:///C:/Users/goldonil/.projects/drd/drd-inbox-raw) folder.
   * Automatically update your [index.md](file:///C:/Users/goldonil/.projects/drd/drd-inbox-raw/index.md) dashboard.

### ⚡ Fast-Path Dependency Speedups
* The bootstrapper `run_digest.bat` now implements an automatic **Fast Path** tagging system.
* On the first run, it installs and updates the virtual environment and packages. It then places a tag file at `.venv\installed.tag`.
* On all subsequent runs (such as automated 4:00 AM tasks), the batch script skips the slow internet check for pip package upgrades and launches the scraper immediately (saving 10–15 seconds and preventing execution failure due to momentary connection loss).

### 🤖 CLI Command Parameters
If you are planning to run or automate the digest scripts yourself:
* `python digest.py` (No arguments): Standard standalone execution using the local `.env` key.
* `python digest.py --get-candidates`: Crawls all feeds, evaluates rolling 7-day category counts, and outputs candidate metadata in pure JSON to standard output (logs are routed cleanly to standard error).
* `python digest.py --compile-digest <json_file>`: Compiles a custom digest using a JSON file containing pre-generated summaries, updating histories and dashboard indexes.

---

## 🛠️ Automated Setup (Standalone Cloud Run)

If you eventually decide to run the aggregator completely standalone and automatically via your morning Windows Task Scheduler task:

1. Obtain a Gemini API Key from [Google AI Studio](https://aistudio.google.com/) (using a personal Google account for 100% free limits).
2. Open your `.env` file and configure your key:
   ```env
   GEMINI_API_KEY=AIzaSyYourFreeKeyHere
   GEMINI_USE_VERTEXAI=false
   ```
3. Run the task scheduler registration script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File register_task.ps1
   ```
