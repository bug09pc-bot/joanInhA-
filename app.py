import streamlit as st
import os
import base64
import requests
from datetime import datetime
from groq import Groq
from PIL import Image
import io
import locale

# Tenta configurar para português (não quebra se não funcionar)
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    pass

st.set_page_config(
    page_title="joanInhA",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTILO ====================
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main { background-color: white; }
    h1 { font-weight: 700; color: #1a1a1a; }
    .stChatMessage { border-radius: 12px; }
    div[data-testid="stSidebar"] { background-color: #f1f3f5; }
    .stButton > button { border-radius: 10px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES DE TEMPO REAL ====================

def get_data_hora_atual():
    agora = datetime.now()
    dias = {
        0: "segunda-feira",
        1: "terça-feira",
        2: "quarta-feira",
        3: "quinta-feira",
        4: "sexta-feira",
        5: "sábado",
        6: "domingo"
    }
    dia_semana = dias[agora.weekday()]
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")
    return f"Hoje é {dia_semana}, {data}. Agora são {hora}."

def get_previsao_tempo(cidade="São Paulo"):
    """Busca previsão do tempo usando Open-Meteo (gratuito)"""
    try:
        # 1. Busca as coordenadas da cidade
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json"
        geo = requests.get(geo_url, timeout=8).json()
        
        if not geo.get("results"):
            return f"Não encontrei a cidade '{cidade}'."
        
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        nome_cidade = geo["results"][0]["name"]
        pais = geo["results"][0].get("country", "")

        # 2. Busca o clima
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            f"&timezone=America/Sao_Paulo&forecast_days=3"
        )
        data = requests.get(weather_url, timeout=8).json()
        
        current = data["current"]
        daily = data["daily"]

        # Códigos de tempo simplificados
        codigos = {
            0: "céu limpo ☀️",
            1: "principalmente limpo 🌤️",
            2: "parcialmente nublado ⛅",
            3: "nublado ☁️",
            45: "neblina 🌫️",
            48: "neblina 🌫️",
            51: "garoa leve 🌧️",
            61: "chuva leve 🌧️",
            63: "chuva moderada 🌧️",
            65: "chuva forte 🌧️",
            80: "pancadas de chuva 🌦️",
            95: "tempestade ⛈️",
        }
        descricao = codigos.get(current["weather_code"], "tempo variável")

        texto = (
            f"**Clima em {nome_cidade} ({pais}):**\n"
            f"- Agora: {current['temperature_2m']}°C, {descricao}\n"
            f"- Umidade: {current['relative_humidity_2m']}%\n"
            f"- Vento: {current['wind_speed_10m']} km/h\n\n"
            f"**Próximos dias:**\n"
            f"- Hoje → Máx {daily['temperature_2m_max'][0]}°C / Mín {daily['temperature_2m_min'][0]}°C "
            f"(chance de chuva: {daily['precipitation_probability_max'][0]}%)\n"
            f"- Amanhã → Máx {daily['temperature_2m_max'][1]}°C / Mín {daily['temperature_2m_min'][1]}°C "
            f"(chance de chuva: {daily['precipitation_probability_max'][1]}%)\n"
            f"- Depois → Máx {daily['temperature_2m_max'][2]}°C / Mín {daily['temperature_2m_min'][2]}°C "
            f"(chance de chuva: {daily['precipitation_probability_max'][2]}%)"
        )
        return texto
    except Exception as e:
        return f"Não consegui buscar o clima agora. Erro: {str(e)}"

def buscar_lugar(nome_lugar):
    """Busca informações básicas de um lugar usando OpenStreetMap"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={nome_lugar}&format=json&limit=1&addressdetails=1"
        headers = {"User-Agent": "joanInhA-App"}
        res = requests.get(url, headers=headers, timeout=8).json()
        
        if not res:
            return f"Não encontrei informações sobre '{nome_lugar}'."
        
        item = res[0]
        endereco = item.get("display_name", "")
        tipo = item.get("type", "")
        return f"**{item.get('name', nome_lugar)}**\nLocalização: {endereco}\nTipo: {tipo}"
    except Exception as e:
        return f"Erro ao buscar o lugar: {str(e)}"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 📚 Memória da Escola")
   
    nome_escola = st.text_input("Nome da Escola", placeholder="Ex: Colégio São João")
    serie = st.text_input("Série/Ano", placeholder="Ex: 8º ano")
    turma = st.text_input("Turma", placeholder="Ex: 8B")
   
    if st.button("💾 Salvar Informações", use_container_width=True):
        st.session_state.escola = {
            "nome": nome_escola,
            "serie": serie,
            "turma": turma
        }
        st.success("Salvo com sucesso!")
   
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.historico = []
        st.rerun()
   
    st.markdown("---")
    st.caption("Powered by Groq ⚡ + Open-Meteo")

# ==================== TÍTULO ====================
st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
    <span style="font-size: 42px;">🐞</span>
    <h1 style="margin: 0; font-size: 2.4rem;">joanInhA</h1>
</div>
""", unsafe_allow_html=True)
st.caption("A joaninha mais rápida e sincera do Groq ✨")

# ==================== CONFIG ====================
# Preferência: st.secrets → se não achar, tenta variável de ambiente
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    st.error("🔑 Configure a GROQ_API_KEY nos Secrets!")
    st.stop()

if "historico" not in st.session_state:
    st.session_state.historico = []
if "escola" not in st.session_state:
    st.session_state.escola = {"nome": "", "serie": "", "turma": ""}

# ==================== HISTÓRICO ====================
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(msg["image"], width=320)
        st.markdown(msg["content"])

# ==================== INPUTS ====================
col1, col2 = st.columns([5, 1])
with col1:
    prompt = st.chat_input("Fala aí, o que tá rolando? 🐞")
with col2:
    uploaded_file = st.file_uploader(
        "📷",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
        key="uploader"
    )

# ==================== PROCESSAR ====================
if prompt or uploaded_file is not None:
   
    user_text = prompt if prompt else "Analisa essa imagem e me conta o que você vê."
   
    user_msg = {"role": "user", "content": user_text}
   
    if uploaded_file:
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image_format = uploaded_file.type.split("/")[-1].upper()
        if image_format == "JPG":
            image_format = "JPEG"
        image.save(buffered, format=image_format)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
       
        user_msg["image"] = uploaded_file
        user_msg["base64"] = img_base64
        user_msg["mime"] = uploaded_file.type
   
    st.session_state.historico.append(user_msg)
   
    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=320)
        st.markdown(user_text)
   
    with st.chat_message("assistant"):
        with st.spinner("joanInhA analisando..." if uploaded_file else "joanInhA pensando..."):
            try:
                client = Groq(api_key=groq_key)
               
                # ---------- Contexto da escola ----------
                contexto_escola = ""
                if st.session_state.escola.get("nome"):
                    contexto_escola = (
                        f"\n\n[Contexto do aluno]: "
                        f"Escola: {st.session_state.escola['nome']}, "
                        f"Série: {st.session_state.escola['serie']}, "
                        f"Turma: {st.session_state.escola['turma']}"
                    )
                
                # ---------- Informações em tempo real ----------
                info_tempo_real = f"\n\n[Informações atuais]: {get_data_hora_atual()}"
                
                # Detecta se o usuário perguntou sobre clima
                texto_lower = user_text.lower()
                if any(palavra in texto_lower for palavra in ["tempo", "clima", "previsão", "chuva", "faz sol", "temperatura", "graus"]):
                    # Tenta extrair o nome da cidade (simples)
                    cidade = "São Paulo"  # padrão
                    for palavra in ["em ", "de ", "para "]:
                        if palavra in texto_lower:
                            partes = texto_lower.split(palavra)
                            if len(partes) > 1:
                                cidade = partes[-1].split()[0].capitalize()
                                break
                    info_tempo_real += f"\n\n{get_previsao_tempo(cidade)}"
                
                # Detecta pergunta sobre lugar
                if any(palavra in texto_lower for palavra in ["onde fica", "localização", "endereço", "fica onde", "o que é"]):
                    # pega as últimas palavras como nome do lugar (simples)
                    possivel_lugar = user_text
                    info_tempo_real += f"\n\n{buscar_lugar(possivel_lugar)}"
               
                system_prompt = (
                    "Você é a joanInhA, uma IA super rápida, sincera, descontraída e amigável. "
                    "Responda sempre em português do Brasil, de forma leve e direta. "
                    "Use o emoji 🐞 quando fizer sentido. "
                    "Quando receber uma imagem, analise com atenção e responda exatamente o que o usuário pediu.\n"
                    "Você tem acesso a informações em tempo real (data, hora e clima). Use essas informações quando forem úteis."
                    + contexto_escola
                    + info_tempo_real
                )
               
                messages = [{"role": "system", "content": system_prompt}]
               
                # Últimas mensagens
                for m in st.session_state.historico[-8:]:
                    if m["role"] == "user" and m.get("base64"):
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": m["content"]},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{m['mime']};base64,{m['base64']}"
                                    }
                                }
                            ]
                        })
                    else:
                        messages.append({
                            "role": m["role"],
                            "content": m["content"]
                        })
               
                # Modelo
                if uploaded_file:
                    model = "llama-3.2-11b-vision-preview"
                else:
                    model = "llama-3.1-8b-instant"  # ou "llama-3.3-70b-versatile" se quiser mais inteligente
               
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
               
                resposta = response.choices[0].message.content
                st.markdown(resposta)
               
            except Exception as e:
                st.error(f"Ops, a joaninha tropeçou 🐞\n\nErro: {str(e)}")
                resposta = "Desculpa, tive um probleminha técnico. Tenta de novo?"
   
    st.session_state.historico.append({"role": "assistant", "content": resposta})
