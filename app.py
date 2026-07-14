import streamlit as st
from openai import OpenAI
import os

# === Tente colocar a chave direto aqui primeiro (para teste) ===
# client = OpenAI(api_key="sk-sua_chave_aqui")   # descomente essa linha e coloque sua chave

# Ou use o .env (recomendado)
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("🐞 joanInhA - Teste")
st.caption("Versão simplificada")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Digite algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8
                )
                resposta = response.choices[0].message.content
                st.markdown(resposta)
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"ERRO: {str(e)}")
                st.info("Verifique se a chave OPENAI_API_KEY está correta no .env")

if st.button("Limpar"):
    st.session_state.messages = []
    st.rerun()
