import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from rake_nltk import Rake
import nltk
from PyPDF2 import PdfReader
from docx import Document
import io

# --- FIX RISORSE NLTK ---
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('punkt_tab')
    except:
        pass

download_nltk_data()

st.set_page_config(page_title="CleanScript AI Ultra", page_icon="🛸", layout="wide")

# Styling Premium
st.markdown("""
    <style>
    .main { background: #f4f7f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff; border-radius: 10px 10px 0px 0px; padding: 10px 20px; border: 1px solid #eee;
    }
    .metric-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; }
    .stButton>button { border-radius: 10px; background: #2563eb; color: white; border: none; font-weight: bold; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI ESTRAZIONE ---
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
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])

# --- INTERFACCIA ---
st.title("🛸 CleanScript AI Ultra 2026")
st.markdown("##### Carica Video, PDF, Word o Testo e ottieni analisi e contenuti puliti istantaneamente.")

input_text = ""

# Creazione Tab
tab_yt, tab_file, tab_manual = st.tabs(["🎥 YouTube Link", "📁 Carica File (PDF/DOC)", "✍️ Incolla Testo"])

with tab_yt:
    url = st.text_input("URL Video:", placeholder="https://www.youtube.com/watch?v=...")
    if st.button("ANALIZZA VIDEO 🎬"):
        v_id = extract_id(url)
        if v_id:
            with st.spinner('Estraendo sottotitoli...'):
                input_text = get_yt_data(v_id)
        else: st.error("Link non valido.")

with tab_file:
    uploaded_file = st.file_uploader("Trascina qui il tuo file (PDF, DOCX o TXT)", type=['pdf', 'docx', 'txt'])
    if uploaded_file and st.button("ELABORA FILE 📑"):
        with st.spinner('Leggendo il file...'):
            if uploaded_file.type == "application/pdf":
                input_text = read_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                input_text = read_docx(uploaded_file)
            else:
                input_text = uploaded_file.read().decode("utf-8")

with tab_manual:
    manual_text = st.text_area("Incolla il tuo testo qui:", height=200)
    if st.button("PULISCI TESTO ✨"):
        input_text = manual_text

# --- ENGINE DI ANALISI ---
if input_text:
    # Pulizia
    input_text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', input_text)
    input_text = " ".join(input_text.split())

    # Sentiment & Keywords
    blob = TextBlob(input_text)
    sentiment = "Positivo 😊" if blob.sentiment.polarity > 0.1 else "Negativo 😟" if blob.sentiment.polarity < -0.1 else "Neutrale 😐"
    
    r = Rake()
    r.extract_keywords_from_text(input_text)
    keywords = r.get_ranked_phrases()[:8]
    
    words = len(input_text.split())
    
    st.divider()
    
    # Dashboard Risultati
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f'<div class="metric-card">📖 Parole<br><h3>{words}</h3></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card">🎭 Mood<br><h3>{sentiment}</h3></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card">🔑 Keywords<br><h3>{len(keywords)}</h3></div>', unsafe_allow_html=True)
    
    st.divider()
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📝 Contenuto Elaborato")
        final_area = st.text_area("", input_text, height=400, label_visibility="collapsed")
        st.download_button("📥 Scarica Risultato .txt", final_area, file_name="cleanscript_ultra.txt")
    
    with c2:
        st.subheader("🏷️ Social & SEO")
        st.write("**Top Keywords:**")
        for kw in keywords: st.code(kw)
        
        st.divider()
        st.write("**Hashtags:**")
        tags = " ".join([f"#{w.replace(' ', '')}" for w in keywords[:5]])
        st.info(tags)
        
        st.markdown("[☕ Supporta il Progetto](https://www.paypal.me/tuo-link)")

st.markdown("---")
st.caption("CleanScript AI Ultra - Gestione Multiformato Avanzata")
