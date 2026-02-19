import streamlit as st
import time
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from fpdf import FPDF
from docx import Document
from PIL import Image
import os

# --- CONFIGURAZIONE PAGINA E CSS MINIMALISTA ---
st.set_page_config(page_title="Universal PDF Converter", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    [data-testid="stHeader"] { background-color: transparent !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 900px !important; }

    .stApp { background-color: #FAFAFA !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important; }
    p, span, label, div { color: #4B5563 !important; }
    h1, h2, h3 { color: #111827 !important; font-weight: 700 !important; letter-spacing: -0.02em; }

    .clean-card {
        background: #FFFFFF !important; padding: 2.5rem; border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        border: 1px solid #E5E7EB; margin-bottom: 2rem; transition: box-shadow 0.2s ease;
    }

    .stTextInput>div>div>input, .stTextArea textarea {
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

# --- MOTORE DI CREAZIONE PDF ---
def generate_pdf_from_text(text_content):
    """Crea un PDF elegante a partire da un testo"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=12)
    
    # Sostituiamo caratteri non supportati dal font base per evitare crash
    safe_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 7, txt=safe_text)
    
    # Restituisce i bytes puri, formato che Streamlit riconosce per il download
    return bytes(pdf.output())

def generate_pdf_from_image(image_bytes):
    """Centra un'immagine caricata all'interno di un PDF"""
    img = Image.open(BytesIO(image_bytes))
    # Converti in RGB se è PNG con trasparenza
    if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
    
    # Salva temporaneamente l'immagine per passarla a fpdf
    temp_img_path = "temp_image.jpg"
    img.save(temp_img_path)
    
    pdf = FPDF()
    pdf.add_page()
    # Inserisci immagine adattandola alla larghezza della pagina (A4: 210x297mm)
    pdf.image(temp_img_path, x=10, y=10, w=190)
    
    os.remove(temp_img_path) # Pulizia file temporaneo
    
    # Restituisce i bytes puri
    return bytes(pdf.output())

def get_webpage_text(url):
    """Estrae testo pulito da un link"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.extract()
        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        clean_text = '\n'.join(line for line in lines if line)
        return clean_text, True
    except Exception as e:
        return f"Errore durante l'estrazione: {e}", False

# --- STATO SESSIONE ---
if 'input_data' not in st.session_state: st.session_state['input_data'] = None
if 'data_type' not in st.session_state: st.session_state['data_type'] = None
if 'pdf_ready' not in st.session_state: st.session_state['pdf_ready'] = None

# --- UI PRINCIPALE ---
spacer_left, main_col, spacer_right = st.columns([1, 8, 1])

with main_col:
    st.markdown("""
        <div style="text-align: center; padding: 2.5rem 0 2rem 0;">
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem; color: #111827;'>Any-to-PDF Converter</h1>
            <p style='font-size: 1.1rem; color: #6B7280; max-width: 600px; margin: 0 auto;'>
                Trasforma Link, Immagini, Word o Testi in documenti PDF professionali.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    
    tab_link, tab_file, tab_text = st.tabs(["🌐 Link Web", "📁 Immagini / Word", "✍️ Incolla Testo"])

    with tab_link:
        url = st.text_input("", placeholder="Incolla l'URL di un articolo o sito web...", label_visibility="collapsed")
        if st.button("Estrai come PDF", key="btn_url"):
            if url:
                with st.spinner("Estrazione contenuto web..."):
                    text, success = get_webpage_text(url)
                    if success:
                        st.session_state['input_data'] = text
                        st.session_state['data_type'] = "text"
                        st.session_state['pdf_ready'] = None
                    else: st.error(text)

    with tab_file:
        up_file = st.file_uploader("Carica JPG, PNG, DOCX o TXT", type=['jpg', 'jpeg', 'png', 'docx', 'txt'], label_visibility="collapsed")
        if up_file and st.button("Converti File", key="btn_file"):
            if up_file.type in ['image/jpeg', 'image/png']:
                st.session_state['input_data'] = up_file.getvalue()
                st.session_state['data_type'] = "image"
            elif up_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.session_state['input_data'] = "\n".join([p.text for p in Document(up_file).paragraphs])
                st.session_state['data_type'] = "text"
            else:
                st.session_state['input_data'] = up_file.read().decode('utf-8')
                st.session_state['data_type'] = "text"
            st.session_state['pdf_ready'] = None

    with tab_text:
        m_txt = st.text_area("", placeholder="Incolla qui i tuoi appunti, codice o testo libero...", height=150, label_visibility="collapsed")
        if st.button("Crea PDF", key="btn_txt"):
            if m_txt:
                st.session_state['input_data'] = m_txt
                st.session_state['data_type'] = "text"
                st.session_state['pdf_ready'] = None
                
    st.markdown('</div>', unsafe_allow_html=True)

    # --- IL SISTEMA DI MONETIZZAZIONE (REWARDED AD) ---
    if st.session_state['input_data'] and not st.session_state['pdf_ready']:
        ad_placeholder = st.empty()
        
        with ad_placeholder.container():
            st.markdown('<div class="clean-card" style="text-align: center; border-color: #6366F1;">', unsafe_allow_html=True)
            st.markdown("<h3 style='margin-bottom: 10px;'>Generazione in corso... ⏳</h3>", unsafe_allow_html=True)
            st.markdown("<p style='margin-bottom: 20px;'>Il nostro servizio è gratuito grazie agli sponsor. Il tuo PDF sarà pronto al termine del video.</p>", unsafe_allow_html=True)
            
            # VIDEO PUBBLICITARIO (Sostituiscilo con il link del tuo sponsor/affiliato)
            st.video("https://www.youtube.com/watch?v=ZiP1l7jlIIA")
            
            progress_text = "Sblocco Download in corso..."
            my_bar = st.progress(0, text=progress_text)
            
            # Timer di 10 secondi
            for percent_complete in range(100):
                time.sleep(0.10) 
                my_bar.progress(percent_complete + 1, text=progress_text)
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Finito il timer, cancelliamo la pubblicità e generiamo il PDF
        ad_placeholder.empty()
        
        with st.spinner("Creazione documento..."):
            if st.session_state['data_type'] == "text":
                st.session_state['pdf_ready'] = generate_pdf_from_text(st.session_state['input_data'])
            elif st.session_state['data_type'] == "image":
                st.session_state['pdf_ready'] = generate_pdf_from_image(st.session_state['input_data'])
        st.rerun()

    # --- OUTPUT FINALE (IL DOWNLOAD) ---
    if st.session_state['pdf_ready']:
        st.markdown('<div class="clean-card" style="border-top: 4px solid #10B981; text-align: center;">', unsafe_allow_html=True)
        st.markdown("<h2 style='margin-bottom: 1rem;'>✅ Il tuo PDF è pronto!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='margin-bottom: 2rem;'>Grazie per l'attesa. Puoi scaricare il tuo file impaginato e pulito.</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.download_button(
                label="📥 SCARICA IL DOCUMENTO PDF",
                data=st.session_state['pdf_ready'],
                file_name="Convertito_CleanScript.pdf",
                mime="application/pdf"
            )
            
            st.write("")
            if st.button("🔄 Converti un altro file", use_container_width=True):
                st.session_state['input_data'] = None
                st.session_state['data_type'] = None
                st.session_state['pdf_ready'] = None
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
