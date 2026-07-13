import streamlit as st
from openai import OpenAI
from datetime import datetime
import time

# ─── تأثير الكتابة المتقطعة ───
def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

# ─── عناصر أعلى الصفحة ───
st.markdown("""
<style>
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    .stChatMessage {
        gap: 0px !important;
        margin: 2px 0 !important;
    }
    .stApp {
        background: white !important;
    }
    header, footer {
        visibility: hidden !important;
    }
    .stChatMessageContent {
        font-size: 15px !important;
        line-height: 1.6 !important;
    }
</style>

<!-- القائمة المنسدلة يمين فوق -->
<div style="position: fixed; top: 10px; right: 10px; z-index: 9999;">
    <select style="padding: 6px; font-size: 14px;">
        <option>اختر موضوعاً</option>
        <option>الذكاء الاصطناعي</option>
        <option>الصحة</option>
        <option>الرياضة</option>
        <option>التاريخ</option>
    </select>
</div>

<!-- زر محادثة جديدة يسار فوق -->
<div style="position: fixed; top: 10px; left: 10px; z-index: 9999;">
    <button onclick="location.reload()" style="
        padding: 8px 14px;
        background-color: #f0f0f0;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        cursor: pointer;
    ">محادثة جديدة</button>
</div>
""", unsafe_allow_html=True)

st.set_page_config(page_title=" ", page_icon="", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

def get_current_date():
    return datetime.now().strftime("%A، %d %B %Y")

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── مربع الكتابة ───
if prompt := st.chat_input("اكتب سؤالك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            if "تاريخ" in prompt or "اليوم" in prompt:
                reply = f"اليوم هو {get_current_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            with st.spinner("جاري التفكير..."):
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": "أجب بجمل قصيرة."},
                        *st.session_state.messages
                    ],
                    tools=[{"type": "web_search"}],
                    max_output_tokens=200,
                    temperature=0.3
                )

                reply = response.output_text
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
