import streamlit as st
from openai import OpenAI
import base64

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="مساعد سند",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- قراءة المفتاح الآمنة --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("⚠️ المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

client = OpenAI(api_key=API_KEY)

import streamlit as st
from openai import OpenAI
import base64

# ------------------ إعداد الصفحة ------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ المفتاح ------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("أضف مفتاح OpenAI داخل secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ------------------ التصميم ------------------
st.markdown("""
<style>
.stApp{
    background-color:#111827;
    color:white;
}

.main-title{
    text-align:center;
    font-size:40px;
    font-weight:bold;
    margin-bottom:5px;
}

.sub-title{
    text-align:center;
    color:#9ca3af;
    margin-bottom:30px;
}

.chat-box{
    background:#1f2937;
    padding:15px;
    border-radius:18px;
    margin-bottom:15px;
}

.user-box{
    border-right:4px solid #3b82f6;
}

.ai-box{
    border-right:4px solid #10b981;
}
</style>
""", unsafe_allow_html=True)

# ------------------ المحادثات ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ القائمة الجانبية ------------------
with st.sidebar:
    st.title("☰ نبراس")

    if st.button("✏️ محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# ------------------ العنوان ------------------
st.markdown(
    '<div class="main-title">نبراس</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">تحدث مع نبراس</div>',
    unsafe_allow_html=True
)

# ------------------ عرض المحادثات ------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-box user-box"><b>أنت:</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-box ai-box"><b>نبراس:</b><br>{msg["content"]}</div>',
            unsafe_allow_html=True
        )

# ------------------ الصوت ------------------
audio = st.audio_input("🎤")

voice_text = ""

if audio:
    try:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            language="ar"
        )
        voice_text = result.text
        st.success(f"تم التعرف على الصوت: {voice_text}")
    except:
        st.error("تعذر تحويل الصوت.")

# ------------------ الإدخال ------------------
prompt = st.chat_input("تحدث مع نبراس")

if voice_text:
    prompt = voice_text

# ------------------ إرسال ------------------
if prompt:

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    messages = [
        {
            "role": "system",
            "content": """
أنت مساعد ذكي اسمك نبراس.

تساعد الناس في:
- البر والكشتات.
- الحلال والمواشي.
- الصيد والطيور المهاجرة.
- الأسئلة العامة.

تجيب بأدب واحترام.

لا تستخدم العنصرية أو التعصب.

إذا لم تكن متأكدًا من معلومة فقل:
لا أملك معلومات مؤكدة حالياً.

إذا سئلت عن اسمك فقل:
اسمي نبراس.
"""
        }
    ]

    messages.extend(st.session_state.messages)

    with st.spinner("يفكر نبراس..."):

        response = client.chat.completions.create(
            model="gpt-5",
            messages=messages
        )

        answer = response.choices[0].message.content

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()

# ------------------ آخر رد صوتي ------------------
if st.session_state.messages:
    last = st.session_state.messages[-1]

    if last["role"] == "assistant":
        try:
            speech = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=last["content"],
                response_format="mp3"
            )

            audio_b64 = base64.b64encode(
                speech.content
            ).decode()

            st.audio(
                f"data:audio/mp3;base64,{audio_b64}"
            )

        except:
            pass
