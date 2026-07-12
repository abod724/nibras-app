"""
🤖 نبراس - المساعد الذكي
بحث قوقل + صوت + صور + تصميم أبيض نظيف
"""
import streamlit as st
from openai import OpenAI
from googlesearch import search as google_search
import base64

# ═══════════════════════════════════════════
# 1) إعدادات الصفحة
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="نبراس - المساعد الذكي",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# 2) استدعاء المفتاح من صندوق الأسرار
# ═══════════════════════════════════════════
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود! أضفه في ملف .streamlit/secrets.toml")
    st.stop()

# ═══════════════════════════════════════════
# 3) التنسيقات (CSS أبيض نظيف)
# ═══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');

* { font-family: 'IBM Plex Sans Arabic', sans-serif; }

.stApp {
    background: #ffffff;
    color: #0d0d0d;
}

#MainMenu, footer, header { visibility: hidden; }

section[data-testid="stSidebar"] {
    background: #f9f9f9;
    border-left: 1px solid #e5e5e5;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #0d0d0d;
    font-size: 0.95rem;
}

[data-testid="stChatMessage"] {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 8px 0;
    max-width: 760px;
    margin: 0 auto;
}

[data-testid="stChatMessageContent"] {
    color: #0d0d0d;
    font-size: 16px;
    line-height: 1.75;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #f7f7f8;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 6px auto;
}

[data-testid="stChatInput"] {
    max-width: 760px;
    margin: 0 auto;
    border-radius: 28px;
    border: 1px solid #e5e5e5;
    background: #ffffff;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
[data-testid="stChatInput"]:focus-within {
    border-color: #0d0d0d;
    box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid #e5e5e5;
    background: #ffffff;
    color: #0d0d0d;
    font-weight: 500;
    transition: all 0.15s;
}
.stButton > button:hover {
    background: #f7f7f8;
    border-color: #d0d0d0;
}

.source-link {
    display: inline-block;
    background: #f7f7f8;
    color: #2563eb;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 3px 12px;
    margin: 3px 2px;
    font-size: 0.82rem;
    text-decoration: none;
    transition: all 0.15s;
}
.source-link:hover {
    background: #eff6ff;
    border-color: #2563eb;
}

.brand {
    text-align: center;
    padding: 1rem 0 0.5rem;
}
.brand h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0d0d0d;
    margin: 0;
}
.brand p {
    color: #8e8e8e;
    font-size: 0.88rem;
    margin-top: 0.2rem;
}

