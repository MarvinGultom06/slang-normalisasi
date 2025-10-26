import streamlit as st
import app  
import base64
from PIL import Image
import os
# --- Path ke logo ---
LOGO_PATH = "assets/logo.png" 

ICON_TEKS_PATH = "assets\logo_pensil.png"
ICON_FILE_PATH = "assets\logo_file.png"
ICON_HASIL_PATH = "assets\logo_party.png"

@st.cache_data 
def get_base64_of_bin_file(bin_file):
    try:
        with open(os.path.normpath(bin_file), 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None 

def get_img_with_href(local_img_path):
    img_base64 = get_base64_of_bin_file(local_img_path)
    if img_base64:
        return f'<img src="data:image/png;base64,{img_base64}" style="height: 50px; margin-right: 8px; vertical-align: middle;">'
    return "" 

def get_content_img_html(local_img_path, height=150):
    img_base64 = get_base64_of_bin_file(local_img_path)
    file_ext = os.path.splitext(local_img_path)[1].lower()
    if file_ext == ".png":
        img_type = "png"
    elif file_ext in [".jpg", ".jpeg"]:
        img_type = "jpeg"
    else:
        return "" 
    
    if img_base64:
        return f'<div style="text-align: center; height: {height+10}px; display: flex; align-items: center; justify-content: center;">' \
               f'<img src="data:image/{img_type};base64,{img_base64}" style="height: {height}px; vertical-align: middle;">' \
               f'</div>'
    return ""
try:
    page_icon = Image.open(os.path.normpath(LOGO_PATH))
except FileNotFoundError:
    page_icon = None 

# 1) KONFIGURASI
st.set_page_config(
    page_title="Home - Normalisasi Slang",
    page_icon=page_icon, # <-- DIUBAH
    layout="wide"
)

# 2) CSS
app.local_css("style.css")

# --- Buat HTML logo ---
LOGO_HTML = get_img_with_href(LOGO_PATH) # <-- DITAMBAHKAN

# --- BUAT HTML UNTUK IKON KONTEN (BARU) ---
ICON_TEKS_HTML = get_content_img_html(ICON_TEKS_PATH)
ICON_FILE_HTML = get_content_img_html(ICON_FILE_PATH)
ICON_HASIL_HTML = get_content_img_html(ICON_HASIL_PATH)
# -----------------------------------

# 3) HEADER (tetap, hanya tampilan)
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


st.write("")

st.markdown("""
<div class="hero">
    <p class="hero-kicker">Normalisasi Kata Slang ke Bahasa Indonesia Baku Secara Otomatis</p>
    <h1 class="hero-title">Langsung dari teks atau file Anda.</h1>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Mulai Normalisasi", use_container_width=True):
        try:
            st.switch_page("pages/input_kalimat.py")
        except Exception as e:
            st.write("Klik tautan berikut untuk masuk:")
            st.page_link("pages/input_kalimat.py", label="➡️ Buka: Input Teks")
st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)


# ==========================================================
# --- BAGIAN BARU 1: CARA PENGGUNAAN (DIUBAH) ---
# ==========================================================
st.divider()
st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>Cara Mudah Menggunakan SlangBuster</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("<h3 style='text-align: center;'>1. Input Teks</h3>", unsafe_allow_html=True)
    st.markdown(
        f"""
        {ICON_TEKS_HTML} 
        <p style="text-align: center; margin-top: 15px;">
        Punya kalimat pendek? Langsung ketik di modul <a href="/input_kalimat" target="_self">Input Teks</a> 
        untuk normalisasi instan.
        </p>
        """, unsafe_allow_html=True
    )

with col2:
    st.markdown("<h3 style='text-align: center;'>2. Input File</h3>", unsafe_allow_html=True)
    st.markdown(
        f"""
        {ICON_FILE_HTML}
        <p style="text-align: center; margin-top: 15px;">
        Punya file <strong>.txt, .csv, .xlsx,</strong> atau <strong>.pdf</strong>? Unggah di modul 
        <a href="/input_file" target="_self">Input File</a> untuk diproses sekaligus.
        </p>
        """, unsafe_allow_html=True
    )

with col3:
    st.markdown("<h3 style='text-align: center;'>3. Dapatkan Hasil</h3>", unsafe_allow_html=True)
    st.markdown(
        f"""
        {ICON_HASIL_HTML}
        <p style="text-align: center; margin-top: 15px;">
        Lihat hasil normalisasi Anda. Untuk file, Anda bisa langsung 
        <strong>mengunduh hasilnya</strong> dalam format yang sama.
        </p>
        """, unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)

# ==========================================================
# --- BAGIAN BARU 2: FITUR UNGGULAN ---
# ==========================================================
st.divider()
st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>Fitur Unggulan</h2>", unsafe_allow_html=True)

col_feat1, col_feat2, col_feat3 = st.columns(3, gap="large")
with col_feat1:
    st.markdown("### 1. Model Hybrid Cerdas")
    st.write(
        """
        Menggunakan **model mT5** yang di-fine-tuning, didukung validasi
        kamus baku dan algoritma Levenshtein untuk akurasi terbaik.
        """
    )
with col_feat2:
    st.markdown("### 2. Mendukung Berbagai Format")
    st.write(
        """
        Tidak hanya teks biasa, Anda bisa langsung menormalisasi
        dokumen <strong>.pdf</strong>, <strong>.txt</strong>, <strong>.csv</strong>, 
        dan <strong>.xlsx</strong>.
        """, unsafe_allow_html=True
    )
with col_feat3:
    st.markdown("### 3. Detail Proses Transparan")
    st.write(
        """
        Pada modul 'Input Teks', Anda bisa melihat detail proses
        normalisasi kata per kata, lengkap dengan metode yang digunakan.
        """
    )


# ==========================================================
# FOOTER
# ==========================================================
st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
    <footer class="app-footer">
        <div class="logo">{LOGO_HTML} SlangBuster</div> <div class="footer-center-text"></div>
        <div class="footer-right">Dikembangkan oleh: Marvin Gultom</div>
    </footer>
    """, unsafe_allow_html=True)