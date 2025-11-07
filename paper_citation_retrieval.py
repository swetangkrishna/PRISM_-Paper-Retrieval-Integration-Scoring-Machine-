"""
Multi-level paper retrieval with citation expansion (arXiv + OpenAlex + Google Scholar).
Each OpenAlex paper expands its citation network recursively up to MAX_DEPTH.
Filters included papers by keyword match and TF-IDF similarity threshold.
"""

import itertools
import os
import requests
import feedparser
import pandas as pd
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time

# ---------- CONFIG ----------
COMPULSORY_KEYWORDS = ["LLM", "AI", "pedagogy", "education"]
OPTIONAL_KEYWORDS = ["knowledge graph", "fine tuning", "benchmarks", "evaluate"]
SERPAPI_KEY = "use your api key not mine :) "
SAVE_DIR = "results_multilevel"
os.makedirs(SAVE_DIR, exist_ok=True)

MAX_DEPTH = 2           # 🔁 recursion depth
SIMILARITY_THRESHOLD = 0.3
REQUEST_SLEEP = 1.5     # polite delay between API calls

# ---------- 1. Keyword Combos ----------
def generate_keyword_combinations():
    combos = []
    for r in range(0, len(OPTIONAL_KEYWORDS) + 1):
        for subset in itertools.combinations(OPTIONAL_KEYWORDS, r):
            combos.append(COMPULSORY_KEYWORDS + list(subset))
    return combos

# ---------- 2. arXiv ----------
def fetch_arxiv_papers(keywords, max_results=200):
    query = " OR ".join(keywords)
    all_entries = []
    for start in range(0, 600, 200):
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start={start}&max_results={max_results}"
        feed = feedparser.parse(requests.get(url, timeout=20).text)
        if not feed.entries:
            break
        all_entries.extend(feed.entries)
        time.sleep(REQUEST_SLEEP)
    return [{
        "id": e.get("id", ""),
        "title": e.title,
        "abstract": e.summary,
        "url": e.link,
        "source": "arXiv",
        "depth": 0
    } for e in all_entries]

# ---------- 3. OpenAlex Base Search ----------
def fetch_openalex_papers(keywords, per_page=100, max_pages=5):
    query = " OR ".join(keywords)
    base_url = "https://api.openalex.org/works"
    cursor = "*"
    papers = []
    for _ in range(max_pages):
        url = f"{base_url}?search={query}&per-page={per_page}&cursor={cursor}"
        data = requests.get(url, timeout=30).json()
        for d in data.get("results", []):
            abs_txt = ""
            if d.get("abstract_inverted_index"):
                abs_txt = " ".join(d["abstract_inverted_index"].keys())
            papers.append({
                "id": d.get("id", ""),
                "title": d.get("title", ""),
                "abstract": abs_txt,
                "url": d.get("id"),
                "source": "OpenAlex",
                "depth": 0
            })
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(REQUEST_SLEEP)
    return papers

# ---------- 4. Google Scholar ----------
def fetch_scholar_papers(keywords, api_key, max_pages=5):
    query = " OR ".join(keywords)
    papers = []
    for page in range(max_pages):
        start = page * 10
        url = f"https://serpapi.com/search.json?engine=google_scholar&q={query}&start={start}&api_key={api_key}"
        data = requests.get(url, timeout=20).json()
        if "organic_results" not in data:
            break
        for res in data.get("organic_results", []):
            papers.append({
                "id": res.get("link", ""),
                "title": res.get("title"),
                "abstract": res.get("snippet", ""),
                "url": res.get("link"),
                "source": "Google Scholar",
                "depth": 0
            })
        if len(data.get("organic_results", [])) < 10:
            break
        time.sleep(REQUEST_SLEEP)
    return papers