.divider {
    border: none;
    border-top: 1px solid #f0f0f0;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 4) الشريط الجانبي - الإعدادات + القائمة
# ═══════════════════════════════════════════
with st.sidebar:
    if st.button("➕  محادثة جديدة", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.sources = []
        st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    model = st.selectbox("🧠 النموذج", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    temperature = st.slider("🌡️ الإبداع", 0.0, 2.0, 0.7, 0.1)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    with st.expander("☰  القائمة"):
        web_search = st.toggle("🌐 بحث قوقل", value=True)
        search_count = st.slider("عدد النتائج", 3, 10, 5, key="sc")
        system_prompt = st.text_area(
            "شخصية المساعد",
            value="أنت نبراس، مساعد ذكي احترافي تجيب بالعربية بوضوح. عند توفّر نتائج بحث استخدمها كمرجع واذكر المصادر بأرقام [1].",
            height=90
        )
        if st.button("🗑️ مسح المحادثة", use_container_width=True):
            st.session_state.messages = []
            st.session_state.sources = []
            st.rerun()

    st.caption(f"💬 الرسائل: {len(st.session_state.get('messages', []))}")

# ═══════════════════════════════════════════
# 5) دوال مساعدة
# ═══════════════════════════════════════════
def search_google(query, max_results=5):
    """بحث قوقل مباشر"""
    try:
        results = list(google_search(query, num_results=max_results, advanced=True))
        if not results:
            return None, []
        context_parts, sources = [], []
        for i, r in enumerate(results, 1):
            title = getattr(r, "title", "")
            desc = getattr(r, "description", "")
            url = getattr(r, "url", str(r))
            context_parts.append(f"[{i}] {title}\n{desc}\nالرابط: {url}")
            sources.append({"title": title, "url": url})
        return "\n\n".join(context_parts), sources
    except Exception:
        return None, []

def image_to_base64(uploaded_file):
    """تحويل الصورة المرفوعة إلى base64"""
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

# ═══════════════════════════════════════════
# 6) الشعار
# ═══════════════════════════════════════════
st.markdown("""
<div class="brand">
    <h1>🤖 نبراس</h1>
    <p>اسألني أي شيء</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 7) تهيئة المحادثة
# ═══════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""

# ═══════════════════════════════════════════
# 8) عرض الرسائل السابقة
# ═══════════════════════════════════════════
for idx, msg in enumerate(st.session_state.messages):
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and idx < len(st.session_state.sources) and st.session_state.sources[idx]:
            links = "".join(
                f'<a class="source-link" href__="{s["url"]}" target="_blank">🔗 {s["title"][:45]}</a>'
                for s in st.session_state.sources[idx]
            )
            st.markdown(f"**📎 المصادر:**<br>{links}", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# 9) شاشة ترحيب + أزرار سريعة
# ═══════════════════════════════════════════
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("أهلاً 👋 كيف أقدر أساعدك؟")

    suggestions = ["📰 آخر الأخبار", "📈 أسعار الأسهم", "⚽ نتائج المباريات", "💡 اكتب لي كود"]
    cols = st.columns(len(suggestions))
    for i, s in enumerate(suggestions):
        with cols[i]:
            if st.button(s, key=f"s{i}", use_container_width=True):
                st.session_state.pending_prompt = s

# ═══════════════════════════════════════════
# 10) رفع صورة + إدخال صوتي + نص
# ═══════════════════════════════════════════
uploaded_image = st.file_uploader("📷 رفع صورة", type=["png", "jpg", "jpeg"], key="img")

prompt = st.chat_input("اكتب رسالتك هنا...")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = ""

# ═══════════════════════════════════════════
# 11) معالجة الرد
# ═══════════════════════════════════════════
if prompt or uploaded_image:

    if not API_KEY:
        st.error("🔴 مفتاح OpenAI غير موجود!")
        st.stop()

    user_text = prompt or "اشرح هذه الصورة"

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_text)

    with st.chat_message("assistant", avatar="🤖"):
        try:
            client = OpenAI(api_key=API_KEY)

            search_context = None
            sources = []
            if web_search and not uploaded_image:
                with st.spinner("🌐 أبحث في قوقل..."):
                    search_context, sources = search_google(user_text, search_count)

            messages_for_api = [{"role": "system", "content": system_prompt}]

            if search_context:
                messages_for_api.append({
                    "role": "system",
                    "content": f"نتائج بحث قوقل:\n{search_context}\n\nاستخدمها كمرجع واستشهد بالمصادر [1] [2]."
                })

            if uploaded_image:
                b64 = image_to_base64(uploaded_image)
                messages_for_api.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                })
            else:
                messages_for_api.extend(st.session_state.messages[-10:])

            stream = client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                temperature=temperature,
                stream=True,
                max_tokens=4096
            )
            response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

            while len(st.session_state.sources) < len(st.session_state.messages):
                st.session_state.sources.append([])
            st.session_state.sources[len(st.session_state.messages) - 1] = sources

            if sources:
                links = "".join(
                    f'<a class="source-link" href__="{s["url"]}" target="_blank">🔗 {s["title"][:45]}</a>'
                    for s in sources
                )
                st.markdown(f"**📎 المصادر:**<br>{links}", unsafe_allow_html=True)

        except Exception as e:
            err = str(e).lower()
            if "api_key" in err:
                st.error("❌ مفتاح API غير صالح")
            elif "rate_limit" in err:
                st.error("⏳ تجاوزت الحد، انتظر دقيقة")
            else:
                st.error(f"❌ {e}")
