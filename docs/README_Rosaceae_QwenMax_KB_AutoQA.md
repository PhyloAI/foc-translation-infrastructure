# Rosaceae Qwen-max + KB AutoQA (no reference Chinese)

**Scope:** Evaluate only Qwen translations (`*_qw`) for FoC Rosaceae **without using** any other Chinese columns.

## Inputs
- `foc_key_qwkc.xlsx`: key table; uses `Description` (EN) and `Description_qw` (ZH)
- `蔷薇科描述翻译.xlsx`: descriptions; uses `Content` (EN), `Content_qw` (ZH), grouped by `CategoryValue`
- `植物形态术语中英名词解释.txt`: morphology term KB (TSV)
- `植物分类命名人数据.xlsx`: nomenclatural author/person KB (XLSX)

## Output
- `Rosaceae_QwenMax_KB_AutoQA_v1.3.xlsx` (recommended)

### Key sheets in the report
- **KPI_Summary**: overall KPIs for Key and Description (in-scope)
- **KPI_by_Category**: KPIs per `CategoryValue` (Description only)
- **Key_Rowwise / Desc_Rowwise**: row-level metrics and flags
- **Top_Issues_Key / Top_Issues_Desc**: rows failing *core* checks
- **Name_Issues**: rows where the person KB provides Chinese name(s) and translation failed
- **Term_Drift**: EN terms mapped to ≥2 CN variants observed in Qwen output (consistency drift)

### KPI definitions (minimal sufficient)
- **Translated_rate**: non-empty translation proportion
- **Mean_TermRecall_when_hit**: among rows where EN hits ≥1 term from the morphology KB, fraction whose expected CN term(s) appear in ZH
- **CriticalPass_rate**: rows passing core fidelity checks (NUM/RANGE/UNIT/NEGATION_CUE/SYMBOL) plus BINOMIAL (only when names are italic-marked)
- **EntityPass_rate**: preservation of italic-marked Latin binomials + `±`/`×` when present
- **Name_accuracy_on_verifiable_rows**: accuracy on rows where the person KB provides Chinese name(s) (verifiable subset)

## Re-run
```bash
python run_qwen_kb_qa.py \
  --key_xlsx foc_key_qwkc.xlsx \
  --desc_xlsx 蔷薇科描述翻译.xlsx \
  --term_tsv 植物形态术语中英名词解释.txt \
  --names_xlsx 植物分类命名人数据.xlsx \
  --out_xlsx Rosaceae_QwenMax_KB_AutoQA_v1.3.xlsx
```
