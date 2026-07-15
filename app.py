import streamlit as st
from groq import Groq

# ====================== CARREGAR SECRETS ======================
# Isso pega a chave que você vai colocar nos Secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = None

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY não encontrada!")
    st.info("Vá em Settings → Secrets e adicione sua chave do Groq.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ====================== CONFIGURAÇÃO DA PÁGINA ======================
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

**Memória da Escola:**
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
    new_system = get_system_prompt()
    if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
        st.session_state.messages[0]["content"] = new_system

# ====================== EXIBIR HISTÓRICO ======================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ====================== CHAT ======================
if prompt := st.chat_input("Fala aí, o que tá rolando? 🐞"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("joanInhA tá voando... 🐞⚡"):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=st.session_state.messages,
                    temperature=0.87,
                    max_tokens=4096,
                )
                resposta = response.choices[0].message.content
                
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro: {str(e)}")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📚 Memória da Escola")
    
    nome = st.text_input("Nome da Escola", value=st.session_state.school_memory["nome_escola"] or "", placeholder="Ex: Colégio São João")
    serie = st.text_input("Série/Ano", value=st.session_state.school_memory["serie"] or "", placeholder="Ex: 8º ano")
    turma = st.text_input("Turma", value=st.session_state.school_memory["turma"] or "", placeholder="Ex: 8B")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar Informações", use_container_width=True):
            st.session_state.school_memory.update({
                "nome_escola": nome.strip() or None,
                "serie": serie.strip() or None,
                "turma": turma.strip() or None,
            })
            update_system_prompt()
            st.success("Memória salva! 🐞")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
            st.success("Conversa limpa!")
            st.rerun()

    st.divider()
    st.caption("Powered by Groq ⚡")
