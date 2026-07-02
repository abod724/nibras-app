import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from gtts import gTTS

# إعداد الصفحة
st.set_page_config(page_title="سند", layout="centered", page_icon="🌵")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. تصميم الرأس (Header) احترافي
header1, header2 = st.columns([0.8, 0.2])

with header1:
    st.title("سند 🌵")

with header2:
    # القلم والنقاط كقوائم منسدلة حقيقية (Popover)
    with st.popover("⋯"):
        st.write("حول سند")
        st.write("إعدادات الصوت")
    
    with st.popover("✏️"):
        st.write("مواضيع مقترحة:")
        if st.button("أسعار الأعلاف"): st.session_state.prompt = "كم أسعار الأعلاف اليوم؟"
        if st.button("أماكن الفقع"): st.session_state.prompt = "وين أحصل الفقع؟"

# 2. عرض المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. معالجة الإدخال
prompt = st.chat_input("سولف مع سند...") or st.session_state.get("prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        
        # الصوت
        tts = gTTS(text=answer, lang='ar')
        tts.save("voice.mp3")
        st.audio("voice.mp3", format="audio/mp3")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.prompt = None # مسح الطلب بعد التنفيذ