import streamlit as st
import re
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

# --- CSS FLUIDO ---
st.markdown("""
    <style>
    .metric-card { background-color: var(--secondary-background-color); padding: 20px; border-radius: 12px; border: 1px solid rgba(128, 128, 128, 0.2); text-align: center; }
    .metric-title { font-size: 0.9rem; color: var(--text-color); opacity: 0.7; text-transform: uppercase; letter-spacing: 1px;}
    .metric-value { font-size: 1.8rem; font-weight: 800; color: var(--text-color); margin-top: 5px; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.2s; border: 1px solid var(--primary-color); width: 100%; }
    .stButton>button:hover { border-color: var(--primary-color); color: var(--primary-color); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 10px 20px; }
    .step-box { background: rgba(37, 99, 235, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #2563eb; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

if 'raw_text' not in st.session_state: st.session_state['raw_text'] = ""
if 'processed_text' not in st.session_state: st.session_state['processed_text'] = ""

# --- SIDEBAR: STRUMENTI AVANZATI ---
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
    words_to_remove = st.text_input("Da rimuovere (separate da virgola):", placeholder="ehm, cioè, allora")
    if st.button("Pulisci Parole") and st.session_state['processed_text']:
        text_temp = st.session_state['processed_text']
        for w in [x.strip() for x in words_to_remove.split(',') if x.strip()]:
            text_temp = re.sub(rf'\b{w}\b', '', text_temp, flags=re.IGNORECASE)
        st.session_state['processed_text'] = " ".join(text_temp.split())
        st.success("Pulizia completata!")
        
    st.subheader("Casing")
    col_c1, col_c2, col_c3 = st.columns(3)
    if col_c1.button("ABC") and st.session_state['processed_text']: st.session_state['processed_text'] = st.session_state['processed_text'].upper()
    if col_c2.button("abc") and st.session_state['processed_text']: st.session_state['processed_text'] = st.session_state['processed_text'].lower()
    if col_c3.button("Abc") and st.session_state['processed_text']: st.session_state['processed_text'] = st.session_state['processed_text'].title()

    st.divider()
    st.markdown("[☕ Supporta il server](https://paypal.me/tuolink)")

# --- UI PRINCIPALE ---
st.title("⚡ CleanScript AI Studio")
st.markdown("Importa, analizza e trasforma i tuoi contenuti in modo impeccabile.")

tab_yt, tab_file, tab_manual = st.tabs(["🎥 Trascrizione YouTube", "📁 Carica Documento", "✍️ Testo Libero"])

with tab_yt:
    st.markdown("""
    <div class="step-box">
        <b>Come aggirare i blocchi di YouTube:</b><br>
        1. Vai sul video YouTube da PC e clicca su <b>"... Altro"</b> (sotto il titolo).<br>
        2. Clicca su <b>"Mostra Trascrizione"</b>.<br>
        3. Fai Copia/Incolla di tutto il testo qui sotto. Il nostro motore pulirà i numeri e i timestamp automaticamente!
    </div>
    """, unsafe_allow_html=True)
    m_txt_yt = st.text_area("Incolla qui la trascrizione sporca di YouTube:", height=200, key="yt_input")
    if st.button("PULISCI E ANALIZZA YOUTUBE", use_container_width=True):
        st.session_state['raw_text'] = m_txt_yt
        st.session_state['processed_text'] = m_txt_yt

with tab_file:
    up_file = st.file_uploader("Formati supportati: PDF, DOCX, TXT", type=['pdf', 'docx', 'txt'])
    if up_file and st.button("ELABORA FILE", use_container_width=True):
        with st.spinner('Lettura in corso...'):
            if up_file.type == "application/pdf": st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
            elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
            else: st.session_state['raw_text'] = up_file.read().decode("utf-8")
            st.session_state['processed_text'] = st.session_state['raw_text']

with tab_manual:
    m_txt = st.text_area("Incolla qui appunti, meeting Zoom o testi grezzi:", height=200, key="manual_input")
    if st.button("ACQUISISCI TESTO", use_container_width=True):
        st.session_state['raw_text'] = m_txt
        st.session_state['processed_text'] = m_txt

# --- MOTORE DI ANALISI E OUTPUT ---
if st.session_state['processed_text']:
    st.divider()
    
    current_text = st.session_state['processed_text']
    # Super-Pulizia Timestamp (rimuove 00:00, [00:00], 00:00:00)
    current_text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', current_text)
    current_text = re.sub(r'^\d{1,2}:\d{2}\s', '', current_text, flags=re.MULTILINE)
    current_text = " ".join(current_text.split())
    st.session_state['processed_text'] = current_text

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        target_lang = st.selectbox("🌍 Traduci Output:", ["Originale", "Italiano", "English", "Spanish", "French", "German"])
        if target_lang != "Originale":
            with st.spinner("Traduzione in corso..."):
                try:
                    chunks = [current_text[i:i+4500] for i in range(0, len(current_text), 4500)]
                    translated_chunks = [GoogleTranslator(source='auto', target=target_lang.lower()).translate(chunk) for chunk in chunks]
                    current_text = " ".join(translated_chunks)
                    st.session_state['processed_text'] = current_text
                except Exception as e: st.error(f"Errore: {e}")

    with col_f2:
        format_style = st.selectbox("📝 Stile Generazione:", ["Testo Pulito (Nessuna formattazione)", "Appunti puntati", "Struttura Blog SEO", "Post Social (LinkedIn/X)"])

    display_text = current_text
    if format_style == "Appunti puntati": display_text = "\n".join([f"- {s.strip()}" for s in current_text.split('. ') if len(s) > 5])
    elif format_style == "Struttura Blog SEO": display_text = f"# Titolo Articolo\n\n## Introduzione\n{current_text[:400]}...\n\n## Sviluppo Principale\n{current_text[400:]}"
    elif format_style == "Post Social (LinkedIn/X)": display_text = f"🚀 NUOVO INSIGHT\n\n{current_text[:300]}...\n\n👇 Scopri i dettagli.\n#content #ai #productivity"

    words = len(display_text.split())
    try:
        sentiment_score = TextBlob(current_text).sentiment.polarity
        mood = "Positivo 😊" if sentiment_score > 0.1 else "Neutrale 😐" if sentiment_score > -0.1 else "Negativo 😟"
    except: mood = "N/D"
    
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="metric-title">Parole</div><div class="metric-value">{words}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-title">Tempo Lettura</div><div class="metric-value">{max(1, words//200)}m</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-title">Mood</div><div class="metric-value">{mood}</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="metric-title">Caratteri</div><div class="metric-value">{len(display_text)}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    out_col, info_col = st.columns([2, 1])
    
    with out_col:
        st.subheader("Risultato Finale")
        st.text_area("", display_text, height=400, label_visibility="collapsed")
        
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        btn_c1.download_button("📥 Scarica .txt", display_text, file_name="cleanscript.txt")
        btn_c2.download_button("📝 Scarica .md", display_text, file_name="cleanscript.md")
        if btn_c3.button("📋 Info Copia"): st.info("Clicca nel testo, premi Ctrl+A e Ctrl+C per copiare.")

    with info_col:
        st.subheader("Intelligenza SEO")
        try:
            r = Rake()
            r.extract_keywords_from_text(current_text)
            kw = r.get_ranked_phrases()[:6]
            st.write("**Parole chiave:**")
            for k in kw: st.code(k)
            st.divider()
            tags = " ".join([f"#{w.replace(' ', '')}" for w in kw[:4]])
            st.info(f"**Hashtags:**\n{tags}")
        except: st.write("Dati insufficienti.")

st.markdown("---")
st.caption("© 2026 CleanScript AI Studio | Elaborazione sicura e locale")
