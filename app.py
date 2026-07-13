import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("🐞 joanInhA")
st.caption("A joaninha mais braba do ChatGPT")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra histórico
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Fala com a joanInhA..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("joanInhA pensando..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Você é a joanInhA, uma garota brasileira divertida, sarcástica, carinhosa e cheia de energia. Fala com gírias, emojis e humor."},
                        *st.session_state.messages
                    ],
                    temperature=0.9,
                    max_tokens=1000
                )
                resposta = response.choices[0].message.content
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro: {str(e)}")
                st.info("Verifique se a chave OPENAI_API_KEY está correta no arquivo .env")

if st.button("Limpar Conversa"):
    st.session_state.messages = []
    st.rerun()