# ---------- 5. Citation Expansion ----------
def fetch_citations_openalex(work_id):
    """Return papers cited by and citing the given paper (OpenAlex only)."""
    results = []
    try:
        # cited-by (downstream)
        citing_url = f"https://api.openalex.org/works?filter=cites:{work_id}"
        citing_resp = requests.get(citing_url, timeout=20).json()
        for ref in citing_resp.get("results", []):
            abs_txt = ""
            if ref.get("abstract_inverted_index"):
                abs_txt = " ".join(ref["abstract_inverted_index"].keys())
            results.append({
                "id": ref.get("id", ""),
                "title": ref.get("title", ""),
                "abstract": abs_txt,
                "url": ref.get("id"),
                "source": "OpenAlex_CITING"
            })

        # references (upstream)
        cited_url = f"{work_id}/referenced_works?per-page=100"
        cited_resp = requests.get(cited_url, timeout=20).json()
        for ref in cited_resp.get("results", []):
            abs_txt = ""
            if ref.get("abstract_inverted_index"):
                abs_txt = " ".join(ref["abstract_inverted_index"].keys())
            results.append({
                "id": ref.get("id", ""),
                "title": ref.get("title", ""),
                "abstract": abs_txt,
                "url": ref.get("id"),
                "source": "OpenAlex_CITED"
            })
    except Exception:
        pass
    time.sleep(REQUEST_SLEEP)
    return results

# ---------- 6. Similarity + Keyword Filter ----------
def filter_papers_by_similarity(parent_paper, related_papers, keywords):
    valid = []
    all_texts = [parent_paper.get("abstract", "")] + [p.get("abstract", "") for p in related_papers if p.get("abstract")]
    if len(all_texts) < 2:
        return valid
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(all_texts)
    sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    for i, paper in enumerate(related_papers):
        if not paper.get("abstract"):
            continue
        score = sims[i]
        text = (paper["title"] + " " + paper["abstract"]).lower()
        if any(k.lower() in text for k in keywords) and score >= SIMILARITY_THRESHOLD:
            paper["similarity"] = score
            valid.append(paper)
    return valid

# ---------- 7. Recursive Citation Expansion ----------
def expand_citations_recursive(paper, keywords, depth, visited):
    """Recursively expand citations up to MAX_DEPTH."""
    if depth >= MAX_DEPTH or not paper.get("id"):
        return []

    related = fetch_citations_openalex(paper["id"])
    related_filtered = filter_papers_by_similarity(paper, related, keywords)
    next_level = []

    for rp in related_filtered:
        if rp["id"] not in visited:
            visited.add(rp["id"])
            rp["depth"] = depth + 1
            next_level.append(rp)
            # recursive call
            next_level.extend(expand_citations_recursive(rp, keywords, depth + 1, visited))

    return next_level

# ---------- 8. Save ----------
def save_combination_results(combo, papers, idx):
    df = pd.DataFrame(papers).drop_duplicates(subset=["title"])
    combo_name = "_".join([k.replace(" ", "_") for k in combo])
    path = os.path.join(SAVE_DIR, f"{idx:02d}_{combo_name}.xlsx")
    df.to_excel(path, index=False)
    print(f"✅ Saved {len(df)} papers for {combo_name}")
    return path

# ---------- MAIN ----------
if __name__ == "__main__":
    combos = generate_keyword_combinations()
    print(f"🔹 Total combinations: {len(combos)}")

    for idx, combo in enumerate(tqdm(combos, desc="Processing combinations")):
        all_papers = []
        visited = set()

        try:
            print(f"\n📚 Keywords: {combo}")
            arxiv = fetch_arxiv_papers(combo)
            openalex = fetch_openalex_papers(combo)
            scholar = fetch_scholar_papers(combo, SERPAPI_KEY)
            all_papers.extend(arxiv + openalex + scholar)

            # multi-level citation expansion
            expanded = []
            for p in tqdm(openalex, desc="Expanding citation tree", leave=False):
                if p["id"] and p["id"] not in visited:
                    visited.add(p["id"])
                    expanded.extend(expand_citations_recursive(p, combo, 0, visited))
            all_papers.extend(expanded)

        except Exception as e:
            print(f"⚠️ Error fetching for {combo}: {e}")

        if all_papers:
            save_combination_results(combo, all_papers, idx)
        else:
            print(f"⚠️ No results for {combo}")