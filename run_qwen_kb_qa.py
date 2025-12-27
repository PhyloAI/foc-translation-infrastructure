#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQA for FoC EN→ZH translations (Qwen-max + KB), no reference Chinese required.

Core idea:
- Use *English source* as the reference.
- Use term KB (morphology glossary) + person/author KB to check specific, verifiable aspects.
- Treat other aspects as heuristic flags, not gold-standard “accuracy”.

Inputs:
  --key_xlsx     foc_key_qwkc.xlsx (expects columns: Description, Description_qw)
  --desc_xlsx    蔷薇科描述翻译.xlsx (expects columns: Content, Content_qw, CategoryValue)
  --term_tsv     植物形态术语中英名词解释.txt (TSV header includes 名词(中文), 名词(英文))
  --names_xlsx   植物分类命名人数据.xlsx (Sheet1 with 标准缩写/去掉空格的缩写/全名/中文名)

Output:
  --out_xlsx     QA report workbook

Implements (minimal sufficient quantification):
  (1) Coverage
  (2) Terminology adherence (term recall) against morphology term KB
  (3) Critical fact fidelity flags (NUM/RANGE/UNIT/NEGATION_CUE/SYMBOL)
  (4) Entity preservation: Latin binomials **only when explicitly marked in source via <i> tags**
  (5) Person-name fidelity on a *verifiable subset* where the KB provides Chinese name(s)

