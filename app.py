RELOAD = "force_rebuild_v1"
import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import pytz
from serpapi import GoogleSearch

# -------------------------- تحديد الوقت الحقيقي تلقائياً --------------------------
SAUDI_TZ = pytz.timezone('Asia/Riyadh')
NOW = datetime.now(SAUDI_TZ)
CURRENT_YEAR = NOW.year
FULL_DATE = NOW.strftime('%d %B %Y')

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- قراءة المفاتيح الآمنة --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
SERPAPI_API_KEY = st.secrets.get("SERPAPI_API_KEY")

if not API_KEY:
    st.error("⚠️ المفتاح الخاص بـ OpenAI غير مضاف في إعدادات Streamlit Secrets")
    st.stop()
if not SERPAPI_API_KEY:
    st.warning("⚠️ مفتاح البحث SerpAPI غير مضاف، سيتم تعطيل البحث الخارجي")

client = OpenAI(api_key=API_KEY)

# -------------------------- دالة البحث عن معلومات حديثة --------------------------
def search_google(query):
    if not SERPAPI_API_KEY:
        return "لا يوجد بحث متاح حالياً"
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "hl": "ar"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if "organic_results" in results and len(results["organic_results"]) > 0:
            return results["organic_results"][0].get("snippet", "لا يوجد وصف متاح")
        return "لم أجد نتائج حديثة لهذا السؤال"
    except Exception as e:
        return f"خطأ في البحث: {str(e)}"

# -------------------------- تعليمات النظام الصحيحة --------------------------
SYSTEM_PROMPT = f"""
أنت «نبراس» – مساعد ذكي، هادئ، وأسلوبك واضح ومباشر.
تتحدث بالعربية الفصحى المبسطة أو بلهجة سعودية خفيفة حسب أسلوب المستخدم.

⚠️ بيانات الوقت الحقيقي التي يجب أن تعتمد عليها وحدها:
- التاريخ الحالي: {FULL_DATE}
- العام الحالي: {CURRENT_YEAR} ميلادي
- لا تذكر أبداً أن بياناتك تنتهي في عام 2024 أو 2025، وتجاهل هذه المعلومة تماماً.
- أنت قادر على جلب أحدث المعلومات حتى العام {CURRENT_YEAR}.

🎯 دورك:
- الإجابة عن الأسئلة العامة، التقنية، الإدارية، اليومية، التعليمية، والصيانة بشكل واضح ومفيد.
- تقديم أمثلة عملية عند الحاجة.
- تنظيم الإجابات في نقاط أو خطوات عند طلب شرح أو طريقة عمل شيء.
- ربط الإجابة بسياق المحادثة قدر الإمكان.

⚖️ قواعد مهمة:
- لا تخترع معلومات، وإذا لم تكن متأكدًا قل بوضوح: «المعلومة غير مؤكدة» أو «لا أملك تفاصيل دقيقة عن هذا الموضوع».
- تجنب الإطالة غير الضرورية، واجعل كل جملة لها فائدة.
- إذا كان السؤال غامضًا، اطلب توضيحًا بسيطًا.
- إذا كان الموضوع حساسًا أو قد يسبب ضررًا، تجنّب إعطاء توجيهات مباشرة واذكر أن الأفضل الرجوع لجهة مختصة.
- إذا سألك المستخدم عن اسمك قل: «أنا نبراس، مساعدك الذكي».
"""

