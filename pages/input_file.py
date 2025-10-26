import streamlit as st
import app # Impor file logika kita
import pandas as pd
import io
import pdfplumber # Library untuk baca PDF
# openpyxl sudah di-install, diperlukan oleh pandas untuk .xlsx

import base64 # <-- Tambahkan ini
from PIL import Image # <-- Tambahkan ini
import os # <-- Tambahkan ini

# --- Path ke logo ---
# DIUBAH: Gunakan forward slash '/' untuk path agar kompatibel di semua OS
LOGO_PATH = "assets/logo.png"

# --- Fungsi untuk encode gambar ---
@st.cache_data # Cache agar tidak dibaca ulang setiap kali
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None # Kembalikan None jika file tidak ada

# --- Fungsi untuk membuat tag HTML gambar ---
def get_img_with_href(local_img_path):
    img_base64 = get_base64_of_bin_file(local_img_path)
    if img_base64:
        return f'<img src="data:image/png;base64,{img_base64}" style="height: 50px; margin-right: 8px; vertical-align: middle;">'
    return "" # Kembalikan string kosong jika file tidak ditemukan

# --- Muat icon untuk tab browser ---
try:
    page_icon = Image.open(LOGO_PATH)
except FileNotFoundError:
    page_icon = None

# ==========================================================
# TEMPLATE WAJIB UNTUK SETIAP HALAMAN
# ==========================================================

# 1. KONFIGURASI (HARUS PERTAMA + layout="wide")
st.set_page_config(
    page_title="Input File",
    page_icon=page_icon,  # <-- DIUBAH
    layout="wide"
)

# 2. PANGGIL CSS (LANGSUNG SETELAH CONFIG)
app.local_css("style.css")

# --- Buat HTML logo ---
LOGO_HTML = get_img_with_href(LOGO_PATH) # <-- DIUBAH

# 3. INJEKSI HEADER (SETELAH CSS)
st.markdown(f"""
    <header class="app-header">
        <a href="/" target="_self" class="logo">{LOGO_HTML} SlangBuster</a> <nav class="nav-links">
            <a href="/" target="_self">Home</a>
            <a href="/input_kalimat" target="_self">Input Teks</a>
            <a href="/input_file" target="_self">Input File</a>
            <a href="/help&about" target="_self">About & Help</a>
        </nav>
        <div class="header-right"></div>
    </header>
    """, unsafe_allow_html=True)
# ==========================================================

# --- Konten Halaman ---
st.title("Modul Input File") # Saya biarkan emoji di sini agar sesuai dengan aslinya
st.write("Modul ini digunakan untuk menormalisasi file `.txt`, `.csv`, `.xlsx`, atau `.pdf`.")

# --- Fungsi Helper untuk Proses File ---

def process_text(text, tokenizer, model, device, slang_dict, baku_list, baku_set):
    """Fungsi untuk menormalisasi satu blok teks (bisa banyak baris)"""
    lines = text.split('\n')
    processed_lines = []
    all_details = []
    
    for line in lines:
        line_strip = line.strip()
        if line_strip:
            norm_line, details = app.normalize_sentence_full(
                line_strip, tokenizer, model, device, slang_dict, baku_list, baku_set
            )
            processed_lines.append(norm_line)
            all_details.extend(details)
    
    return "\n".join(processed_lines), all_details

def process_dataframe(df, col_to_normalize, tokenizer, model, device, slang_dict, baku_list, baku_set):
    """Fungsi untuk menormalisasi satu kolom di DataFrame"""
    
    # Buat list untuk menampung hasil
    normalized_column = []
    
    # Progress bar
    progress_bar = st.progress(0, text="Memproses DataFrame...")
    
    total_rows = len(df)
    
    for i, text in enumerate(df[col_to_normalize].astype(str)):
        if pd.isna(text) or text.strip() == "":
            normalized_column.append("")
        else:
            norm_text, _ = app.normalize_sentence_full(
                text, tokenizer, model, device, slang_dict, baku_list, baku_set
            )
            normalized_column.append(norm_text)
        
        # Update progress bar
        progress_bar.progress((i + 1) / total_rows, text=f"Memproses baris {i+1}/{total_rows}")
        
    progress_bar.empty() # Hapus progress bar setelah selesai
    
    # Tambah kolom baru ke df
    df[f"hasil_normalisasi_{col_to_normalize}"] = normalized_column
    return df

# --- UI Utama ---

# SOLUSI MASALAH LOADING LAMA
with st.spinner("Sedang memuat model & kamus..."):
    tokenizer, model, device, slang_dict, baku_list, baku_set, error = app.load_model_and_data()

if error:
    st.error(f"Gagal memuat model atau data: {error}")
    st.error("Aplikasi tidak dapat berjalan. Harap periksa `1_Home.py` untuk detail error.")
