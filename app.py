import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from rake_nltk import Rake
import nltk

# Download necessario per le keyword
nltk.download('punkt')
nltk.download('stopwords')

st.set_page_config(page_title="CleanScript AI 4.0 | Ultra-Content Tool", page_icon="🚀", layout="wide")

# Custom CSS per l'effetto "Premium"
st.markdown("""
    <style>
    .main { background: #f8f9fc; }
    .stAlert { border-radius: 12px; }
    .metric-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; }
    .stButton>button { border-radius: 50px; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); color: white; border: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA TECNICA ---
def extract_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_data(v_id):
    try:
        t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['it', 'en'])
        return " ".join([t['text'] for t in t_list])
    except: return None

# --- UI ---
st.title("🚀 CleanScript AI 4.0 Ultra")
st.markdown("##### Il coltellino svizzero per Content Creator, Studenti e Marketers.")

with st.container():
    col_url, col_btn = st.columns([3, 1])
    with col_url:
        url = st.text_input("", placeholder="Incolla URL YouTube qui per la magia...", label_visibility="collapsed")
    with col_btn:
        process = st.button("ANALIZZA ORA ⚡")

if process and url:
    v_id = extract_id(url)
    if v_id:
        with st.spinner('Analisi profonda in corso...'):
            raw_text = get_data(v_id)
            if raw_text:
                # Analisi Sentiment
                blob = TextBlob(raw_text)
                sentiment = "Positivo 😊" if blob.sentiment.polarity > 0.1 else "Negativo 😟" if blob.sentiment.polarity < -0.1 else "Neutrale 😐"
                
                # Analisi Keyword
                r = Rake()
                r.extract_keywords_from_text(raw_text)
                keywords = r.get_ranked_phrases()[:8]
                
                # Statistiche
                words = len(raw_text.split())
                time_saved = max(1, round(words / 150)) # stima minuti risparmiati
                
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
                    st.subheader("📝 Testo Pulito")
                    final_txt = st.text_area("", raw_text, height=400, label_visibility="collapsed")
                    st.download_button("📥 Scarica Report .txt", final_txt)
                
                with c2:
                    st.subheader("🏷️ Social & SEO")
                    st.write("**Top Keywords:**")
                    for kw in keywords:
                        st.code(kw)
                    
                    st.divider()
                    st.write("**Hashtags Generati:**")
                    tags = " ".join([f"#{w.replace(' ', '')}" for w in keywords[:5]])
                    st.info(tags)
                    
                    st.divider()
                    st.button("☕ Offrimi un caffè per sbloccare l'export PDF")
            else:
                st.error("Sottotitoli non trovati per questo video.")
    else:
        st.error("URL non valido.")

# Footer Esteso (Migliora la percezione di qualità)
st.markdown("---")
f1, f2, f3 = st.columns(3)
with f1: st.caption("🛡️ **Privacy Focus**: Nessun dato salvato.")
with f2: st.caption("⚡ **Speed**: Elaborazione in < 3 secondi.")
with f3: st.caption("📈 **SEO Ready**: Ottimizzato per blog e social.")
