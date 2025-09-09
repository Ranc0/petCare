import re
import json
from typing import Dict, List, Tuple
from rapidfuzz import process, fuzz
import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the full path to symptoms.json in that same folder
SYMPTOMS_PATH = os.path.join(BASE_DIR, "symptoms.json")

with open(SYMPTOMS_PATH, "r") as f:
    ONTOLOGY = json.load(f)

SYNONYM_INDEX = ONTOLOGY["synonym_index"]
DISEASE_MAP = ONTOLOGY["diseases"]
DISEASE_INFO = ONTOLOGY["disease_info"]

SVM_MODEL_PATH = os.path.join(BASE_DIR, "dog_disease_svm_model.pkl")
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, "disease_label_encoder.pkl")

SVM_MODEL = joblib.load(SVM_MODEL_PATH)
LABEL_ENCODER = joblib.load(LABEL_ENCODER_PATH)

# ---------- Config ----------
# ---------- Config (keep your own) ----------
NEGATION_CUES = {"no", "not", "never", "without", "hasnt", "hasn't", "doesnt", "doesn't",
                 "didnt", "didn't", "stopped", "free of"}
UNCERTAINTY_CUES = {"maybe", "might", "seems", "seem", "looks like", "i think", "possible"}
WINDOW_TOKENS = 4
PUNCT_REGEX = re.compile(r"[^\w\s]+", re.UNICODE)
MAX_NGRAM = 5

# Fuzzy thresholds by phrase length (token count)
THRESH_LEN = {
    1: 90,   # stricter for unigrams (avoid false positives)
    2: 88,
    3: 86,
    4: 85,
    5: 84
}

# ---------- Helpers ----------
def normalize_text(text: str) -> str:
    t = text.lower()
    t = t.replace("’", "'").replace("‘", "'").replace("`", "'")
    t = re.sub(r"\s+", " ", t)
    t = PUNCT_REGEX.sub(" ", t)
    return t.strip()

def build_vocab(syn_index: Dict[str, List[str]]):
    """
    Returns:
      norm2canon: normalized phrase -> canonical key
      buckets: {length_in_tokens: [normalized phrases]}
    """
    split_pattern = re.compile(r'[;,]|\band\b|\bor\b', flags=re.IGNORECASE)
    norm2canon = {}
    for canonical, variants in syn_index.items():
        all_forms = set([canonical] + variants)
        for phrase in all_forms:
                norm = normalize_text(phrase) 
                if not norm:
                    continue
                # keep first seen canonical for a norm (stable)
                norm2canon.setdefault(norm, canonical)

    buckets = {}
    for norm_phrase in norm2canon.keys():
        L = len(norm_phrase.split())
        buckets.setdefault(L, []).append(norm_phrase)
    return norm2canon, buckets

def sliding_windows(tokens: List[str], max_n: int):
    for n in range(1, max_n + 1):  # NOTE: short to long works better once we have exact pass
        for i in range(0, len(tokens) - n + 1):
            yield i, tokens[i:i+n]

def window_has_cue_tokens(tokens: List[str], start_idx: int, end_idx_excl: int, cues: set, radius: int) -> bool:
    lo = max(0, start_idx - radius)
    hi = min(len(tokens), end_idx_excl + radius)
    window_text = " ".join(tokens[lo:hi])
    return any(cue in window_text for cue in cues)

