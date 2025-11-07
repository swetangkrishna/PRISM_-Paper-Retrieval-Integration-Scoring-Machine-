
content = """# 🧩 Research Paper Retrieval & Analysis Pipeline

This repository provides an automated end-to-end pipeline for retrieving, ranking, combining, and visualizing research papers based on predefined keywords.  
It integrates multiple scripts into one seamless workflow, requiring only minimal setup.

---

## ⚙️ Overview

The pipeline performs the following steps automatically:

1. **Paper Retrieval** – Searches for research papers online using your specified compulsory and optional keywords.  
2. **TF-IDF Scoring** – Calculates the importance of keywords and ranks papers accordingly.  
3. **Result Combination** – Merges outputs from multiple ranking levels into a consolidated Excel file.  
4. **Visualization & Analysis** – Generates keyword overlap charts, distribution plots, and statistical summaries.  

All results are automatically saved in structured output files for further review or analysis.

---

## 🧠 Workflow Summary

| Step | Script | Function |
|:----:|:-----------------------------|:--------------------------------------------|
| 1️⃣ | `paper_citation_retrieval.py` | Retrieves papers using the API and extracts keywords. |
| 2️⃣ | `tf-idf_scoring_multi-level.py` | Performs multi-level TF-IDF scoring for ranking. |
| 3️⃣ | `combine_multi-level.py` | Combines intermediate results into one Excel file. |
| 4️⃣ | `data_representation_citaton.ipynb` | Generates data visualizations and summary statistics. |
| 🚀 | `run_pipeline.py` | Automates execution of all steps above in sequence. |

---

## 🧰 Requirements

**Python Version:**  
Python 3.9 or higher  

**Dependencies:**
```bash
pip install pandas numpy matplotlib seaborn requests openai jupyter
```

**Optional but recommended:**  
Use `virtualenv` or `conda` to isolate dependencies.

---

## 🔑 API Configuration

The paper retrieval step requires access to an API such as **OpenAI** or **Semantic Scholar**.

1. Obtain your API key from the chosen service.  
2. Add it as an environment variable in your system:

**Linux / macOS:**
```bash
export API_KEY="your_api_key_here"
```

In your script:
```python
api_key = os.getenv("API_KEY")
```

This allows the script to access your key securely.

---

## 🧩 Defining Keywords

Edit the following lists at the top of **`paper_citation_retrieval.py`**:

```python
COMPULSORY_KEYWORDS = ["LLM", "AI", "pedagogy", "education"]
OPTIONAL_KEYWORDS = ["knowledge graph", "fine tuning", "benchmarks", "evaluate"]
```

- **COMPULSORY_KEYWORDS** – must appear in every paper retrieved.  
- **OPTIONAL_KEYWORDS** – add contextual variety to the search and ranking process.

You can modify these lists anytime to analyze different topics.

---

## 🚀 Running the Pipeline

Once your API key and keywords are set, run the complete workflow with:

```bash
python run_pipeline.py
```

The script will automatically execute the following steps in order:
1. Retrieve papers  
2. Apply TF-IDF scoring  
3. Combine and rank results  
4. Generate visual and statistical outputs  

---

## 📊 Output Files

| Output File | Description |
|:-----------------------------|:---------------------------------------------|
| `all_ranked_combined.xlsx` | Final merged Excel file containing ranked papers and extracted keywords. |
| `analysis_outputs/` | Folder containing generated plots, charts, and summaries. |
| `data_representation_output.ipynb` | Executed version of the visualization notebook. |
| `pipeline_log.txt` *(optional)* | Can be added to track pipeline progress and errors. |

---

## 📁 Folder Structure

```
project_root/
│
├── paper_citation_retrieval.py
├── tf-idf_scoring_multi-level.py
├── combine_multi-level.py
├── data_representation_citaton.ipynb
├── run_pipeline.py
└── README.md
```

---

## 🧩 Example Modification

If you want to analyze **“AI in healthcare education”**, edit:

```python
COMPULSORY_KEYWORDS = ["AI", "education", "healthcare"]
OPTIONAL_KEYWORDS = ["deep learning", "knowledge graph", "LLM"]
```

Then simply run:
```bash
python run_pipeline.py
```

---

## 🧠 Troubleshooting

- **Missing API Key →** Ensure `API_KEY` is set as an environment variable.  
- **Missing Notebook →** Install Jupyter via `pip install notebook`.  
- **File Not Found →** Ensure all scripts are in the same project folder.  
- **Permission Errors (macOS/Linux) →** Run `chmod +x run_pipeline.py` once.  

---

## 🧾 Summary

This pipeline is designed to simplify literature exploration for research.  
By adjusting a few keywords, you can:

- Fetch relevant academic papers  
- Rank and analyze them  
- Visualize keyword trends  

—all in one command.
"""

path = "/mnt/data/Research_Paper_Retrieval_and_Analysis_README.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

path
