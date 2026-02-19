import streamlit as st
import re
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi
import tempfile
import os
import time
import requests
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="CleanScript AI | Universal", page_icon="🌐", layout="wide")

# --- CSS MINIMALISTA ---
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
# --- SETUP INTELLIGENZA ARTIFICIALE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # 1. Chiediamo a Google quali modelli sono disponibili per questa chiave
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 2. Scegliamo dinamicamente il migliore in ordine di potenza/velocità
    if 'models/gemini-1.5-flash' in available_models:
        best_model = 'gemini-1.5-flash'
    elif 'models/gemini-1.5-pro' in available_models:
        best_model = 'gemini-1.5-pro'
    elif 'models/gemini-pro' in available_models: # Versione ultra-stabile precedente
        best_model = 'gemini-pro'
    else:
        # Piano di emergenza assoluto: prende il primo modello testuale che trova
        best_model = available_models[0].replace('models/', '')
        
    model = genai.GenerativeModel(best_model)
    ai_ready = True
except Exception as e:
    ai_ready = False
    st.error(f"Errore di configurazione API: {e}")

# --- FUNZIONI DI ESTRAZIONE ---
def extract_yt_id(url):
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

def get_webpage_text(url):
    """Estrae il testo leggibile da un qualsiasi sito web/blog/articolo"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.extract()
            
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text, True
    except Exception as e:
        return f"Errore durante la lettura del sito web: {str(e)}", False

def transcribe_audio_video_with_ai(file_path):
    try:
        uploaded_file = genai.upload_file(file_path)
        while uploaded_file.state.name == 'PROCESSING':
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
        if uploaded_file.state.name == 'FAILED': return "Errore IA nell'elaborazione multimediale."
        
        prompt = "Trascrivi esattamente questo file audio/video parola per parola."
        response = model.generate_content([uploaded_file, prompt])
        genai.delete_file(uploaded_file.name)
        return response.text
    except Exception as e: return str(e)

def process_with_ai(text, mode, language):
    if not text.strip(): return "Errore: Testo vuoto."
    prompts = {
        "Pulizia Rigorosa": "Sei un editor. Rimuovi errori e formatta con cura in paragrafi leggibili.",
        "Riassunto TL;DR": "Sei un analista. Crea un riassunto: 1 paragrafo introduttivo e una lista dei concetti chiave.",
        "Articolo Blog SEO": "Sei un Copywriter. Trasforma questo contenuto in un articolo (Titolo H1, intro, paragrafi con H2).",
        "Post LinkedIn/X": "Crea un post professionale estraendo il concetto migliore. Usa un hook e hashtag pertinenti.",
        "Meeting (Action Items)": "Analizza e crea: 1. Argomenti. 2. Decisioni. 3. Action Items."
    }
    prompt_base = prompts.get(mode, prompts["Pulizia Rigorosa"])
    full_prompt = f"{prompt_base}\n\nREGOLE: Scrivi ESCLUSIVAMENTE in lingua {language}.\n\nTESTO:\n{text}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e: return f"Errore IA: {str(e)}"

# --- STATO SESSIONE ---
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
                Estrai contenuti da Link, Video, Audio o Documenti e trasformali con l'IA.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if not ai_ready: st.error("⚠️ Chiave API Gemini non trovata nei Secrets di Streamlit.")

    if not st.session_state['raw_text']:
        f1, f2, f3 = st.columns(3)
        with f1: st.markdown('<div class="feature-box"><div class="feature-icon">🌐</div><div class="feature-title">Estrai dal Web</div><div class="feature-desc">Incolla link di articoli, blog o video.</div></div>', unsafe_allow_html=True)
        with f2: st.markdown('<div class="feature-box"><div class="feature-icon">🎙️</div><div class="feature-title">Trascrivi Media</div><div class="feature-desc">Carica MP3, MP4, PDF o Word.</div></div>', unsafe_allow_html=True)
        with f3: st.markdown('<div class="feature-box"><div class="feature-icon">🧠</div><div class="feature-title">Motore IA</div><div class="feature-desc">Formatta, traduci e riassumi in secondi.</div></div>', unsafe_allow_html=True)
        st.write("")

    # --- AREA INPUT ---
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    
    # Testi dei tab resi universali
    tab_link, tab_file, tab_manual = st.tabs(["🌐 Inserisci Link", "📁 Carica File (Media/Testo)", "✍️ Incolla Testo"])

    with tab_link:
        col_url, col_btn = st.columns([3, 1])
        # Placeholder reso universale
        url = col_url.text_input("", placeholder="Incolla qui qualsiasi link (Sito web, Articolo, Video)...", label_visibility="collapsed")
        if col_btn.button("Estrai Contenuto"):
            if url:
                with st.spinner('Connessione al link in corso...'):
                    # Controllo intelligente: È un video YouTube o un normale sito web?
                    yt_id = extract_yt_id(url)
                    
                    if yt_id:
                        # È YouTube
                        testo, successo = get_yt_data(yt_id)
                        if successo:
                            st.session_state['raw_text'] = testo
                            st.rerun()
                        else:
                            st.error("⚠️ Piattaforma video protetta. Copia il testo manualmente e usa 'Incolla Testo'.")
                    else:
                        # È un sito generico (articolo, blog, news)
                        testo, successo = get_webpage_text(url)
                        if successo and len(testo) > 50:
                            st.session_state['raw_text'] = testo
                            st.rerun()
                        else:
                            st.error("⚠️ Impossibile estrarre testo da questa pagina. Potrebbe essere protetta o vuota.")
            else: st.error("Inserisci un link valido.")

    with tab_file:
        up_file = st.file_uploader("Trascina qui PDF, DOCX, TXT, MP3, WAV, M4A o MP4", type=['pdf', 'docx', 'txt', 'mp3', 'wav', 'm4a', 'mp4'], label_visibility="collapsed")
        if up_file and st.button("Elabora Documento / Media"):
            file_type = up_file.type
            with st.spinner("Analisi in corso (per audio/video potrebbe volerci un minuto)..."):
                if file_type == "application/pdf": st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
                elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
                elif file_type.startswith("text/"): st.session_state['raw_text'] = up_file.read().decode("utf-8")
                elif file_type.startswith("audio/") or file_type.startswith("video/"):
                    if ai_ready:
                        temp_ext = "." + up_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=temp_ext) as tmp_file:
                            tmp_file.write(up_file.getvalue())
                            tmp_path = tmp_file.name
                        transcription_result = transcribe_audio_video_with_ai(tmp_path)
                        st.session_state['raw_text'] = transcription_result
                        os.remove(tmp_path)
                    else: st.error("⚠️ La chiave API Gemini è necessaria per i file multimediali.")
                st.rerun()

    with tab_manual:
        m_txt = st.text_area("", placeholder="Incolla qui la tua trascrizione, codice o appunti liberi...", height=120, label_visibility="collapsed")
        if st.button("Acquisisci Testo"): 
            st.session_state['raw_text'] = m_txt
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # --- AREA MOTORE IA ---
    if st.session_state['raw_text'] and ai_ready:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 1.5rem; font-size: 1.25rem;'>Configurazione Output</h3>", unsafe_allow_html=True)
        
        with st.expander("👀 Mostra il testo grezzo estratto/trascritto"): st.write(st.session_state['raw_text'])

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: ai_mode = st.selectbox("Formato desiderato:", ["Pulizia Rigorosa", "Riassunto TL;DR", "Articolo Blog SEO", "Post LinkedIn/X", "Meeting (Action Items)"], label_visibility="collapsed")
        with c2: ai_lang = st.selectbox("Lingua:", ["Italiano", "English", "Español", "Français"], label_visibility="collapsed")
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
        with col_btn1: st.download_button("Scarica .txt", st.session_state['ai_result'], file_name="cleanscript_ai.txt")
        with col_btn2:
            if st.button("Svuota tutto"):
                st.session_state['raw_text'] = ""
                st.session_state['ai_result'] = ""
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-top: 2rem;'><a href='https://paypal.me/tuolink' style='color: #6B7280; text-decoration: none; font-size: 0.9rem;'>Se questo tool ti è utile, offrimi un caffè ☕</a></div>", unsafe_allow_html=True)
