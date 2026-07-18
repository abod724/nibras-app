import streamlit as st
from openai import OpenAI
import time

# ============================
# إعداد مفتاح OpenAI
# ============================

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============================
# إعداد صفحة نبراس
# ============================

st.set_page_config(
    page_title="Nabras AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 نبراس - مساعدك الذكي")

# ============================
# دالة الكتابة المتدرجة (اختيارية)
# ============================

def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

# ============================
# تخزين المحادثات
# ============================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحبًا عبدالله، أنا نبراس. كيف أقدر أساعدك اليوم؟"}
    ]

# ============================
# عرض المحادثات السابقة
# ============================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ============================
# استقبال رسالة المستخدم
# ============================

prompt = st.chat_input("اكتب رسالتك هنا...")

if prompt:

    # منع سؤال المؤسس
    founder_keywords = [
        "من اسسك", "مين اسسك", "من طورك", "مين طورك",
        "من برمجك", "مين برمجك", "من جهتك", "وش جهتك",
        "من صانعك", "مين صانعك", "من سواك", "مين سواك",
        "من مطورك", "مين مطورك", "من صنعك", "مين صنعك",
        "من ابتكرك", "من ابتكر نبراس", "من صممك"
    ]

    if any(k in prompt for k in founder_keywords):
        reply = "أنا نبراس، مساعد ذكي، ولا أذكر معلومات عن من أسسني أو طورني."
        with st.chat_message("assistant"):
            typewriter(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.stop()

    # حفظ رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    # ============================
    # رد نبراس باستخدام OpenAI فقط
    # ============================

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )

            reply = response.choices[0].message["content"]

            typewriter(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ حدث خطأ: {str(e)}")
