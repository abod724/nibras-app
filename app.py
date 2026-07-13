import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime

st.set_page_config(page_title="نبراس 2026", page_icon="📅", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

def get_current_date():
    return datetime.now().strftime("%A، %d %B %Y")

# ─── بحث بالويب (يعمل 100%) ───
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return ""
        context = ""
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            context += f"• {title}: {body[:200]}...\n"
        return context.strip()
    except Exception as e:
        return ""

with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، مساعد ذكي ومحدث. أجب بحد أقصى 3 جمل."},
            {"role": "assistant", "content": f"مرحباً! أنا نبراس، اليوم هو {get_current_date()}. كيف أساعدك؟"}
        ]
        st.rerun()
    st.divider()
    st.toggle("🌐 بحث في الويب", value=True, key="enable_search", disabled=False)
    st.caption(f"📅 التاريخ اليوم: {get_current_date()}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، مساعد ذكي ومحدث. أجب بحد أقصى 3 جمل."},
        {"role": "assistant", "content": f"مرحباً! أنا نبراس، اليوم هو {get_current_date()}. كيف أساعدك؟"}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

if prompt := st.chat_input("اكتب سؤالك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            if "تاريخ" in prompt or "اليوم" in prompt:
                reply = f"اليوم هو {get_current_date()}."
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            search_context = ""
            if st.session_state.enable_search:
                with st.spinner("🌐 جاري البحث..."):
                    search_context = search_web(prompt)

            system_prompt = "أنت نبراس، مساعد ذكي ومحدث. أجب بحد أقصى 3 جمل."
            if search_context:
                system_prompt += f"\n\n📌 معلومات محدثة من البحث:\n{search_context}"

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(st.session_state.messages)

            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200,
                temperature=0.3,
                stream=True
            )

            reply = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
