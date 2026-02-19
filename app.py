import streamlit as st
import re
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CleanScript AI | Studio", page_icon="✨", layout="wide")

# --- CSS AESTHETIC & GLASSMORPHISM ---
st.markdown("""
    <style>
    /* Nasconde header default e menu */
    [data-testid="stHeader"] { background-color: transparent !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1200px !important; }

    /* Sfondo Mesh Gradient sottile */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.05) 0%, rgba(255, 255, 255, 1) 90%) !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* Testi */
    p, span, label, div { color: #475569 !important; }
    h1, h2, h3 { color: #0f172a !important; font-weight: 800 !important; letter-spacing: -0.5px; }

    /* Glassmorphism Card (Effetto Vetro) */
    .glass-card {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 2.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03), inset 0 1px 0 rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(226, 232, 240, 0.8);
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
    }

    /* Mini-Card per le Features (Empty State) */
    .feature-box {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 1rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
    .feature-title { font-weight: 700; color: #1e293b; margin-bottom: 0.5rem; font-size: 1.1rem; }
    .feature-desc { font-size: 0.9rem; color: #64748b; }

    /* Input ed Elementi interattivi */
    .stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div>div {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s;
    }
    .stTextArea textarea:focus, .stTextInput>div>div>input:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.15) !important;
    }

    /* Bottoni Aestethic */
    .stButton>button {
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 1rem !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        width: 100%;
        text-transform: uppercase;
        font-size: 0.9rem !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px -5px rgba(236, 72, 153, 0.4) !important;
    }

    /* Tabs ridisegnate */
    .stTabs [data-baseweb="tab-list"] { gap: 1rem; background: transparent; justify-content: center; margin-bottom: 1rem;}
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: 1px solid #e2e8f0;
        border-radius: 2rem;
        padding: 0.5rem 1.5rem;
        color: #64748b !important;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #1e293b;
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
        "Pulizia Perfetta": "Sei un editor. Pulisci il testo da errori, tic verbali e timestamp. Mantieni il significato esatto e formatta in paragrafi leggibili.",
        "Riassunto TL;DR": "Sei un analista. Crea un riassunto: 1 paragrafo introduttivo e una lista puntata dei concetti chiave.",
        "Articolo Blog SEO": "Sei un Copywriter. Trasforma questa trascrizione in un articolo di blog. Metti un Titolo H1, introduzione, paragrafi con H2 e conclusione.",
        "Post LinkedIn/X": "Sei un Social Media Manager. Estrai il concetto più interessante e crea un post per i social. Usa un hook potente, frasi brevi e 3 hashtag.",
        "Action Items (Meeting)": "Analizza questa trascrizione e crea: 1. Argomenti discussi. 2. Decisioni prese. 3. Action Items (Cose da fare)."
    }
    prompt_base = prompts.get(mode, prompts["Pulizia Perfetta"])
    full_prompt = f"{prompt_base}\n\nREGOLE: Scrivi la risposta finale ESCLUSIVAMENTE in lingua {language}.\n\nTESTO:\n{text}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Errore nell'elaborazione IA: {str(e)}"

if 'raw_text' not in st.session_state: st.session_state['raw_text'] = ""
if 'ai_result' not in st.session_state: st.session_state['ai_result'] = ""

# --- STRUTTURA A COLONNE (Per non allargare troppo lo schermo) ---
spacer_left, main_col, spacer_right = st.columns([1, 6, 1])

with main_col:
    # --- HERO SECTION (Intestazione bellissima) ---
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 3rem 0;">
            <h1 style='font-size: 3.5rem; margin-bottom: 0.5rem; background: -webkit-linear-gradient(45deg, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                CleanScript AI
            </h1>
            <p style='font-size: 1.2rem; color: #64748b; max-width: 600px; margin: 0 auto;'>
                Trasforma trascrizioni disordinate, PDF e video in contenuti perfetti, spinti dall'Intelligenza Artificiale.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if not ai_ready:
        st.error("⚠️ Chiave API Gemini non trovata nei Secrets di Streamlit!")

    # --- EMPTY STATE (Mostra le features solo se non c'è testo caricato) ---
    if not st.session_state['raw_text']:
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown('<div class="feature-box"><div class="feature-icon">🎥</div><div class="feature-title">Estrai da YouTube</div><div class="feature-desc">Incolla il link e lascia che il bot legga il video per te.</div></div>', unsafe_allow_html=True)
        with f2:
            st.markdown('<div class="feature-box"><div class="feature-icon">📄</div><div class="feature-title">Carica Documenti</div><div class="feature-desc">Analizza PDF, Word o file di testo in un istante.</div></div>', unsafe_allow_html=True)
        with f3:
            st.markdown('<div class="feature-box"><div class="feature-icon">🧠</div><div class="feature-title">Generazione IA</div><div class="feature-desc">Riassunti, Post Social e Articoli scritti da Gemini.</div></div>', unsafe_allow_html=True)
        st.write("") # Spazio

    # --- AREA INPUT (Glass Card) ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    tab_yt, tab_file, tab_manual = st.tabs(["🎥 Da YouTube", "📁 Carica File", "✍️ Incolla Testo"])

    with tab_yt:
        col_url, col_btn = st.columns([3, 1])
        url = col_url.text_input("", placeholder="Incolla il link YouTube qui...", label_visibility="collapsed")
        if col_btn.button("🚀 ESTRAI VIDEO"):
            if url:
                v_id = extract_id(url)
                if v_id:
                    with st.spinner('Estrazione in corso...'):
                        testo, successo = get_yt_data(v_id)
                        if successo:
                            st.session_state['raw_text'] = testo
                            st.rerun()
                        else:
                            st.error("⚠️ YouTube ha bloccato questo video.")
                            st.info("Vai su YouTube, clicca 'Mostra Trascrizione', copia e incolla nel tab a destra.")
                else: st.error("Link non valido.")

    with tab_file:
        up_file = st.file_uploader("Trascina qui PDF, DOCX o TXT", type=['pdf', 'docx', 'txt'], label_visibility="collapsed")
        if up_file and st.button("📄 LEGGI DOCUMENTO"):
            with st.spinner('Lettura in corso...'):
                if up_file.type == "application/pdf": st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
                elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
                else: st.session_state['raw_text'] = up_file.read().decode("utf-8")
                st.rerun()

    with tab_manual:
        m_txt = st.text_area("", placeholder="Incolla qui la tua trascrizione, appunti o meeting...", height=120, label_visibility="collapsed")
        if st.button("✍️ ACQUISISCI TESTO"): 
            st.session_state['raw_text'] = m_txt
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # --- AREA MOTORE IA (Visibile solo se c'è testo) ---
    if st.session_state['raw_text'] and ai_ready:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem;'>🧠 Configura l'IA</h3>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            ai_mode = st.selectbox("🎯 Obiettivo:", ["Pulizia Perfetta", "Riassunto TL;DR", "Articolo Blog SEO", "Post LinkedIn/X", "Action Items (Meeting)"], label_visibility="collapsed")
        with c2:
            ai_lang = st.selectbox("🌍 Lingua:", ["Italiano", "English", "Español", "Français"], label_visibility="collapsed")
        with c3:
            if st.button("✨ GENERA", use_container_width=True):
                with st.spinner("Elaborazione creativa in corso..."):
                    clean_raw = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', st.session_state['raw_text'])
                    st.session_state['ai_result'] = process_with_ai(clean_raw, ai_mode, ai_lang)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- OUTPUT FINALE ---
    if st.session_state['ai_result']:
        st.markdown('<div class="glass-card" style="border: 2px solid #a855f7;">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1rem;'>🏆 Il tuo capolavoro</h3>", unsafe_allow_html=True)
        
        st.text_area("", st.session_state['ai_result'], height=350, label_visibility="collapsed")
        
        col_btn1, col_btn2, col_space = st.columns([1, 1, 3])
        with col_btn1:
            st.download_button("📥 SCARICA .TXT", st.session_state['ai_result'], file_name="cleanscript_ai.txt")
        with col_btn2:
            if st.button("🗑️ RESET"):
                st.session_state['raw_text'] = ""
                st.session_state['ai_result'] = ""
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; margin-top: 2rem;'><a href='https://paypal.me/tuolink' style='color: #a855f7; text-decoration: none; font-weight: 600;'>☕ Il tool ti è stato utile? Offrici un caffè per supportare i server!</a></div>", unsafe_allow_html=True)
