import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi

# 1. Configurazione della pagina
st.set_page_config(page_title="CleanScript AI 3.0", page_icon="🎬", layout="wide")

# 2. Design Moderno
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTextInput>div>div>input { border-radius: 20px; border: 2px solid #667eea; }
    .stButton>button { 
        background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%); 
        color: white; border-radius: 20px; font-weight: bold;
    }
    .video-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI TECNICHE ---
def extract_video_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['it', 'en'])
        full_transcript = " ".join([t['text'] for t in transcript_list])
        return full_transcript
    except Exception as e:
        return f"Errore: Impossibile recuperare i sottotitoli. Assicurati che il video abbia i sottotitoli generati. ({str(e)})"

def clean_text(text):
    text = re.sub(r'\[.*?\]', '', text) # Rimuove annotazioni tipo [Musica]
    text = " ".join(text.split()) # Pulisce spazi
    return text

# --- INTERFACCIA ---
st.title("🎬 CleanScript AI 3.0")
st.subheader("Incolla un link YouTube o il tuo testo per trasformarlo in contenuto.")

tab1, tab2 = st.tabs(["🎥 Da YouTube", "📄 Incolla Testo"])

with tab1:
    st.markdown('<div class="video-card">', unsafe_allow_html=True)
    video_url = st.text_input("Inserisci il link del video YouTube (es: https://www.youtube.com/watch?v=...)", placeholder="https://www.youtube.com/...")
    
    if st.button("ESTRAI E PULISCI VIDEO"):
        v_id = extract_video_id(video_url)
        if v_id:
            with st.spinner('Sto leggendo il video per te...'):
                raw_t = get_youtube_transcript(v_id)
                if "Errore" not in raw_t:
                    st.session_state['transcript'] = clean_text(raw_t)
                    st.success("Sottotitoli estratti con successo!")
                else:
                    st.error(raw_t)
        else:
            st.warning("Link non valido. Controlla l'URL.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    manual_text = st.text_area("Oppure incolla qui il tuo testo sporco:", height=200)
    if st.button("PULISCI TESTO MANUALE"):
        st.session_state['transcript'] = clean_text(manual_text)

# --- AREA RISULTATO (Sempre visibile se c'è testo) ---
if 'transcript' in st.session_state:
    st.divider()
    col_res, col_opt = st.columns([2, 1])
    
    with col_res:
        st.markdown("### ✨ Testo Elaborato")
        final_text = st.text_area("Risultato pronto:", st.session_state['transcript'], height=400)
        st.download_button("📥 Scarica .txt", final_text, file_name="cleanscript_video.txt")
        
    with col_opt:
        st.markdown("### 🛠️ Azioni Rapide")
        style = st.selectbox("Cosa vuoi creare?", ["Testo Pulito", "Articolo per Blog", "Thread per X", "Riassunto Punti"])
        
        if st.button("OTTIMIZZA FORMATO"):
            t = st.session_state['transcript']
            if style == "Articolo per Blog":
                formatted = f"# ANALISI VIDEO\n\n{t[:500]}...\n\n## Punti Chiave\n- {t[500:800]}..."
            elif style == "Thread per X":
                formatted = f"🧵 DAL VIDEO:\n\n{t[:240]}...\n\n#YouTube #Insight"
            else:
                formatted = t
            st.session_state['transcript'] = formatted
            st.rerun()

# Footer
st.markdown("---")
st.caption("CleanScript AI 3.0 - Trasforma i video in asset senza sforzo.")
