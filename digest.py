#!/usr/bin/env python3
"""
Daily Industry News Digest Workflow
Fetches news from Commercial Real Estate, Real Estate Development, AI, and Engineering.
Maintains rolling 7-day category representation.
Summarizes via Gemini focused on "Why it Matters" and specific industry impacts.
"""

import os
import sys
import json
import datetime
import re
import urllib.parse
from pathlib import Path
import xml.etree.ElementTree as ET
import urllib3
import requests
from bs4 import BeautifulSoup
import feedparser
from dotenv import load_dotenv
from google import genai
import ssl

# Suppress SSL certificate warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

# Load environment variables
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

# Configure directories
OUTPUT_DIR = PROJECT_DIR / "drd-inbox-raw"
OUTPUT_DIR.mkdir(exist_ok=True)
HISTORY_FILE = OUTPUT_DIR / "history.json"
INDEX_FILE = OUTPUT_DIR / "index.md"

# Global date override (useful for agent testing and overrides)
OVERRIDE_DATE_OBJ = None

def get_current_date():
    global OVERRIDE_DATE_OBJ
    if OVERRIDE_DATE_OBJ:
        return OVERRIDE_DATE_OBJ
    return datetime.date.today()

# Configure Categories
CATEGORIES = {
    "Commercial Real Estate": {
        "feeds": [
            "https://therealdeal.com/feed/",
            "https://commercialobserver.com/feed/"
        ],
        "search_query": "commercial real estate OR office market OR retail real estate"
    },
    "Real Estate Development": {
        "feeds": [
            "https://urbanland.uli.org/feed/"
        ],
        "search_query": '("real estate development" OR "multifamily development" OR "urban planning") AND ("New York City" OR "NYC" OR "New Jersey" OR "Philadelphia" OR "Boston")'
    },
    "Artificial Intelligence": {
        "feeds": [
            "https://venturebeat.com/category/ai/feed/",
            "https://techcrunch.com/category/artificial-intelligence/feed/"
        ],
        "search_query": '("Google AI" OR "Gemini" OR "Anthropic" OR "Claude" OR "Google DeepMind") AND ("generative AI" OR "LLM" OR "AI release" OR "intelligence" OR "neural network")'
    },
    "Engineering Principles": {
        "feeds": [
            "https://phys.org/rss-feed/engineering-news/",
            "https://techxplore.com/rss-feed/"
        ],
        "search_query": "mechanical engineering OR engineering principles OR structural engineering OR construction technology"
    }
}

# Request headers for web scraping
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", file=sys.stderr)

