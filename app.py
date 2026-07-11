import streamlit as st
from openai import OpenAI
import os
import time

st.set_page_config(page_title="نبراس", page_icon="⚡", layout="centered")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.warning("🔑 أضف مفتاح OpenAI في الأسرار (secrets).")
    API_KEY = st.text_input("أدخل مفتاح OpenAI مؤقتاً:", type="password")
    if not API_KEY:
        st.stop()
    client = OpenAI(api_key=API_KEY)
else:
    client = OpenAI(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_time():
    return time.strftime("%I:%M %p")

# ===== الشريط العلوي =====
col1, col2, col3 = st.columns([1, 8, 1])
with col1:
    if st.button("➕", help="محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()
with col2:
    st.markdown('<div style="text-align:center; font-weight:600; font-size:20px;">⚡ نبراس</div>', unsafe_allow_html=True)
with col3:
    with st.popover("☰"):
        st.markdown("### 📋 القائمة")
        if st.button("🗑️ مسح المحادثة", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.info(f"📊 عدد الرسائل: {len(st.session_state.messages)}")

# ===== نص الترحيب =====
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding:40px 0;">
        <h2>👋 أنا نبراس</h2>
        <p style="color:#6b7280; font-size:18px;">كيف يمكنني مساعدتك؟</p>
    </div>
    """, unsafe_allow_html=True)

# ===== عرض المحادثة =====
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        st.caption(get_time())

# ===== مربع الكتابة =====
prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        st.caption(get_time())

    with st.chat_message("assistant"):
        with st.spinner("نبراس يفكر..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[{"role": "system", "content": "أنت نبراس، مساعد ذكي ومختصر."}] + st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=400
                )
                reply = response.output_text
                st.write(reply)
                st.caption(get_time())
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ {str(e)}")
