import streamlit as st
import os
import base64
import json
from groq import Groq
from PIL import Image
import io

# ==================== ARQUIVO DE MEMÓRIA ====================
MEMORIA_PATH = "memoria_escola.json"

def carregar_memoria():
    if os.path.exists(MEMORIA_PATH):
        try:
            with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_memoria(dados):
    with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
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

# ==================== CARREGA MEMÓRIA ====================
if "memoria" not in st.session_state:
    st.session_state.memoria = carregar_memoria()

if "historico" not in st.session_state:
    st.session_state.historico = []

# ==================== SIDEBAR - MEMÓRIA DA ESCOLA ====================
with st.sidebar:
    st.markdown("### 📚 Memória da Escola")
    
    nome_escola = st.text_input(
        "Nome da Escola", 
        value=st.session_state.memoria.get("nome_escola", ""),
        placeholder="Ex: Colégio São João"
    )
    
    serie = st.text_input(
        "Série/Ano", 
        value=st.session_state.memoria.get("serie", ""),
        placeholder="Ex: 8º ano"
    )
    
    turma = st.text_input(
        "Turma", 
        value=st.session_state.memoria.get("turma", ""),
        placeholder="Ex: 8B"
    )
    
    professor = st.text_input(
        "Professor(a) principal", 
        value=st.session_state.memoria.get("professor", ""),
        placeholder="Ex: Prof. Carlos"
    )
    
    materias = st.text_area(
        "Matérias / Observações", 
        value=st.session_state.memoria.get("materias", ""),
        placeholder="Ex: Matemática, Português, História...\nOu qualquer anotação importante"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar Memória", use_container_width=True):
            nova_memoria = {
                "nome_escola": nome_escola,
                "serie": serie,
                "turma": turma,
                "professor": professor,
                "materias": materias
            }
            st.session_state.memoria = nova_memoria
            salvar_memoria(nova_memoria)
            st.success("Memória salva!")
    
    with col2:
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            st.session_state.historico = []
            st.rerun()
    
    if st.button("🔄 Recarregar Memória", use_container_width=True):
        st.session_state.memoria = carregar_memoria()
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by Groq ⚡")

# ==================== TÍTULO ====================
st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
    <span style="font-size: 42px;">🐞</span>
    <h1 style="margin: 0; font-size: 2.4rem;">joanInhA</h1>
</div>
""", unsafe_allow_html=True)

st.caption("A joaninha mais rápida e sincera do Groq ✨")

# ==================== GROQ ====================
groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    st.error("🔑 Configure a GROQ_API_KEY nos Secrets!")
    st.stop()

# ==================== HISTÓRICO ====================
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(msg["image"], width=320)
        st.markdown(msg["content"])

# ==================== INPUTS ====================
col_chat, col_up = st.columns([5, 1])

with col_chat:
    prompt = st.chat_input("Fala aí, o que tá rolando? 🐞")

with col_up:
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
        fmt = uploaded_file.type.split("/")[-1].upper()
        if fmt == "JPG":
            fmt = "JPEG"
        image.save(buffered, format=fmt)
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
        with st.spinner("joanInhA pensando..." if not uploaded_file else "joanInhA analisando a imagem..."):
            try:
                client = Groq(api_key=groq_key)
                
                # Monta o contexto da escola
                mem = st.session_state.memoria
                contexto = ""
                if any(mem.values()):
                    contexto = f"""
[Memória da Escola]
- Nome da Escola: {mem.get('nome_escola', 'não informado')}
- Série/Ano: {mem.get('serie', 'não informado')}
- Turma: {mem.get('turma', 'não informado')}
- Professor(a): {mem.get('professor', 'não informado')}
- Matérias/Observações: {mem.get('materias', 'nenhuma')}
"""
                
                system_prompt = f"""Você é a joanInhA, uma IA feita especialmente para ajudar alunos e professores de uma escola.
Você é rápida, sincera, descontraída e amigável. Responda sempre em português do Brasil.
Use o emoji 🐞 de vez em quando.
Você conhece o contexto da escola abaixo e deve usar essas informações sempre que for útil.

{contexto}

Quando o usuário mandar uma imagem, analise com atenção e responda exatamente o que ele pediu.
"""
                
                messages = [{"role": "system", "content": system_prompt}]
                
                # Histórico (últimas 8 mensagens)
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
                
                model = "llama-3.2-11b-vision-preview" if uploaded_file else "llama-3.1-8b-instant"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                resposta = response.choices[0].message.content
                st.markdown(resposta)
                
            except Exception as e:
                st.error(f"Ops, a joaninha deu uma pausa 🐞\n\n{str(e)}")
                resposta = "Desculpa, tive um probleminha técnico. Tenta de novo?"
    
    st.session_state.historico.append({"role": "assistant", "content": resposta})
