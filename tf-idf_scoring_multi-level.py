# tfidf_scoring_multilevel.py
"""
Apply unified TF-IDF scoring to the combined multi-level citation dataset.
Each 'sub_category' group (keyword combination) is ranked by relevance to its keywords.
Outputs one ranked Excel per sub_category and a master ranked file.
"""

import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

# ---------- CONFIG ----------
INPUT_FILE = "all_multilevel_combined.xlsx"
SAVE_DIR = "results_multilevel_ranked"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------- TF-IDF scoring function ----------
def extract_tfidf(df, keywords):
    corpus = df["abstract"].fillna("").astype(str)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 3), max_features=10000)
    X = vectorizer.fit_transform(corpus)
    keyword_vector = vectorizer.transform([" ".join(keywords)])
    scores = (X * keyword_vector.T).toarray().flatten()
    df["tfidf_score"] = scores
    return df.sort_values("tfidf_score", ascending=False)

# ---------- MAIN ----------
if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"⚠️ Combined file '{INPUT_FILE}' not found.")
        exit()

    df_all = pd.read_excel(INPUT_FILE)
    print(f"🔹 Loaded {len(df_all)} total papers from {INPUT_FILE}")

    if "sub_category" not in df_all.columns:
        print("⚠️ 'sub_category' column not found — cannot group by keyword combination.")
        exit()

    ranked_groups = []
    subcategories = df_all["sub_category"].dropna().unique()

    # ---------- Process each subcategory ----------
    for subcat in tqdm(subcategories, desc="Scoring subcategories"):
        group_df = df_all[df_all["sub_category"] == subcat].copy()
        keywords = [k.strip() for k in subcat.split(",")]

        if group_df.empty:
            print(f"⚠️ Skipping empty group: {subcat}")
            continue

        ranked_df = extract_tfidf(group_df, keywords)
        ranked_df["sub_category"] = subcat
        ranked_groups.append(ranked_df)

        # save individual ranked file
        safe_name = subcat.replace(", ", "_").replace(" ", "_")
        out_path = os.path.join(SAVE_DIR, f"ranked_{safe_name}.xlsx")
        ranked_df.to_excel(out_path, index=False)

    # ---------- Combine all ranked results ----------
    final_df = pd.concat(ranked_groups, ignore_index=True)
    combined_path = os.path.join(SAVE_DIR, "all_multilevel_ranked_combined.xlsx")
    final_df.to_excel(combined_path, index=False)

    print(f"\n✅ TF-IDF ranking completed.")
    print(f"📘 Total combined ranked papers: {len(final_df)}")
    print(f"📂 Saved master ranked file: {combined_path}")

    # ---------- Optional summary ----------
    summary = (
        final_df.groupby("sub_category")["tfidf_score"]
        .mean()
        .reset_index()
        .sort_values("tfidf_score", ascending=False)
    )
    summary.to_excel(os.path.join(SAVE_DIR, "subcategory_tfidf_summary.xlsx"), index=False)
    print("📊 Saved subcategory TF-IDF summary: subcategory_tfidf_summary.xlsx")