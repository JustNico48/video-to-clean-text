import streamlit as st
import re
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CleanScript AI | Premium", page_icon="✨", layout="wide")

# --- CSS PREMIUM (Forza un tema moderno, elegante e leggibile) ---
st.markdown("""
    <style>
    /* Sfondo generale dell'app */
    .stApp {
        background-color: #f8fafc !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* Forza il colore del testo principale per evitare conflitti con la Dark Mode */
    .stApp p, .stApp div, .stApp span, .stApp label {
        color: #334155 !important;
    }
    .stApp h1, .stApp h2, .stApp h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* Card eleganti (Sfondo bianco, ombra morbida, testo scuro) */
    .premium-card {
        background-color: #ffffff !important;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* Input testuali leggibili e puliti */
    .stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div>div {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 0.75rem !important;
        padding: 0.5rem 1rem !important;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02) !important;
    }
    .stTextArea textarea:focus, .stTextInput>div>div>input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Stile Bottoni Primari (Gradiente, Hover effect) */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4) !important;
        color: #ffffff !important;
    }
    
    /* Stile Bottoni Secondari (Sidebar o Download) */
    .stDownloadButton>button {
        background: #10b981 !important;
    }
    .stDownloadButton>button:hover {
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4) !important;
    }

    /* Tabs eleganti */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        color: #475569 !important;
        font-weight: 600;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important;
        color: #ffffff !important;
    }
    
    /* Alert e Info Box */
    .stAlert {
        border-radius: 0.75rem !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SETUP INTELLIGENZA ARTIFICIALE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
except Exception as e:
    st.error("⚠️ Chiave API Gemini non trovata nei Secrets di Streamlit!")
    ai_ready = False

# --- FUNZIONI DI SUPPORTO ---
def extract_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    m = re.search(pattern, url)
    return m.group(1) if m else None

def get_yt_data(v_id):
    try:
        t_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['it', 'en'])
        return " ".join([t['text'] for t in t_list]), True
    except:
        try:
            t_list = YouTubeTranscriptApi.get_transcript(v_id)
            return " ".join([t['text'] for t in t_list]), True
        except Exception as e:
            return str(e), False

def process_with_ai(text, mode, language):
    if not text.strip(): return "Errore: Testo vuoto."
    prompts = {
        "Pulizia e Correzione Perfetta": "Sei un editor professionista. Pulisci il testo seguente da errori grammaticali, tic verbali e timestamp. Mantieni il significato esatto e formatta in paragrafi leggibili.",
        "Riassunto Esecutivo (TL;DR)": "Sei un analista. Crea un riassunto strutturato: 1 paragrafo introduttivo e una lista puntata dei concetti chiave più importanti.",
        "Articolo Blog SEO": "Sei un SEO Copywriter. Trasforma questa trascrizione in un articolo di blog. Metti un Titolo H1 accattivante, un'introduzione, paragrafi con H2 e una conclusione.",
        "Post Social Virale (LinkedIn/X)": "Sei un esperto di comunicazione digitale. Estrai il concetto più interessante e crea un post per LinkedIn/X. Usa un hook iniziale potente, frasi brevi, emoji e 3 hashtag.",
        "Meeting Manager (Action Items)": "Sei un Project Manager. Analizza questa trascrizione e crea: 1. Argomenti discussi. 2. Decisioni prese. 3. Action Items chiari."
    }
    prompt_base = prompts.get(mode, prompts["Pulizia e Correzione Perfetta"])
    full_prompt = f"{prompt_base}\n\nREGOLE: Scrivi la risposta finale ESCLUSIVAMENTE in lingua {language}.\n\nTESTO:\n{text}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Errore nell'elaborazione IA: {str(e)}"

# --- STATO DELLA SESSIONE ---
if 'raw_text' not in st.session_state: st.session_state['raw_text'] = ""
if 'ai_result' not in st.session_state: st.session_state['ai_result'] = ""

# --- SIDEBAR (Strumenti Extra) ---
with st.sidebar:
    st.markdown("<h2 style='color: #6366f1 !important;'>🛠️ Tool Rapidi</h2>", unsafe_allow_html=True)
    st.info("Applica queste modifiche rapide al testo originale prima di passarlo all'IA.")
    
    st.subheader("Trova & Sostituisci")
    find_word = st.text_input("Trova parola:")
    replace_word = st.text_input("Sostituisci con:")
    if st.button("Applica"):
        if st.session_state['raw_text']:
            st.session_state['raw_text'] = st.session_state['raw_text'].replace(find_word, replace_word)
            st.success("Testo aggiornato!")
            
    st.divider()
    st.markdown("[☕ Offrimi un caffè](https://paypal.me/tuolink)")

# --- INTERFACCIA PRINCIPALE ---
st.markdown("<h1 style='text-align: center; font-size: 3rem; background: -webkit-linear-gradient(45deg, #6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>✨ CleanScript AI Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem; margin-bottom: 2rem;'>L'hub definitivo per trasformare contenuti grezzi in capolavori.</p>", unsafe_allow_html=True)

st.markdown('<div class="premium-card">', unsafe_allow_html=True)
tab_yt, tab_file, tab_manual = st.tabs(["🎥 Video YouTube", "📁 Carica Documento", "✍️ Incolla Testo"])

with tab_yt:
    c1, c2 = st.columns([3, 1])
    with c1: url = st.text_input("Link YouTube:", placeholder="https://youtube.com/watch?v=...", label_visibility="collapsed")
    with c2: btn_yt = st.button("🚀 ESTRAI VIDEO")
    
    if btn_yt and url:
        v_id = extract_id(url)
        if v_id:
            st.video(url)
            with st.spinner('Estrazione in corso...'):
                testo, successo = get_yt_data(v_id)
                if successo:
                    st.session_state['raw_text'] = testo
                    st.success("✅ Trascrizione acquisita! Scorri giù per usare l'IA.")
                else:
                    st.error("⚠️ YouTube ha bloccato l'estrazione automatica per questo video.")
                    st.info("💡 Nessun problema! Vai su YouTube, clicca su 'Mostra Trascrizione', copia il testo e usa il tab '✍️ Incolla Testo' qui a destra.")
        else:
            st.error("Link non valido.")

with tab_file:
    up_file = st.file_uploader("Formati supportati: PDF, DOCX, TXT", type=['pdf', 'docx', 'txt'])
    if up_file and st.button("📄 LEGGI DOCUMENTO"):
        with st.spinner('Lettura...'):
            if up_file.type == "application/pdf": st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
            elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
            else: st.session_state['raw_text'] = up_file.read().decode("utf-8")
            st.success("✅ Documento acquisito! Scorri giù per usare l'IA.")

with tab_manual:
    m_txt = st.text_area("Incolla qui la tua trascrizione, appunti o meeting:", height=150)
    if st.button("✍️ ACQUISISCI TESTO"): 
        st.session_state['raw_text'] = m_txt
        st.success("✅ Testo acquisito! Scorri giù per usare l'IA.")

st.markdown('</div>', unsafe_allow_html=True)

# --- MOTORE INTELLIGENZA ARTIFICIALE ---
if st.session_state['raw_text'] and ai_ready:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h2>🧠 Motore di Generazione IA</h2>", unsafe_allow_html=True)
    
    col_settings, col_action = st.columns([2, 1])
    with col_settings:
        c1, c2 = st.columns(2)
        ai_mode = c1.selectbox("🎯 Seleziona l'obiettivo:", [
            "Pulizia e Correzione Perfetta", 
            "Riassunto Esecutivo (TL;DR)", 
            "Articolo Blog SEO", 
            "Post Social Virale (LinkedIn/X)", 
            "Meeting Manager (Action Items)"
        ])
        ai_lang = c2.selectbox("🌍 Lingua di output:", ["Italiano", "English", "Español", "Français", "Deutsch"])
        
    with col_action:
        st.write("") 
        st.write("")
        if st.button("✨ GENERA CAPOLAVORO", use_container_width=True):
            with st.spinner(f"Elaborazione avanzata in corso..."):
                clean_raw = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', st.session_state['raw_text'])
                st.session_state['ai_result'] = process_with_ai(clean_raw, ai_mode, ai_lang)
    st.markdown('</div>', unsafe_allow_html=True)

# --- OUTPUT FINALE ---
if st.session_state['ai_result']:
    st.markdown('<div class="premium-card" style="border: 2px solid #6366f1;">', unsafe_allow_html=True)
    st.markdown("<h2>🏆 Il tuo risultato</h2>", unsafe_allow_html=True)
    
    st.text_area("", st.session_state['ai_result'], height=400, label_visibility="collapsed")
    
    col_d1, col_d2, col_d3 = st.columns([1, 1, 2])
    with col_d1:
        st.download_button("📥 SCARICA .TXT", st.session_state['ai_result'], file_name="cleanscript_pro.txt")
    with col_d2:
        if st.button("🗑️ CANCELLA"):
            st.session_state['raw_text'] = ""
            st.session_state['ai_result'] = ""
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
