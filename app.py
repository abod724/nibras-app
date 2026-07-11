import streamlit as st
from openai import OpenAI
import os

st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="centered"
)

st.title("💬 نبراس - مساعدك الذكي")
st.caption("يعمل بأحدث نموذج + بحث في الويب")

# ============================================================
# استدعاء المفتاح من الأسرار
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف في الأسرار")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ============================================================
# ذاكرة المحادثة
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
        {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
    ]

# ============================================================
# عرض المحادثة
# ============================================================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ============================================================
# مربع الإدخال
# ============================================================
if prompt := st.chat_input("اكتب سؤالك هنا..."):
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # الرد
    with st.chat_message("assistant"):
        with st.spinner("نبراس يبحث ويفكر..."):
            try:
                # ===== استخدام البحث في الويب =====
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": "أنت نبراس، صديق ذكي ودود. ابحث في الويب إذا لزم الأمر."},
                        *st.session_state.messages
                    ],
                    tools=[{"type": "web_search"}],
                    max_output_tokens=500
                )
                
                reply = response.output_text
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"⚠️ حدث خطأ: {str(e)}")
