import streamlit as st
import os
import base64
import requests
from datetime import datetime
from groq import Groq
from PIL import Image
import io
import locale
import uuid

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

# ==================== FUNÇÕES ====================
def get_data_hora_atual():
    agora = datetime.now()
    dias = {
        0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira",
        3: "quinta-feira", 4: "sexta-feira", 5: "sábado", 6: "domingo"
    }
    dia_semana = dias[agora.weekday()]
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M")
    return f"Hoje é {dia_semana}, {data}. Agora são {hora}."

def get_previsao_tempo(cidade="São Paulo"):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json"
        geo = requests.get(geo_url, timeout=8).json()
        
        if not geo.get("results"):
            return f"Não encontrei a cidade '{cidade}'."
        
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        nome_cidade = geo["results"][0]["name"]
        pais = geo["results"][0].get("country", "")
        
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
        
        codigos = {
            0: "céu limpo ☀️", 1: "principalmente limpo 🌤️", 2: "parcialmente nublado ⛅",
            3: "nublado ☁️", 45: "neblina 🌫️", 48: "neblina 🌫️",
            51: "garoa leve 🌧️", 61: "chuva leve 🌧️", 63: "chuva moderada 🌧️",
            65: "chuva forte 🌧️", 80: "pancadas de chuva 🌦️", 95: "tempestade ⛈️",
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

# ==================== ESTADO DAS CONVERSAS ====================
if "conversas" not in st.session_state:
    st.session_state.conversas = {}          # id -> {"titulo": str, "mensagens": list}
if "conversa_atual_id" not in st.session_state:
    st.session_state.conversa_atual_id = None

def criar_nova_conversa():
    novo_id = str(uuid.uuid4())
    st.session_state.conversas[novo_id] = {
        "titulo": "Nova conversa",
        "mensagens": []
    }
    st.session_state.conversa_atual_id = novo_id
    st.rerun()

def carregar_conversa(cid):
    st.session_state.conversa_atual_id = cid
    st.rerun()

# Se não tem nenhuma conversa, cria a primeira
if not st.session_state.conversas:
    criar_nova_conversa()

# Pega a conversa atual
conversa_atual = st.session_state.conversas[st.session_state.conversa_atual_id]
historico = conversa_atual["mensagens"]

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🐞 joanInhA")
    st.caption("A joaninha mais rápida e sincera")
    
    # Botão Nova Conversa
    if st.button("＋ Nova Conversa", use_container_width=True, type="primary"):
        criar_nova_conversa()
    
    st.markdown("---")
    st.markdown("**Histórico de Conversas**")
    
    # Lista das conversas (mais recentes primeiro)
    for cid, conv in reversed(list(st.session_state.conversas.items())):
        titulo = conv["titulo"]
        if len(titulo) > 32:
            titulo = titulo[:32] + "..."
        
        # Destaca a conversa atual
        if cid == st.session_state.conversa_atual_id:
            st.button(f"➤ {titulo}", key=f"btn_{cid}", use_container_width=True, type="secondary")
        else:
            if st.button(titulo, key=f"btn_{cid}", use_container_width=True):
                carregar_conversa(cid)
    
    st.markdown("---")
    
    if st.button("🗑️ Limpar Conversa Atual", use_container_width=True):
        st.session_state.conversas[st.session_state.conversa_atual_id]["mensagens"] = []
        st.session_state.conversas[st.session_state.conversa_atual_id]["titulo"] = "Nova conversa"
        st.rerun()
    
    st.caption("Powered by Groq ⚡")

# ==================== TÍTULO + LOGO ====================
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

try:
    st.image("logo.png", width=160)
except:
    st.markdown("<div style='font-size: 80px;'>🐞</div>", unsafe_allow_html=True)

st.markdown("""
    <h1 style="margin: 10px 0 0 0; font-size: 2.6rem; font-weight: 700;">joanInhA</h1>
    <p style="margin: 0; color: #666; font-size: 1.05rem;">A Inteligência Artificial da Escola Joana Alves ✨</p>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==================== CONFIG ====================
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    st.error("🔑 Configure a GROQ_API_KEY nos Secrets!")
    st.stop()

# ==================== HISTÓRICO DA CONVERSA ATUAL ====================
for msg in historico:
    avatar = "🐞" if msg["role"] == "assistant" else "😊"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("image"):
            try:
                st.image(msg["image"], width=320)
            except:
                pass
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
   
    img_base64 = None
    mime = None
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        
        max_size = 1024
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size))
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        mime = "image/jpeg"
       
        user_msg["image"] = uploaded_file
        user_msg["base64"] = img_base64
        user_msg["mime"] = mime
   
    # Adiciona mensagem do usuário
    historico.append(user_msg)
    
    # Atualiza o título da conversa com a primeira mensagem
    if conversa_atual["titulo"] == "Nova conversa" and user_text:
        titulo_curto = user_text[:40] + ("..." if len(user_text) > 40 else "")
        conversa_atual["titulo"] = titulo_curto
   
    with st.chat_message("user", avatar="😊"):
        if uploaded_file:
            st.image(uploaded_file, width=320)
        st.markdown(user_text)
   
    with st.chat_message("assistant", avatar="🐞"):
        with st.spinner("joanInhA analisando..." if uploaded_file else "joanInhA pensando..."):
            try:
                client = Groq(api_key=groq_key)
               
                info_tempo_real = f"\n\n[Informações atuais]: {get_data_hora_atual()}"
                
                texto_lower = user_text.lower()
                if any(palavra in texto_lower for palavra in ["tempo", "clima", "previsão", "chuva", "faz sol", "temperatura", "graus"]):
                    cidade = "São Paulo"
                    for palavra in ["em ", "de ", "para "]:
                        if palavra in texto_lower:
                            partes = texto_lower.split(palavra)
                            if len(partes) > 1:
                                cidade = partes[-1].split()[0].capitalize()
                                break
                    info_tempo_real += f"\n\n{get_previsao_tempo(cidade)}"
                
                if any(palavra in texto_lower for palavra in ["onde fica", "localização", "endereço", "fica onde"]):
                    info_tempo_real += f"\n\n{buscar_lugar(user_text)}"
               
                info_escola = """
[Informações da Escola - use SOMENTE quando o usuário perguntar]
- Nome completo: Escola Municipal e Centro de Formação Joana Alves Lima
- Data de fundação: 13 de julho de 2011
- E-mail: joanalvesescola@gmail.com
- Endereço: Rua Belmonte, 13 - Cajupiranga, Parnamirim - RN (Lote Jardim Blumenau)

Regras importantes:
- Só fale essas informações se a pessoa perguntar sobre a escola, o nome, a data de fundação, o e-mail ou a localização.
- Não fique repetindo essas informações em toda resposta.
- Responda de forma natural e amigável.
"""
               
                system_prompt = (
                    "Você é a joanInhA, uma IA super rápida, sincera, descontraída e amigável. "
                    "Responda sempre em português do Brasil, de forma leve e direta. "
                    "Use o emoji 🐞 quando fizer sentido. "
                    "Quando receber uma imagem, analise com atenção e responda exatamente o que o usuário pediu.\n"
                    "Você tem acesso a informações em tempo real (data, hora e clima). Use essas informações quando forem úteis.\n"
                    + info_escola
                    + info_tempo_real
                )
               
                messages = [{"role": "system", "content": system_prompt}]
               
                # Histórico antigo (só texto)
                for m in historico[:-1]:
                    messages.append({
                        "role": m["role"],
                        "content": m["content"]
                    })
                
                # Última mensagem (com imagem se existir)
                if img_base64:
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{img_base64}"
                                }
                            }
                        ]
                    })
                else:
                    messages.append({
                        "role": "user",
                        "content": user_text
                    })
               
                # ========== MODELOS ==========
                if img_base64:
                    modelos_visao = [
                        "qwen/qwen3.8-27b",
                        "qwen/qwen3.6-27b",
                        "meta-llama/llama-4-scout-17b-16e-instruct",
                    ]
                    
                    resposta = None
                    for model in modelos_visao:
                        try:
                            response = client.chat.completions.create(
                                model=model,
                                messages=messages,
                                temperature=0.7,
                                max_tokens=1024
                            )
                            resposta = response.choices[0].message.content
                            break
                        except:
                            continue
                    
                    if resposta is None:
                        resposta = "Desculpa, não consegui ver a imagem agora. Sua conta do Groq não tem acesso a modelos de visão 🐞"
                else:
                    model = "openai/gpt-oss-20b"
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
   
    # Salva a resposta no histórico da conversa atual
    historico.append({"role": "assistant", "content": resposta})
    st.session_state.conversas[st.session_state.conversa_atual_id]["mensagens"] = historico
