# combine_multilevel_results.py
"""
Combine all multi-level citation result Excel files into one master file.
Adds:
  - 'sub_category' = keywords from filename
  - 'source_file'  = original file name
  - 'depth_level'  = average or most common depth of that file’s entries (if column exists)
Outputs:
  - all_multilevel_combined.xlsx
  - subcategory_summary.xlsx
"""

import os
import pandas as pd
from tqdm import tqdm

# ---------- CONFIG ----------
MULTILEVEL_DIR = "results_multilevel"
OUTPUT_FILE = "all_multilevel_combined.xlsx"

# ---------- 1. Collect all result files ----------
files = [f for f in os.listdir(MULTILEVEL_DIR) if f.endswith(".xlsx")]

if not files:
    print("⚠️ No Excel files found in 'results_multilevel/' folder.")
    exit()

combined_df = []

# ---------- 2. Combine all ----------
for file in tqdm(files, desc="Combining multi-level citation files"):
    path = os.path.join(MULTILEVEL_DIR, file)
    df = pd.read_excel(path)

    # Extract subcategory keywords from filename
    # Example: 03_LLM_AI_pedagogy_education_fine_tuning.xlsx
    filename = file.replace(".xlsx", "")
    parts = filename.split("_")
    # Remove numeric prefix if present (first part is usually 01, 02, etc.)
    keywords = parts[1:] if parts[0].isdigit() else parts
    keywords = [kw.replace("_", " ") for kw in keywords]
    sub_category = ", ".join(keywords)

    # Add metadata columns
    df["sub_category"] = sub_category
    df["source_file"] = file

    # Optional: Add file-level depth info if 'depth' column exists
    if "depth" in df.columns:
        df["depth_level"] = df["depth"]
    else:
        df["depth_level"] = None

    combined_df.append(df)

# ---------- 3. Merge all data ----------
final_df = pd.concat(combined_df, ignore_index=True)
print(f"✅ Combined total records: {len(final_df)}")

# ---------- 4. Save to one master Excel ----------
final_df.to_excel(OUTPUT_FILE, index=False)
print(f"📘 Saved all combined multi-level citation papers to: {OUTPUT_FILE}")

# ---------- 5. Optional summary by sub_category ----------
if "similarity" in final_df.columns:
    summary = (
        final_df.groupby("sub_category")["similarity"]
        .mean()
        .reset_index()
        .sort_values("similarity", ascending=False)
    )
    summary.to_excel("subcategory_summary.xlsx", index=False)
    print("📊 Saved average similarity summary: subcategory_summary.xlsx")
else:
    print("ℹ️ No 'similarity' column found — skipped summary creation.")