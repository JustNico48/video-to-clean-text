import streamlit as st

# 1. Configurazione della pagina
st.set_page_config(page_title="CleanScript AI", page_icon="🪄", layout="wide")

# 2. UI Styling (Look professionale e pulito)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { 
        background: linear-gradient(45deg, #007bff, #6610f2); 
        color: white; 
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); }
    .stTextArea textarea { border: 1px solid #e0e0e0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Struttura della Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🪄 CleanScript AI")
    st.write("Trasforma le tue trascrizioni disordinate in contenuti pronti per essere pubblicati.")
    
    # Area di input per l'utente
    raw_input = st.text_area(
        "Incolla qui il testo (con timestamp, nomi speaker o errori):", 
        height=450, 
        placeholder="00:12 Benvenuti nel video... [00:45] Speaker 1: Grazie per essere qui..."
    )

with col2:
    st.header("Impostazioni")
    language = st.selectbox("Lingua Originale", ["Italiano", "English", "Español", "Français"])
    
    output_style = st.radio(
        "Converti in:",
        [
            "Testo Pulito (Senza numeri/tempi)", 
            "Articolo Blog (SEO)", 
            "Thread LinkedIn/X", 
            "Riassunto per Punti"
        ]
    )
    
    st.divider()
    
    # Sezione Monetizzazione/Supporto
    st.markdown("### 💎 Supporta il Progetto")
    st.write("Se questo tool ti ha risparmiato ore di lavoro, offrimi un caffè!")
    st.markdown("[☕ Offrimi un caffè (PayPal)](https://www.paypal.me/tuo-link)") # Sostituisci con il tuo link
    
    st.info("💡 **Tip:** Per risultati migliori, incolla trascrizioni generate da YouTube o Zoom.")

# 4. Motore di Elaborazione (Logica AI-lite)
def process_text(text, style):
    import re
    
    # Rimozione dei timestamp (es: 00:00, [00:00], 00:00:00)
    text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', text)
    
    # Rimozione etichette speaker (es: Speaker 1:, Speaker A:)
    text = re.sub(r'Speaker\s[A-Z\d]:', '', text, flags=re.IGNORECASE)
    
    # Pulizia spazi e a capo doppi
    text = " ".join(text.split())
    
    # Formattazione in base allo stile scelto
    if style == "Articolo Blog (SEO)":
        return f"# ANALISI APPROFONDITA\n\n## Introduzione\n{text[:500]}...\n\n## Punti Trattati\n{text[500:1200]}...\n\n---\n*Generato da CleanScript AI*"
    
    elif style == "Thread LinkedIn/X":
        return f"🧵 NUOVO INSIGHT\n\n{text[:250]}...\n\n👇 Scopri di più nel link in bio.\n#contentcreator #ai"
    
    elif style == "Riassunto per Punti":
        summary_points = text[:1000].split('. ')
        points_str = "\n".join([f"- {p.strip()}" for p in summary_points[:5] if len(p) > 10])
        return f"📝 RIASSUNTO VELOCE:\n\n{points_str}"
    
    return text

# 5. Pulsante di Azione e Risultato
if st.button("✨ ELABORA TESTO"):
    if raw_input:
        with st.spinner('Pulizia in corso...'):
            processed = process_text(raw_input, output_style)
            st.success("Testo pronto!")
            st.text_area("Copia il risultato:", processed, height=300)
            
            # Bottone di download
            st.download_button(
                label="📥 Scarica come .txt",
                data=processed,
                file_name="cleanscript_output.txt",
                mime="text/plain"
            )
    else:
        st.error("Ops! Incolla prima del testo nell'area a sinistra.")

# 6. Footer (Chiusura file)
st.markdown("---")
st.caption("© 2026 CleanScript AI | Privacy: Nessun testo viene salvato sui nostri server.")
