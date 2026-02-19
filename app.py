import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from rake_nltk import Rake
import nltk

# --- FIX PER IL DOWNLOAD DELLE RISORSE NLTK ---
@st.cache_resource # Questo evita di scaricare tutto ogni volta che rinfreschi la pagina
def download_nltk_data():
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('punkt_tab') # Necessario per le nuove versioni
    except Exception as e:
        st.error(f"Errore nel download dei dati NLTK: {e}")

download_nltk_data()

# Configurazione Pagina
st.set_page_config(page_title="CleanScript AI 4.0 Ultra", page_icon="🚀", layout="wide")

# CSS Migliorato
st.markdown("""
    <style>
    .main { background: #f8f9fc; }
    .metric-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; }
    .stButton>button { border-radius: 50px; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); color: white; border: none; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA ---
def extract_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_data(v_id):
    try:
        # Tenta di prendere i sottotitoli in italiano, altrimenti inglese
        t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['it', 'en'])
        return " ".join([t['text'] for t in t_list])
    except Exception as e:
        return None

# --- UI ---
st.title("🚀 CleanScript AI 4.0 Ultra")
st.markdown("##### Analizzatore di Video YouTube - Da video a contenuto in 3 secondi.")

url = st.text_input("Incolla URL YouTube qui:", placeholder="https://www.youtube.com/watch?v=...")
process = st.button("ANALIZZA ORA ⚡")

if process and url:
    v_id = extract_id(url)
    if v_id:
        with st.spinner('Analisi profonda in corso...'):
            raw_text = get_data(v_id)
            if raw_text:
                # 1. Sentiment Analysis
                blob = TextBlob(raw_text)
                sentiment = "Positivo 😊" if blob.sentiment.polarity > 0.1 else "Negativo 😟" if blob.sentiment.polarity < -0.1 else "Neutrale 😐"
                
                # 2. Keyword Extraction
                r = Rake()
                r.extract_keywords_from_text(raw_text)
                keywords = r.get_ranked_phrases()[:8]
                
                # 3. Statistiche
                words = len(raw_text.split())
                time_saved = max(1, round(words / 150))
                
                # Visualizzazione Dashboard
                st.divider()
                m1, m2, m3, m4 = st.columns(4)
                with m1: st.markdown(f'<div class="metric-card">📖 Parole<br><h3>{words}</h3></div>', unsafe_allow_html=True)
                with m2: st.markdown(f'<div class="metric-card">🎭 Mood<br><h3>{sentiment}</h3></div>', unsafe_allow_html=True)
                with m3: st.markdown(f'<div class="metric-card">⏱️ Risparmiati<br><h3>{time_saved} min</h3></div>', unsafe_allow_html=True)
                with m4: st.markdown(f'<div class="metric-card">🔑 Keyword<br><h3>{len(keywords)}</h3></div>', unsafe_allow_html=True)
                
                st.divider()
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.subheader("📝 Trascrizione Pulita")
                    st.text_area("", raw_text, height=400, label_visibility="collapsed")
                    st.download_button("📥 Scarica Report .txt", raw_text)
                
                with c2:
                    st.subheader("🏷️ SEO & Social")
                    st.write("**Keywords principali:**")
                    for kw in keywords:
                        st.code(kw)
                    
                    st.divider()
                    st.write("**Hashtags suggeriti:**")
                    tags = " ".join([f"#{w.replace(' ', '')}" for w in keywords[:5]])
                    st.info(tags)
                    st.markdown("[☕ Offrimi un caffè](https://www.paypal.me/tuo-link)")
            else:
                st.error("Errore: Sottotitoli non disponibili per questo video (disattivati dall'autore o assenti).")
    else:
        st.error("URL non valido. Assicurati che sia un link YouTube corretto.")

st.markdown("---")
st.caption("CleanScript AI 4.0 - Versione Stabile 2026")
