# Data dictionary

This repository bundles the minimal open components used in our automated QA workflow for the LLM-assisted Chinese translation of *Flora of China* (FoC), plus a fully open Rosaceae slice (keys + descriptions) translated with **Qwen3-Max** under knowledge-base constraints.

## 1) Morphology glossary (ZH–EN)
**File(s)**: `knowledge_bases/plant_morphology_glossary_zh_en_v1.{txt,tsv,csv}`

**Columns**
- `名词(中文)`: Chinese preferred term
- `名词(英文)`: English term
- `解释(中文)`: Chinese definition/explanation
- `解释(英文)`: English definition/explanation

## 2) Person / author name authority file
**File(s)**: `knowledge_bases/author_name_authority_file_v1.{xlsx,csv}`

**Typical columns** (as present in the provided spreadsheet)
- `中文名`: Chinese name (may be blank)
- `标准缩写`: standard author abbreviation
- `去掉空格的缩写`: abbreviation with spaces removed
- `全名`: full name (e.g., “Wang, Bin”)
- `全名，把逗号换成了空格`: full name with comma replaced by space
- `专长类群`: taxonomic group code (if provided)
- `工作单位`: affiliation (if provided)
- `姓`: family name
- `名`: given name(s)

## 3) Rosaceae keys translation (FoC)
**File**: `data/raw/rosaceae_keys_qwen3max_kb.xlsx`

Key fields include:
- `Description`: source English key line/couplet text
- `Description_qw`: Qwen3-Max (+ knowledge bases) Chinese translation
- Couplet structure fields such as `KeyNo`, `ItemNo`, `Branch`, `CoupletLink`, etc.

## 4) Rosaceae descriptions translation (FoC)
**File**: `data/raw/rosaceae_descriptions_qwen3max_kb.xlsx`

Key fields include:
- `CategoryValue`: record category (e.g., Synonym, Description, etc.)
- `Content`: source English text (may include HTML tags)
- `Content_qw`: Qwen3-Max (+ knowledge bases) Chinese translation

## 5) Automated QA outputs
**File**: `data/qa_outputs/rosaceae_autoqa_summary_v1.3.xlsx`

Contains per-unit QA flags and summary tables (see `docs/README_Rosaceae_QwenMax_KB_AutoQA.md` for the metric definitions and how to reproduce).

