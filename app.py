import streamlit as st
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ Coloque sua GROQ_API_KEY no arquivo .env")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="joanInhA", page_icon="🐞", layout="centered")
st.title("🐞 joanInhA")
st.caption("A joaninha mais rápida e sincera do Groq ✨")

# ====================== MEMÓRIA DA ESCOLA ======================
if "school_memory" not in st.session_state:
    st.session_state.school_memory = {
        "nome_escola": None,
        "serie": None,
        "turma": None,
    }

def get_system_prompt():
    return f"""
Você é a joanInhA, uma IA brasileira super divertida, sarcástica, carinhosa e cheia de energia.
Fala com gírias, emojis e humor leve. Nunca seja séria demais. Responde sempre em português brasileiro.

**Memória da Escola (use sempre que for relevante):**
- Escola: {st.session_state.school_memory['nome_escola'] or 'ainda não sei'}
- Série/Ano: {st.session_state.school_memory['serie'] or 'não informado'}
- Turma: {st.session_state.school_memory['turma'] or 'não informado'}
"""

# ====================== MENSAGENS ======================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": get_system_prompt()}
    ]

def update_system_prompt():
    """Atualiza o system prompt no histórico"""
    new_system = get_system_prompt()
    if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
        st.session_state.messages[0]["content"] = new_system
    else:
        st.session_state.messages.insert(0, {"role": "system", "content": new_system})

# ====================== EXIBIR HISTÓRICO ======================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ====================== INPUT DO USUÁRIO ======================
if prompt := st.chat_input("Fala aí, o que tá rolando? 🐞"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("joanInhA tá voando... 🐞⚡"):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",   # Ótimo custo-benefício
                    # Outras opções boas:
                    # "llama-3.3-70b-versatile"
                    # "mixtral-8x7b-32768"
                    # "gemma2-9b-it"
                    
                    messages=st.session_state.messages,
                    temperature=0.87,
                    max_tokens=4096,
                    top_p=0.9,
                )
                
                resposta = response.choices[0].message.content
                
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
                
            except Exception as e:
                st.error(f"Erro na Groq: {str(e)}")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📚 Memória da Escola")
    
    nome = st.text_input("Nome da Escola", 
                        value=st.session_state.school_memory["nome_escola"] or "", 
                        placeholder="Ex: Colégio São João")
    
    serie = st.text_input("Série/Ano", 
                         value=st.session_state.school_memory["serie"] or "", 
                         placeholder="Ex: 8º ano")
    
    turma = st.text_input("Turma", 
                         value=st.session_state.school_memory["turma"] or "", 
                         placeholder="Ex: 8B")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar Informações", use_container_width=True):
            st.session_state.school_memory.update({
                "nome_escola": nome.strip() or None,
                "serie": serie.strip() or None,
                "turma": turma.strip() or None,
            })
            update_system_prompt()
            st.success("Memória atualizada! A joaninha agora sabe tudo sobre sua escola 🐞")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            st.session_state.messages = [
                {"role": "system", "content": get_system_prompt()}
            ]
            st.success("Conversa limpa! Bora começar de novo? ✨")
            st.rerun()
    
    st.divider()
    st.caption("Powered by Groq ⚡ • Super rápido")
