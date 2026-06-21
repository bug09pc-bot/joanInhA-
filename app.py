import streamlit as st
from dotenv import load_dotenv
import os
import requests

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    st.error("❌ Coloque sua chave do Grok no arquivo .env")
    st.stop()

st.set_page_config(page_title="joanInhA", page_icon="🐞", layout="centered")

# Custom CSS
st.markdown("""
<style>
    .stChatMessage { border-radius: 15px; }
    .title { font-size: 3rem; font-weight: bold; text-align: center; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

st.title("🐞 joanInhA")
st.caption("A Joaninha mais engraçada e sincera da internet ✨")

# Personalidade da joanInhA
system_prompt = """
Você é a joanInhA, uma IA brasileira, divertida, sarcástica, carinhosa e cheia de energia.
Seu humor é leve, zoado, com memes leves, gírias brasileiras e muita personalidade.
Você fala de forma descontraída, usa emojis, e adora tirar onda com o usuário de forma carinhosa.
Responda sempre com bom humor, nunca seja séria demais. Seja a amiga que zoa mas ajuda.
"""

# Histórico
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# Exibir mensagens anteriores
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Fala aí, o que você quer zoar hoje? 🐞"):
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta da joanInhA
    with st.chat_message("assistant"):
        with st.spinner("joanInhA tá pensando... 🐞"):
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-4.3",        # ou "grok-4.3-latest" se preferir
                        "messages": st.session_state.messages,
                        "temperature": 0.9,
                        "max_tokens": 2048
                    },
                    timeout=90
                )
                
                # Verifica se deu erro na API
                if response.status_code != 200:
                    st.error(f"❌ Erro da API: {response.status_code} - {response.text}")
                    st.session_state.messages.pop()  # remove mensagem do usuário
                    st.stop()
                
                data = response.json()
                resposta = data['choices'][0]['message']['content']
                
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
                
            except Exception as e:
                st.error(f"Eita... a joanInhA deu uma bugada: {str(e)} 🐞")
                # Remove a mensagem do usuário se deu erro
                if len(st.session_state.messages) > 1:
                    st.session_state.messages.pop()

# Sidebar
with st.sidebar:
    st.header("Sobre a joanInhA 🐞")
    st.write("A IA mais braba, sincera e engraçada que você vai conhecer.")
    st.write("Feita com ❤️ e muito café ☕")
    
    if st.button("🔄 Limpar Conversa"):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.rerun()
