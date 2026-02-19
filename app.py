import streamlit as st
import re
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document

# --- CONFIGURAZIONE PAGINA E DESIGN ---
st.set_page_config(page_title="CleanScript AI 5.0 | God Mode", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .feature-card { background: white; padding: 25px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .stButton>button { background-color: #2563EB !important; color: white !important; border-radius: 12px; padding: 12px; font-weight: 700; border: none; transition: 0.3s; width: 100%; }
    .stButton>button:hover { background-color: #1D4ED8 !important; transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2); }
    .stTextArea textarea { border-radius: 12px; border: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

# --- SETUP INTELLIGENZA ARTIFICIALE ---
# Controlla se hai inserito la chiave segreta
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Usiamo il modello "flash" che è ultra veloce e gratuito
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
except Exception as e:
    st.error("⚠️ Chiave API non trovata! Vai nei Secrets di Streamlit e inserisci GEMINI_API_KEY.")
    ai_ready = False

# --- LOGICA DEL MOTORE IA ---
def process_with_ai(text, mode, language):
    if not text.strip(): return "Errore: Testo vuoto."
    
    # Prompt da vero Copywriter/Analista
    prompts = {
        "Pulizia e Correzione Perfetta": "Sei un editor professionista. Pulisci il testo seguente da errori grammaticali, tic verbali, ripetizioni e timestamp. Rendi il testo fluido ma mantieni il significato esatto e il tono originale. Non inventare nulla.",
        "Riassunto Esecutivo (TL;DR)": "Sei un analista aziendale. Leggi il seguente testo e crea un riassunto esecutivo. Struttura: 1. Un paragrafo breve sul succo del discorso. 2. Una lista puntata con i 3-5 concetti chiave.",
        "Articolo Blog SEO": "Sei un SEO Copywriter esperto. Trasforma questa trascrizione in un articolo di blog accattivante. Aggiungi un Titolo forte (H1), un'introduzione gancio, dividi in paragrafi con sottotitoli (H2), e chiudi con una conclusione o call to action.",
        "Post Social Virale (LinkedIn/X)": "Sei un Social Media Manager. Estrai il concetto più interessante da questo testo e crea un post per LinkedIn/X. Usa frasi brevi, spaziature ampie, un hook iniziale forte, e aggiungi 3 hashtag rilevanti alla fine.",
        "Meeting Manager (Action Items)": "Sei un Project Manager. Analizza questa trascrizione di una riunione o discorso. Crea una lista chiara: 1. Argomenti discussi. 2. Decisioni prese. 3. Action Items (Cose da fare e, se menzionato, da chi)."
    }
    
    prompt_base = prompts.get(mode, prompts["Pulizia e Correzione Perfetta"])
    full_prompt = f"{prompt_base}\n\nREGOLE IMPORTANTI:\nScrivi la risposta ESCLUSIVAMENTE in lingua {language}.\n\nTESTO DA ANALIZZARE:\n{text}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Errore nell'elaborazione IA: {str(e)}"

# --- INTERFACCIA UTENTE ---
st.title("🧠 CleanScript AI 5.0")
st.markdown("<p style='color: #64748B; font-size: 1.1em;'>Il primo Content Hub potenziato da Intelligenza Artificiale Reale.</p>", unsafe_allow_html=True)

if 'raw_text' not in st.session_state: st.session_state['raw_text'] = ""

st.markdown('<div class="feature-card">', unsafe_allow_html=True)
tab_yt, tab_file, tab_manual = st.tabs(["🎥 Trascrizione YouTube", "📁 Carica Documento", "✍️ Testo Libero"])

with tab_yt:
    st.info("💡 Vai su YouTube da PC -> Clicca '... Altro' sotto il video -> 'Mostra Trascrizione' -> Copia e Incolla qui.")
    m_txt_yt = st.text_area("Incolla qui la trascrizione sporca di YouTube:", height=150, key="yt_in")
    if st.button("CARICA TESTO YOUTUBE", key="btn_yt"): st.session_state['raw_text'] = m_txt_yt

with tab_file:
    up_file = st.file_uploader("Formati supportati: PDF, DOCX, TXT", type=['pdf', 'docx', 'txt'])
    if up_file and st.button("LEGGI FILE"):
        with st.spinner('Lettura in corso...'):
            if up_file.type == "application/pdf": st.session_state['raw_text'] = "".join([p.extract_text() for p in PdfReader(up_file).pages])
            elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": st.session_state['raw_text'] = " ".join([p.text for p in Document(up_file).paragraphs])
            else: st.session_state['raw_text'] = up_file.read().decode("utf-8")

with tab_manual:
    m_txt = st.text_area("Incolla appunti o testi grezzi:", height=150, key="man_in")
    if st.button("CARICA TESTO", key="btn_man"): st.session_state['raw_text'] = m_txt

st.markdown('</div>', unsafe_allow_html=True)

# --- PANNELLO DI CONTROLLO IA ---
if st.session_state['raw_text'] and ai_ready:
    st.markdown("---")
    st.subheader("⚙️ Cosa vuoi farci con questo testo?")
    
    col_settings, col_action = st.columns([2, 1])
    
    with col_settings:
        c1, c2 = st.columns(2)
        ai_mode = c1.selectbox("🧠 Potere dell'IA:", [
            "Pulizia e Correzione Perfetta", 
            "Riassunto Esecutivo (TL;DR)", 
            "Articolo Blog SEO", 
            "Post Social Virale (LinkedIn/X)",
            "Meeting Manager (Action Items)"
        ])
        ai_lang = c2.selectbox("🌍 Lingua Output:", ["Italiano", "English", "Español", "Français", "Deutsch"])
        
    with col_action:
        st.write("") # Spazio per allineare il bottone
        st.write("")
        if st.button("✨ GENERA CON IA", use_container_width=True):
            with st.spinner(f"Sto elaborando in modalità '{ai_mode}'..."):
                # Pulizia base preventiva
                clean_raw = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', st.session_state['raw_text'])
                # Chiamata a Gemini
                result = process_with_ai(clean_raw, ai_mode, ai_lang)
                st.session_state['ai_result'] = result

# --- MOSTRA IL RISULTATO ---
if 'ai_result' in st.session_state:
    st.markdown("---")
    res_col, side_col = st.columns([3, 1])
    
    with res_col:
        st.subheader("🎯 Il tuo capolavoro è pronto")
        st.text_area("", st.session_state['ai_result'], height=450, label_visibility="collapsed")
        
        b1, b2 = st.columns(2)
        b1.download_button("📥 Scarica Risultato (.txt)", st.session_state['ai_result'], file_name="cleanscript_ai.txt")
        if b2.button("📋 Info Copia"): st.info("Clicca nel testo, premi Ctrl+A e Ctrl+C per copiare.")
        
    with side_col:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 💎 Valore Generato")
        st.write("L'Intelligenza Artificiale ha appena risparmiato ore del tuo tempo. Hai generato un testo di alta qualità pronto per essere pubblicato o utilizzato nel tuo lavoro.")
        st.divider()
        st.markdown("Se questo tool ti ha svoltato la giornata, considera di supportare i costi del server.")
        st.markdown("[☕ **Offrimi un caffè**](https://paypal.me/tuolink)")
        st.markdown('</div>', unsafe_allow_html=True)