def clean_html(html_content):
    """Clean HTML and return clean plaintext."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove script and style elements
    for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
        script.decompose()
    # Get text
    text = soup.get_text(separator="\n")
    # Clean whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text[:6000]  # Cap length for LLM context limits and speed

def fetch_feed_articles(feed_url, category_name, max_articles=5):
    """Fetch recent articles from an RSS feed."""
    articles = []
    try:
        log(f"Fetching RSS: {feed_url}")
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:max_articles]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            published = entry.get("published", "") or entry.get("pubDate", "")
            
            # Clean summaries
            summary_clean = BeautifulSoup(summary, "html.parser").get_text() if summary else ""
            
            if title and link:
                articles.append({
                    "title": title,
                    "link": link,
                    "snippet": summary_clean[:400] + "..." if len(summary_clean) > 400 else summary_clean,
                    "published": published,
                    "category": category_name,
                    "source": urllib.parse.urlparse(link).netloc.replace("www.", "")
                })
    except Exception as e:
        log(f"Error parsing RSS feed {feed_url}: {e}")
    return articles

def fetch_google_news_articles(query, category_name, max_articles=5):
    """Fetch dynamic latest articles using Google News search RSS feed (free, fast, and fresh)."""
    articles = []
    try:
        # Encode query and build Google News RSS url (past 24 hours via when:24h)
        encoded_query = urllib.parse.quote(f"{query} when:2d")
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        log(f"Fetching Google News RSS for query '{query}'")
        
        # Bypass SSL verification to handle enterprise decryption proxies and local SSL config issues
        response = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")
            for item in items[:max_articles]:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                source = item.find("source").text if item.find("source") is not None else ""
                
                # Split Google News title standard formatting "Title - Source"
                clean_title = title
                if " - " in title:
                    clean_title = " - ".join(title.split(" - ")[:-1])
                
                if clean_title and link:
                    articles.append({
                        "title": clean_title,
                        "link": link,
                        "snippet": "Latest article from search query. Fetching content directly...",
                        "published": pub_date,
                        "category": category_name,
                        "source": source or urllib.parse.urlparse(link).netloc.replace("www.", "")
                    })
        else:
            log(f"Google News search request failed with status code {response.status_code}")
    except Exception as e:
        log(f"Error executing search query fallback: {e}")
    return articles

def fetch_claude_release_notes(category_name="Artificial Intelligence"):
    """Fetch and parse the latest Claude release notes as a candidate article."""
    articles = []
    url = "https://platform.claude.com/docs/en/release-notes/overview"
    try:
        log(f"Fetching Claude release notes: {url}")
        # Bypass SSL verification to handle enterprise decryption proxies and local SSL config issues
        response = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            
            # Find all dates in format Month DD, YYYY
            dates = re.findall(r'([A-Z][a-z]+ \d{1,2}, \d{4})', text)
            if dates:
                # Get the most recent date
                latest_date = dates[0]
                date_pos = text.find(latest_date)
                
                # Extract snippet from the date onwards
                snippet_text = text[date_pos:date_pos+1800].strip()
                # Clean up multiple newlines/whitespace
                snippet_clean = re.sub(r'\s+', ' ', snippet_text)
                
                articles.append({
                    "title": f"Claude API & Platform Release Notes ({latest_date})",
                    "link": url,
                    "snippet": snippet_clean[:1000] + "...",
                    "published": latest_date,
                    "category": category_name,
                    "source": "anthropic.com"
                })
                log(f"Successfully scraped Claude Release Notes dated {latest_date}")
            else:
                # Fallback if no date matches
                articles.append({
                    "title": "Claude API & Platform Release Notes Overview",
                    "link": url,
                    "snippet": "Latest release updates and feature announcements from the Claude platform docs.",
                    "published": "Recent",
                    "category": category_name,
                    "source": "anthropic.com"
                })
        else:
            log(f"Failed to fetch Claude release notes (status {response.status_code})")
    except Exception as e:
        log(f"Error fetching Claude release notes: {e}")
    return articles

def scrape_full_content(url):
    """Attempt to scrape full text content of an article."""
    try:
        log(f"Scraping full article content: {url}")
        # Bypass SSL verification to handle enterprise decryption proxies and local SSL config issues
        response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if response.status_code == 200:
            return clean_html(response.text)
        else:
            log(f"Failed to scrape article (status code {response.status_code})")
    except Exception as e:
        log(f"Error scraping article: {e}")
    return ""

def load_history():
    """Load selection history JSON."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Error reading history.json: {e}")
    return {"history": []}

