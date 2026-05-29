import os
import sys
import datetime
from pathlib import Path
import json

PROJECT_DIR = Path(r"C:\Users\goldonil\.projects\drd")
OUTPUT_DIR = PROJECT_DIR / "drd-inbox-raw"
HISTORY_FILE = OUTPUT_DIR / "history.json"
INDEX_FILE = OUTPUT_DIR / "index.md"

today_str = "2026-05-27"
today_formatted = "May 27, 2026"
digest_filename = f"{today_str}_digest.md"
digest_path = OUTPUT_DIR / digest_filename

selected_articles = [
    {
        "title": "SL Green Sells 49% Stake in 346 Madison Avenue to Mori Building Co.",
        "category": "Commercial Real Estate",
        "link": "https://commercialobserver.com/2026/05/sl-green-346-madison-mori-new-tower/",
        "source": "commercialobserver.com",
        "selection_rationale": "Selected for outstanding industry relevance and impact on Midtown high-density transit developments."
    },
    {
        "title": "Google just redesigned the search box for the first time in 25 years — here’s why it matters more than you think.",
        "category": "Artificial Intelligence",
        "link": "https://venturebeat.com/technology/google-just-redesigned-the-search-box-for-the-first-time-in-25-years-heres-why-it-matters-more-than-you-think",
        "source": "venturebeat.com",
        "selection_rationale": "Selected for representing an epochal interface shift that redirects digital search strategies."
    },
    {
        "title": "Pea-size liquid-metal pump runs robot butterfly on under 0.1 V",
        "category": "Engineering Principles",
        "link": "https://techxplore.com/news/2026-05-pea-size-liquid-metal-robot.html",
        "source": "techxplore.com",
        "selection_rationale": "Selected for showcasing an innovative material-science breakthrough with vast soft-robotics application potential."
    }
]

article_1_summary = """1. **Why It Matters & Selection Rationale**:
   - SL Green's transaction represents a significant validation of Midtown Manhattan's premium commercial office sector. Valuing the 346 Madison Avenue site at a gross $175 million, this joint venture with Mori Building Co.—one of Japan's most prominent real estate developers—proves that international capital remains highly attracted to core, transit-oriented Manhattan redevelopments. This venture will replace the existing structures with a state-of-the-art 46-story, 850,000-square-foot office tower adjacent to Grand Central Terminal, leveraging the landmark Grand Central East Midtown rezoning framework.

2. **Robust Article Breakdown**:
   - **Deal Structure**: SL Green sold a 49% stake in 346 Madison Avenue to Mori Building Co. at a gross property valuation of $175 million.
   - **Development Scale**: The joint venture will construct a 46-story, 850,000-square-foot Class A office tower.
   - **Geographic Strategic Value**: The site is situated within the Grand Central submarket, immediately benefiting from the high-density rezoning provisions of East Midtown.
   - **Mori's Entry**: This represents a notable entry/expansion for Tokyo-based Mori Building Co. into the NYC market, highlighting international confidence in prime US commercial real estate.

3. **Industry Rationale & Impact**:
   - **Real Estate Development Impact**: Developers should note the ongoing strength of "flight-to-quality" in commercial office assets. While B- and C-class office assets struggle, premium transit-connected developments continue to command joint-venture premiums. The transaction demonstrates that combining local development expertise (SL Green) with international long-term equity (Mori) is an effective strategy to capitalize mega-projects in high-interest rate environments.
   - **Engineering Consulting & Construction Impact**: Constructing an 850,000-square-foot tower in a dense Midtown submarket presents intense structural and logistical constraints. The proximity to Grand Central Terminal requires highly sophisticated foundation design, seismic monitoring, and vibration isolation systems to mitigate impact on subterranean transit tunnels. Additionally, achieving LEED Gold or Platinum certification will be mandatory to comply with NYC’s Local Law 97 carbon limits.

4. **Professional Value & Leverage**:
   - For professionals in development and engineering, this deal reinforces the critical value of master planning and transit-oriented density. Understanding how municipal rezoning (East Midtown Rezoning) directly unlocks hundreds of millions in land value is key for negotiating joint ventures and planning large-scale urban infrastructure."""