# ---------- Core ----------
def extract_symptom_binary(text: str, syn_index: Dict[str, List[str]]) -> Dict[str, int]:
    norm_text = normalize_text(text)
    tokens = norm_text.split()

    norm2canon, buckets = build_vocab(syn_index)

    # Initialize result map
    binary_map = {symptom: 0 for symptom in sorted(syn_index.keys())}
    used_token_indices = set()

    # 1) Exact matches first, longer phrases first (claim whole multi-word symptoms)
    max_len = min(MAX_NGRAM, max(buckets.keys()) if buckets else 1)
    for n in range(max_len, 0, -1):
        for start_idx in range(0, len(tokens) - n + 1):
            # skip tokens already claimed
            span_idx = set(range(start_idx, start_idx + n))
            if span_idx & used_token_indices:
                continue

            surface = " ".join(tokens[start_idx:start_idx + n])
            if surface in norm2canon:
                canonical = norm2canon[surface]

                # scope checks
                neg = window_has_cue_tokens(tokens, start_idx, start_idx + n, NEGATION_CUES, WINDOW_TOKENS)
                unc = window_has_cue_tokens(tokens, start_idx, start_idx + n, UNCERTAINTY_CUES, WINDOW_TOKENS)
                if neg or unc:
                    continue

                binary_map[canonical] = 1
                used_token_indices |= span_idx

    # 2) Fuzzy matches for remaining spans, length-aware to prevent long windows swallowing neighbors
    for n in range(1, max_len + 1):
        candidates = buckets.get(n, [])
        if not candidates:
            continue
        thresh = THRESH_LEN.get(n, 85)

        for start_idx in range(0, len(tokens) - n + 1):
            span_idx = set(range(start_idx, start_idx + n))
            if span_idx & used_token_indices:
                continue

            surface = " ".join(tokens[start_idx:start_idx + n])
            # If we already have an exact norm, we handled it above; here only fuzzy
            if surface in norm2canon:
                continue

            match = process.extractOne(surface, candidates, scorer=fuzz.partial_ratio)
            if not match or match[1] < thresh:
                # try a secondary scorer for edge cases
                match = process.extractOne(surface, candidates, scorer=fuzz.WRatio)
                if not match or match[1] < thresh:
                    continue

            best_norm, score, _ = match
            canonical = norm2canon[best_norm]

            neg = window_has_cue_tokens(tokens, start_idx, start_idx + n, NEGATION_CUES, WINDOW_TOKENS)
            unc = window_has_cue_tokens(tokens, start_idx, start_idx + n, UNCERTAINTY_CUES, WINDOW_TOKENS)
            if neg or unc:
                continue

            binary_map[canonical] = 1
            used_token_indices |= span_idx

    return binary_map





def match_diseases(symptom_binary: Dict[str, int], disease_map: Dict[str, List[str]]) -> Dict[str, int]:
    return {
        disease: int(any(symptom_binary[sym] for sym in symptoms))
        for disease, symptoms in disease_map.items()
    }

# ---------- Main callable ----------
def doTheJob(sample: str) -> Dict:
    symptom_result = extract_symptom_binary(sample, SYNONYM_INDEX)
    # disease_result = match_diseases(symptom_result, DISEASE_MAP)
    for symptom, present in symptom_result.items():
        if present == 1:  # use equality, not identity
            print(symptom)
    # expected = list(SVM_MODEL.feature_names_in_)  # if trained from pandas DataFrame
    # current = list(symptom_result.keys())

    # print("Expected feature count:", len(expected))
    # print("Current  feature count:", len(current))

    # missing = set(expected) - set(current)
    # extra   = set(current)  - set(expected)

    # print("Missing keys:", missing)
    # print("Extra keys:  ", extra)

    vec = np.array([symptom_result[x] for x in symptom_result]).reshape(1, -1)
   

    probs = SVM_MODEL.predict_proba(vec)[0]
    predicted_label = SVM_MODEL.predict(vec)[0]
    confidence = max(probs) * 100
    disease_name = predicted_label

    class_labels = LABEL_ENCODER.classes_
    label_probs  = list(zip(class_labels, probs))
    top_preds    = sorted(label_probs, key=lambda x: x[1], reverse=True)[:3]

    top_pred_text = "Top 3 Model Predictions:\n" + "\n".join(
        f"  - {label}: {prob * 100:.2f}%" for label, prob in top_preds
    )

    return {
        "diagnosis": disease_name,
        "confidence": f"{confidence:.2f}%",
        "tips": DISEASE_INFO[disease_name]["care_tips"],
        "common_symptoms":DISEASE_INFO[disease_name]["symptoms"],
        "possible_causes": DISEASE_INFO[disease_name]["causes"],
        "top_3_predictions": top_pred_text
    }