def save_history(history_data):
    """Save selection history JSON."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Error writing history.json: {e}")

def get_rolling_variety_counts(history_data, days=7):
    """Count how many times each category was selected in the last `days` days."""
    counts = {cat: 0 for cat in CATEGORIES.keys()}
    today = get_current_date()
    cutoff_date = today - datetime.timedelta(days=days)
    
    for entry in history_data.get("history", []):
        try:
            entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
            if entry_date >= cutoff_date:
                for article in entry.get("articles", []):
                    cat = article.get("category")
                    if cat in counts:
                        counts[cat] += 1
        except ValueError:
            continue
    return counts

def select_candidates():
    """Fetch candidate articles from all categories, prioritizing direct feeds then falling back to search."""
    candidates = {}
    for cat_name, info in CATEGORIES.items():
        cat_candidates = []
        
        # 0. If Artificial Intelligence, explicitly scrape the Claude release notes page
        if cat_name == "Artificial Intelligence":
            claude_notes = fetch_claude_release_notes(cat_name)
            cat_candidates.extend(claude_notes)
            
        # 1. Try curated feeds first
        for feed in info["feeds"]:
            feed_articles = fetch_feed_articles(feed, cat_name, max_articles=4)
            cat_candidates.extend(feed_articles)
        
        # Deduplicate
        seen_links = set()
        dedup_candidates = []
        for c in cat_candidates:
            if c["link"] not in seen_links:
                seen_links.add(c["link"])
                dedup_candidates.append(c)
        
        # 2. If we have fewer than 3 candidates, pull from Google News RSS search
        if len(dedup_candidates) < 3:
            search_articles = fetch_google_news_articles(info["search_query"], cat_name, max_articles=4)
            for s in search_articles:
                if s["link"] not in seen_links:
                    seen_links.add(s["link"])
                    dedup_candidates.append(s)
        
        candidates[cat_name] = dedup_candidates[:5]  # Limit to top 5 candidates per category
        log(f"Category '{cat_name}': Found {len(candidates[cat_name])} candidates.")
    
    return candidates

def get_genai_client():
    """Initialize and return the GenAI client using either Vertex AI or standard Developer API."""
    use_vertex = os.getenv("GEMINI_USE_VERTEXAI", "false").lower() == "true"
    api_key = os.getenv("GEMINI_API_KEY")
    
    if use_vertex:
        project = os.getenv("GCP_PROJECT", "project-drd")
        location = os.getenv("GCP_LOCATION", "us-central1")
        log(f"Initializing Vertex AI GenAI Client (Project: {project}, Location: {location})...")
        return genai.Client(
            vertexai=True,
            project=project,
            location=location,
            api_key=api_key if api_key else None
        )
    else:
        if not api_key:
            log("CRITICAL ERROR: GEMINI_API_KEY environment variable is not set in .env!")
            print("\n--- Setup Guide ---", file=sys.stderr)
            print("Please edit 'C:\\Users\\goldonil\\.projects\\drd\\.env' and set your GEMINI_API_KEY.", file=sys.stderr)
            print("You can get a free key from Google AI Studio: https://aistudio.google.com/", file=sys.stderr)
            print("Alternatively, if you are using Google Cloud Vertex AI, set GEMINI_USE_VERTEXAI=true in your .env.\n", file=sys.stderr)
            sys.exit(1)
        log("Initializing standard Gemini Developer Client...")
        return genai.Client(api_key=api_key)

def choose_top_articles_with_llm(candidates_dict, variety_counts):
    """Use Gemini to select the top 3 articles while considering rolling 7-day diversity."""
    client = get_genai_client()
    
    # Flatten candidates list and give them unique IDs for LLM referencing
    flattened_candidates = []
    idx = 1
    for cat, articles in candidates_dict.items():
        for art in articles:
            art["id"] = idx
            flattened_candidates.append(art)
            idx += 1
            
    # Serialize candidates lightly for prompt
    candidates_list_str = []
    for art in flattened_candidates:
        candidates_list_str.append(
            f"ID: {art['id']}\n"
            f"Category: {art['category']}\n"
            f"Title: {art['title']}\n"
            f"Source: {art['source']}\n"
            f"Snippet: {art['snippet']}\n"
            f"Link: {art['link']}\n"
            f"---"
        )
    candidates_prompt_data = "\n".join(candidates_list_str)
    
    # Format current variety stats
    variety_stats_str = "\n".join([f"- {cat}: {count} articles in last 7 days" for cat, count in variety_counts.items()])
    
    # Calculate underrepresented categories
    underrepresented = [cat for cat, count in variety_counts.items() if count == 0]
    underrepresented_guideline = ""
    if underrepresented:
        underrepresented_guideline = f"CRITICAL: The categories {underrepresented} have ZERO coverage in the last 7 days. You MUST prioritize selecting at least one article from these categories if a viable article is available."

    prompt = f"""You are a professional research agent specializing in industry intelligence.
Your task is to analyze candidate articles and select exactly THREE (3) total articles to feature in today's daily morning digest.

### Core Objectives:
1. Select articles of high technical depth, relevance, and genuine interest to a professional working in **Real Estate Development, Engineering Consulting, and Construction**.
2. Avoid low-quality clickbait, listicles, or generic press releases. Focus on industry trends, technical advances, economic changes, and real-world projects.
3. Enforce **category diversity** over a rolling 7-day period.

