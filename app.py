import streamlit as st
import re
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi
import tempfile
import os
import time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CleanScript AI | Multimodal", page_icon="🖋️", layout="wide")

# --- CSS MINIMALISTA (Stile Notion / Vercel) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] { background-color: transparent !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1000px !important; }

    .stApp { background-color: #FAFAFA !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important; }
    p, span, label, div { color: #4B5563 !important; }
    h1, h2, h3 { color: #111827 !important; font-weight: 700 !important; letter-spacing: -0.02em; }

    .clean-card {
        background: #FFFFFF !important; padding: 2.5rem; border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        border: 1px solid #E5E7EB; margin-bottom: 2rem; transition: box-shadow 0.2s ease;
    }
    .clean-card:hover { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); }

    .feature-box { text-align: center; padding: 2rem 1.5rem; background: #FFFFFF; border-radius: 12px; border: 1px solid #F3F4F6; }
    .feature-icon { font-size: 2rem; margin-bottom: 1rem; color: #111827; }
    .feature-title { font-weight: 600; color: #111827; margin-bottom: 0.5rem; font-size: 1.1rem; }
    .feature-desc { font-size: 0.9rem; color: #6B7280; line-height: 1.5; }

    .stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div>div {
        background-color: #F9FAFB !important; border: 1px solid #D1D5DB !important;
        border-radius: 8px !important; padding: 0.75rem 1rem !important; color: #111827 !important; transition: all 0.2s;
    }
    .stTextArea textarea:focus, .stTextInput>div>div>input:focus {
        background-color: #FFFFFF !important; border-color: #111827 !important; box-shadow: 0 0 0 1px #111827 !important;
    }

    .stButton>button {
        background-color: #111827 !important; color: #FFFFFF !important; border: 1px solid #111827 !important;
        border-radius: 8px !important; padding: 0.75rem 1.5rem !important; font-weight: 600 !important;
        transition: all 0.2s ease !important; width: 100%; font-size: 0.95rem !important;
    }
    .stButton>button:hover { background-color: #FFFFFF !important; color: #111827 !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 1rem; background: transparent; justify-content: center; margin-bottom: 1.5rem; border-bottom: 1px solid #E5E7EB; padding-bottom: 0.5rem;}
    .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; padding: 0.5rem 1rem; color: #6B7280 !important; font-weight: 500; transition: all 0.2s; }
    .stTabs [aria-selected="true"] { color: #111827 !important; border-bottom: 2px solid #111827 !important; }
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

def transcribe_audio_video_with_ai(file_path):
    """Sfrutta Gemini per ascoltare e trascrivere file multimediali"""
    try:
        # Carica il file temporaneo su Gemini
        uploaded_file = genai.upload_file(file_path)
        
        # Se è un video, Gemini ha bisogno di qualche secondo per processarlo
        while uploaded_file.state.name == 'PROCESSING':
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
            
        if uploaded_file.state.name == 'FAILED':
            return "Errore: Elaborazione del file multimediale fallita da parte dell'IA."
        
        # Prompt diretto per la trascrizione fedele
        prompt = "Sei un trascrittore esperto. Ascolta/Guarda questo file e scrivi l'esatta trascrizione parola per parola in lingua originale. Non riassumere. Se non c'è voce, scrivi 'Nessun parlato rilevato'."
        response = model.generate_content([uploaded_file, prompt])
        
        # Cancella il file dai server di Google per privacy
        genai.delete_file(uploaded_file.name)
        
        return response.text
    except Exception as e:
        return f"Errore durante la trascrizione IA: {str(e)}"

def process_with_ai(text, mode, language):
    if not text.strip(): return "Errore: Testo vuoto."
    prompts = {
        "Pulizia Rigorosa": "Sei un editor. Pulisci il testo da errori, tic verbali e timestamp. Mantieni il significato esatto. Formatta con cura in paragrafi.",
        "Riassunto TL;DR": "Sei un analista. Crea un riassunto diretto: 1 paragrafo introduttivo e una lista puntata dei concetti chiave.",
        "Articolo Blog SEO": "Sei un Copywriter. Trasforma questa trascrizione in un articolo strutturato (Titolo H1, introduzione, paragrafi con H2).",
        "Post LinkedIn/X": "Sei un Social Media Manager. Crea un post professionale estraendo il concetto migliore. Usa un hook, paragrafi brevi e hashtag pertinenti.",
        "Meeting (Action Items)": "Analizza questa trascrizione e crea: 1. Argomenti discussi. 2. Decisioni prese. 3. Action Items chiari."
    }
    prompt_base = prompts.get(mode, prompts["Pulizia Rigorosa"])
    full_prompt = f"{prompt_base}\n\nREGOLE: Scrivi la risposta finale ESCLUSIVAMENTE in lingua {language}.\n\nTESTO:\n{text}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Errore nell'elaborazione IA: {str(e)}"

if 'raw_text' not in st.session_state: st.session_state['raw_text'] = ""
if 'ai_result' not in st.session_state: st.session_state['ai_result'] = ""

# --- STRUTTURA A COLONNE ---
spacer_left, main_col, spacer_right = st.columns([1, 8, 1])

with main_col:
    # --- HERO SECTION ---
    st.markdown("""
        <div style="text-align: center; padding: 2.5rem 0 3.5rem 0;">
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; color: #111827;'>CleanScript AI</h1>
            <p style='font-size: 1.1rem; color: #6B7280; max-width: 600px; margin: 0 auto;'>
                L'editor intelligente per testi, audio e video.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if not ai_ready:
        st.error("⚠️ Chiave API Gemini non trovata nei Secrets di Streamlit.")

    # --- EMPTY STATE ---
    if not st.session_state['raw_text']:
        f1, f2, f3 = st.columns(3)
        with f1: st.markdown('<div class="feature-box"><div class="feature-icon">▶️</div><div class="feature-title">Estrai da YouTube</div><div class="feature-desc">Incolla un link per la trascrizione.</div></div>', unsafe_allow_html=True)
        with f2: st.markdown('<div class="feature-box"><div class="feature-icon">🎙️</div><div class="feature-title">Trascrivi Audio/Video</div><div class="feature-desc">Carica MP3 o MP4 per la trascrizione IA.</div></div>', unsafe_allow_html=True)
        with f3: st.markdown('<div class="feature-box"><div class="feature-icon">🧠</div><div class="feature-title">Motore IA</div><div class="feature-desc">Formatta, traduci e riassumi in secondi.</div></div>', unsafe_allow_html=True)
        st.write("")

    # --- AREA INPUT ---
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    
    tab_yt, tab_file, tab_manual = st.tabs(["Link YouTube", "Carica File (Testo/Audio/Video)", "Incolla Testo"])

    with tab_yt:
        col_url, col_btn = st.columns([3, 1])
        url = col_url.text_input("", placeholder="https://youtube.com/watch?v=...", label_visibility="collapsed")
        if col_btn.button("Estrai Testo"):
            if url:
                v_id = extract_id(url)
                if v_id:
                    with st.spinner('Estrazione in corso...'):
                        testo, successo = get_yt_data(v_id)
                        if successo:
                            st.session_state['raw_text'] = testo
                            st.rerun()
                        else:
                            st.error("⚠️ YouTube ha bloccato questo video. Copia la trascrizione e usa 'Incolla Testo'.")
                else: st.error("Link non valido.")

    with tab_file:
        # Aggiunti formati multimediali
        up_file = st.file_uploader("Trascina qui PDF, DOCX, TXT, MP3, WAV, M4A o MP4", type=['pdf', 'docx', 'txt', 'mp3', 'wav', 'm4a', 'mp4'], label_visibility="collapsed")
        if up_file and st.button("Elabora Documento / Media"):
            file_type = up_file.type
            
            with st.spinner("Analisi del file in corso (per audio/video potrebbe volerci un minuto)..."):
                # --- GESTIONE FILE TESTUALI ---
                if file_type == "application/pdf": 
                    st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
                elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": 
                    st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
                elif file_type.startswith("text/"): 
                    st.session_state['raw_text'] = up_file.read().decode("utf-8")
                    
                # --- GESTIONE FILE AUDIO/VIDEO TRAMITE GEMINI ---
                elif file_type.startswith("audio/") or file_type.startswith("video/"):
                    if ai_ready:
                        # 1. Salva il file temporaneamente sul server
                        temp_ext = "." + up_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=temp_ext) as tmp_file:
                            tmp_file.write(up_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # 2. Invia all'IA per la trascrizione
                        transcription_result = transcribe_audio_video_with_ai(tmp_path)
                        st.session_state['raw_text'] = transcription_result
                        
                        # 3. Elimina il file temporaneo dal server per pulizia
                        os.remove(tmp_path)
                    else:
                        st.error("⚠️ La trascrizione audio/video richiede che la chiave API Gemini sia configurata correttamente.")
                        
                st.rerun()

    with tab_manual:
        m_txt = st.text_area("", placeholder="Incolla qui la tua trascrizione o i tuoi appunti...", height=120, label_visibility="collapsed")
        if st.button("Acquisisci Testo"): 
            st.session_state['raw_text'] = m_txt
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # --- AREA MOTORE IA ---
    if st.session_state['raw_text'] and ai_ready:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; font-size: 1.25rem;'>Configurazione Output</h3>", unsafe_allow_html=True)
        
        # Mostra in anteprima i primi 200 caratteri di ciò che è stato estratto/trascritto
        with st.expander("👀 Mostra il testo grezzo estratto/trascritto"):
            st.write(st.session_state['raw_text'])

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            ai_mode = st.selectbox("Formato desiderato:", ["Pulizia Rigorosa", "Riassunto TL;DR", "Articolo Blog SEO", "Post LinkedIn/X", "Meeting (Action Items)"], label_visibility="collapsed")
        with c2:
            ai_lang = st.selectbox("Lingua:", ["Italiano", "English", "Español", "Français"], label_visibility="collapsed")
        with c3:
            if st.button("Genera", use_container_width=True):
                with st.spinner("Elaborazione IA in corso..."):
                    clean_raw = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', st.session_state['raw_text'])
                    st.session_state['ai_result'] = process_with_ai(clean_raw, ai_mode, ai_lang)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- OUTPUT FINALE ---
    if st.session_state['ai_result']:
        st.markdown('<div class="clean-card" style="border-top: 4px solid #111827;">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1rem; font-size: 1.25rem;'>Risultato</h3>", unsafe_allow_html=True)
        
        st.text_area("", st.session_state['ai_result'], height=350, label_visibility="collapsed")
        
        col_btn1, col_btn2, col_space = st.columns([1, 1, 3])
        with col_btn1:
            st.download_button("Scarica .txt", st.session_state['ai_result'], file_name="cleanscript_ai.txt")
        with col_btn2:
            if st.button("Svuota tutto"):
                st.session_state['raw_text'] = ""
                st.session_state['ai_result'] = ""
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; margin-top: 2rem;'><a href='https://paypal.me/tuolink' style='color: #6B7280; text-decoration: none; font-size: 0.9rem;'>Se questo tool ti è utile, offrimi un caffè ☕</a></div>", unsafe_allow_html=True)
