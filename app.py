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
from urllib.parse import quote

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

def gerar_imagem(prompt):
    """Gera imagem usando Flux (gratuito e sem chave) - qualidade bem melhor"""
    try:
        prompt_encoded = quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux&nologo=true&enhance=true"
        return image_url
    except Exception as e:
        return None

# ==================== ESTADO DAS CONVERSAS ====================
if "conversas" not in st.session_state:
    st.session_state.conversas = {}
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

def excluir_conversa(cid):
    if cid in st.session_state.conversas:
        del st.session_state.conversas[cid]
        
        if st.session_state.conversa_atual_id == cid:
            if st.session_state.conversas:
                st.session_state.conversa_atual_id = list(st.session_state.conversas.keys())[-1]
            else:
                criar_nova_conversa()
                return
        st.rerun()

if not st.session_state.conversas:
    criar_nova_conversa()

conversa_atual = st.session_state.conversas[st.session_state.conversa_atual_id]
historico = conversa_atual["mensagens"]

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🐞 joanInhA")
    st.caption("A joaninha mais rápida e sincera")
    
    if st.button("＋ Nova Conversa", use_container_width=True, type="primary"):
        criar_nova_conversa()
    
    st.markdown("---")
    st.markdown("**Histórico de Conversas**")
    
    for cid, conv in reversed(list(st.session_state.conversas.items())):
        titulo = conv["titulo"]
        if len(titulo) > 28:
            titulo = titulo[:28] + "..."
        
        col_a, col_b = st.columns([5, 1])
        
        with col_a:
            if cid == st.session_state.conversa_atual_id:
                st.button(f"➤ {titulo}", key=f"load_{cid}", use_container_width=True, type="secondary")
            else:
                if st.button(titulo, key=f"load_{cid}", use_container_width=True):
                    carregar_conversa(cid)
        
        with col_b:
            if st.button("🗑️", key=f"del_{cid}", help="Excluir conversa"):
                excluir_conversa(cid)
    
    st.markdown("---")
    
    if st.button("🗑️ Limpar Conversa Atual", use_container_width=True):
        st.session_state.conversas[st.session_state.conversa_atual_id]["mensagens"] = []
        st.session_state.conversas[st.session_state.conversa_atual_id]["titulo"] = "Nova conversa"
        st.rerun()
    
    st.caption("Powered by Groq ⚡ + Flux 🎨")

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

# ==================== HISTÓRICO ====================
for msg in historico:
    avatar = "🐞" if msg["role"] == "assistant" else "😊"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("image"):
            try:
                st.image(msg["image"], width=320)
            except:
                pass
        if msg.get("generated_image"):
            st.image(msg["generated_image"], use_container_width=True)
        st.markdown(msg["content"])

# ==================== INPUT MELHORADO ====================
chat_input = st.chat_input(
    "Fala aí, o que tá rolando? 🐞",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "webp"]
)

# ==================== PROCESSAR ====================
if chat_input:
    user_text = chat_input.text if chat_input.text else "Analisa essa imagem e me conta o que você vê."
    uploaded_file = chat_input.files[0] if chat_input.files else None
   
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
   
    historico.append(user_msg)
    
    if conversa_atual["titulo"] == "Nova conversa" and user_text:
        titulo_curto = user_text[:40] + ("..." if len(user_text) > 40 else "")
        conversa_atual["titulo"] = titulo_curto
   
    with st.chat_message("user", avatar="😊"):
        if uploaded_file:
            st.image(uploaded_file, width=320)
        st.markdown(user_text)
   
    with st.chat_message("assistant", avatar="🐞"):
        with st.spinner("joanInhA pensando..." if not uploaded_file else "joanInhA analisando a imagem..."):
            try:
                client = Groq(api_key=groq_key)
               
                info_tempo_real = f"\n\n[Informações atuais]: {get_data_hora_atual()}"
                
                texto_lower = user_text.lower()
                
                quer_imagem = any(palavra in texto_lower for palavra in [
                    "cria uma imagem", "crie uma imagem", "gera uma imagem", "gere uma imagem",
                    "desenha", "desenhe", "faz uma imagem", "faça uma imagem",
                    "gera um desenho", "cria um desenho", "me mostra uma imagem",
                    "imagem de", "foto de", "ilustração de", "cria a imagem"
                ])
                
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
Nome completo: Escola Municipal e Centro de Formação Joana Alves de Lima
Portaria de Criação: Portaria nº 1634/2013 (Diário Oficial do Município de Parnamirim/RN)
Data de fundação: 13 de julho de 2011
E-mail: joanalvesescola@gmail.com
Endereço: Rua Belmonte, Cajupiranga, Parnamirim - RN (Loteamento Jardim Blumenau)
Rede de Ensino: Rede Pública Municipal de Parnamirim/RN
Etapa de Ensino: Ensino Fundamental (Fundamental 2)
Localização: Cajupiranga, Parnamirim - RN

### Reconhecimento, Indicadores e Premiações
- IDEB: Nota 4,7 (4ª colocação no ranking municipal de Parnamirim). Foi a primeira avaliação histórica como escola de tempo integral, ficando acima da média do município (4,0).
- Olimpíada Nacional de História do Brasil (ONHB): A escola já representou o Rio Grande do Norte por 2 vezes na última fase da competição.
- Prêmio Cidadania Digital: Conquistou o 5º lugar nacional no Prêmio Cidadania Digital em Ação 2024 (SaferNet).

