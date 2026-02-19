import streamlit as st

# Configurazione della pagina
st.set_page_config(page_title="CleanScript AI", page_icon="✨", layout="centered")

# Stile CSS personalizzato per un look professionale
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Intestazione
st.title("✨ CleanScript AI")
st.subheader("Trasforma trascrizioni grezze in contenuti pronti all'uso.")
st.write("Dimentica i timestamp e gli errori. Ottieni un testo pulito in un click.")

# Barra laterale per Monetizzazione/Info
with st.sidebar:
    st.header("Opzioni Premium")
    st.info("Stai usando la versione gratuita. Limite: 5000 parole.")
    if st.button("🚀 Sblocca Versione Illimitata"):
        st.write("---")
        st.write("🔗 [Clicca qui per pagare con Stripe](https://tuo-link-di-pagamento.com)")

# Area di Input
text_input = st.text_area("Incolla qui la tua trascrizione sporca (o file .srt):", height=300, placeholder="00:01 Ciao a tutti 00:05 oggi parliamo di...")

# Opzioni di Formattazione
format_type = st.radio(
    "Come vuoi trasformare il testo?",
    ["Articolo Strutturato", "Post LinkedIn Virale", "Riassunto Esecutivo"]
)

# Funzione di "Cleaning" (Logica del Motore)
def clean_transcript(raw_text, mode):
    import re
    # 1. Rimuove timestamp (formati comuni 00:00 o [00:00])
    cleaned = re.sub(r'\d{1,2}:\d{2}(:\d{2})?', '', raw_text)
    cleaned = re.sub(r'\[.*?\]', '', cleaned)
    
    # 2. Pulizia spazi bianchi
    cleaned = " ".join(cleaned.split())
    
    # 3. Logica di formattazione base (Simulazione AI)
    if mode == "Articolo Strutturato":
        return f"## Titolo Generato\n\n{cleaned[:300]}...\n\n### Analisi Approfondita\n\n{cleaned[300:]}"
    elif mode == "Post LinkedIn Virale":
        return f"🚀 INSIGHT DEL GIORNO\n\n💡 {cleaned[:200]}\n\n👇 Cosa ne pensate?\n#CleanScript #Efficiency"
    else:
        return f"**Riassunto:** {cleaned[:500]}..."

# Tasto di Azione
if st.button("Pulisci e Formatta"):
    if text_input:
        with st.spinner('L\'intelligenza artificiale sta elaborando...'):
            result = clean_transcript(text_input, format_type)
            st.success("Fatto! Ecco il tuo contenuto pulito:")
            st.text_area("Risultato:", value=result, height=400)
            st.download_button("Scarica file .txt", result, file_name="cleanscript_output.txt")
    else:
        st.warning("Per favore, inserisci del testo prima di procedere.")

# Footer
st.markdown("---")
st.caption("© 2026 CleanScript AI - Nessun dato viene salvato sui nostri server.")
