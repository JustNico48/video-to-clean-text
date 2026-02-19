import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from rake_nltk import Rake
import nltk
from PyPDF2 import PdfReader
from docx import Document
from deep_translator import GoogleTranslator
import io

# --- SETUP RISORSE ---
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('punkt_tab')
    except: pass

download_nltk_data()

st.set_page_config(page_title="CleanScript AI | All-in-One Content Hub", page_icon="🪄", layout="wide")

# --- CSS AESTHETIC ENTERPRISE ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .main-card { background: white; padding: 30px; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    .stButton>button { 
        background-color: #0F172A !important; color: white !important; 
        border-radius: 12px !important; font-weight: 600 !important; 
        height: 3.5rem !important; transition: 0.3s; border: none !important;
    }
    .stButton>button:hover { background-color: #334155 !important; transform: translateY(-2px); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: white; border: 1px solid #E2E8F0; 
        border-radius: 10px; padding: 10px 20px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #0F172A !important; color: white !important; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI SUPPORTO ---
def extract_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_yt_data(v_id):
    try:
        t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['it', 'en', 'es', 'fr', 'de'])
        return " ".join([t['text'] for t in t_list])
    except: return None

# --- UI PRINCIPALE ---
st.title("🪄 CleanScript AI")
st.markdown("<p style='font-size: 1.2em; color: #64748B;'>Converti qualsiasi fonte video o documentale in contenuti ottimizzati.</p>", unsafe_allow_html=True)

if 'processed_text' not in st.session_state:
    st.session_state['processed_text'] = ""

# Layout Input
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    tab_yt, tab_file, tab_manual = st.tabs(["🎥 YouTube", "📁 Documenti", "✍️ Testo"])
    
    with tab_yt:
        c1, c2 = st.columns([3, 1])
        with c1: url = st.text_input("Link Video", placeholder="Incolla URL YouTube...")
        with c2: 
            if st.button("ESTRAI VIDEO"):
                v_id = extract_id(url)
                if v_id:
                    with st.spinner('Analisi...'):
                        res = get_yt_data(v_id)
                        if res: st.session_state['processed_text'] = res
                        else: st.error("Sottotitoli non trovati.")
                else: st.error("URL non valido.")

    with tab_file:
        up_file = st.file_uploader("Carica PDF o Word", type=['pdf', 'docx', 'txt'])
        if up_file:
            if st.button("ELABORA FILE"):
                if up_file.type == "application/pdf":
                    st.session_state['processed_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
                elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    st.session_state['processed_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
                else:
                    st.session_state['processed_text'] = up_file.read().decode("utf-8")

    with tab_manual:
        m_txt = st.text_area("Incolla qui", height=150)
        if st.button("PULISCI"):
            st.session_state['processed_text'] = m_txt
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANALISI E RISULTATI ---
if st.session_state['processed_text']:
    raw = st.session_state['processed_text']
    # Pulizia Timestamp
    clean = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', raw)
    clean = " ".join(clean.split())

    st.markdown("### 📊 Insight & Strumenti")
    
    # Tool di Traduzione e Formattazione
    col_tools1, col_tools2 = st.columns(2)
    with col_tools1:
        target_lang = st.selectbox("🌍 Traduci in:", ["Nessuna", "Italiano", "English", "Spanish", "French", "German"])
        if target_lang != "Nessuna":
            clean = GoogleTranslator(source='auto', target=target_lang.lower()).translate(clean)
    
    with col_tools2:
        format_style = st.select_slider("📝 Stile Formattazione:", options=["Grezzo", "Riassunto", "Blog Post", "LinkedIn Thread"])

    # Dashboard Metriche
    m1, m2, m3, m4 = st.columns(4)
    words = len(clean.split())
    sentiment = TextBlob(clean).sentiment.polarity
    mood = "Positivo 😊" if sentiment > 0.1 else "Neutrale 😐" if sentiment > -0.1 else "Negativo 😟"
    
    m1.metric("Parole", words)
    m2.metric("Mood", mood)
    m3.metric("Tempo Lettura", f"{max(1, words//180)} min")
    m4.metric("Stato", "Analizzato ✅")

    st.markdown("---")
    
    res_col, side_col = st.columns([2, 1])
    
    with res_col:
        st.subheader("Output Finale")
        # Logica Formattazione
        display_text = clean
        if format_style == "Riassunto": display_text = f"📍 RIASSUNTO:\n\n{clean[:800]}..."
        elif format_style == "Blog Post": display_text = f"# TITOLO ARTICOLO\n\n{clean[:400]}...\n\n## Analisi\n{clean[400:]}"
        elif format_style == "LinkedIn Thread": display_text = f"🧵 THREAD\n\n1/5 {clean[:200]}..."

        st.text_area("Risultato:", display_text, height=400, label_visibility="collapsed")
        
        btn_c1, btn_c2 = st.columns(2)
        btn_c1.download_button("📥 Scarica .txt", display_text, file_name="cleanscript_pro.txt")
        if btn_c2.button("📋 Copia negli appunti"):
            st.write('<script>navigator.clipboard.writeText(`' + display_text + '`);</script>', unsafe_allow_html=True)
            st.success("Copiato!")

    with side_col:
        st.subheader("SEO & Social")
        r = Rake()
        r.extract_keywords_from_text(clean)
        kw = r.get_ranked_phrases()[:5]
        for k in kw: st.code(f"🔑 {k}")
        
        st.divider()
        tags = " ".join([f"#{w.replace(' ', '')}" for w in kw])
        st.info(f"**Hashtags:**\n{tags}")
        
        st.markdown("[☕ Supporta il progetto](https://paypal.me/tuolink)")

st.markdown("<br><center><p style='color: #94A3B8;'>CleanScript AI 4.0 Pro — Ultimate Content Assistant</p></center>", unsafe_allow_html=True)
