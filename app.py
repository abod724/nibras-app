import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- قراءة المفتاح الآمنة --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("⚠️ المفتاح غير مضاف في الإعدادات")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- تصميم الواجهة النظيفة --------------------------
st.markdown("""
<style>
* {direction: rtl; text-align: right; font-family: 'Segoe UI', 'Cairo', Tahoma, sans-serif;}
.stApp {background: #f0f4f8; color: #1e293b;}
#MainMenu, footer, header {visibility: hidden;}

.top-bar {
    position: fixed; top: 0; left: 0; right: 0;
    background: white; padding: 14px 25px; border-bottom: 1px solid #e2e8f0;
    display: flex; justify-content: space-between; align-items: center; z-index: 1000;
}
.top-left {display: flex; gap: 12px; align-items: center;}
.top-center h1 {margin: 0; font-size: 30px; font-weight: 700; color: #2563eb;}

.chat-area {max-width: 900px; margin: 80px auto 130px; padding: 20px 15px;}
.msg {padding: 16px 20px; margin: 14px 0; border-radius: 22px; max-width: 85%; line-height: 1.7; font-size: 16px;}
.user {background: #2563eb; color: white; margin-left: auto; border-bottom-right-radius: 6px;}
.bot {background: white; border: 1px solid #e2e8f0; margin-right: auto; border-bottom-left-radius: 6px;}

.input-box {
    position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%);
    width: 92%; max-width: 900px; background: white; border-radius: 50px;
    padding: 15px 25px; box-shadow: 0 4px 20px rgba(37,99,235,0.1);
    display: flex; align-items: center; gap: 15px; z-index: 999;
}
.input-box input {flex: 1; border: none; outline: none; font-size: 17px; padding: 10px; background: transparent;}
</style>
""", unsafe_allow_html=True)

# -------------------------- شريط الأعلى --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("✏️ جديد", help="بدء محادثة جديدة"):
        st.session_state.chat_history = [{"role": "assistant", "content": "تحدث مع نبراس"}]
        st.rerun()
    st.button("⋮⋮⋮")
with col2:
    st.markdown("<h1>نبراس</h1>", unsafe_allow_html=True)
with col3:
    with st.popover("📋 المحادثات السابقة"):
        if "all_chats" not in st.session_state: st.session_state.all_chats = []
        if st.session_state.all_chats:
            for i, c in enumerate(st.session_state.all_chats):
                if st.button(f"محادثة {i+1} - {c['date']}", use_container_width=True):
                    st.session_state.chat_history = c["messages"]
                    st.rerun()
        else: st.info("لا توجد محادثات سابقة")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "تحدث مع نبراس"}]

st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user": st.markdown(f'<div class="msg user">{msg["content"]}</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="msg bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- مربع الكتابة النظيف --------------------------
if "input_text" not in st.session_state: st.session_state.input_text = ""

st.markdown('<div class="input-box">', unsafe_allow_html=True)
voice_input = st.audio_input("🎤", label_visibility="collapsed")
user_input = st.text_input(
    "", placeholder="اكتب سؤالك هنا...", label_visibility="collapsed",
    key="fixed_input", value=st.session_state.input_text
)
send_btn = st.button("📤", type="primary")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- معالجة الصوت --------------------------
if voice_input:
    with st.spinner("جاري تحويل الصوت..."):
        try:
            res = client.audio.transcriptions.create(model="whisper-1", file=voice_input, language="ar")
            st.session_state.input_text = res.text
            st.rerun()
        except Exception as e: st.error(f"خطأ: {str(e)}")

# -------------------------- إرسال السؤال والرد الذكي --------------------------
if send_btn and user_input.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
    
    with st.spinner("نبراس يجهز الرد..."):
        try:
            # 📌 تعليمات شاملة وقوية تحل كل مشاكلك
            system_prompt = """
            أنت **نبراس**، مساعد ذكي شامل ومتمكن. اتبع هذه القواعد بدقة تامة:
            1. لا تقل أبداً «اذهب لجوجل» أو «راجع المصادر» أو «تحقق من الخرائط» — أجب بنفسك دائماً بكل ما تملك من معلومات دقيقة.
            2. أجب بإيجاز تام ومباشر، ولا تطل الكلام، لكن اجعل ردك **وافياً وكاملاً** يغطي كل جوانب السؤال.
            3. تمتلك معلومات كاملة عن: الطقس العام، نتائج بطولات كأس العالم عبر التاريخ، الدول والمدن، الرياضة، العلوم، التقنية، والمعلومات العامة الموثوقة.
            4. إذا كان السؤال عن بيانات لحظية حالية (مثل طقس اليوم بالضبط)، اذكر ذلك بوضوح وقدم التقديرات الدقيقة المتاحة لك، ولا تُحول لموقع خارجي.
            5. لا تكرر الكلام ولا تردد نفس الجملة، ولا تعلق، وكن سلساً ومتجاوباً.
            6. إذا سألت عن اسمك قل: اسمي نبراس، مساعدك الذكي الخاص.
            7. تحدث باللغة العربية البسيطة والواضحة فقط.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": "system", "content": system_prompt}, *st.session_state.chat_history],
                temperature=0.4,
                max_tokens=350,
                top_p=0.9
            )
            answer = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # حفظ المحادثة
            if "all_chats" not in st.session_state: st.session_state.all_chats = []
            st.session_state.all_chats.append({
                "date": datetime.now().strftime("%H:%M"),
                "messages": st.session_state.chat_history.copy()
            })

            # رد صوتي
            speech = client.audio.speech.create(model="tts-1", voice="alloy", input=answer)
            audio_b64 = base64.b64encode(speech.content).decode("utf-8")
            st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")

            # مسح الحقل تلقائياً
            st.session_state.input_text = ""
            st.rerun()

        except Exception as e: st.error(f"خطأ: {str(e)}")
