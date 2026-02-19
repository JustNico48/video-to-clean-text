import streamlit as st
import re
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from youtube_transcript_api import YouTubeTranscriptApi

# --- CONFIGURAZIONE PAGINA E DESIGN ---
st.set_page_config(page_title="CleanScript AI 5.1 | God Mode", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .feature-card { background: white; padding: 25px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .stButton>button { background-color: #2563EB !important; color: white !important; border-radius: 12px; padding: 12px; font-weight: 700; border: none; transition: 0.3s; width: 100%; }
    .stButton>button:hover { background-color: #1D4ED8 !important; transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }
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
        "Pulizia e Correzione Perfetta": "Sei un editor professionista. Pulisci il testo seguente da errori grammaticali, tic verbali e timestamp. Mantieni il significato esatto. Nessuna invenzione.",
        "Riassunto Esecutivo (TL;DR)": "Sei un analista. Crea un riassunto: 1 paragrafo introduttivo e una lista dei 3-5 concetti chiave.",
        "Articolo Blog SEO": "Sei un SEO Copywriter. Trasforma questa trascrizione in un articolo di blog. Metti Titolo H1, introduzione, e paragrafi con H2.",
        "Post Social Virale (LinkedIn/X)": "Sei un Social Media Manager. Estrai il concetto più interessante e crea un post per LinkedIn/X con hook iniziale e 3 hashtag.",
        "Meeting Manager (Action Items)": "Analizza questa trascrizione e crea: 1. Argomenti discussi. 2. Decisioni prese. 3. Action Items (Cose da fare)."
    }
    prompt_base = prompts.get(mode, prompts["Pulizia e Correzione Perfetta"])
    full_prompt = f"{prompt_base}\n\nREGOLE: Scrivi ESCLUSIVAMENTE in lingua {language}.\n\nTESTO:\n{text}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Errore IA: {str(e)}"

# --- INTERFACCIA UTENTE ---
st.title("🧠 CleanScript AI 5.1")
st.markdown("<p style='color: #64748B; font-size: 1.1em;'>Inserisci un link YouTube o carica un file. L'IA farà il resto.</p>", unsafe_allow_html=True)

if 'raw_text' not in st.session_state: st.session_state['raw_text'] = ""

st.markdown('<div class="feature-card">', unsafe_allow_html=True)
tab_yt, tab_file, tab_manual = st.tabs(["🎥 Video YouTube", "📁 Documenti", "✍️ Testo"])

with tab_yt:
    url = st.text_input("Incolla il link del video YouTube:", placeholder="https://youtube.com/watch?v=...")
    if url:
        v_id = extract_id(url)
        if v_id:
            # Mostra il player video!
            st.video(url)
            
            if st.button("🚀 ESTRAI E ANALIZZA", use_container_width=True):
                with st.spinner('Tentativo di estrazione in corso...'):
                    testo, successo = get_yt_data(v_id)
                    if successo:
                        st.session_state['raw_text'] = testo
                        st.success("✅ Sottotitoli estratti con successo!")
                    else:
                        st.warning("⚠️ YouTube ha bloccato il server per questo video. Nessun problema: copia la trascrizione da YouTube e incollala qui sotto.")
                        # Fallback manuale immediato
                        fallback_txt = st.text_area("Incolla qui la trascrizione:", height=150)
                        if st.button("PROCEDI CON QUESTO TESTO"):
                            st.session_state['raw_text'] = fallback_txt
        else:
            st.error("Link non valido.")

with tab_file:
    up_file = st.file_uploader("Formati supportati: PDF, DOCX, TXT", type=['pdf', 'docx', 'txt'])
    if up_file and st.button("LEGGI FILE"):
        with st.spinner('Lettura...'):
            if up_file.type == "application/pdf": st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
            elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
            else: st.session_state['raw_text'] = up_file.read().decode("utf-8")

with tab_manual:
    m_txt = st.text_area("Incolla appunti o testi grezzi:", height=150)
    if st.button("CARICA TESTO"): st.session_state['raw_text'] = m_txt

st.markdown('</div>', unsafe_allow_html=True)

# --- PANNELLO IA ---
if st.session_state['raw_text'] and ai_ready:
    st.markdown("---")
    st.subheader("⚙️ Dai un ordine all'Intelligenza Artificiale")
    
    col_settings, col_action = st.columns([2, 1])
    with col_settings:
        c1, c2 = st.columns(2)
        ai_mode = c1.selectbox("🧠 Potere dell'IA:", ["Pulizia e Correzione Perfetta", "Riassunto Esecutivo (TL;DR)", "Articolo Blog SEO", "Post Social Virale (LinkedIn/X)", "Meeting Manager (Action Items)"])
        ai_lang = c2.selectbox("🌍 Lingua Output:", ["Italiano", "English", "Español", "Français", "Deutsch"])
        
    with col_action:
        st.write(""); st.write("")
        if st.button("✨ GENERA MAGIA", use_container_width=True):
            with st.spinner(f"Sto pensando..."):
                clean_raw = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', st.session_state['raw_text'])
                st.session_state['ai_result'] = process_with_ai(clean_raw, ai_mode, ai_lang)

# --- RISULTATO ---
if 'ai_result' in st.session_state:
    st.markdown("---")
    res_col, side_col = st.columns([3, 1])
    with res_col:
        st.subheader("🎯 Risultato")
        st.text_area("", st.session_state['ai_result'], height=450, label_visibility="collapsed")
        st.download_button("📥 Scarica .txt", st.session_state['ai_result'], file_name="cleanscript_ai.txt")
    with side_col:
        st.markdown("### 💎 Supporta")
        st.write("Hai appena risparmiato ore di lavoro.")
        st.markdown("[☕ **Offrimi un caffè**](https://paypal.me/tuolink)")
