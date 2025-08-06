import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .synonyms import *
from .symptoms import symptom_list
from .regexx import regex_detector
from .info import *

# 🔧 Load sentence embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 🧹 Preprocess
def preprocess(text):
    return re.sub(r"[^\w\s]", "", text.lower())

# 🔍 Semantic Matching
def embed_match(input_text, synonym_map, threshold=0.6):
    input_chunks = re.split(r"[,.;]|and|but|so", input_text.lower())
    matched = {}

    # print(f"\n Debugging phrase chunks:")
    for chunk in input_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        chunk_emb = model.encode([chunk])
        print(f" Chunk: '{chunk}'")

        for alias, canonical in synonym_map.items():
            alias_emb = model.encode([alias])
            sim = cosine_similarity(chunk_emb, alias_emb)[0][0]

            if sim >= threshold:
                print(f"   '{alias}' -> '{canonical}' — score: {sim:.3f}")
                matched[canonical] = max(matched.get(canonical, 0), sim)
            elif sim >= 0.5:
                print(f"   '{alias}' -> '{canonical}' — borderline: {sim:.3f}")

    return matched

# 🚦 Conflict Resolution
def resolve_conflicts(symptoms_with_scores):
    resolved = symptoms_with_scores.copy()
    conflict_pairs = [
        ("increasedthirst", "decreasedthirst"),
        ("increasedurination", "decreasedurination"),
        ("reducedappetite", "Hunger")
    ]
    for s1, s2 in conflict_pairs:
        if s1 in resolved and s2 in resolved:
            resolved.pop(s2 if resolved[s1] >= resolved[s2] else s1)
    return resolved

# ✅ Filter to Dataset Features
def filter_to_known_attributes(extracted_symptoms, known_attributes):
    return [symptom for symptom in extracted_symptoms if symptom in known_attributes]

# 🔬 Final Extractor
def extract_smart_symptoms(user_input):
    clean_text = preprocess(user_input)
    semantic_matches = embed_match(clean_text, synonym_map)
    regex_matches = regex_detector(clean_text)
    all_matches = {**semantic_matches, **regex_matches}
    resolved = resolve_conflicts(all_matches)
    return filter_to_known_attributes(resolved.keys(), symptom_list)


def doTheJob(user_input):
    import pandas as pd
    from django.conf import settings
    import joblib
    import os


    # 🔧 Load classifier and label encoder
    model_path = os.path.join(settings.BASE_DIR, 'base', 'ai_stuff', 'dog_disease_svm_model.pkl')
    encoder_path = os.path.join(settings.BASE_DIR, 'base', 'ai_stuff', 'disease_label_encoder.pkl')
    svm_model = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)

  

    # 🧠 Symptom Extraction (assumes function returns both names and match scores)
    matched_symptoms = extract_smart_symptoms(user_input)
    print("Matched symptoms:", matched_symptoms)

    if len(user_input.strip()) < 5 or len(matched_symptoms) == 0:
        print("I couldn't find enough information to make a reliable diagnosis. Please describe your dog's symptoms more clearly.")
    else:
        # 🧮 Build input vector
        symptom_vector = [1 if symptom in matched_symptoms else 0 for symptom in symptom_list]
        input_df = pd.DataFrame([symptom_vector], columns=symptom_list)

        # 🔬 Predict
        probs = svm_model.predict_proba(input_df)[0]
        confidence = max(probs) * 100
        predicted_label = svm_model.predict(input_df)[0]
        disease_name = predicted_label

        # 📊 Top 3 predicted diseases by probability
        class_labels = label_encoder.classes_
        label_probs = list(zip(class_labels, probs))
        top_preds = sorted(label_probs, key=lambda x: x[1], reverse=True)[:3]

        top_pred_text = "Top 3 Model Predictions:\n"
        for label, prob in top_preds:
            top_pred_text += f"  - {label}: {prob * 100:.2f}%\n"
        top_pred_text += "\n"

        # 🧾 Build diagnosis output
        result = {
            "diagnosis":disease_name,
            "confidence": confidence,
            "tips": {care_tips[disease_name]},
            "common_symptoms": {', '.join(disease_info[disease_name]['Symptoms'])},
            "possible_causes": {', '.join(disease_info[disease_name]['Causes'])},
            "top_3_predictions":{top_pred_text}
        }

    return result