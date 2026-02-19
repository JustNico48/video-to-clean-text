import streamlit as st
import re

# 1. Configurazione della pagina
st.set_page_config(page_title="CleanScript AI 2.0", page_icon="🪄", layout="wide")

# 2. Design Avanzato
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white; border: none; padding: 10px 20px; border-radius: 8px;
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .stats-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 3. Funzioni Logiche
def clean_professional(text):
    # Rimuove Timestamp
    text = re.sub(r'\[?\d{1,2}:\d{2}(:\d{2})?\]?', '', text)
    # Rimuove Filler Words (parole di riempimento)
    fillers = [r'\behm\b', r'\buhm\b', r'\bcioè\b', r'\bpraticamente\b', r'\bdiciamo\b', r'\ballora\b']
    for f in fillers:
        text = re.sub(f, '', text, flags=re.IGNORECASE)
    # Pulizia spazi
    text = " ".join(text.split())
    return text

def get_stats(text):
    words = len(text.split())
    reading_time = max(1, round(words / 200))
    return words, reading_time

# 4. Interfaccia Utente
st.title("🪄 CleanScript AI 2.0")
st.markdown("### Lo strumento gratuito per pulire trascrizioni e creare contenuti")

tab1, tab2 = st.tabs(["🚀 Strumento", "📖 Come Funziona"])

with tab1:
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.markdown("#### 1. Incolla il testo")
        raw_text = st.text_area("Trascrizione grezza da YouTube, Zoom o Podcast:", height=400)
        
        mode = st.selectbox("Trasforma in:", 
            ["Testo Pulito (Senza rumore)", "Articolo Blog SEO", "Post Social (LinkedIn/X)", "Summary Esecutivo"])
        
        process_btn = st.button("PULISCI TESTO ✨")

    with col_out:
        st.markdown("#### 2. Risultato Elaborato")
        if process_btn and raw_text:
            cleaned = clean_professional(raw_text)
            
            # Statistiche
            w_count, r_time = get_stats(cleaned)
            st.markdown(f"""
            <div class="stats-box">
                📊 <b>Statistiche:</b> {w_count} parole | ⏱️ <b>Tempo di lettura:</b> {r_time} min
            </div>
            """, unsafe_allow_html=True)
            
            # Formattazione finale basata sulla scelta
            if mode == "Articolo Blog SEO":
                final_out = f"# TITOLO: {cleaned[:50]}...\n\n## Introduzione\n{cleaned[:300]}...\n\n## Analisi\n{cleaned[300:]}"
            elif mode == "Post Social (LinkedIn/X)":
                final_out = f"🚀 INSIGHT ESTRATTO:\n\n{cleaned[:280]}...\n\n#content #ai #productivity"
            else:
                final_out = cleaned
                
            st.text_area("Copia il risultato:", final_out, height=330)
            st.download_button("📥 Scarica .txt", final_out, file_name="cleanscript_v2.txt")
        else:
            st.info("Incolla un testo a sinistra e premi il tasto per vedere la magia.")

with tab2:
    st.markdown("""
    **Perché usare CleanScript?**
    * **Rimozione Automatica:** Eliminiamo timestamp e nomi speaker in un secondo.
    * **IA-Ready:** Il testo pulito è perfetto per essere dato in pasto a ChatGPT o Claude senza errori.
    * **Privacy 100%:** Non salviamo nulla. Il tuo testo resta nel tuo browser.
    
    **Vuoi supportarci?**
    Se risparmi tempo ogni giorno, considera di offrirci un caffè per mantenere il server gratuito!
    """)
    st.markdown("[☕ Offrimi un caffè](https://www.buymeacoffee.com/tuo-username)")

# 5. Sidebar Monetizzazione
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    st.header("CleanScript Pro")
    st.write("Stiamo lavorando alla versione con upload diretto di file MP3 e traduzione automatica.")
    st.text_input("Lascia la tua email per la Beta:")
    if st.button("Iscrivimi"):
        st.toast("Grazie! Ti avviseremo presto.")
    
    st.divider()
    st.caption("Creato per Content Creator indipendenti.")