### Rolling 7-Day Category Coverage Statistics:
{variety_stats_str}

{underrepresented_guideline}

### Candidate Articles Pool:
{candidates_prompt_data}

### Instructions:
Select exactly three (3) article IDs from the pool.
Return your decision in raw JSON format using exactly this schema:
{{
  "selected_ids": [id1, id2, id3],
  "selection_rationale": {{
     "id1": "A brief explanation of why this article was selected, specifically highlighting how it contributes to variety or brings critical value.",
     "id2": "A brief explanation...",
     "id3": "A brief explanation..."
  }}
}}

Ensure you only output valid JSON. Do not wrap it in markdown code blocks. Just output raw JSON.
"""

    log("Consulting Gemini to select the optimal 3 articles considering rolling variety...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Clean JSON markdown fences if LLM included them anyway
        if response_text.startswith("```json"):
            response_text = response_text.split("```json", 1)[1].rsplit("```", 1)[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```", 1)[1].rsplit("```", 1)[0].strip()
            
        selection_data = json.loads(response_text)
        selected_ids = selection_data.get("selected_ids", [])
        rationales = selection_data.get("selection_rationale", {})
        
        final_articles = []
        for art in flattened_candidates:
            if art["id"] in selected_ids:
                art["selection_rationale"] = rationales.get(str(art["id"]), "Selected for relevance and impact.")
                final_articles.append(art)
                
        # Fallback if something went wrong
        if len(final_articles) < 3 and flattened_candidates:
            log("LLM selection returned fewer than 3 articles. Falling back to default selection.")
            final_articles = flattened_candidates[:3]
            
        return final_articles
    except Exception as e:
        log(f"Error during LLM selection: {e}")
        # Return first article of each of the first three categories as safety fallback
        fallback = []
        for cat, list_art in candidates_dict.items():
            if list_art:
                fallback.append(list_art[0])
            if len(fallback) == 3:
                break
        return fallback

def generate_deep_article_summary(article, client):
    """Scrapes the full text of an article and calls Gemini to create a rich, structured summary."""
    full_text = scrape_full_content(article["link"])
    
    # If scraper blocked or failed, fall back to snippet
    if not full_text or len(full_text) < 300:
        log(f"Scrape details insufficient for full text. Using RSS snippet as context.")
        full_text = f"Article Title: {article['title']}\nSnippet/Context: {article['snippet']}\nCategory: {article['category']}"
        
    prompt = f"""You are an elite industry intelligence analyst summarizing a critical news development for a leading real estate developer and engineering consultant.

Analyze the article below:
---
Category: {article['category']}
Title: {article['title']}
Source: {article['source']}
Link: {article['link']}

Raw Content / Context:
{full_text}
---

### Output Requirements:
Generate a beautiful, concise, and highly scannable Markdown analysis. Focus heavily on "the WHY it matters". Break the response into these exact Markdown sections:

1. **Core Development & Rationale**:
   - Write a single, punchy paragraph explaining *what* happened and *why* this development was selected today over standard daily news.
2. **Key Industry Impacts**:
   - **Real Estate**: 1-2 highly specific, concise bullet points on how this impacts development strategy, financing, zoning, or valuation.
   - **Engineering & Construction**: 1-2 highly specific, concise bullet points on how this impacts structural/MEP design, construction technology, or workflows.
3. **Strategic Takeaway**:
   - Write a single, high-impact sentence on how this insight strengthens the user's professional leverage or foresight.

Keep your writing extremely sharp, analytical, and professional. Avoid any introductory or conversational filler text—start directly with the Markdown sections.

"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        log(f"Error generating summary for '{article['title']}': {e}")
        return f"### Summary unavailable due to generation error.\n\n*Error details: {e}*\n\nOriginal link: [Read article here]({article['link']})"

