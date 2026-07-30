import streamlit as st
import os
import base64
from groq import Groq
from PIL import Image
import io

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
    st.caption("Powered by Groq ⚡")

# ==================== TÍTULO ====================
st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
    <span style="font-size: 42px;">🐞</span>
    <h1 style="margin: 0; font-size: 2.4rem;">joanInhA</h1>
</div>
""", unsafe_allow_html=True)

st.caption("A joaninha mais rápida e sincera do Groq ✨")

# ==================== CONFIG ====================
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
    
    # Texto padrão se só mandar foto
    user_text = prompt if prompt else "Analisa essa imagem e me conta o que você vê."
    
    user_msg = {"role": "user", "content": user_text}
    
    if uploaded_file:
        # Converte a imagem pra base64
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
    
    # Mostra a mensagem do usuário
    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=320)
        st.markdown(user_text)
    
    # Resposta da joanInhA
    with st.chat_message("assistant"):
        with st.spinner("joanInhA analisando..." if uploaded_file else "joanInhA pensando..."):
            try:
                client = Groq(api_key=groq_key)
                
                # Contexto da escola
                contexto_escola = ""
                if st.session_state.escola.get("nome"):
                    contexto_escola = (
                        f"\n\n[Contexto do aluno]: "
                        f"Escola: {st.session_state.escola['nome']}, "
                        f"Série: {st.session_state.escola['serie']}, "
                        f"Turma: {st.session_state.escola['turma']}"
                    )
                
                system_prompt = (
                    "Você é a joanInhA, uma IA super rápida, sincera, descontraída e amigável. "
                    "Responda sempre em português do Brasil, de forma leve e direta. "
                    "Use o emoji 🐞 quando fizer sentido. "
                    "Quando receber uma imagem, analise com atenção e responda exatamente o que o usuário pediu."
                    + contexto_escola
                )
                
                messages = [{"role": "system", "content": system_prompt}]
                
                # Últimas mensagens (só texto pra não estourar)
                for m in st.session_state.historico[-8:]:
                    if m["role"] == "user" and m.get("base64"):
                        # Mensagem com imagem
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
                
                # Escolhe o modelo
                if uploaded_file:
                    model = "llama-3.2-11b-vision-preview"   # modelo de visão
                else:
                    model = "llama-3.1-8b-instant"
                
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
