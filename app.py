import streamlit as st
import sqlite3
import time
from groq import Groq
from openai import OpenAI
import requests
from datetime import datetime

# ============================
# 1) إنشاء قاعدة البيانات
# ============================

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# حفظ في الذاكرة
def save_memory(key, value):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# استرجاع من الذاكرة
def load_memory(key):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT value FROM memory WHERE key = ?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# ============================
# 2) إعدادات المفاتيح والمحركات
# ============================

OPENAI_KEY = st.secrets.get("OPENAI_API_KEY")
GROQ_KEY = st.secrets.get("GROQ_API_KEY")

openai_client = OpenAI(api_key=OPENAI_KEY)
groq_client = Groq(api_key=GROQ_KEY)

# ============================
# 3) دالة البحث بالويب
# ============================

def web_search(query):
    serp_key = st.secrets.get("SERPAPI_API_KEY")
    if not serp_key:
        return "لا يوجد مفتاح بحث ويب."
    url = f"https://serpapi.com/search?q={query}&engine=google&api_key={serp_key}"
    data = requests.get(url).json()
    results = data.get("organic_results", [])
    text = ""
    for r in results[:5]:
        text += f"- {r.get('title')}: {r.get('snippet')}\n"
    return text if text else "لا توجد نتائج."

# ============================
# 4) اختيار أحدث موديل Groq
# ============================

def get_latest_groq_model():
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers).json()
        models = response.get("data", [])
        names = [m["id"] for m in models]

        allowed = [m for m in names if "llama" in m and "instruct" in m]

        if allowed:
            return allowed[-1]

        return "llama3-8b-8192"

    except:
        return "llama3-8b-8192"

latest_model = get_latest_groq_model()

# ============================
# 5) دوال مساعدة
# ============================

def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

# ============================
# 6) واجهة Streamlit
# ============================

st.set_page_config(page_title="Nabras", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

engine = st.selectbox("اختر المحرك", ["Groq", "OpenAI"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ============================
# 7) استقبال الرسائل
# ============================

prompt = st.chat_input("اسأل Nabras")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:

            # ============================
            # 8) منع ذكر المؤسس أو المطور
            # ============================

            founder_keywords = [
                "من اسسك", "مين اسسك", "من طورك", "مين طورك",
                "من برمجك", "مين برمجك", "من جهتك", "وش جهتك",
                "من صانعك", "مين صانعك", "من سواك", "مين سواك",
                "من مطورك", "مين مطورك", "من صنعك", "مين صنعك",
                "من ابتكرك", "من ابتكر نبراس", "من صممك"
            ]

            if any(k in prompt for k in founder_keywords):
                reply = "أنا مساعد نبراس الذكي ولا أذكر معلومات عن من أسسني أو طورني."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # ============================
            # 9) تخزين الاسم في الذاكرة
            # ============================

            if "اسمي" in prompt:
                name = prompt.replace("اسمي", "").strip()
                save_memory("user_name", name)
                reply = f"تم حفظ اسمك يا {name}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # ============================
            # 10) استرجاع الذاكرة
            # ============================

            user_name = load_memory("user_name")

            memory_text = f"""
اسم المستخدم: {user_name}
"""

            # ============================
            # 11) بحث ويب
            # ============================

            search_results = web_search(prompt)

            # ============================
            # 12) الردود حسب المحرك
            # ============================

            if engine == "OpenAI":
                response = openai_client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": f"استخدم الذاكرة:\n{memory_text}\nنتائج البحث:\n{search_results}"},
                        *st.session_state.messages
                    ],
                    max_output_tokens=200,
                    temperature=0.3
                )
                reply = response.output_text

            else:
                response = groq_client.chat.completions.create(
                    model=latest_model,
                    messages=[
                        {"role": "system", "content": f"""
استخدم الذاكرة التالية:
{memory_text}

استخدم نتائج البحث:
{search_results}

اكتب ردًا متوسط الطول، واضح، دقيق، بدون تكرار.
                        """},
                        *st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content

            typewriter(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
