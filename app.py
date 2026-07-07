import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
from serpapi import GoogleSearch
import concurrent.futures
import time

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- المفاتيح --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
SERPAPI_API_KEY = st.secrets.get("SERPAPI_API_KEY")

if not API_KEY:
    st.error("⚠️ المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

if not SERPAPI_API_KEY:
    st.warning("⚠️ مفتاح SerpAPI غير مضاف، البحث في الإنترنت لن يعمل")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- دالة البحث المحسنة --------------------------
def search_google(query):
    """بحث في قوقل مع timeout"""
    if not SERPAPI_API_KEY:
        return ""
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(_do_search, query)
            try:
                result = future.result(timeout=8)
                return result if result else ""
            except concurrent.futures.TimeoutError:
                return "⏱️ انتهى وقت البحث، سأجيب من معرفتي."
    except Exception as e:
        return ""

def _do_search(query):
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": 5
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        snippets = []
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                snippet = result.get("snippet", "")
                title = result.get("title", "")
                if snippet:
                    snippets.append(f"• {title}: {snippet}")
        
        if snippets:
            return "\n".join(snippets)
        return ""
    except Exception as e:
        return ""

# -------------------------- CSS (واجهة بيضاء وسوداء) --------------------------
st.markdown("""
<style>
* {
    direction: rtl;
    text-align: right;
    font-family: 'Segoe UI', Tahoma, sans-serif;
}
.stApp {
    background: #ffffff;
    color: #1a1a1a;
}
#MainMenu, footer, header {visibility: hidden;}

.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    padding: 10px 20px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.top-center p {
    margin: 0;
    font-size: 13px;
    color: #6b7280;
}
.chat-area {
    max-width: 850px;
    margin: 70px auto 100px;
    padding: 8px 5px 20px;
}
.msg {
    padding: 12px 16px;
    margin: 6px 0;
    border-radius: 16px;
    max-width: 80%;
    line-height: 1.6;
    font-size: 15px;
}
.user {
    background: #1a1a1a;
    color: #ffffff;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.bot {
    background: #f3f4f6;
    color: #1a1a1a;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}
div[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 2px 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
div[data-testid="stChatInput"] input {
    color: #1a1a1a !important;
    font-weight: 500 !important;
    background: #ffffff !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 15px !important;
}
div[data-testid="stChatInput"] input::placeholder {
    color: #9ca3af !important;
}
div[data-testid="stChatInput"] button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border-radius: 50% !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- الشريط العلوي --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)
col_left, col_center, col_right = st.columns([1.2, 2, 1.2])

with col_left:
    if st.button("✏️ جديد", help="بدء محادثة جديدة"):
        st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]
        st.rerun()

with col_center:
    st.markdown(
        """
        <div class="top-center">
            <p>مساعدك الذكي – بسيط، سريع، واضح</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_right:
    with st.popover("📋 المحادثات السابقة"):
        if "all_chats" not in st.session_state:
            st.session_state.all_chats = []
        if st.session_state.all_chats:
            for i, c in enumerate(st.session_state.all_chats):
                if st.button(f"محادثة {i+1} - {c['date']}", use_container_width=True):
                    st.session_state.chat_history = c["messages"]
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]

# عرض المحادثة
st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- مربع الكتابة --------------------------
user_input = st.chat_input(
    "اكتب سؤالك هنا...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf", "csv", "txt"],
    accept_audio=True
)

# -------------------------- معالجة الإدخال --------------------------
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})

        with st.spinner("🔍 جاري البحث والتفكير..."):
            try:
                # 1. البحث في قوقل (مع timeout)
                search_results = search_google(query)
                
                # 2. تحديد ما إذا كان هناك نتائج بحث
                has_search = search_results and "⏱️" not in search_results and "بحث" not in search_results
                
                # 3. تحضير النظام مع نتائج البحث
                if has_search:
                    system_prompt = f"""
أنت «نبراس» – مساعد ذكي، سريع، وأسلوبك بسيط وواضح.

🔥 **قاعدة أساسية**: استخدم معلومات البحث أدناه في إجابتك، لأنها أحدث من معرفتك.

📌 **نتائج البحث** (محدثة):
{search_results}

⚠️ إذا لم تكن المعلومات كافية، قل: «المعلومات محدودة، لكن بناءً على ما وجدت...»
"""
                else:
                    system_prompt = """
أنت «نبراس» – مساعد ذكي، سريع، وأسلوبك بسيط وواضح.

🎯 دورك:
- الإجابة عن الأسئلة العامة، التقنية، اليومية، التعليمية.
- استخدم نقاطاً مختصرة.
- اجعل الإجابة مباشرة قدر الإمكان.
- إذا لم تكن متأكداً، قل: «ليس لدي معلومة مؤكدة».
"""

                # 4. استدعاء النموذج
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.chat_history
                    ],
                    max_tokens=600,
                    temperature=0.7
                )

                answer = response.choices[0].message.content

                # 5. إضافة مصدر البحث إذا وجد
                if has_search:
                    answer += "\n\n🔍 *معلومات محدثة من البحث*"

                st.session_state.chat_history.append({"role": "assistant", "content": answer})

                # حفظ المحادثة
                if "all_chats" not in st.session_state:
                    st.session_state.all_chats = []
                st.session_state.all_chats.append({
                    "date": datetime.now().strftime("%H:%M - %d/%m"),
                    "messages": st.session_state.chat_history.copy()
                })

                # تحويل الرد إلى صوت (اختياري)
                try:
                    speech = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=answer[:500],  # اختصار للسرعة
                        response_format="mp3"
                    )
                    audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                    st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                except Exception:
                    pass

                st.rerun()

            except Exception as e:
                st.error(f"❌ حدث خطأ: {str(e)}")
                st.session_state.chat_history.pop()  # حذف رسالة المستخدم إذا فشل
