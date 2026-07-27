import streamlit as st
import os
from groq import Groq

st.set_page_config(
    page_title="joanInhA",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTILO LIMPO (igual às fotos) ====================
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main {
        background-color: white;
    }
    h1 {
        font-weight: 700;
        color: #1a1a1a;
    }
    .stChatMessage {
        border-radius: 12px;
    }
    div[data-testid="stSidebar"] {
        background-color: #f1f3f5;
    }
    .stButton > button {
        border-radius: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR - MEMÓRIA DA ESCOLA ====================
with st.sidebar:
    st.markdown("### 📚 Memória da Escola")
    
    nome_escola = st.text_input("Nome da Escola", placeholder="Ex: Colégio São João")
    serie = st.text_input("Série/Ano", placeholder="Ex: 8º ano")
    turma = st.text_input("Turma", placeholder="Ex: 8B")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("💾 Salvar Informações", use_container_width=True):
            st.session_state.escola = {
                "nome": nome_escola,
                "serie": serie,
                "turma": turma
            }
            st.success("Salvo!")
    
    with col_s2:
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            st.session_state.historico = []
            st.rerun()
    
    st.markdown("---")
    st.caption("Powered by Groq ⚡")

# ==================== TELA PRINCIPAL ====================
st.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
    <span style="font-size: 42px;">🐞</span>
    <h1 style="margin: 0; font-size: 2.4rem;">joanInhA</h1>
</div>
""", unsafe_allow_html=True)

st.caption("A joaninha mais rápida e sincera do Groq ✨")

# ==================== CONFIGURAÇÃO GROQ ====================
groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    st.error("🔑 Configure a GROQ_API_KEY nos Secrets!")
    st.stop()

if "historico" not in st.session_state:
    st.session_state.historico = []

if "escola" not in st.session_state:
    st.session_state.escola = {"nome": "", "serie": "", "turma": ""}

# Mostra histórico
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do chat
prompt = st.chat_input("Fala aí, o que tá rolando? 🐞")

# Processar mensagem
if prompt:
    # Monta contexto da escola (se tiver)
    contexto_escola = ""
    if st.session_state.escola["nome"]:
        contexto_escola = (
            f"\n\n[Contexto do aluno]: "
            f"Escola: {st.session_state.escola['nome']}, "
            f"Série: {st.session_state.escola['serie']}, "
            f"Turma: {st.session_state.escola['turma']}"
        )

    st.session_state.historico.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("joanInhA pensando..."):
            try:
                client = Groq(api_key=groq_key)

                system_prompt = (
                    "Você é a joanInhA, uma IA super rápida, sincera e descontraída. "
                    "Responda sempre em português do Brasil, de forma leve, direta e amigável. "
                    "Use emojis de joaninha 🐞 quando fizer sentido."
                    + contexto_escola
                )

                messages = [{"role": "system", "content": system_prompt}]

                # Últimas 12 mensagens pra memória
                for m in st.session_state.historico[-12:]:
                    messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800
                )

                resposta = response.choices[0].message.content
                st.markdown(resposta)

            except Exception as e:
                st.error("Ops, a joaninha deu uma pausa. Tenta de novo em alguns segundos 🐞")
                resposta = "Desculpa, tive um probleminha técnico. Me pergunta de novo?"

    st.session_state.historico.append({"role": "assistant", "content": resposta})
