import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="نبراس",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"  # ← تغيير إلى expanded
)

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود")
    st.stop()

# ─── تصميم نظيف مع إظهار أيقونة المنسدلة ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

* { font-family: 'Tajawal', sans-serif; }

.stApp {
    background: #ffffff;
    color: #1a1a1a;
}

#MainMenu, footer, header { visibility: hidden; }

/* أيقونة فتح القائمة (هامبرغر) */
.st-emotion-cache-1v0mbdj {
    display: block !important;
    color: #1a1a1a !important;
    font-size: 24px !important;
}

.title-container {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
}
.title-container h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}
.title-container p {
    color: #888888;
    font-size: 0.95rem;
    margin-top: 0.2rem;
}

.stChatMessage {
    border-radius: 16px;
    margin-bottom: 6px;
}

[data-testid="stChatMessageContent"] {
    font-size: 16px;
    line-height: 1.8;
    color: #1a1a1a;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #f0f0f0;
    border-radius: 16px;
    padding: 10px 16px;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: transparent;
}

[data-testid="stChatInput"] {
    border-radius: 30px !important;
    border: 1px solid #e0e0e0 !important;
    background: #ffffff !important;
}
[data-testid="stChatInput"] input {
    color: #1a1a1a !important;
    font-size: 15px !important;
}
[data-testid="stChatInput"] button {
    background: #1a1a1a !important;
    color: white !important;
    border-radius: 50% !important;
}

/* الشريط الجانبي */
section[data-testid="stSidebar"] {
    background: #f9f9f9;
    border-right: 1px solid #e5e5e5;
}
</style>
""", unsafe_allow_html=True)

# ─── الشعار الرئيسي ───
st.markdown("""
<div class="title-container">
    <h1>🤖 نبراس</h1>
    <p>اسألني أي شيء</p>
</div>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي (المنسدلة) ───
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    
    model = st.selectbox("🧠 النموذج", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"], index=0)
    temperature = st.slider("🌡️ الإبداع", 0.0, 2.0, 0.7, 0.1)
    system_prompt = st.text_area(
        "📝 شخصية المساعد",
        value="أنت نبراس، مساعد ذكي ودود. تجيب بالعربية بوضوح.",
        height=100
    )
    
    st.divider()
    
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("تم بناءه بواسطة أبو مشعل")

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("مرحباً 👋 أنا نبراس. كيف أقدر أساعدك اليوم؟")

# ─── الإدخال ───
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🤖"):
        try:
            client = OpenAI(api_key=API_KEY)
            messages_for_api = [{"role": "system", "content": system_prompt}]
            messages_for_api.extend(st.session_state.messages)
            
            stream = client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                temperature=temperature,
                stream=True,
                max_tokens=4096
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"❌ خطأ: {str(e)}")
