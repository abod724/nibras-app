import streamlit as st
from openai import OpenAI
from googlesearch import search as google_search

st.set_page_config(page_title="نبراس", page_icon="🤖", layout="centered")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── تهيئة المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "أهلاً 👋 أنا نبراس، كيف أساعدك؟"}]

# ─── عرض المحادثة ───
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── الإدخال ───
prompt = st.chat_input("اكتب رسالتك...")

if prompt:
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # ─── بحث Google (اختياري، يعمل في الخلفية) ───
    search_results = ""
    try:
        results = list(google_search(prompt, num_results=2, advanced=True))
        for r in results:
            search_results += f"- {getattr(r, 'title', '')}: {getattr(r, 'description', '')}\n"
    except:
        pass
    
    # ─── رد المساعد ───
    with st.chat_message("assistant"):
        try:
            system_prompt = "أنت نبراس، مساعد ذكي."
            if search_results:
                system_prompt += f"\n\nمعلومات من البحث:\n{search_results}"
            
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                stream=True,
                max_tokens=500
            )
            
            # كتابة الرد مباشرة (بدون st.rerun())
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"خطأ: {e}")
