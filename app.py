import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from rake_nltk import Rake
import nltk
from PyPDF2 import PdfReader
from docx import Document
import io

# --- SETUP RISORSE ---
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('punkt_tab')
    except:
        pass

download_nltk_data()

st.set_page_config(page_title="CleanScript Ultra", page_icon="🛸", layout="wide")

# --- CSS AESTHETIC 2026 ---
st.markdown("""
    <style>
    /* Sfondo e font generale */
    .stApp {
        background-color: #F9FAFB;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Card per i risultati */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }

    /* Pulsanti ultra-leggibili */
    .stButton>button {
        background-color: #1F2937 !important; /* Grigio scuro/Nero */
        color: #FFFFFF !important; /* Testo bianco puro */
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background-color: #374151 !important;
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Styling dei Tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        color: #4B5563;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1F2937 !important;
        color: white !important;
    }

    /* Text Area più elegante */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #E5E7EB !important;
        padding: 15px !important;
    }
    
    h1, h2, h3 {
        color: #111827;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA FUNZIONI ---
def extract_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_yt_data(v_id):
    try:
        t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['it', 'en'])
        return " ".join([t['text'] for t in t_list])
    except: return None

def read_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages])

def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])

# --- INTERFACCIA ---
st.title("🛸 CleanScript Ultra")
st.markdown("<p style='color: #6B7280; font-size: 1.1em;'>L'hub definitivo per trasformare video e documenti in contenuti puliti.</p>", unsafe_allow_html=True)

input_text = ""

# Layout Tab
tab_yt, tab_file, tab_manual = st.tabs(["🎥 YouTube Link", "📁 Upload Documenti", "✍️ Incolla Testo"])

with tab_yt:
    url = st.text_input("Inserisci URL YouTube", placeholder="https://youtube.com/watch?v=...")
    if st.button("ANALIZZA VIDEO"):
        v_id = extract_id(url)
        if v_id:
            with st.spinner('Estraendo sottotitoli...'):
                input_text = get_yt_data(v_id)
        else: st.error("Link non valido.")

with tab_file:
    uploaded_file = st.file_uploader("Trascina PDF o Word", type=['pdf', 'docx', 'txt'])
    if uploaded_file:
        if st.button("ELABORA DOCUMENTO"):
            with st.spinner('Lettura file...'):
                if uploaded_file.type == "application/pdf":
                    input_text = read_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    input_text = read_docx(uploaded_file)
                else:
                    input_text = uploaded_file.read().decode("utf-8")

with tab_manual:
    manual_text = st.text_area("Incolla qui il testo sporco", height=200)
    if st.button("PULISCI TESTO"):
        input_text = manual_text

# --- ENGINE ANALISI ---
if input_text:
    # Pulizia
    input_text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', input_text)
    input_text = " ".join(input_text.split())

    # Statistiche
    words = len(input_text.split())
    blob = TextBlob(input_text)
    sentiment = "Positivo" if blob.sentiment.polarity > 0.1 else "Negativo" if blob.sentiment.polarity < -0.1 else "Neutrale"
    
    r = Rake()
    r.extract_keywords_from_text(input_text)
    keywords = r.get_ranked_phrases()[:6]
    
    st.markdown("---")
    
    # Dashboard Card
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card"><span style="color:#6B7280">PAROLE</span><br><h2 style="margin:0">{words}</h2></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card"><span style="color:#6B7280">SENTIMENT</span><br><h2 style="margin:0">{sentiment}</h2></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card"><span style="color:#6B7280">KEYWORDS</span><br><h2 style="margin:0">{len(keywords)}</h2></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📝 Testo Elaborato")
        final_area = st.text_area("", input_text, height=450, label_visibility="collapsed")
        st.download_button("📥 SCARICA TESTO", final_area, file_name="cleanscript_pro.txt")
    
    with c2:
        st.subheader("🏷️ SEO & Social")
        st.write("**Keywords identificate:**")
        for kw in keywords: st.code(kw)
        
        st.divider()
        st.write("**Hashtags consigliati:**")
        tags = " ".join([f"#{w.replace(' ', '')}" for w in keywords[:4]])
        st.info(tags)
        
        st.markdown("[☕ Supporta lo sviluppo](https://paypal.me/tuolink)")

st.markdown("<br><hr><center><p style='color: #9CA3AF;'>CleanScript AI Pro — Minimal & Powerful</p></center>", unsafe_allow_html=True)
