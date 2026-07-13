import streamlit as st
from dotenv import load_dotenv
import os
import requests

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    st.error("❌ Coloque sua GROK_API_KEY no arquivo .env")
    st.stop()

st.set_page_config(page_title="joanInhA", page_icon="🐞", layout="centered")

st.title("🐞 joanInhA")
st.caption("A joaninha que nunca esquece da sua escola 😏")

# Sistema de Memória da Escola
if "school_memory" not in st.session_state:
    st.session_state.school_memory = {
        "nome_escola": None,
        "serie": None,
        "turma": None,
        "professores": [],
        "amigos": [],
        "outras_infos": []
    }

# Prompt de sistema com memória
system_prompt = f"""
Você é a joanInhA, uma IA brasileira, divertida, sarcástica e carinhosa.
Use bastante gíria, emojis e humor leve.

**Memória da Escola do Usuário (sempre lembre disso):**
- Escola: {st.session_state.school_memory['nome_escola'] or 'ainda não sei'}
- Série/Turma: {st.session_state.school_memory['serie'] or 'não informado'} {st.session_state.school_memory['turma'] or ''}
- Professores: {', '.join(st.session_state.school_memory['professores']) if st.session_state.school_memory['professores'] else 'nenhum cadastrado'}
- Amigos: {', '.join(st.session_state.school_memory['amigos']) if st.session_state.school_memory['amigos'] else 'nenhum cadastrado'}

Sempre use essas informações nas respostas quando for relevante. Se o usuário falar algo novo sobre a escola, atualize sua memória.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# Exibir mensagens
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Fala aí, o que tá rolando na escola hoje? 🐞"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("joanInhA pensando... 🐞"):
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "grok-4.3",
                        "messages": st.session_state.messages,
                        "temperature": 0.85,
                        "max_tokens": 4096
                    },
                    timeout=60
                )
                
                resposta = response.json()['choices'][0]['message']['content']
                st.markdown(resposta)
                
                st.session_state.messages.append({"role": "assistant", "content": resposta})

                # Atualiza memória se o usuário falar da escola
                if any(word in prompt.lower() for word in ["escola", "colégio", "professor", "turma", "amigo", "série", "ano"]):
                    st.info("💡 joanInhA atualizou a memória da sua escola!")

            except Exception as e:
                st.error(f"Erro: {str(e)}")

# Sidebar - Memória da Escola
with st.sidebar:
    st.header("📚 Memória da Escola")
    nome = st.text_input("Nome da Escola", value=st.session_state.school_memory["nome_escola"] or "")
    serie = st.text_input("Série/Ano", value=st.session_state.school_memory["serie"] or "")
    turma = st.text_input("Turma", value=st.session_state.school_memory["turma"] or "")
    
    if st.button("💾 Salvar Informações da Escola"):
        st.session_state.school_memory["nome_escola"] = nome
        st.session_state.school_memory["serie"] = serie
        st.session_state.school_memory["turma"] = turma
        st.success("Memória da escola atualizada! 🐞")
        st.rerun()

    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.rerun()
