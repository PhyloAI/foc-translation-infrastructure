# Rosaceae Step-by-Step Guide: Reproducing the QA Workflow

## 1. What this guide is for

This guide provides a practical, beginner-friendly walkthrough for reproducing the automated QA workflow reported in our Correspondence on LLM-assisted flora translation. It uses the Rosaceae dataset from *Flora of China* as a worked example.

The aim is not to teach every possible implementation detail of LLM-assisted translation. Instead, this guide shows how the released Rosaceae files, open knowledge bases, and QA scripts fit together in a reproducible workflow, and how the resulting outputs relate to the integrity metrics reported in the paper.

## 2. What you will reproduce

Using the public Rosaceae example, you will be able to:

- identify the main input files used in the workflow
- run the automated QA script locally
- inspect the output workbook and summary sheets
- understand how the reported QA metrics are generated
- see what kinds of errors are detected automatically
- understand the current scope and limits of the automated QA layer

This worked example focuses on the automated QA step. It does **not** reproduce the full translation-generation process from scratch, and it does **not** replace expert review.

## 3. Files used in the Rosaceae example

The Rosaceae example uses four main file types.

### 3.1 Input data

These are the Rosaceae source/translation units used for the QA workflow.

- **Keys file**: Rosaceae key units
- **Descriptions file**: Rosaceae description units

These files contain stable unit-level records used for line-by-line or segment-level checking.

### 3.2 Knowledge bases

These files support terminology and entity control.

- **Morphology glossary**: bilingual terminology resource for botanical description terms
- **Author/person-name resource**: curated name authority file used to stabilize personal and author-name strings

### 3.3 QA script

This is the script that runs the automated checks.

- `code/run_qwen_kb_qa.py`

### 3.4 Output example

This is the released QA workbook showing the expected output structure.

- Rosaceae QA workbook
- summary sheets
- row-level pass/fail flags
- error-category sheets or columns, if present

See `DATA_DICTIONARY.md` for file definitions and field descriptions.

## 4. Environment setup

### Step 1. Clone the repository

```bash
git clone https://github.com/PhyloAI/foc-translation-infrastructure.git
cd foc-translation-infrastructure
```

### Step 2. Create a Python environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, use:

```bash
.venv\Scripts\activate
```

### Step 3. Install dependencies

If a requirements file is provided:

```bash
pip install -r requirements.txt
```

If dependencies are documented elsewhere, follow the repository instructions.

## 5. Run the QA workflow

Run the Rosaceae QA script using the released example files.

A typical command is:

```bash
python code/run_qwen_kb_qa.py \
  --input_keys data/rosaceae_keys_example.xlsx \
  --input_descriptions data/rosaceae_descriptions_example.xlsx \
  --glossary knowledge_bases/morphology_glossary.xlsx \
  --author_kb knowledge_bases/author_person_kb.xlsx \
  --output outputs/rosaceae_qwen_kb_qa.xlsx
```

Please adjust file paths if the repository structure changes.

This command performs automated checks on the Rosaceae example using the released knowledge-base resources and writes the results to an output workbook.

## 6. Understand the outputs

The output workbook is the main result of the workflow. It typically contains the following layers.

### 6.1 Summary-level outputs

These sheets report aggregate counts or percentages, such as:

- number of units checked
- number or proportion of units passing selected checks
- key-level versus description-level results

These are the sheets most directly related to the summary metrics reported in the paper.

### 6.2 Row-level outputs

These sheets record pass/fail flags for individual units.

Typical row-level fields include:

- stable unit ID
- source text
- translated text
- check-specific flags
- optional notes or issue categories

These row-level outputs are useful for locating failures and understanding why a unit did not pass.

### 6.3 Error-type outputs

Depending on the release version, the workbook may include explicit columns or sheets for different issue types, such as:

- numbers and ranges
- units
- negation cues
- special symbols
- formatting constraints
- glossary-term presence
- entity/name integrity

## 7. How the outputs map to the paper

The Correspondence reports aggregate QA metrics for Rosaceae keys and descriptions. These should be interpreted as **integrity indicators for selected reuse-critical, machine-detectable elements**, not as full semantic equivalence scores.

In particular:

- **Key-level checks** focus on structure-sensitive elements such as numbering, pairing logic, formatting, and selected integrity-critical markers.
- **Description-level checks** focus on selected reuse-critical features such as numeric ranges, units, negation cues, special symbols, and selected entity strings.

The reported percentages in the paper are derived from the released summary outputs generated by this workflow.

## 8. What this workflow checks—and what it does not

This automated QA workflow is designed to detect a limited but high-impact set of machine-checkable failures.

It is well suited to checking:

- numeric range integrity
- units
- negation cues
- special symbols
- selected formatting constraints
- selected terminology presence
- scientific-name and author/person-name integrity

However, it does **not** fully evaluate all meaning-bearing constructions in floristic text.

In particular, the current automated QA layer does **not** systematically capture:

- comparative expressions
- vague locative expressions
- relative or experiential wording
- deeper semantic paraphrases
- subtle semantic hallucinations that preserve surface structure

For this reason, the workflow should be understood as a first-pass integrity filter for reuse-critical failures, not as a substitute for expert audit.

## 9. How to adapt this workflow to another family

To reuse this workflow for another family, the core logic remains the same. In most cases, you would replace:

- the keys input file
- the descriptions input file
- any family-specific terminology resources, if needed

The general steps are:

1. segment source and translated text into stable units
2. assign persistent IDs
3. prepare or reuse the glossary and authority resources
4. run the QA script
5. inspect the summary and row-level outputs
6. review flagged units
7. document the release version and known limitations

For new families, it is especially important to check whether the existing glossary and name resources are adequate for the target material.

## 10. Key take-home points

- This workflow is intended to make flora translation more auditable, inspectable, and reusable.
- The Rosaceae example demonstrates how automated QA can be run reproducibly on released data.
- The reported metrics are not claims of full semantic identity.
- Automated QA is most useful when paired with expert review and explicit versioning.
- The workflow is designed to support release-oriented, versioned improvement rather than one-off translation output.