def compile_daily_digest(selected_articles):
    """Generate the markdown document for today's digest and update the dashboard index."""
    current_date = get_current_date()
    today_str = current_date.strftime("%Y-%m-%d")
    today_formatted = current_date.strftime("%B %d, %Y")
    now = datetime.datetime.now()
    current_time_formatted = now.strftime("%I:%M %p")
    
    digest_filename = f"{today_str}_digest.md"
    digest_path = OUTPUT_DIR / digest_filename
    
    log(f"Compiling daily digest: {digest_path}")
    
    # Initialize client
    client = get_genai_client()
    
    # Generate content for each selected article
    digest_sections = []
    for idx, art in enumerate(selected_articles, 1):
        log(f"Generating rich summary {idx}/3: '{art['title']}'...")
        rich_summary = generate_deep_article_summary(art, client)
        
        section_md = f"""## Article {idx}: {art['title']}

* **Category**: `{art['category']}`
* **Source**: *{art['source']}*
* **Link**: [Original Article]({art['link']})
* **Selection Rationale**: {art.get('selection_rationale', 'Selected for outstanding industry relevance.')}

{rich_summary}

---
"""
        digest_sections.append(section_md)
        
    full_digest_md = f"""# Daily Industry Intelligence Digest
**Date**: {today_formatted}

Welcome to your curated morning digest. The selected articles below have been parsed, filtered, and analyzed specifically for their strategic relevance to **Real Estate Development**, **Engineering Consulting**, and **Modern Construction**.

---

{"".join(digest_sections)}

*Digest generated automatically at {current_time_formatted}. Selection history and rotation logic updated in `history.json`.*
"""

    # Save daily digest
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(full_digest_md)
    log(f"Daily digest successfully saved to {digest_path}")
    
    # Update master index/dashboard
    update_index_file(today_str, today_formatted, selected_articles)

def compile_daily_digest_from_provided(selected_articles):
    """Generate the markdown document using pre-generated agent summaries and update the dashboard index."""
    current_date = get_current_date()
    today_str = current_date.strftime("%Y-%m-%d")
    today_formatted = current_date.strftime("%B %d, %Y")
    now = datetime.datetime.now()
    current_time_formatted = now.strftime("%I:%M %p")
    
    digest_filename = f"{today_str}_digest.md"
    digest_path = OUTPUT_DIR / digest_filename
    
    log(f"Compiling daily digest: {digest_path}")
    
    # Generate content for each selected article
    digest_sections = []
    for idx, art in enumerate(selected_articles, 1):
        rich_summary = art.get("rich_summary", "Summary unavailable.")
        section_md = f"""## Article {idx}: {art['title']}

* **Category**: `{art['category']}`
* **Source**: *{art['source']}*
* **Link**: [Original Article]({art['link']})
* **Selection Rationale**: {art.get('selection_rationale', 'Selected for outstanding industry relevance.')}

{rich_summary}

---
"""
        digest_sections.append(section_md)
        
    full_digest_md = f"""# Daily Industry Intelligence Digest
**Date**: {today_formatted}

Welcome to your curated morning digest. The selected articles below have been parsed, filtered, and analyzed specifically for their strategic relevance to **Real Estate Development**, **Engineering Consulting**, and **Modern Construction**.

---

{"".join(digest_sections)}

*Digest generated automatically at {current_time_formatted}. Selection history and rotation logic updated in `history.json`.*
"""

    # Save daily digest
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(full_digest_md)
    log(f"Daily digest successfully saved to {digest_path}")
    
    # Update master index/dashboard
    update_index_file(today_str, today_formatted, selected_articles)

