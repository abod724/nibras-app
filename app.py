import streamlit as st
from openai import OpenAI
import os
import time

st.set_page_config(page_title="نبراس", page_icon="⚡", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_time():
    return time.strftime("%I:%M %p")

# ===== الشريط العلوي =====
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("### ⚡ نبراس")
with col2:
    if st.button("🔄 جديد"):
        st.session_state.messages = []
        st.rerun()

# ===== عرض المحادثة =====
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ===== مربع الكتابة =====
prompt = st.chat_input("اكتب سؤالك...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("نبراس يفكر..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=300
                )
                reply = response.output_text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.write(reply)
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
