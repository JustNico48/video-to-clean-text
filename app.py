import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textblob import TextBlob
from rake_nltk import Rake
import nltk
from PyPDF2 import PdfReader
from docx import Document
from deep_translator import GoogleTranslator

# --- SETUP RISORSE ---
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt_tab', quiet=True)
    except: pass

download_nltk_data()

st.set_page_config(page_title="CleanScript AI | Ultimate Studio", page_icon="⚡", layout="wide")

# --- CSS FLUIDO (Si adatta a Light/Dark Mode automaticamente) ---
st.markdown("""
    <style>
    .metric-card { 
        background-color: var(--secondary-background-color); 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        text-align: center; 
    }
    .metric-title { font-size: 0.9rem; color: var(--text-color); opacity: 0.7; text-transform: uppercase; letter-spacing: 1px;}
    .metric-value { font-size: 1.8rem; font-weight: 800; color: var(--text-color); margin-top: 5px; }
    .stButton>button { 
        border-radius: 8px; 
        font-weight: 600; 
        transition: all 0.2s; 
        border: 1px solid var(--primary-color);
        width: 100%;
    }
    .stButton>button:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE MEMORIA (Session State) ---
if 'raw_text' not in st.session_state:
    st.session_state['raw_text'] = ""
if 'processed_text' not in st.session_state:
    st.session_state['processed_text'] = ""

# --- FUNZIONI UTILI E DI ESTRAZIONE ---
def extract_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_yt_data(v_id):
    try:
        # Tentativo 1: Prova a forzare i sottotitoli in italiano o inglese
        t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['it', 'en'])
        return " ".join([t['text'] for t in t_list]), None
    except Exception as e1:
        try:
            # Tentativo 2: Se fallisce, scarica QUALSIASI trascrizione di default (senza specificare la lingua)
            t_list = YouTubeTranscriptApi.get_transcript(v_id)
            return " ".join([t['text'] for t in t_list]), None
        except Exception as e2:
            # Se fallisce anche questo, cattura l'errore finale
            return None, str(e2)

# --- SIDEBAR: STRUMENTI DI TESTO AVANZATI ---
with st.sidebar:
    st.title("🛠️ Strumenti Avanzati")
    st.info("Questi filtri si applicano al testo elaborato.")
    
    st.subheader("Trova & Sostituisci")
    find_word = st.text_input("Parola da trovare:")
    replace_word = st.text_input("Sostituisci con:")
    if st.button("Applica Sostituzione") and st.session_state['processed_text']:
        st.session_state['processed_text'] = st.session_state['processed_text'].replace(find_word, replace_word)
        st.success("Sostituito!")

    st.subheader("Filtro Parole")
    words_to_remove = st.text_input("Parole da rimuovere (separate da virgola):", placeholder="ehm, cioè, allora")
    if st.button("Pulisci Parole") and st.session_state['processed_text']:
        text_temp = st.session_state['processed_text']
        for w in [x.strip() for x in words_to_remove.split(',') if x.strip()]:
            text_temp = re.sub(rf'\b{w}\b', '', text_temp, flags=re.IGNORECASE)
        st.session_state['processed_text'] = " ".join(text_temp.split())
        st.success("Pulizia completata!")
        
    st.subheader("Casing")
    col_c1, col_c2, col_c3 = st.columns(3)
    if col_c1.button("ABC") and st.session_state['processed_text']:
        st.session_state['processed_text'] = st.session_state['processed_text'].upper()
    if col_c2.button("abc") and st.session_state['processed_text']:
        st.session_state['processed_text'] = st.session_state['processed_text'].lower()
    if col_c3.button("Abc") and st.session_state['processed_text']:
        st.session_state['processed_text'] = st.session_state['processed_text'].title()

    st.divider()
    st.markdown("[☕ Supporta il server](https://paypal.me/tuolink)")

# --- UI PRINCIPALE ---
st.title("⚡ CleanScript AI Studio")
st.markdown("Importa, analizza e trasforma i tuoi contenuti in modo impeccabile.")

# Layout Input (Tab)
tab_yt, tab_file, tab_manual = st.tabs(["🎥 Estrai da YouTube", "📁 Carica Documento", "✍️ Incolla Testo"])

with tab_yt:
    c1, c2 = st.columns([4, 1])
    url = c1.text_input("Link YouTube:", placeholder="https://youtube.com/watch?v=...", label_visibility="collapsed")
    if c2.button("ESTRAI", use_container_width=True):
        v_id = extract_id(url)
        if v_id:
            with st.spinner('Tentativo di estrazione da YouTube in corso...'):
                res, error_msg = get_yt_data(v_id)
                if res: 
                    st.session_state['raw_text'] = res
                    st.session_state['processed_text'] = res
                    st.success("Estratto con successo!")
                else: 
                    st.error("YouTube ha bloccato l'estrazione per questo video o i sottotitoli non esistono.")
                    st.warning(f"Dettaglio Tecnico: {error_msg}")
                    st.info("💡 Usa il tab '✍️ Incolla Testo': vai su YouTube, clicca su 'Mostra Trascrizione', copia tutto e incollalo manualmente!")
        else: st.error("URL non valido.")

with tab_file:
    up_file = st.file_uploader("Formati supportati: PDF, DOCX, TXT", type=['pdf', 'docx', 'txt'])
    if up_file and st.button("ELABORA FILE"):
        with st.spinner('Lettura in corso...'):
            if up_file.type == "application/pdf":
                st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
            elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
            else:
                st.session_state['raw_text'] = up_file.read().decode("utf-8")
            st.session_state['processed_text'] = st.session_state['raw_text']

with tab_manual:
    m_txt = st.text_area("Incolla qui gli appunti o la trascrizione grezza di YouTube:", height=150)
    if st.button("ACQUISISCI TESTO"):
        st.session_state['raw_text'] = m_txt
        st.session_state['processed_text'] = m_txt

# --- MOTORE DI ANALISI E OUTPUT ---
if st.session_state['processed_text']:
    st.divider()
    
    # Pulizia automatica di base (Rimuove [00:00:00] o simili)
    current_text = st.session_state['processed_text']
    current_text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', current_text)
    current_text = " ".join(current_text.split())
    st.session_state['processed_text'] = current_text

    # Formattazione & Traduzione Rapida
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        target_lang = st.selectbox("🌍 Traduci Output:", ["Originale", "Italiano", "English", "Spanish", "French", "German"])
        if target_lang != "Originale":
            with st.spinner("Traduzione in corso... (potrebbe richiedere qualche secondo)"):
                try:
                    # Dividiamo in blocchi per evitare limiti del traduttore gratuito
                    chunks = [current_text[i:i+4500] for i in range(0, len(current_text), 4500)]
                    translated_chunks = [GoogleTranslator(source='auto', target=target_lang.lower()).translate(chunk) for chunk in chunks]
                    current_text = " ".join(translated_chunks)
                    st.session_state['processed_text'] = current_text
                except Exception as e:
                    st.error(f"Errore di traduzione: {e}")

    with col_f2:
        format_style = st.selectbox("📝 Stile Generazione:", ["Testo Pulito (Nessuna formattazione)", "Appunti puntati", "Struttura Blog SEO", "Post Social (LinkedIn/X)"])

    # Applica lo stile
    display_text = current_text
    if format_style == "Appunti puntati":
        display_text = "\n".join([f"- {sentence.strip()}" for sentence in current_text.split('. ') if len(sentence) > 5])
    elif format_style == "Struttura Blog SEO":
        display_text = f"# Titolo Articolo\n\n## Introduzione\n{current_text[:400]}...\n\n## Sviluppo Principale\n{current_text[400:]}"
    elif format_style == "Post Social (LinkedIn/X)":
        display_text = f"🚀 NUOVO INSIGHT\n\n{current_text[:300]}...\n\n👇 Scopri i dettagli qui sotto.\n#content #ai #productivity"

    # Calcolo Metriche
    words = len(display_text.split())
    try:
        sentiment_score = TextBlob(current_text).sentiment.polarity
        mood = "Positivo 😊" if sentiment_score > 0.1 else "Neutrale 😐" if sentiment_score > -0.1 else "Negativo 😟"
    except: mood = "N/D"
    
    # Dashboard Metriche
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="metric-title">Parole</div><div class="metric-value">{words}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-title">Tempo Lettura</div><div class="metric-value">{max(1, words//200)}m</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-title">Mood</div><div class="metric-value">{mood}</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="metric-title">Caratteri</div><div class="metric-value">{len(display_text)}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Output finale
    out_col, info_col = st.columns([2, 1])
    
    with out_col:
        st.subheader("Risultato Finale")
        st.text_area("", display_text, height=400, label_visibility="collapsed")
        
        # Bottoni di download/copia
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        btn_c1.download_button("📥 Scarica .txt", display_text, file_name="cleanscript.txt")
        btn_c2.download_button("📝 Scarica .md", display_text, file_name="cleanscript.md")
        if btn_c3.button("📋 Info Copia"):
            st.info("Per copiare, clicca dentro l'area di testo sopra, premi Ctrl+A (o Cmd+A) e poi Ctrl+C.")

    with info_col:
        st.subheader("Intelligenza SEO")
        try:
            r = Rake()
            r.extract_keywords_from_text(current_text)
            kw = r.get_ranked_phrases()[:6]
            st.write("**Parole chiave dominanti:**")
            for k in kw: st.code(k)
            st.divider()
            tags = " ".join([f"#{w.replace(' ', '')}" for w in kw[:4]])
            st.info(f"**Hashtags generati:**\n{tags}")
        except:
            st.write("Dati insufficienti per estrarre parole chiave.")

st.markdown("---")
st.caption("© 2026 CleanScript AI Studio | Elaborazione locale senza memorizzazione dati")
