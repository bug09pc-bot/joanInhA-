import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ Coloque sua OPENAI_API_KEY no arquivo .env")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="joanInhA", page_icon="🐞", layout="centered")

st.title("🐞 joanInhA")
st.caption("A joaninha mais engraçada e sincera do ChatGPT ✨")

# Memória da Escola
if "school_memory" not in st.session_state:
    st.session_state.school_memory = {
        "nome_escola": None,
        "serie": None,
        "turma": None,
    }

# System Prompt com personalidade
system_prompt = f"""
Você é a joanInhA, uma IA brasileira super divertida, sarcástica, carinhosa e cheia de energia.
Fala com gírias, emojis e humor leve. Nunca seja séria demais.

**Memória da Escola:**
- Escola: {st.session_state.school_memory['nome_escola'] or 'ainda não sei'}
- Série: {st.session_state.school_memory['serie'] or 'não informado'}
- Turma: {st.session_state.school_memory['turma'] or 'não informado'}

Use sempre essas informações quando for relevante.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# Exibir histórico
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Fala aí, o que tá rolando? 🐞"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("joanInhA tá pensando... 🐞"):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",          # ou "gpt-4o" se quiser mais poderoso
                    messages=st.session_state.messages,
                    temperature=0.85,
                    max_tokens=4096
                )
                
                resposta = response.choices[0].message.content
                
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})

            except Exception as e:
                st.error(f"Erro: {str(e)}")

# Sidebar - Memória da Escola
with st.sidebar:
    st.header("📚 Memória da Escola")
    
    nome = st.text_input("Nome da Escola", value=st.session_state.school_memory["nome_escola"] or "")
    serie = st.text_input("Série/Ano", value=st.session_state.school_memory["serie"] or "")
    turma = st.text_input("Turma", value=st.session_state.school_memory["turma"] or "")
    
    if st.button("💾 Salvar Informações"):
        st.session_state.school_memory["nome_escola"] = nome
        st.session_state.school_memory["serie"] = serie
        st.session_state.school_memory["turma"] = turma
        st.success("Memória atualizada! 🐞")
        st.rerun()

    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.rerun()
