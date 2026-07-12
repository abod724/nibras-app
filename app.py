import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import re

# ─── إعدادات الصفحة ───
st.set_page_config(
    page_title="نبراس - المساعد الذكي",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── استدعاء المفتاح من صندوق الأسرار ───
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود! أضفه في ملف .streamlit/secrets.toml")
    st.stop()

# ─── التنسيق ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');

* { font-family: 'Tajawal', sans-serif; }

.stApp {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
}

.main { background: transparent; }

.header-title {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
}
.header-title h1 {
    background: linear-gradient(135deg, #10a37f 0%, #1aabd9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
}
.header-title p {
    color: #8e8ea0;
    font-size: 0.95rem;
    margin-top: 0.3rem;
}

[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    margin-bottom: 6px;
    padding: 14px 18px;
    backdrop-filter: blur(10px);
    transition: all 0.2s;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(16,163,127,0.2);
}

[data-testid="stChatMessageContent"] {
    color: #ececf1;
    font-size: 15.5px;
    line-height: 1.85;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(16,163,127,0.06);
    border-color: rgba(16,163,127,0.12);
}

[data-testid="stChatInput"] {
    border-radius: 24px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
}
[data-testid="stChatInput"]:focus-within {
    border-color: #10a37f;
    box-shadow: 0 0 0 3px rgba(16,163,127,0.15);
}

.source-link {
    display: inline-block;
    background: rgba(26,171,217,0.1);
    color: #1aabd9;
    border: 1px solid rgba(26,171,217,0.2);
    border-radius: 8px;
    padding: 2px 10px;
    margin: 2px;
    font-size: 0.8rem;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي ───
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    model = st.selectbox(
        "🧠 النموذج",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0
    )
    
    st.divider()
    
    web_search = st.toggle(
        "🌐 البحث بالويب",
        value=True,
        help="عند التفعيل: يبحث بالويب قبل الرد (محدّث بأحدث الأحداث)"
    )
    
    search_results_count = st.slider(
        "📄 عدد النتائج",
        min_value=3,
        max_value=10,
        value=5,
        help="عدد صفحات الويب للبحث عنها"
    )
    
    temperature = st.slider(
        "🌡️ درجة الإبداع",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )
    
    system_prompt = st.text_area(
        "📝 شخصية المساعد",
        value="أنت نبراس، مساعد ذكي احترافي ودود. تجيب باللغة العربية بشكل واضح ومفصل ومنظم. استخدم الإيموجي عند الحاجة.",
        height=110
    )
    
    st.divider()
    
    if st.button("🗑️ محادثة جديدة", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.sources = []
        st.rerun()

# ─── دالة البحث بالويب ───
def search_web(query, max_results=5):
    """البحث في الويب باستخدام DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return None, []
        
        context_parts = []
        sources = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            url = r.get("href", r.get("url", ""))
            
            context_parts.append(f"[{i}] العنوان: {title}\n    المحتوى: {body}\n    الرابط: {url}")
            if url:
                sources.append({"title": title, "url": url})
        
        context = "\n\n".join(context_parts)
        return context, sources
    
    except Exception as e:
        return None, []

# ─── العنوان ───
st.markdown("""
<div class="header-title">
    <h1>🧠 نبراس</h1>
    <p>مدعوم بالبحث المباشر بالويب 🌐</p>
</div>
""", unsafe_allow_html=True)

# ─── تهيئة المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []

# ─── عرض الرسائل السابقة ───
for idx, message in enumerate(st.session_state.messages):
    avatar = "🧑" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        
        if message["role"] == "assistant" and idx < len(st.session_state.sources) and st.session_state.sources[idx]:
            sources = st.session_state.sources[idx]
            if sources:
                st.markdown("**📎 المصادر:**")
                links_html = ""
                for s in sources:
                    links_html += f'<a class="source-link" href__="{s["url"]}" target="_blank">🔗 {s["title"][:50]}...</a>'
                st.markdown(links_html, unsafe_allow_html=True)

# ─── رسالة ترحيب ───
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("مرحباً 👋 أنا نبراس، مساعدك الذكي المحدّث بالويب!\n\nاسألني عن أي شيء وبه أحدث المعلومات 🌐")

# ─── الإدخال ───
prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    
    # ─── إضافة رسالة المستخدم ───
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    
    # ─── رد المساعد ───
    with st.chat_message("assistant", avatar="🤖"):
        try:
            client = OpenAI(api_key=API_KEY)
            
            search_context = None
            sources = []
            
            # ─── البحث بالويب ───
            if web_search:
                with st.spinner("🌐 أبحث في الويب..."):
                    search_context, sources = search_web(prompt, search_results_count)
            
            # بناء الرسائل للنموذج
            messages_for_api = [{"role": "system", "content": system_prompt}]
            
            if search_context:
                messages_for_api.append({
                    "role": "system",
                    "content": f"""🌐 نتائج البحث من الويب (محدّثة):
{search_context}

استخدم هذه المعلومات كمرجع أساسي للإجابة. اذكر المصادر بالأرقام [1], [2] إلخ. إذا كانت المعلومات غير كافية، أكمل من معرفتك."""
                })
            
            messages_for_api.extend(st.session_state.messages[-10:])
            
            # ─── Streaming ───
            stream = client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                temperature=temperature,
                stream=True,
                max_tokens=4096
            )
            
            response = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # حفظ المصادر
            while len(st.session_state.sources) < len(st.session_state.messages):
                st.session_state.sources.append([])
            st.session_state.sources[len(st.session_state.messages) - 1] = sources
            
            # عرض المصادر
            if sources:
                st.markdown("**📎 المصادر:**")
                links_html = ""
                for s in sources:
                    links_html += f'<a class="source-link" href__="{s["url"]}" target="_blank">🔗 {s["title"][:50]}...</a>'
                st.markdown(links_html, unsafe_allow_html=True)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "api_key" in error_msg or "auth" in error_msg:
                st.error("❌ مفتاح API غير صالح. تأكد من صحته في ملف الأسرار.")
            elif "rate_limit" in error_msg:
                st.error("⏳ تجاوزت حد الاستخدام. انتظر دقيقة وحاول مجدداً.")
            elif "model" in error_msg:
                st.error(f"❌ النموذج '{model}' غير متاح. جرب نموذج آخر.")
            else:
                st.error(f"❌ خطأ: {str(e)}")
