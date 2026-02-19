import streamlit as st

# Configurazione della pagina
st.set_page_config(page_title="CleanScript AI", page_icon="🪄", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { 
        background: linear-gradient(45deg, #007bff, #6610f2); 
        color: white; 
        font-weight: bold;
        border: none;
    }
    .stTextArea textarea { border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# Layout a due colonne
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🪄 CleanScript AI")
    st.write("Il tool definitivo per pulire trascrizioni da YouTube, Zoom e Podcast.")
    
    raw_input = st.text_area("Incolla qui il testo sporco:", height=400, placeholder="00:12 Benvenuti nel video... [00:45] Grazie per essere qui...")

with col2:
    st.header("Configurazione")
    language = st.selectbox("Lingua Originale", ["Italiano", "English", "Español", "Français"])
    output_style = st.radio(
        "Formato Desiderato:",
        ["Articolo Blog (SEO)", "Thread LinkedIn/X", "Punti Elenco (Summary)", "Testo Pulito (No Timestamp)"]
    )
    
    st.divider()
    st.write("💎 **Versione Pro**")
    st.caption("Sblocca l'export in PDF e la rimozione automatica delle 'parole di riempimento' (ehm, ah, cioè).")
    st.button("Ottieni l'accesso Pro")

# Logica di Trasformazione
def process_text(text, style):
    import re
    # Rimozione Timestamp standard
    text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', text)
    # Rimozione nomi speaker (es. Speaker 1:)
    text = re.sub(r'Speaker \d+:', '', text)
    text = " ".join(text.split())
    
    if style == "Articolo Blog (SEO)":
        return f"# Titolo: Analisi del Contenuto\n\n## Introduzione\n{text[:400]}...\n\n## Punti Chiave\n- Approfondimento 1\n- Approfondimento 2"
    elif style == "Thread LinkedIn/X":
        return f"🧵 THREAD\n\n1/ Ho analizzato l'ultimo intervento su questo tema.\n\n2/ Ecco i punti principali: {text[:200]}..."
    return text

if st.button("✨ TRASFORMA ORA"):
    if raw_input:
        processed = process_text(raw_input, output_style)
        st.success("Testo elaborato con successo!")
        st.text_area("Risultato:", processed, height=300)
        st.download_button("Scarica Risultato", processed, file_name="cleanscript_export.txt")
    else:
        st.error("Inserisci del testo per continuare.")
