import streamlit as st
import json
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Configura la API de Google Gemini
GEMINI_API_KEY = "AIzaSyA6N_QZYxODLEaqcu7sP1t7Wq_Hhfk4X6U"  # Obtén de Google AI Studio: https://aistudio.google.com/
genai.configure(api_key=GEMINI_API_KEY)

def extract_features(info):
    # Prompt optimizado para extraer hasta 10 características clave
    prompt = f"""
    Eres un asistente experto en equipos de movimiento de fluidos. De la siguiente información, extrae hasta 10 características clave para una ficha técnica de 1 hoja, priorizando: caudal, presión máxima, materiales (eje, carcasa), potencia del motor, voltaje, tipo de bomba, diámetro de conexiones, peso, dimensiones y velocidad de rotación. Si no hay suficiente info para 10, extrae lo más relevante disponible. Devuelve solo un objeto JSON con una lista de pares clave-valor, sin texto adicional. Ejemplo:
    [
        {{"Caudal": "100-500 L/min"}},
        {{"Presión máxima": "10 bar"}},
        ...
    ]
    Información del equipo: {info}
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # O usa otro modelo disponible, como gemini-1.5-pro
        response = model.generate_content(prompt)
        features = json.loads(response.text.strip())  # Gemini devuelve texto, parseamos el JSON
        return features
    except Exception as e:
        st.error(f"Error al conectar con Gemini API: {e}")
        return []

def generate_pdf(features, output_path="ficha_tecnica.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    
    # Estilos para el PDF
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]
    
    # Título
    elements.append(Paragraph("Ficha Técnica - Equipo", title_style))
    
    # Tabla de características
    data = [["Característica", "Valor"]]
    for feature in features:
        key = list(feature.keys())[0]
        value = feature[key]
        data.append([key, value])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    # Construir PDF
    doc.build(elements)
    return output_path

# Interfaz de Streamlit
st.title("Generador de Fichas Técnicas (con Google Gemini)")

info = st.text_area("Ingresa toda la información del equipo:", height=200)

if st.button("Generar Ficha"):
    if info:
        # Extraer características
        features = extract_features(info)
        
        if features:
            # Mostrar características extraídas
            st.write("Características extraídas:")
            st.json(features)
            
            # Generar PDF
            pdf_path = generate_pdf(features)
            
            # Botón para descargar PDF
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Descargar Ficha Técnica (PDF)",
                    data=f,
                    file_name="ficha_tecnica.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("No se pudieron extraer características. Revisa la información ingresada.")
    else:
        st.warning("Por favor, ingresa la información del equipo.")
