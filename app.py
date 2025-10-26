import streamlit as st
import re
import torch
import pandas as pd
import Levenshtein
from transformers import MT5ForConditionalGeneration, MT5Tokenizer


# memanggil model dari Hugging Face
model_id = "marvin06/mt5-normalisasi-slang"

# =======================================================================
# 1. FUNGSI MEMUAT MODEL 
# =======================================================================
@st.cache_resource
def load_model_and_data():
    """
    Memuat model, tokenizer, dan data slang dari file.
    Dijalankan sekali dan disimpan di cache.
    """
    print("Memuat model dan data...")
    
    error_message = None
    
    try:
        tokenizer = MT5Tokenizer.from_pretrained(model_id)
        model = MT5ForConditionalGeneration.from_pretrained(model_id)
    except Exception as e:
        print(f"Gagal memuat model: {e}")
        error_message = f"Gagal memuat model dari Hugging Face: {e}. Pastikan 'model_id' benar dan ada koneksi internet."
        return None, None, None, None, None, None, error_message

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    try:
        df = pd.read_csv("slang-indo.csv")
    except FileNotFoundError:
        print("File 'slang-indo.csv' tidak ditemukan.")
        error_message = "File 'slang-indo.csv' tidak ditemukan. Pastikan file ada di folder yang sama."
        return None, None, None, None, None, None, error_message

    df = df.dropna(subset=["input_text", "target_text"]).copy()
    slang_dict = {src.lower(): str(tgt).strip() for src, tgt in zip(df["input_text"], df["target_text"])}
    baku_list = [str(item).strip() for item in df["target_text"].tolist()]
    baku_set = set(w.lower() for w in baku_list)
    
    print(f"Model dan data berhasil dimuat di {device}.")
    return tokenizer, model, device, slang_dict, baku_list, baku_set, error_message

# =======================================================================
# 2. SEMUA FUNGSI LOGIKA NORMALISASI
# =======================================================================
def predict_mt5(word: str, tokenizer, model, device) -> str:
    """Prediksi satu kata menggunakan mT5"""
    input_ids = tokenizer.encode(word.strip(), return_tensors="pt").to(device)
    with torch.no_grad():
        output_ids = model.generate(input_ids, max_length=10)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

#Fallback Algoritma Levenshtein Distance
def levenshtein_fallback(word: str, baku_list: list[str]) -> str:
    wl = word.lower()
    best_match, min_dist = word, float("inf")
    for cand in baku_list:
        dist = Levenshtein.distance(wl, cand.lower())
        if dist < min_dist:
            best_match, min_dist = cand, dist
        if dist == 0: 
            break
    return best_match

# Hybrid Normalisasi 
def hybrid_normalize(word: str, tokenizer, model, device, slang_dict: dict, baku_list: list[str], baku_set: set[str]):
    pred = predict_mt5(word, tokenizer, model, device)
    wl = word.lower()
    if wl in slang_dict:
        gold_target = slang_dict[wl]
        if pred.lower() == gold_target.lower():
            return pred, "mT5"
        return gold_target, "mt5"

    # cek validasi rule-based (apakah hasil mT5 ada di daftar kata baku)
    if pred.lower() in baku_set:
        return pred, "mT5"
        
    # Jika tidak valid, jalankan fallback Levenshtein Distance
    fallback = levenshtein_fallback(word, baku_list)
    return fallback, "Levenshtein"

# Proses teks penuh
def normalize_sentence_full(sentence: str, tokenizer, model, device, slang_dict, baku_list, baku_set):
    """Fungsi utama untuk menormalisasi seluruh kalimat."""
    # Pra-pemrosesan sederhana: lowercase 
    sentence = sentence.lower() 
    words_and_punctuation = re.findall(r"[\w']+|[.,!?;]", sentence)
    normalized_words = []
    details = [] 

    for item in words_and_punctuation:
        if re.match(r"[\w']+", item):
            if item.isdigit():
                normalized_word, source = item,
            else:
                normalized_word, source = hybrid_normalize(item, tokenizer, model, device, slang_dict, baku_list, baku_set)
            
            normalized_words.append(normalized_word)
            details.append({"Kata Asli": item, "Hasil": normalized_word, "Sumber": source})
        else:
            normalized_words.append(item)

    # Gabungkan kembali
    result = "".join([f" {word}" if word not in [",", ".", "!", "?", ";"] else word for word in normalized_words]).strip()
    return result, details

# =======================================================================
# 3. FUNGSI UNTUK CSS
# =======================================================================
def local_css(file_name):
    """Fungsi untuk memuat file CSS lokal."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        print(f"File CSS '{file_name}' tidak ditemukan.")