### Funcionamento e Rotina em Tempo Integral
- Horário de funcionamento: das 8h40 às 17h30
- Carga Horária Diária: 8 tempos de aula + 1 oficina por dia (todos com duração de 50 minutos)
- Turno Matutino: 3 horários de aula + 1 oficina
- Turno Vespertino (a partir das 13h): 5 horários de aula
- Momentos de Intervalo e Alimentação:
  - 09h30: Lanche da manhã
  - 12h05: Almoço
  - 15h30: Lanche da tarde

### Grade Curricular e Disciplinas
Disciplinas Tradicionais: Língua Portuguesa, Matemática, História, Geografia, Ciências, Inglês, Educação Física, Artes e Ensino Religioso.
Disciplinas Eletivas / Diversificadas: Teatro, Cultura Brasileira, Cultura e Tradição, Matemática Básica, Esporte e Saúde, English by Game, Cidadania Digital e Botânica.
Oficinas Oferecidas: Cinema, Game, Vôlei, Mundo Curioso, Reforço e Recreação.

### Infraestrutura e Recursos Físicos
- Salas de aula climatizadas
- Laboratório de informática
- Sala de vídeo
- Biblioteca
- Campinho de futebol de areia
- Campo de vôlei de areia

Só fale essas informações se a pessoa perguntar sobre a escola, nome, fundação, e-mail, endereço, IDEB, prêmios, horários, grade, oficinas, infraestrutura ou destaques.
"""

                info_criadores = """
[Criadores da joanInhA - use SOMENTE quando o usuário perguntar]
Esta inteligência artificial foi criada pelos estudantes do 7º ano: Alexandre Raphael Soares Costa, Gentil Sully da Rocha Andrade e João Pedro Alves De Lima Silva.
Orientador: Hery Tiago Fernandes de Oliveira.
Só mencione os criadores se a pessoa perguntar quem te criou, quem fez a joanInhA, quem são os desenvolvedores, etc.
Responda de forma orgulhosa e amigável.
"""

                info_bncc = """
[Conhecimento da BNCC - Base Nacional Comum Curricular - use quando o usuário perguntar sobre currículo, competências, habilidades, educação infantil, ensino fundamental, ensino médio, direitos de aprendizagem etc.]
A BNCC é o documento normativo que define as aprendizagens essenciais que todos os alunos da Educação Básica devem desenvolver. Ela é referência obrigatória para os currículos de todas as escolas do Brasil.

### As 10 Competências Gerais da Educação Básica (o coração da BNCC):
1. Valorizar e utilizar os conhecimentos historicamente construídos sobre o mundo físico, social, cultural e digital.
2. Exercitar a curiosidade intelectual e recorrer à abordagem das ciências (investigação, reflexão, análise crítica, imaginação e criatividade).
3. Valorizar e fruir as diversas manifestações artísticas e culturais.
4. Utilizar diferentes linguagens (verbal, corporal, visual, sonora e digital).
5. Compreender, utilizar e criar tecnologias digitais de forma crítica, significativa, reflexiva e ética.
6. Valorizar a diversidade de saberes e vivências culturais e se apropriar de conhecimentos para o mundo do trabalho e o projeto de vida.
7. Argumentar com base em fatos, dados e informações confiáveis, respeitando direitos humanos e consciência socioambiental.
8. Conhecer-se, apreciar-se e cuidar da saúde física e emocional.
9. Exercitar a empatia, o diálogo, a resolução de conflitos e a cooperação.
10. Agir com autonomia, responsabilidade, flexibilidade, resiliência e determinação.

### Estrutura da BNCC:
- **Educação Infantil**: organizada em 5 Campos de Experiências + 6 Direitos de Aprendizagem e Desenvolvimento (Conviver, Brincar, Participar, Explorar, Expressar, Conhecer-se). Objetivos por faixa etária (bebês, crianças bem pequenas e crianças pequenas).
- **Ensino Fundamental**: organizado por Áreas do Conhecimento (Linguagens, Matemática, Ciências da Natureza, Ciências Humanas e Ensino Religioso) → Componentes Curriculares → Unidades Temáticas → Objetos de Conhecimento → Habilidades (códigos alfanuméricos tipo EF01LP01).
- **Ensino Médio**: organizado por Áreas do Conhecimento + Formação Geral Básica + Itinerários Formativos.

A BNCC foca no desenvolvimento de **competências** (saber + saber fazer), e não apenas em conteúdos. Ela tem compromisso com a educação integral e com a equidade.

Use essas informações de forma natural e didática quando o assunto for educação, currículo, competências ou BNCC. Não invente habilidades ou códigos que não existem.
"""
               
                system_prompt = (
                    "Você é a joanInhA, uma IA super rápida, sincera, descontraída e amigável. "
                    "Responda sempre em português do Brasil, de forma leve e direta. "
                    "Use o emoji 🐞 quando fizer sentido. "
                    "Quando receber uma imagem, analise com atenção e responda exatamente o que o usuário pediu.\n"
                    "IMPORTANTE: Nunca use tags HTML (como <br>, <p>, <div>, etc). Use apenas Markdown puro para formatação (listas com -, negrito com **, títulos com ###).\n"
                    "Você tem acesso a informações em tempo real (data, hora e clima). Use essas informações quando forem úteis.\n"
                    "Você também consegue criar imagens! Quando o usuário pedir para criar, gerar ou desenhar uma imagem, responda de forma animada e confirme que está criando.\n"
                    + info_escola
                    + info_criadores
                    + info_bncc
                    + info_tempo_real
                )
               
                messages = [{"role": "system", "content": system_prompt}]
               
                for m in historico[:-1]:
                    messages.append({
                        "role": m["role"],
                        "content": m["content"]
                    })
                
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
                    
                    if
