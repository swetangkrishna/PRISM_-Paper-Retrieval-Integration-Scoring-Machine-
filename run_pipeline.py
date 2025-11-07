"""
run_pipeline.py
Unified pipeline to retrieve, combine, rank, and visualize research papers.
Reads keyword lists directly from paper_citation_retrieval.py.
"""

import subprocess
import os

def ensure_output_dir(path="analysis_outputs"):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 Created output directory: {path}")

def run_step(description, command):
    print(f"\n➡️ {description}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error in step: {description}")
        print(f"   Command: {' '.join(command)}")
        print(f"   Error: {e}\n")

def main():
    print("\n🚀 Starting full citation analysis pipeline...\n")

    # Step 1: Retrieve papers
    run_step("Step 1: Retrieving papers based on COMPULSORY and OPTIONAL keywords...", 
             ["python", "paper_citation_retrieval.py"])
    
    # Step 2: Combine results (moved before TF-IDF)
    run_step("Step 2: Combining multi-level data...", 
             ["python", "combine_multi-level.py"])
    
    # Step 3: TF-IDF Scoring
    run_step("Step 3: Calculating TF-IDF scores...", 
             ["python", "tf-idf_scoring_multi-level.py"])
    
    # Step 4: Visualization
    ensure_output_dir("analysis_outputs")
    run_step("Step 4: Generating visual analysis from combined data...", [
        "jupyter", "nbconvert",
        "--to", "notebook",
        "--execute", "data_representation_citaton.ipynb",
        "--output", "data_representation_output.ipynb"
    ])

    print("\n✅ Pipeline completed successfully!")
    print("📘 Outputs:")
    print(" - all_multilevel_combined.xlsx")
    print(" - all_multilevel_ranked_combined.xlsx")
    print(" - subcategory_tfidf_summary.xlsx")
    print(" - analysis_outputs/ folder (visuals)\n")

if __name__ == "__main__":
    main()