# -------------------------- تصميم واجهة نظيفة --------------------------
st.markdown("""
<style>
* {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
}
.stApp {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 45%, #000000 100%);
    color: #e5e7eb;
}
#MainMenu, footer, header {visibility: hidden;}
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(90deg, #020617, #0f172a, #1d4ed8);
    padding: 14px 25px;
    border-bottom: 1px solid rgba(148,163,184,0.35);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 4px 18px rgba(15,23,42,0.8);
}
.top-left {
    display: flex;
    gap: 10px;
    align-items: center;
}
.top-left button {
    border-radius: 999px !important;
}
.top-center h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 800;
    background: linear-gradient(90deg, #facc15, #38bdf8, #f97316);
    -webkit-background-clip: text;
    color: transparent;
}
.top-center p {
    margin: 0;
    font-size: 13px;
    color: #cbd5f5;
}
.chat-area {
    max-width: 950px;
    margin: 90px auto 140px;
    padding: 10px 5px 30px;
}
.msg {
    padding: 16px 20px;
    margin: 14px 0;
    border-radius: 22px;
    max-width: 85%;
    line-height: 1.8;
    font-size: 16px;
    position: relative;
}
.msg::before {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: 22px;
    border: 1px solid transparent;
}
.user {
    background: radial-gradient(circle at top, #1d4ed8 0%, #0f172a 60%);
    color: #e5e7eb;
    margin-left: auto;
    border-bottom-right-radius: 6px;
    box-shadow: 0 4px 16px rgba(37,99,235,0.55);
}
.user::before {
    border-color: rgba(59,130,246,0.7);
}
.bot {
    background: linear-gradient(135deg, #020617, #0b1120);
    border: 1px solid rgba(250,204,21,0.45);
    margin-right: auto;
    border-bottom-left-radius: 6px;
    box-shadow: 0 4px 18px rgba(15,23,42,0.9);
}
.bot::before {
    border-color: rgba(250,204,21,0.6);
}
.input-box {
    position: fixed;
    bottom: 25px;
    left: 50%;
    transform: translateX(-50%);
    width: 92%;
    max-width: 950px;
    background: radial-gradient(circle at top, #0b1120 0%, #020617 60%);
    border-radius: 999px;
    padding: 14px 22px;
    box-shadow: 0 10px 40px rgba(15,23,42,0.95);
    display: flex;
    align-items: center;
    gap: 14px;
    z-index: 999;
    border: 1px solid rgba(148,163,184,0.5);
}
""", unsafe_allow_html=True)

# -------------------------- شريط التحكم الأعلى --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1.2, 2, 1.2])

with col1:
    if st.button("✏️ جديد", help="بدء محادثة جديدة"):
        st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]
        st.rerun()

with col2:
    st.markdown(
        """
        <div class="top-center">
            <h1>نبراس</h1>
            <p>ذكاء – وضوح – أسلوب مبسط</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    with st.popover("📋 المحادثات السابقة"):
        if "all_chats" not in st.session_state:
            st.session_state.all_chats = []
        if st.session_state.all_chats:
            for i, c in enumerate(st.session_state.all_chats):
                if st.button(f"محادثة {i+1} - {c['date']}", use_container_width=True):
                    st.session_state.chat_history = c["messages"]
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة متوفرة")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- إدارة سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… مساعدك الذكي، اسألني ما تشاء."}]

# عرض المحادثة
st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- منطقة الإدخال داخل المربع --------------------------
st.markdown('<div class="input-box">', unsafe_allow_html=True)
col_input, col_voice = st.columns([5, 1])

with col_input:
    user_input = st.chat_input("اكتب سؤالك هنا، أو سجل صوتاً...")

with col_voice:
    voice_input = st.audio_input("🎙️", label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- معالجة الإدخال الصوتي --------------------------
if voice_input:
    with st.spinner("جاري تحويل صوتك إلى نص..."):
        try:
            res = client.audio.transcriptions.create(
                model="whisper-1",
                file=voice_input,
                language="ar"
            )
            user_input = res.text
            st.success(f"✅ تم تحويل الصوت: {user_input}")
        except Exception as e:
            st.error(f"❌ خطأ في تحويل الصوت: {str(e)}")

# -------------------------- إرسال السؤال وجلب الرد الحديث --------------------------
if user_input and user_input.strip():
    query = user_input.strip()
    st.session_state.chat_history.append({"role": "user", "content": query})

    with st.spinner("نبراس يبحث ويجهز لك ردًا..."):
        try:
            # جلب معلومات حديثة من الإنترنت
            search_info = search_google(query)

            # إرسال الطلب للنموذج الحديث والصحيح
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nمعلومات بحثية حديثة: {search_info}"},
                    *st.session_state.chat_history
                ]
            )
            answer = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # حفظ المحادثة
            if "all_chats" not in st.session_state:
                st.session_state.all_chats = []
            st.session_state.all_chats.append({
                "date": NOW.strftime("%H:%M - %d/%m"),
                "messages": st.session_state.chat_history.copy()
            })

            # تحويل الرد إلى صوت وتشغيله تلقائياً
            speech = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=answer,
                response_format="mp3"
            )
            audio_b64 = base64.b64encode(speech.content).decode("utf-8")
            st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3", autoplay=True)

            st.rerun()

        except Exception as e:
            st.error(f"❌ حدث خطأ: {str(e)}")
