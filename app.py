import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from rake_nltk import Rake
import nltk

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

st.set_page_config(page_title="CleanScript AI 4.0 Ultra", page_icon="🚀", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .main { background: #f8f9fc; }
    .metric-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eee; }
    .stButton>button { border-radius: 50px; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); color: white; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI ---
def extract_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_yt_data(v_id):
    try:
        t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['it', 'en'])
        return " ".join([t['text'] for t in t_list])
    except: return None

# --- INTERFACCIA ---
st.title("🚀 CleanScript AI 4.0 Ultra")
st.markdown("##### Trasforma video YouTube o testi grezzi in contenuti professionali.")

# Tab per scegliere la fonte
tab_yt, tab_manual = st.tabs(["🎥 Da Link YouTube", "✍️ Incolla Testo Manuale"])

input_text = "" # Variabile che conterrà il testo da analizzare

with tab_yt:
    url = st.text_input("Inserisci URL YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    if st.button("ESTRAI DA YOUTUBE ⚡"):
        v_id = extract_id(url)
        if v_id:
            with st.spinner('Estrazione in corso...'):
                input_text = get_yt_data(v_id)
                if not input_text:
                    st.error("Sottotitoli non disponibili per questo video.")
        else:
            st.error("URL non valido.")

with tab_manual:
    manual_text = st.text_area("Incolla qui il tuo testo sporco (es. trascrizioni Zoom, appunti, etc.):", height=250)
    if st.button("PULISCI TESTO MANUALE ✨"):
        if manual_text:
            input_text = manual_text
        else:
            st.warning("Incolla del testo prima di procedere.")

# --- AREA ANALISI (Si attiva solo se c'è del testo) ---
if input_text:
    # Pulizia base (rimozione timestamp se presenti)
    input_text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', input_text)
    input_text = " ".join(input_text.split())

    # Analisi Sentiment
    blob = TextBlob(input_text)
    sentiment = "Positivo 😊" if blob.sentiment.polarity > 0.1 else "Negativo 😟" if blob.sentiment.polarity < -0.1 else "Neutrale 😐"
    
    # Analisi Keyword
    r = Rake()
    r.extract_keywords_from_text(input_text)
    keywords = r.get_ranked_phrases()[:8]
    
    # Statistiche
    words = len(input_text.split())
    time_saved = max(1, round(words / 150))
    
    st.divider()
    
    # Dashboard Metriche
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-card">📖 Parole<br><h3>{words}</h3></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-card">🎭 Mood<br><h3>{sentiment}</h3></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-card">⏱️ Risparmiati<br><h3>{time_saved} min</h3></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-card">🔑 Keyword<br><h3>{len(keywords)}</h3></div>', unsafe_allow_html=True)
    
    st.divider()
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📝 Risultato Pulito")
        st.text_area("Contenuto pronto all'uso:", input_text, height=400)
        st.download_button("📥 Scarica Report .txt", input_text, file_name="cleanscript_output.txt")
    
    with c2:
        st.subheader("🏷️ Social & SEO")
        st.write("**Keywords:**")
        for kw in keywords:
            st.code(kw)
        
        st.divider()
        st.write("**Hashtags:**")
        tags = " ".join([f"#{w.replace(' ', '')}" for w in keywords[:5]])
        st.info(tags)
        
        st.markdown("[☕ Offrimi un caffè](https://www.paypal.me/tuo-link)")

st.markdown("---")
st.caption("© 2026 CleanScript AI - Nessun dato viene salvato.")
