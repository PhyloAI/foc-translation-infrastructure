# FoC-LLM: LLM-assisted Chinese translation of *Flora of China* with auditable QA

This repository provides **open, reusable building blocks** for treating floras/monographs as **computable, auditable, versioned taxonomic knowledge infrastructure**, together with an example Rosaceae slice translated with **Qwen3-Max** using **domain knowledge bases**.

**Public portal for the full translated FoC corpus:** https://www.iplant.cn/foc

## What is included here
1. **Open knowledge bases**
   - **Morphology glossary (ZH–EN)**: `knowledge_bases/plant_morphology_glossary_zh_en_v1.*`
   - **Author/person-name authority file**: `knowledge_bases/author_name_authority_file_v1.*`

2. **Open Rosaceae slice (FoC) translated with Qwen3-Max (+ knowledge bases)**
   - **Keys**: `data/raw/rosaceae_keys_qwen3max_kb.xlsx`
   - **Descriptions**: `data/raw/rosaceae_descriptions_qwen3max_kb.xlsx`

3. **Automated QA outputs and scripts**
   - QA workbook: `data/qa_outputs/rosaceae_autoqa_summary_v1.3.xlsx`
   - Reproducible script entry point: `code/run_qwen_kb_qa.py`
   - Metric definitions: `docs/README_Rosaceae_QwenMax_KB_AutoQA.md`

4. **Manuscript draft (for reference)**
   - `manuscript/FOC-LLM_correspondence_draft.docx`

## Quick start (reproduce the QA checks)
> This reproduces the *reported* automated checks on the Rosaceae slice. It does **not** require model access.

1. Create a fresh Python environment (3.10+ recommended).
2. Install dependencies:
   ```bash
   pip install pandas openpyxl numpy regex
   ```
3. Run:
   ```bash
   python code/run_qwen_kb_qa.py \
     --keys data/raw/rosaceae_keys_qwen3max_kb.xlsx \
     --descriptions data/raw/rosaceae_descriptions_qwen3max_kb.xlsx \
     --glossary knowledge_bases/plant_morphology_glossary_zh_en_v1.tsv \
     --name_lib knowledge_bases/author_name_authority_file_v1.xlsx \
     --out data/qa_outputs/reproduced_autoqa.xlsx
   ```

## How to cite
- Please cite the associated Plant Diversity Correspondence (in preparation) and the iPlant FoC portal (https://www.iplant.cn/foc).
- See `CITATION.cff` for a citation stub.

## Licenses
- **Code**: MIT (see `LICENSE_CODE_MIT.txt`)
- **Data/knowledge bases**: recommended CC BY 4.0 (see `LICENSE_DATA_CC-BY-4.0_SUGGESTED.txt`)
- **FoC text**: the complete translated corpus is served via the iPlant portal; redistribution should follow applicable licensing constraints of the source work and platform.

## Repository layout
See `docs/DATA_DICTIONARY.md` for column definitions and file-level descriptions.

