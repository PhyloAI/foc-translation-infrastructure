# FoC-LLM: LLM-assisted Chinese translation of *Flora of China* with auditable QA

This repository provides **open, reusable building blocks** for treating floras and monographs as **computable, auditable, and versioned taxonomic knowledge infrastructure**. It includes an example **Rosaceae slice** from *Flora of China* translated with **Qwen3-Max** under **domain knowledge-base constraints**, together with reproducible QA outputs and supporting documentation.

**Public portal for the translated *Flora of China* corpus:** `https://www.iplant.cn/foc`

## What is included here

### 1. Open knowledge bases
These resources are used to improve terminology consistency and entity control.

- **Morphology glossary (ZH–EN)**  
  `knowledge_bases/plant_morphology_glossary_zh_en_v1.*`

- **Author/person-name authority file**  
  `knowledge_bases/author_name_authority_file_v1.*`

### 2. Open Rosaceae example translated with Qwen3-Max (+ knowledge bases)
This worked example is the Rosaceae slice used in the Correspondence.

- **Keys**  
  `data/raw/rosaceae_keys_qwen3max_kb.xlsx`

- **Descriptions**  
  `data/raw/rosaceae_descriptions_qwen3max_kb.xlsx`

### 3. Automated QA outputs and scripts
These files reproduce the reported automated checks on the Rosaceae example.

- **QA workbook**  
  `data/qa_outputs/rosaceae_autoqa_summary_v1.3.xlsx`

- **Reproducible script entry point**  
  `code/run_qwen_kb_qa.py`

- **Metric definitions and QA notes**  
  `docs/README_Rosaceae_QwenMax_KB_AutoQA.md`

### 4. Practical guide and supporting documentation
These files are intended for readers who want a more intuitive walkthrough.

- **Beginner-friendly step-by-step guide**  
  `docs/STEP_BY_STEP_GUIDE_Rosaceae.md`

- **Data dictionary**  
  `docs/DATA_DICTIONARY.md`

- **Release notes**  
  `docs/RELEASE_NOTES_v1.0.0.md`

### 5. Manuscript draft (for reference)
- `manuscript/FOC-LLM_correspondence_draft.docx`

---

## Quick start: reproduce the Rosaceae QA checks

> This reproduces the **reported automated checks** on the Rosaceae slice.  
> It does **not** require model access.  
> It reproduces the **QA step**, not the full translation-generation process.

### Step 1. Create a fresh Python environment
Python 3.10+ is recommended.

### Step 2. Install dependencies

```bash
pip install pandas openpyxl numpy regex
```

### Step 3. Run the QA script

```bash
python code/run_qwen_kb_qa.py \
  --keys data/raw/rosaceae_keys_qwen3max_kb.xlsx \
  --descriptions data/raw/rosaceae_descriptions_qwen3max_kb.xlsx \
  --glossary knowledge_bases/plant_morphology_glossary_zh_en_v1.tsv \
  --name_lib knowledge_bases/author_name_authority_file_v1.xlsx \
  --out data/qa_outputs/reproduced_autoqa.xlsx
```

### Step 4. Inspect the output workbook
The output workbook contains:

- summary-level QA metrics
- row-level pass/fail flags
- check-specific outputs for selected integrity features

Compare the reproduced output with:

`data/qa_outputs/rosaceae_autoqa_summary_v1.3.xlsx`

For a worked example explaining how to interpret these outputs, see:

`docs/STEP_BY_STEP_GUIDE_Rosaceae.md`

---

## What this workflow checks

The current automated QA layer is designed to detect **selected reuse-critical, machine-checkable failures**, including:

- numbers and numeric ranges
- units
- negation cues
- special symbols
- selected formatting constraints
- glossary-term presence
- scientific-name and author/person-name integrity

These checks are intended as **release-level integrity diagnostics**, not as full semantic evaluation.

## What this workflow does not check

The current automated QA layer does **not** provide full semantic validation of floristic text.

In particular, it does **not** systematically capture:

- comparative expressions
- vague locative expressions
- relative or experiential wording
- deeper semantic paraphrases
- subtle semantic hallucinations that preserve surface structure

For this reason, the QA outputs should be interpreted as **diagnostic indicators for selected reuse-critical elements**, not as evidence of full semantic equivalence between source and translation.

---

## Practical reuse

Readers who want a more intuitive worked example should start with:

- `docs/STEP_BY_STEP_GUIDE_Rosaceae.md`

This guide explains:

- which files are used in the Rosaceae example
- how to run the QA workflow
- how to read the output workbook
- how the outputs relate to the metrics reported in the paper
- what the current QA layer can and cannot detect

---

## Repository layout

### Main directories

- `code/` — scripts for automated QA and related processing
- `data/` — Rosaceae example files and QA outputs
- `knowledge_bases/` — open terminology and entity-control resources
- `docs/` — practical guides, metric definitions, data dictionary, and release notes
- `manuscript/` — draft manuscript and related writing materials

For file-level descriptions and column definitions, see:

- `docs/DATA_DICTIONARY.md`

---

## How to cite

Please cite:

1. the associated *Plant Diversity* Correspondence, when available
2. the iPlant *Flora of China* portal: `https://www.iplant.cn/foc`
3. this repository release, where appropriate

See:

- `CITATION.cff`

---

## Licenses

- **Code**: MIT  
  `LICENSE_CODE_MIT.txt`

- **Data and knowledge bases**: recommended CC BY 4.0  
  `LICENSE_DATA_CC-BY-4.0_SUGGESTED.txt`

- **Complete translated *Flora of China* corpus**: served through the iPlant portal; redistribution should follow applicable licensing constraints of the source work and platform.

---

## Notes for readers

This repository is designed as a **worked example and infrastructure layer**, not as a claim of complete semantic translation validation. The Rosaceae example demonstrates how LLM-assisted flora translation can be released with **explicit QA, terminology control, entity normalization, and versioned documentation** so that future improvements can be made transparently and reproducibly.