def update_index_file(date_str, date_formatted, selected_articles):
    """Append the new digest to a beautiful central README index dashboard."""
    log("Updating master digest index...")
    
    articles_list_md = ""
    for art in selected_articles:
        articles_list_md += f"- **[{art['category']}]** [{art['title']}]({art['link']}) *(via {art['source']})*\n"
        
    entry_md = f"""### 📅 [{date_formatted}](file:///{OUTPUT_DIR.resolve()}/{date_str}_digest.md)
{articles_list_md}
"""
    
    if not INDEX_FILE.exists():
        # Create fresh central index
        index_header = f"""# Industry Intelligence Digests Index
Welcome to your personal learning and industry intelligence repository. Below is a comprehensive index of all daily digests generated for **Real Estate Development, Engineering, and AI**.

---

## Daily Digests Archive

{entry_md}
"""
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(index_header)
    else:
        # Read index, inject below header
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find the header "## Daily Digests Archive" and inject directly below it
            anchor = "## Daily Digests Archive"
            if anchor in content:
                parts = content.split(anchor, 1)
                new_content = f"{parts[0]}{anchor}\n\n{entry_md}{parts[1]}"
                with open(INDEX_FILE, "w", encoding="utf-8") as f:
                    f.write(new_content)
            else:
                # Fallback append
                with open(INDEX_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n{entry_md}")
        except Exception as e:
            log(f"Error updating index file: {e}")

def update_history_and_save(selected_articles):
    """Record selected articles in history.json."""
    log("Updating history log...")
    history_data = load_history()
    current_date = get_current_date()
    today_str = current_date.strftime("%Y-%m-%d")
    
    # Build clean history record
    history_record = {
        "date": today_str,
        "articles": [
            {
                "title": art["title"],
                "category": art["category"],
                "link": art["link"],
                "source": art["source"]
            } for art in selected_articles
        ]
    }
    
    # Remove any existing entry for today to prevent duplicates on manual re-runs
    history_data["history"] = [entry for entry in history_data["history"] if entry.get("date") != today_str]
    history_data["history"].append(history_record)
    
    # Limit history list size to last 100 entries to prevent endless growth
    if len(history_data["history"]) > 100:
        history_data["history"] = history_data["history"][-100:]
        
    save_history(history_data)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Daily News Digest workflow.")
    parser.add_argument("--get-candidates", action="store_true", help="Scrape all latest candidates and output as JSON.")
    parser.add_argument("--compile-digest", type=str, help="Compile digest using pre-generated summaries from a JSON file.")
    parser.add_argument("--date", type=str, help="Override date in YYYY-MM-DD format (defaults to today).")
    
    args = parser.parse_args()
    
    if args.date:
        global OVERRIDE_DATE_OBJ
        try:
            OVERRIDE_DATE_OBJ = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
            log(f"Date override activated: {OVERRIDE_DATE_OBJ}")
        except ValueError:
            log(f"Error: Invalid date format '{args.date}'. Expected YYYY-MM-DD.")
            sys.exit(1)
            
    if args.get_candidates:
        log("Getting candidates...")
        # 1. Fetch Candidates
        candidates = select_candidates()
        
        # 2. Load History and counts
        history_data = load_history()
        variety_counts = get_rolling_variety_counts(history_data)
        
        output_data = {
            "candidates": candidates,
            "variety_counts": variety_counts
        }
        
        # Print pure JSON to stdout
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
        sys.exit(0)
        
    elif args.compile_digest:
        log(f"Compiling digest from file: {args.compile_digest}")
        if not os.path.exists(args.compile_digest):
            log(f"Error: JSON file not found: {args.compile_digest}")
            sys.exit(1)
            
        try:
            with open(args.compile_digest, "r", encoding="utf-8") as f:
                selected_articles = json.load(f)
        except Exception as e:
            log(f"Error reading selections JSON: {e}")
            sys.exit(1)
            
        # Verify shape
        if not isinstance(selected_articles, list) or len(selected_articles) == 0:
            log("Error: Invalid JSON format. Expected a list of articles.")
            sys.exit(1)
            
        # Compile
        compile_daily_digest_from_provided(selected_articles)
        
        # Update history
        update_history_and_save(selected_articles)
        log("Digest compiled successfully from agent-provided data.")
        sys.exit(0)
        
    else:
        # Standard workflow
        log("Starting Daily News Digest Workflow Execution...")
        
        # 1. Fetch Candidates
        candidates = select_candidates()
        
        # 2. Load History and counts
        history_data = load_history()
        variety_counts = get_rolling_variety_counts(history_data)
        log(f"Rolling 7-day category counts: {variety_counts}")
        
        # 3. Select top 3 articles
        selected_articles = choose_top_articles_with_llm(candidates, variety_counts)
        log(f"Selected articles: {[a['title'] for a in selected_articles]}")
        
        # 4. Generate summaries and compile Markdown
        compile_daily_digest(selected_articles)
        
        # 5. Record today's selection in History
        update_history_and_save(selected_articles)
        log("Daily News Digest Workflow completed successfully!")

if __name__ == "__main__":
    main()
