import streamlit as st
import app  # Impor file logika kita
import base64 # <-- Tambahkan ini
from PIL import Image # <-- Tambahkan ini
import os # <-- Tambahkan ini

# --- Path ke logo ---
# Ini adalah path relatif dari root folder proyek (tempat Anda menjalankan `streamlit run`)
LOGO_PATH = "assets\logo.png"

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
    page_icon = None # Default jika file tidak ada

# ==========================================================
# TEMPLATE WAJIB UNTUK SETIAP HALAMAN
# ==========================================================

# 1. KONFIGURASI
st.set_page_config(
    page_title="Input Kalimat",
    page_icon=page_icon,  # <-- DIUBAH: Menggunakan objek gambar PIL
    layout="wide"
)

# 2. PANGGIL CSS (LANGSUNG SETELAH CONFIG)
app.local_css("style.css")

# --- Buat HTML logo ---
LOGO_HTML = get_img_with_href(LOGO_PATH) # <-- DIUBAH: Memanggil fungsi Base64

# 3. INJEKSI HEADER (SETELAH CSS)
st.markdown(f"""
    <header class="app-header">
        <a href="/" target="_self" class="logo">{LOGO_HTML} SlangBuster</a>
        <nav class="nav-links">
            <a href="/" target="_self">Home</a>
            <a href="/input_kalimat" target="_self">Input Teks</a>
            <a href="/input_file" target="_self">Input File</a>
            <a href="/help&about" target="_self">About & Help</a>
        </nav>
        <div class="header-right"></div>
    </header>
""", unsafe_allow_html=True)

# ==========================================================
# KONTEN HALAMAN
# ==========================================================

st.title("Modul Input Teks")
st.write("Modul ini digunakan untuk menormalisasi kalimat slang yang diketik langsung.")


with st.spinner("Sedang memuat model & data..."):
    tokenizer, model, device, slang_dict, baku_list, baku_set, error = app.load_model_and_data()

# Jika model gagal dimuat
if error:
    st.error(f"Gagal memuat model atau data: {error}")
    st.error("Aplikasi tidak dapat berjalan. Harap periksa `home.py` untuk detail error.")
    st.stop()

# ==========================================================
# Gunakan Kolom (Layout dari respons sebelumnya)
# ==========================================================

col1, col2 = st.columns(2)

with col1:
    input_sentence = st.text_area("Masukkan kalimat slang:", placeholder="cth: lo bgt g si? mager bgt...", height=150)
    button_pressed = st.button("Normalisasi Kalimat", use_container_width=True)

with col2:
    output_container = st.empty()
    with output_container.container():
        st.info("Hasil normalisasi akan muncul di sini.")

details = None

if button_pressed:
    if input_sentence:
        with st.spinner("Sedang memproses..."):
            normalized_sentence, details = app.normalize_sentence_full(
                input_sentence, tokenizer, model, device, slang_dict, baku_list, baku_set
            )

        with output_container.container():
            st.success("Hasil Normalisasi:")
            
            # Tampilan hasil normalisasi (CSS Anda)
            st.markdown(f"""
            <div style="
                background: #ffffff;
                padding: 18px 22px;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
                box-shadow: 0px 4px 14px rgba(0,0,0,0.05);
                font-size: 17px;
                line-height: 1.65;
                color: #1f1f1f;
                font-weight: 500;
                white-space: pre-wrap;
                min-height: 150px;
            ">
            {normalized_sentence}
            </div>
            """, unsafe_allow_html=True)

    else:
        with col1:
            st.warning("Mohon masukkan kalimat terlebih dahulu.")

if details is not None: 
    st.divider()
    st.subheader("Detail Proses Normalisasi (per kata)")
    st.dataframe(details, use_container_width=True)


# ==========================================================
# FOOTER
# ==========================================================
st.markdown(f"""
    <footer class="app-footer">
        <div class="logo">{LOGO_HTML} SlangBuster</div> 
        <div class="footer-center-text"></div>
        <div class="footer-right">Dikembangkan oleh: Marvin Gultom</div>
    </footer>
    """, unsafe_allow_html=True)