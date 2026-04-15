# Mini-Glossary for the FoC Translation Workflow

This short glossary explains a few key terms used in this repository and in the associated *Plant Diversity* Correspondence.

## Computable
In this project, **computable** does **not** mean that flora text has been fully formalized or exhaustively represented in machine logic.  
Instead, it means that translated units become more reusable under explicit constraints, so that they can support downstream tasks such as cross-lingual search, key-structure checking, trait-oriented extraction, and machine-assisted linkage to external biodiversity resources.

## LLM
**LLM** stands for **large language model**.  
Here, LLMs are used as translation engines under explicit constraints, rather than as free-form text generators without control.

## QA
**QA** stands for **quality assurance**.  
In this workflow, QA refers to automated checks designed to detect selected reuse-critical, machine-checkable failures, such as problems with numeric ranges, units, negation cues, special symbols, selected formatting constraints, and entity/name integrity.

## Terminology alignment
**Terminology alignment** means using a controlled glossary or terminology resource to reduce inconsistent translation of the same botanical concept across units, taxa, or runs.

## Entity normalization
**Entity normalization** means making important strings more stable and reusable across records.  
In this project, this mainly refers to scientific names and author/person-name strings, so that they can function more reliably as joinable data objects.

## Versioned release
A **versioned release** is a citable release of the corpus tied to a specific combination of model settings, knowledge-base resources, QA rules, and scope.  
If these components change, the release should also change in a traceable way.

## Reuse-critical elements
**Reuse-critical elements** are parts of floristic text whose corruption can break downstream use even if the sentence still looks fluent to a human reader.  
Examples include numeric ranges, units, negation cues, special symbols, stable numbering in keys, and normalized names.

## Minimum sufficient QA
**Minimum sufficient QA** refers to a deliberately limited QA strategy that targets high-impact, machine-detectable failures without claiming full semantic validation of translation quality.

## Human audit
**Human audit** refers to expert review of translated units, especially in cases where automated checks are insufficient, such as comparative expressions, vague locatives, relative wording, or deeper semantic hallucinations.

## Living, versioned flora
A **living, versioned flora** is not simply a webpage that changes over time.  
In this project, it means a provenance-rich, citable, and updateable release process in which changes are documented, QA is visible, and downstream users can trace what changed and why.