else:
    # 2. Tampilkan file uploader
    uploaded_file = st.file_uploader(
        "Pilih file (.txt, .csv, .xlsx, .pdf)", 
        type=["txt", "csv", "xlsx", "pdf"]
    )

    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' berhasil diunggah.")
        
        # Siapkan variabel untuk hasil
        result_text = ""
        original_text = "" # <-- DIUBAH: Tambahkan variabel untuk teks asli
        result_df = None
        output_data = None
        output_filename = f"hasil_{uploaded_file.name}"

        try:
            # --- Logika Pemrosesan berdasarkan Tipe File ---
            
            # Tipe .TXT
            if uploaded_file.type == "text/plain":
                with st.spinner("Membaca dan memproses file .txt..."):
                    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                    file_content = stringio.read()
                    original_text = file_content # <-- DIUBAH: Simpan teks asli
                    result_text, _ = process_text(file_content, tokenizer, model, device, slang_dict, baku_list, baku_set)
                    output_data = result_text.encode("utf-8")
                    output_filename = f"hasil_{uploaded_file.name.split('.')[0]}.txt"

            # Tipe .PDF
            elif uploaded_file.type == "application/pdf":
                with st.spinner("Mengekstrak dan memproses file .pdf... (Hanya teks, gambar diabaikan)"):
                    full_text = ""
                    with pdfplumber.open(uploaded_file) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                full_text += page_text + "\n"
                    
                    original_text = full_text # <-- DIUBAH: Simpan teks asli
                    result_text, _ = process_text(full_text, tokenizer, model, device, slang_dict, baku_list, baku_set)
                    output_data = result_text.encode("utf-8")
                    output_filename = f"hasil_{uploaded_file.name.split('.')[0]}.txt"

            # Tipe .CSV atau .XLSX (Excel)
            else: 
                with st.spinner("Membaca file tabular..."):
                    if uploaded_file.type == "text/csv":
                        df = pd.read_csv(uploaded_file)
                    else: # .xlsx
                        df = pd.read_excel(uploaded_file)
                
                st.subheader("Preview Data:")
                st.dataframe(df.head())
                
                col_to_normalize = st.selectbox("Pilih kolom yang ingin dinormalisasi:", df.columns)
                
                # <-- DIUBAH: Typo "Mai" -> "Mulai"
                if st.button(f"Mulai Normalisasi Kolom '{col_to_normalize}'"):
                    result_df = process_dataframe(df.copy(), col_to_normalize, tokenizer, model, device, slang_dict, baku_list, baku_set)
                    
                    # Siapkan data untuk download
                    output_stream = io.BytesIO()
                    if uploaded_file.type == "text/csv":
                        result_df.to_csv(output_stream, index=False, encoding="utf-8")
                        output_data = output_stream.getvalue()
                        output_filename = f"hasil_{uploaded_file.name.split('.')[0]}.csv"
                    else: # .xlsx
                        result_df.to_excel(output_stream, index=False, engine='openpyxl')
                        output_data = output_stream.getvalue()
                        output_filename = f"hasil_{uploaded_file.name.split('.')[0]}.xlsx"

            # ==========================================================
            # --- Tampilkan Hasil (BAGIAN INI DIUBAH TOTAL) ---
            # ==========================================================
            
            if result_text:
                st.subheader("Perbandingan Hasil Normalisasi Teks")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h5>Teks Asli:</h5>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="
                        background: #F4F4F5; /* Warna abu-abu muda untuk teks asli */
                        padding: 18px 22px;
                        border-radius: 12px;
                        border: 1px solid #E0E0E0;
                        font-size: 16px;
                        line-height: 1.6;
                        color: #52525B;
                        white-space: pre-wrap; /* Agar baris baru tetap ada */
                        height: 400px; /* Tinggi tetap */
                        overflow-y: auto; /* Tambah scrollbar jika teks panjang */
                    ">
                    {original_text}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<h5>Teks Normalisasi:</h5>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="
                        background: #ffffff;
                        padding: 18px 22px;
                        border-radius: 12px;
                        border: 1px solid #E0E0E0;
                        box-shadow: 0px 4px 14px rgba(0,0,0,0.05);
                        font-size: 16px;
                        line-height: 1.6;
                        color: #1f1f1f;
                        font-weight: 500;
                        white-space: pre-wrap; /* Agar baris baru tetap ada */
                        height: 400px; /* Tinggi tetap */
                        overflow-y: auto; /* Tambah scrollbar jika teks panjang */
                    ">
                    {result_text}
                    </div>
                    """, unsafe_allow_html=True)
            
            if result_df is not None:
                st.subheader("Hasil Normalisasi DataFrame:")
                st.dataframe(result_df)
            
            # 4. Tombol Download (hanya muncul jika ada data)
            if output_data:
                st.download_button(
                    label=f"Download {output_filename}",
                    data=output_data,
                    file_name=output_filename,
                    mime='text/plain' if uploaded_file.type == "text/plain" or uploaded_file.type == "application/pdf" else 
                         ('text/csv' if uploaded_file.type == "text/csv" else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                )
                
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")
            st.exception(e) # Tampilkan detail error untuk debugging


# FOOTER (PALING BAWAH)
st.markdown(f"""
    <footer class="app-footer">
        <div class="logo">{LOGO_HTML} SlangBuster</div> <div class="footer-center-text">Dikembangkan oleh: Marvin Gultom</div>
        <div class="footer-right"></div>
    </footer>
    """, unsafe_allow_html=True)