article_2_summary = """1. **Why It Matters & Selection Rationale**:
   - For over 25 years, the simple white search bar has been the primary gateway to the internet. Google's announcement at I/O to retire this text-and-blue-links paradigm in favor of an AI-native, multi-modal conversational canvas marks an epochal shift in digital interfaces. This transition directly impacts how users discover services, how businesses optimize for visibility, and how technical consultants design enterprise information systems.

2. **Robust Article Breakdown**:
   - **Interface Metamorphosis**: The traditional search box is being replaced with a multi-modal conversational canvas that digests text, voice, video, and image inputs simultaneously.
   - **Generative Search Experience (SGE)**: Rather than routing users to a list of external URLs, Google will synthesize direct, multi-source answers, keeping user traffic within the Google ecosystem.
   - **Technical Infrastructure Surges**: Bypassing traditional indexing in favor of real-time multi-agent reasoning models requires highly specialized hyper-scale data center architectures.

3. **Industry Rationale & Impact**:
   - **Real Estate Development Impact**: As AI-native search engines bypass traditional SEO, the digital footprint of real estate assets must evolve. Traditional website traffic will decrease, while direct structured data feeds (Schema.org, Yext, and API integrations) will become the primary source for AI engines indexing multi-family rental availability, retail spaces, and commercial properties.
   - **Engineering Consulting & Construction Impact**: The rapid scaling of real-time AI search models is driving unprecedented demand for next-generation data center infrastructure. Engineering consultants must pivot to designing facilities that accommodate ultra-high-density rack power requirements (50kW to 100kW+ per rack), transition from air cooling to liquid-to-chip direct cooling, and optimize power delivery architectures to handle massive load swings.

4. **Professional Value & Leverage**:
   - Understanding this shift allows technology and development consultants to prepare client architectures for a post-SEO world. Strategically designing digital assets as structured, query-ready AI knowledge nodes ensures your projects remain highly visible and discoverable in conversational search ecosystems."""

article_3_summary = """1. **Why It Matters & Selection Rationale**:
   - Published in *Nature Communications* by engineers at the University of Bristol, this breakthrough solves one of the most persistent bottlenecks in soft robotics and wearable devices: the power-to-weight ratio of high-voltage pumps. By creating an ingenious, pea-size electromagnetic pump using gallium-based liquid metal that operates at an ultra-low voltage of under 0.1 V, researchers have unlocked a new paradigm for silent, highly efficient fluidic actuation.

2. **Robust Article Breakdown**:
   - **Ultra-Low Voltage Operation**: The pump operates successfully on under 0.1 V, a massive drop from the thousands of volts typically required by traditional electrohydrodynamic pumps.
   - **Miniaturization**: The entire pump assembly is the size of a single pea, allowing it to fit into highly constrained spaces.
   - **Actuation Capability**: Despite its size, it generates sufficient fluid flow to actuate a soft-robotic butterfly and can be scaled for complex soft actuators.
   - **Material Science**: Uses a non-toxic gallium-indium liquid metal alloy (EGaIn) to enable low-resistance electric current conduction and direct fluid propulsion.

3. **Industry Rationale & Impact**:
   - **Real Estate Development Impact**: While soft robotics may seem distant, this breakthrough accelerates the commercial viability of smart buildings and active building skins. Liquid-metal micro-pumps can be integrated into window glass or facade panels to dynamically circulate temperature-regulating or light-filtering fluids, drastically reducing heating and cooling loads without noisy mechanical infrastructure.
   - **Engineering Consulting & Construction Impact**: The principles of liquid-metal magnetohydrodynamics open new channels for micro-fluidic engineering. Mechanical and structural consultants can leverage this technology for ultra-quiet, localized cooling loops in building systems, smart wearable safety gear for construction workers (such as active-cooling haptic gloves), and structural health monitoring sensors that use micro-circulating conductive fluids to detect stress fractures in concrete or steel.

4. **Professional Value & Leverage**:
   - Keeping pace with advancements in micro-scale fluidics and liquid-metal systems positions engineering consultants at the cutting edge of materials science. It provides deep foresight into the future of biomimetic building systems and advanced wearable automation."""

summaries = [article_1_summary, article_2_summary, article_3_summary]

digest_sections = []
for idx, art in enumerate(selected_articles, 1):
    rich_summary = summaries[idx - 1]
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

*Digest generated automatically at 5:00 AM. Selection history and rotation logic updated in `history.json`.*
"""

# Save daily digest
with open(digest_path, "w", encoding="utf-8") as f:
    f.write(full_digest_md)
print(f"Daily digest successfully saved to {digest_path}")

# Update index.md
articles_list_md = ""
for art in selected_articles:
    articles_list_md += f"- **[{art['category']}]** [{art['title']}]({art['link']}) *(via {art['source']})*\n"
    
entry_md = f"### 📅 [{today_formatted}](file:///{OUTPUT_DIR.resolve()}/{today_str}_digest.md)\n{articles_list_md}\n"

if not INDEX_FILE.exists():
    index_header = f"""# Industry Intelligence Digests Index
Welcome to your personal learning and industry intelligence repository. Below is a comprehensive index of all daily digests generated for **Real Estate Development, Engineering, and AI**.

---

## Daily Digests Archive

{entry_md}
"""
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_header)
else:
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    anchor = "## Daily Digests Archive"
    if anchor in content:
        parts = content.split(anchor, 1)
        new_content = f"{parts[0]}{anchor}\n\n{entry_md}{parts[1]}"
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
    else:
        with open(INDEX_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{entry_md}")

# Update history.json
if HISTORY_FILE.exists():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history_data = json.load(f)
    except Exception:
        history_data = {"history": []}
else:
    history_data = {"history": []}

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

history_data["history"] = [entry for entry in history_data["history"] if entry.get("date") != today_str]
history_data["history"].append(history_record)

if len(history_data["history"]) > 100:
    history_data["history"] = history_data["history"][-100:]

with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(history_data, f, indent=2, ensure_ascii=False)

print("Updated history.json and index.md successfully!")