Notes:
- BINOMIAL check is restricted to italic-marked names to avoid false positives (e.g., “Fruit a …”).
- NUM uses multiset comparison to tolerate re-ordering of phrases.
"""

import argparse, re
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

def norm_ws(s):
    return re.sub(r'\s+', ' ', str(s or '')).strip()

def strip_html(s):
    return re.sub(r'<[^>]+>', '', str(s or ''))

# --- month normalization (to tolerate May–Jun -> 5–6月 conversions) ---
month_map = {
    "jan": "1", "january":"1",
    "feb":"2","february":"2",
    "mar":"3","march":"3",
    "apr":"4","april":"4",
    "may":"5",
    "jun":"6","june":"6",
    "jul":"7","july":"7",
    "aug":"8","august":"8",
    "sep":"9","sept":"9","september":"9",
    "oct":"10","october":"10",
    "nov":"11","november":"11",
    "dec":"12","december":"12",
}
month_re = re.compile(r'\b(' + "|".join(sorted(month_map.keys(), key=len, reverse=True)) + r')\.?\b', re.I)

def normalize_months(text):
    t = strip_html(text or "")
    def repl(m):
        return month_map[m.group(1).lower()]
    return month_re.sub(repl, t)


# regex
num_re = re.compile(r'(?<![A-Za-z])(\d+(?:\.\d+)?)')
range_re = re.compile(r'(\d+(?:\.\d+)?)\s*[–\-~－]\s*(\d+(?:\.\d+)?)')
unit_en_re = re.compile(r'\b(mm|cm|dm|m|km|µm|um)\b', re.IGNORECASE)
abbr_candidate_re = re.compile(r'\b(?:[A-Z]\.){1,4}(?:\s?[A-Za-z]{2,}\.)?\b')
surname_period_re = re.compile(r'\b[A-Z][A-Za-z\-]{2,}\.\b')
word_re = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*")
tag_re = re.compile(r'<\s*/?\s*([A-Za-z0-9]+)[^>]*>')

unit_map = {
    "mm": ["mm","毫米"],
    "cm": ["cm","厘米"],
    "dm": ["dm","分米"],
    "m":  ["m","米"],
    "km": ["km","千米"],
    "µm": ["µm","um","微米"],
    "um": ["µm","um","微米"],
}
neg_triggers = ["not","without","rarely","usually","often","sometimes","absent","lacking","except"]
zh_cues = ["不","无","未","非","缺","没有","罕","稀","很少","常","通常","一般","除外","而非","而不是"]

def extract_numbers(s): 
    return num_re.findall(s or "")

def has_range(s):
    return bool(range_re.search(s or ""))

def extract_units_en(s):
    return [u.lower() for u in unit_en_re.findall(s or "")]

def units_pass(en, zh):
    en_units = extract_units_en(en)
    if not en_units:
        return True
    z = str(zh or "")
    for u in en_units:
        candidates = unit_map.get(u, [u])
        if not any(c in z for c in candidates):
            return False
    return True

def negation_pass(en, zh):
    en_l = (en or "").lower()
    triggers = [t for t in neg_triggers if t in en_l]
    if not triggers:
        return True
    z = str(zh or "")
    return any(c in z for c in zh_cues)

def italic_binomials(text):
    s = str(text or "")
    ital = re.findall(r'<i>\s*([^<]+?)\s*</i>', s, flags=re.I)
    bins=[]
    for it in ital:
        it = strip_html(it)
        bins += re.findall(r'\b([A-Z][a-z-]+)\s+([a-z-]{2,})\b', it)
    return bins

def binomial_pass(en, zh):
    # enforce only when source explicitly marks taxa with <i> tags
    bins = italic_binomials(en)
    if not bins:
        return True
    z = strip_html(zh).lower()
    for g,s in bins:
        if f"{g} {s}".lower() not in z:
            return False
    return True

def symbols_pass(en, zh):
    for sym in ["±","×"]:
        if sym in (en or "") and sym not in (zh or ""):
            return False
    return True

def tag_mismatch(en, zh):
    return bool(tag_re.findall(en or "")) and (Counter([t.lower() for t in tag_re.findall(en or "")]) != Counter([t.lower() for t in tag_re.findall(zh or "")]))

# --- term KB ---
def normalize_en_term(en):
    en = norm_ws(en).lower()
    en = re.sub(r'\s*\(.*?\)\s*', ' ', en)
    en = re.sub(r'\s+',' ', en).strip()
    return en

def singularize_token(tok):
    if tok.endswith("ies") and len(tok) > 4:
        return tok[:-3] + "y"
    if tok.endswith("es") and len(tok) > 4:
        return tok[:-2]
    if tok.endswith("s") and len(tok) > 3 and not tok.endswith("ss"):
        return tok[:-1]
    return tok

def make_en_variants(en_term):
    base = normalize_en_term(en_term)
    if not base:
        return []
    variants=set()
    variants.add(base)
    variants.add(base.replace("-", " "))
    variants.add(base.replace(" ", "-"))
    toks = base.split()
    if toks:
        variants.add(" ".join(toks[:-1] + [singularize_token(toks[-1])]))
    return [v for v in variants if v]

def build_term_kb(term_tsv):
    term_df = pd.read_csv(term_tsv, sep='\t').fillna("")
    term_df = term_df.rename(columns={"名词(中文)":"zh","名词(英文)":"en"})
    en2zh = defaultdict(set)
    for _,r in term_df.iterrows():
        zh = norm_ws(r.get("zh",""))
        en = norm_ws(r.get("en",""))
        if not zh or not en:
            continue
        for v in make_en_variants(en):
            en2zh[v].add(zh)
    max_words = min(max((len(k.split()) for k in en2zh.keys()), default=4), 6)
    return en2zh, max_words

def match_terms(en2zh, max_words, en_text):
    tokens = [t.lower() for t in word_re.findall(strip_html(en_text or ""))]
    hits=set()
    L=len(tokens)
    for n in range(1, max_words+1):
        for i in range(0, L-n+1):
            ng=" ".join(tokens[i:i+n])
            if ng in en2zh:
                hits.add(ng)
    return sorted(hits)

def term_metrics(en2zh, max_words, en_text, zh_text):
    hits = match_terms(en2zh, max_words, en_text)
    if not hits:
        return 0, 0, None, [], {}
    zh = str(zh_text or "")
    ok=0
    missing=[]
    found_map={}
    for en_term in hits:
        cands = en2zh[en_term]
        found=[z for z in cands if z and z in zh]
        if found:
            ok += 1
            found_map[en_term]=sorted(found)
        else:
            missing.append(en_term)
    recall = ok/len(hits) if hits else None
    return len(hits), ok, recall, missing[:20], found_map

# --- name KB (verifiable subset) ---
def build_name_kb(names_xlsx):
    df = pd.read_excel(names_xlsx, sheet_name="Sheet1").fillna("")
    abbr_map={}
    fullname_map={}
    cn_map={}
    for i,r in df.iterrows():
        cn_map[i]=norm_ws(r.get("中文名",""))
        for k in ["去掉空格的缩写","标准缩写"]:
            ab = re.sub(r'\s+','', str(r.get(k,""))).strip()
            if ab:
                abbr_map[ab]=i
        for k in ["全名，把逗号换成了空格","全名"]:
            fn = norm_ws(r.get(k,""))
            if fn:
                fn_norm = re.sub(r'[^a-z ]','', fn.lower())
                fn_norm = re.sub(r'\s+',' ', fn_norm).strip()
                if fn_norm:
                    fullname_map[fn_norm]=i
    return abbr_map, fullname_map, cn_map

def extract_person_abbr(en_text):
    en = en_text or ""
    cands=set()
    for m in abbr_candidate_re.findall(en):
        cands.add(re.sub(r'\s+','', m))
    for m in surname_period_re.findall(en):
        cands.add(re.sub(r'\s+','', m))
    return cands

def extract_fullname(en_text):
    en = en_text or ""
    en_no_par = re.sub(r'\([^)]*\)', ' ', en)
    parts = re.split(r'[;，,]| and ', en_no_par)
    cands=set()
    for p in parts:
        p = norm_ws(p)
        if not p:
            continue
        p2 = re.sub(r'[^A-Za-z.\- ]+', ' ', p)
        p2 = re.sub(r'\s+',' ', p2).strip()
        words=[w for w in p2.split() if re.search(r'[A-Za-z]', w)]
        if len(words) >= 2:
            cand_norm = re.sub(r'[^a-z ]','', " ".join(words).lower())
            cand_norm = re.sub(r'\s+',' ', cand_norm).strip()
            if cand_norm:
                cands.add(cand_norm)
    return cands

def person_eval(abbr_map, fullname_map, cn_map, en_text, zh_text):
    en = en_text or ""
    zh = str(zh_text or "")
    matched=set()
    expected=set()
    verifiable=0
    ok=True
    reasons=set()
    for ab in extract_person_abbr(en):
        if ab in abbr_map:
            idx=abbr_map[ab]
            matched.add(idx)
            cn=cn_map.get(idx,"")
            if cn and cn not in ["【空】","?","？"]:
                verifiable += 1
                if cn not in zh:
                    ok=False
                    expected.add(cn)
                    reasons.add("CN_MISSING")
    for fn in extract_fullname(en):
        if fn in fullname_map:
            idx=fullname_map[fn]
            matched.add(idx)
            cn=cn_map.get(idx,"")
            if cn and cn not in ["【空】","?","？"]:
                verifiable += 1
                if cn not in zh:
                    ok=False
                    expected.add(cn)
                    reasons.add("CN_MISSING")
    if not matched:
        return {"status":"NA","verifiable_n":0,"expected_cn":"","reason":"","matched_ids":""}
    return {
        "status":"OK" if ok else "FAIL",
        "verifiable_n":verifiable,
        "expected_cn":";".join(sorted(expected)),
        "reason":",".join(sorted(reasons)),
        "matched_ids":";".join(str(i) for i in sorted(matched))
    }

# --- core flags ---
def critical_flags(en, zh):
    flags=[]
    en_clean = strip_html(en or "")
    zh_clean = strip_html(zh or "")
    en_nums = extract_numbers(en_clean)
    zh_nums = extract_numbers(zh_clean)
    if en_nums and Counter(en_nums) != Counter(zh_nums):
        flags.append("NUM")
    if has_range(en_clean) and not has_range(zh_clean):
        flags.append("RANGE")
    if not units_pass(en_clean, zh_clean):
        flags.append("UNIT")
    if not negation_pass(en_clean, zh_clean):
        flags.append("NEGATION_CUE")
    if not binomial_pass(en, zh):
        flags.append("BINOMIAL")
    if not symbols_pass(en, zh):
        flags.append("SYMBOL")
    # soft indicator only
    if tag_mismatch(en or "", zh or ""):
        flags.append("TAG")
    return flags

def short(s, n=260):
    s = norm_ws(s)
    return s if len(s)<=n else s[:n]+"…"

def summarize_block(df):
    out = {}
    out["N_rows"] = len(df)
    out["Translated_rate"] = df["Translated"].mean() if len(df) else np.nan
    out["Term_hit_row_rate"] = (df["TermHits"]>0).mean() if len(df) else np.nan
    sub = df[(df["Translated"]==1) & (df["TermHits"]>0)]
    out["Mean_TermRecall_when_hit"] = sub["TermRecall"].mean() if len(sub) else np.nan
    out["CriticalPass_rate"] = df["CriticalPass"].mean() if len(df) else np.nan
    out["EntityPass_rate"] = df["EntityPass"].mean() if len(df) else np.nan
    ver = df[df.get("PersonVerifiableN",0)>0] if "PersonVerifiableN" in df.columns else df.iloc[0:0]
    out["Name_verifiable_rows"] = len(ver)
    out["Name_accuracy_on_verifiable_rows"] = (ver["PersonStatus"]=="OK").mean() if len(ver) else np.nan
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key_xlsx", required=True)
    ap.add_argument("--desc_xlsx", required=True)
    ap.add_argument("--term_tsv", required=True)
    ap.add_argument("--names_xlsx", required=True)
    ap.add_argument("--out_xlsx", required=True)
    args = ap.parse_args()

    en2zh, max_words = build_term_kb(args.term_tsv)
    abbr_map, fullname_map, cn_map = build_name_kb(args.names_xlsx)

    df_key = pd.read_excel(args.key_xlsx).fillna("")
    df_desc = pd.read_excel(args.desc_xlsx).fillna("")

    term_variant_found = defaultdict(set)

    # key
    key_rows=[]
    for _,r in df_key.iterrows():
        en = r.get("Description","")
        zh = r.get("Description_qw","")
        translated = bool(norm_ws(zh))
        th, tok, trec, tmiss, found_map = term_metrics(en2zh, max_words, en, zh) if translated else (0,0,None,[],{})
        for en_term, zhs in found_map.items():
            for z in zhs:
                term_variant_found[en_term].add(z)
        flags = critical_flags(en, zh) if translated else ["UNTRANSLATED"]
        core=[f for f in flags if f not in ["TAG"]]
        crit_pass = int(translated and len(core)==0)
        entity_pass = int(translated and symbols_pass(en, zh))
        key_rows.append({
            "ID": r.get("ID",""),
            "KeyNo": r.get("KeyNo",""),
            "ItemNo": r.get("ItemNo",""),
            "Branch": r.get("Branch",""),
            "EN": en,
            "ZH_qw": zh,
            "Translated": int(translated),
            "TermHits": th,
            "TermOK": tok,
            "TermRecall": trec,
            "TermMissing(<=20)": ";".join(tmiss),
            "CriticalFlags": ",".join(flags),
            "CriticalPass": crit_pass,
            "EntityPass": entity_pass,
        })
    df_key_q = pd.DataFrame(key_rows)

    # desc
    desc_rows=[]
    for _,r in df_desc.iterrows():
        cat = r.get("CategoryValue","")
        en = r.get("Content","")
        zh = r.get("Content_qw","")
        translated = bool(norm_ws(zh))
        scope = 0 if str(cat).strip().lower()=="synonym" else 1
        th, tok, trec, tmiss, found_map = term_metrics(en2zh, max_words, en, zh) if (translated and scope) else (0,0,None,[],{})
        for en_term, zhs in found_map.items():
            for z in zhs:
                term_variant_found[en_term].add(z)
        flags = critical_flags(en, zh) if (translated and scope) else (["UNTRANSLATED"] if (scope and not translated) else ["OUT_OF_SCOPE"])
        core=[f for f in flags if f not in ["TAG"]]
        crit_pass = int(scope and translated and len(core)==0)
        entity_pass = int(scope and translated and binomial_pass(en, zh) and symbols_pass(en, zh))
        pe = person_eval(abbr_map, fullname_map, cn_map, en, zh) if (scope and translated) else {"status":"NA","verifiable_n":0,"expected_cn":"","reason":"","matched_ids":""}
        desc_rows.append({
            "id": r.get("id",""),
            "TaxonId": r.get("TaxonId",""),
            "CategoryValue": cat,
            "EN": en,
            "ZH_qw": zh,
            "InScope": scope,
            "Translated": int(translated),
            "TermHits": th,
            "TermOK": tok,
            "TermRecall": trec,
            "TermMissing(<=20)": ";".join(tmiss),
            "CriticalFlags": ",".join(flags),
            "CriticalPass": crit_pass,
            "EntityPass": entity_pass,
            "PersonStatus": pe["status"],
            "PersonVerifiableN": pe["verifiable_n"],
            "PersonExpectedCN": pe["expected_cn"],
            "PersonReason": pe["reason"],
            "PersonMatchedIDs": pe["matched_ids"],
        })
    df_desc_q = pd.DataFrame(desc_rows)
    d_inscope = df_desc_q[df_desc_q["InScope"]==1]

    # summary tables
    df_kpi = pd.DataFrame([
        {"Block":"Key (foc_key_qwkc)", **summarize_block(df_key_q)},
        {"Block":"Description (in-scope)", **summarize_block(d_inscope)},
    ])

    cat_summ=[]
    for cat, sub in d_inscope.groupby("CategoryValue"):
        s = summarize_block(sub)
        s["CategoryValue"]=cat
        cat_summ.append(s)
    df_cat_summary = pd.DataFrame(cat_summ).sort_values("N_rows", ascending=False)

    term_drift=[]
    for en_term, zhset in term_variant_found.items():
        if len(zhset) >= 2:
            term_drift.append({"en_term": en_term, "n_cn_variants": len(zhset), "cn_variants": " | ".join(sorted(zhset))})
    df_term_drift = pd.DataFrame(term_drift).sort_values(["n_cn_variants","en_term"], ascending=[False, True])

    top_key_issues = df_key_q[(df_key_q["Translated"]==1) & (df_key_q["CriticalPass"]==0)].copy()
    top_key_issues["EN"]=top_key_issues["EN"].map(short)
    top_key_issues["ZH_qw"]=top_key_issues["ZH_qw"].map(short)

    top_desc_issues = d_inscope[(d_inscope["Translated"]==1) & (d_inscope["CriticalPass"]==0)].copy()
    top_desc_issues["EN"]=top_desc_issues["EN"].map(short)
    top_desc_issues["ZH_qw"]=top_desc_issues["ZH_qw"].map(short)

    name_issues = d_inscope[(d_inscope["PersonVerifiableN"]>0) & (d_inscope["PersonStatus"]=="FAIL")].copy()
    if len(name_issues):
        name_issues["EN"]=name_issues["EN"].map(short)
        name_issues["ZH_qw"]=name_issues["ZH_qw"].map(short)

    with pd.ExcelWriter(args.out_xlsx, engine="xlsxwriter") as w:
        df_kpi.to_excel(w, sheet_name="KPI_Summary", index=False)
        df_cat_summary.to_excel(w, sheet_name="KPI_by_Category", index=False)
        df_key_q.to_excel(w, sheet_name="Key_Rowwise", index=False)
        df_desc_q.to_excel(w, sheet_name="Desc_Rowwise", index=False)
        top_key_issues.to_excel(w, sheet_name="Top_Issues_Key", index=False)
        top_desc_issues.to_excel(w, sheet_name="Top_Issues_Desc", index=False)
        name_issues.to_excel(w, sheet_name="Name_Issues", index=False)
        df_term_drift.to_excel(w, sheet_name="Term_Drift", index=False)

if __name__ == "__main__":
    main()
