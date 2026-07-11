import streamlit as st
import openai
import os
import time
import base64
import requests
import json

# ============================================================
# إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="نبراس",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# المفتاح والعميل
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.warning("🔑 أضف مفتاح OpenAI في الأسرار (secrets) لتشغيل الذكاء الاصطناعي.")
    # نعطي خيار كتابة المفتاح يدوياً في الواجهة (للتجربة)
    API_KEY = st.text_input("أدخل مفتاح OpenAI مؤقتاً:", type="password")
    if not API_KEY:
        st.stop()
    else:
        st.success("✅ تم إدخال المفتاح، يمكنك الآن الدردشة!")

client = openai.OpenAI(api_key=API_KEY)

# ============================================================
# تهيئة الجلسة
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

# ============================================================
# دوال مساعدة
# ============================================================
def get_time():
    return time.strftime("%I:%M %p")

def search_web(query):
    """بحث في الويب (اختياري) باستخدام Bing أو أي API آخر"""
    try:
        BING_KEY = st.secrets.get("BING_API_KEY")
        if not BING_KEY:
            return ""
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": BING_KEY}
        params = {"q": query, "count": 3, "mkt": "ar-XA"}
        response = requests.get(url, headers=headers, params=params, timeout=5)
        data = response.json()
        results = []
        for item in data.get("webPages", {}).get("value", []):
            results.append(f"• {item['name']}: {item['snippet']}")
        return "\n".join(results) if results else ""
    except:
        return ""

def get_ai_response(messages):
    try:
        # إذا كان المستخدم كتب استفساراً عن بحث
        user_msg = messages[-1]["content"]
        web_results = search_web(user_msg)

        system_prompt = "أنت نبراس، مساعد ذكي ومختصر، تجيب بحد أقصى 3 جمل."

        if "فكرة" in user_msg or "إبداع" in user_msg:
            system_prompt = "أنت نبراس، خبير إبداعي، تقدم فكرة واحدة ملهمة."
        elif "شرح" in user_msg or "درس" in user_msg:
            system_prompt = "أنت نبراس، معلم، تشرح الدرس بأسلوب بسيط في نقاط."
        elif "أخبار" in user_msg or "تقنية" in user_msg:
            system_prompt = "أنت نبراس، باحث، تقدم ملخصاً محدثاً لأخبار التقنية."

        if web_results:
            system_prompt += f"\n\nمعلومات من البحث:\n{web_results}"

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "system", "content": system_prompt}] + messages,
            tools=[{"type": "web_search"}],
            max_output_tokens=400
        )

        return response.output_text
    except Exception as e:
        return f"⚠️ حدث خطأ: {str(e)}"

# ============================================================
# CSS الأساسي
# ============================================================
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f7fa; }
.chat-container {
    max-width: 780px;
    margin: 70px auto 100px;
    padding: 0 20px;
}
.msg-user {
    padding: 12px 18px;
    margin: 6px 0 6px auto;
    background: #1a1a1a;
    color: white;
    border-radius: 20px 20px 4px 20px;
    max-width: 75%;
    width: fit-content;
}
.msg-bot {
    padding: 12px 18px;
    margin: 6px auto 6px 0;
    background: #ffffff;
    border-radius: 20px 20px 20px 4px;
    max-width: 75%;
    width: fit-content;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.time-badge {
    font-size: 10px;
    color: #aaa;
    margin-top: 4px;
    display: block;
}
.input-tools {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 760px;
    max-width: 94%;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    border-radius: 40px;
    border: 1px solid rgba(0,0,0,0.04);
    padding: 4px 6px;
}
.input-tools .stChatInput {
    flex: 1;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    background: transparent !important;
}
.input-tools .stChatInput input {
    border: none !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    background: transparent !important;
}
.input-tools .stChatInput button {
    background: #1a1a1a !important;
    border-radius: 50% !important;
    padding: 6px 14px !important;
    color: white !important;
}
.input-tools .tool-btn {
    background: transparent;
    border: none;
    font-size: 20px;
    cursor: pointer;
    padding: 8px 10px;
    border-radius: 50%;
    transition: 0.2s;
    color: #1a1a1a;
}
.input-tools .tool-btn:hover {
    background: #f0f0f0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# الشريط العلوي بأزرار HTML تعمل (باستخدام st.html)
# ============================================================
st.html("""
<div style="
    position: fixed; top: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(12px);
    padding: 8px 20px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    height: 56px;
">
    <button onclick="location.reload()" style="
        background: transparent; border: none; font-size: 22px;
        cursor: pointer; padding: 6px 12px; border-radius: 50%;
    " onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='transparent'">
        ➕
    </button>
    <span style="font-weight:600; font-size:16px;">⚡ نبراس</span>
    <button onclick="alert('📋 قائمة المحادثات')" style="
        background: transparent; border: none; font-size: 22px;
        cursor: pointer; padding: 6px 12px; border-radius: 50%;
    " onmouseover="this.style.background='#f0f0f0'" onmouseout="this.style.background='transparent'">
        ☰
    </button>
</div>
""", unsafe_allow_javascript=True)

# ============================================================
# عرض المحادثة
# ============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# أدوات الإدخال (مربع الكتابة + رفع ملف + صوت)
# ============================================================
st.markdown("""
<div class="input-tools">
    <button class="tool-btn" onclick="document.getElementById('fileInput').click()">📎</button>
    <div id="chatInputContainer" style="flex:1;"></div>
    <button class="tool-btn" onclick="document.getElementById('micInput').click()">🎤</button>
</div>
<input type="file" id="fileInput" style="display:none;" accept="image/*,audio/*" />
<input type="file" id="micInput" style="display:none;" accept="audio/*" />
""", unsafe_allow_html=True)

# ============================================================
# رفع الملفات والصوت عبر أدوات Streamlit الأصلية
# ============================================================
with st.sidebar:
    st.markdown("### 📎 رفع ملفات")
    uploaded_file = st.file_uploader("اختر صورة أو ملف", type=["jpg", "jpeg", "png", "pdf", "txt", "csv"])
    if uploaded_file:
        st.success(f"✅ تم رفع الملف: {uploaded_file.name}")
        # هنا يمكنك معالجة الملف كما تشاء

    st.markdown("### 🎤 تسجيل صوت")
    audio_value = st.audio_input("سجل صوتك هنا")
    if audio_value:
        st.success("✅ تم تسجيل الصوت، جاري معالجته...")
        # هنا يمكنك تحويل الصوت إلى نص باستخدام Whisper

# ============================================================
# مربع الكتابة الرئيسي
# ============================================================
prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")

if prompt and not st.session_state.processing:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing = True
    st.rerun()

# ============================================================
# معالجة الرد من الذكاء الاصطناعي
# ============================================================
if st.session_state.processing and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    st.session_state.processing = False

    with st.spinner("نبراس يفكر..."):
        reply = get_ai_response(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
