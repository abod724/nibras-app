import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="نبراس",
    page_icon="🦅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود")
    st.stop()

# ─── تصميم قوي وجريء ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@500;700;900&display=swap');

* { font-family: 'Tajawal', sans-serif; }

.stApp {
    background: #0a0a0a;
    color: #ffffff;
}

#MainMenu, footer, header { visibility: hidden; }

.title-container {
    text-align: center;
    padding: 2rem 0 0.5rem;
    border-bottom: 3px solid #d4a017;
}
.title-container h1 {
    font-size: 3rem;
    font-weight: 900;
    color: #d4a017;
    text-shadow: 0 0 20px rgba(212, 160, 23, 0.3);
    margin: 0;
}
.title-container p {
    color: #aaaaaa;
    font-size: 1.1rem;
    margin-top: 0.2rem;
}

.stChatMessage {
    border-radius: 12px;
    margin-bottom: 8px;
    border: 1px solid #2a2a2a;
}

[data-testid="stChatMessageContent"] {
    font-size: 17px;
    line-height: 1.8;
    color: #f0f0f0;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #1a1a1a;
    border-color: #d4a017;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #121212;
    border-color: #333333;
}

[data-testid="stChatInput"] {
    border-radius: 30px !important;
    border: 2px solid #d4a017 !important;
    background: #1a1a1a !important;
}
[data-testid="stChatInput"] input {
    color: #ffffff !important;
    font-size: 16px !important;
}
[data-testid="stChatInput"] button {
    background: #d4a017 !important;
    color: #0a0a0a !important;
    font-weight: 700 !important;
}

.stButton > button {
    background: #d4a017 !important;
    color: #0a0a0a !important;
    font-weight: 700;
    border: none;
    border-radius: 30px;
    padding: 10px 24px;
    transition: 0.3s;
}
.stButton > button:hover {
    background: #f0c020 !important;
    transform: scale(1.02);
}

.sidebar-title {
    color: #d4a017;
    font-size: 1.2rem;
    font-weight: 700;
    border-bottom: 2px solid #d4a017;
    padding-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─── الشعار ───
st.markdown("""
<div class="title-container">
    <h1>🦅 نبراس</h1>
    <p>الذكاء الاصطناعي القوي</p>
</div>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي (القائمة المنسدلة) ───
with st.sidebar:
    st.markdown('<p class="sidebar-title">⚙️ الإعدادات</p>', unsafe_allow_html=True)
    
    model = st.selectbox("🧠 النموذج", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"], index=0)
    temperature = st.slider("🌡️ الإبداع", 0.0, 2.0, 0.7, 0.1)
    
    system_prompt = st.text_area(
        "📝 شخصية المساعد",
        value="أنت نبراس، مساعد ذكي قوي وحازم. تجيب بالعربية بوضوح ودقة، بدون إطالة.",
        height=100
    )
    
    st.divider()
    
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # ─── هنا التعديل: وضع التوقيع داخل القائمة ───
    st.markdown("""
    <div style="text-align: center; color: #888888; font-size: 0.8rem; border-top: 1px solid #333333; padding-top: 10px; margin-top: 10px;">
        تم بناءه وإنشاءه بواسطة <span style="color: #d4a017; font-weight: 700;">أبو مشعل</span>
    </div>
    """, unsafe_allow_html=True)

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🦅"):
        st.markdown(message["content"])

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🦅"):
        st.markdown("مرحباً 👋 أنا نبراس. كيف أقدر أساعدك اليوم؟")

# ─── الإدخال ───
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🦅"):
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
