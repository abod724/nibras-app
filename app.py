import streamlit as st
from openai import OpenAI

# ---------------- إعداد الصفحة ----------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- المفتاح ----------------
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("⚠️ لم يتم العثور على مفتاح OpenAI في Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ---------------- التصميم ----------------
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp {
    background: white;
}

.title {
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:#111827;
    margin-top:15px;
}

.sub {
    text-align:center;
    color:#6b7280;
    margin-bottom:25px;
}

[data-testid="stChatInput"]{
    max-width:750px;
    margin:auto;
}

[data-testid="stChatInput"] textarea{
    border-radius:30px !important;
    min-height:55px !important;
    max-height:55px !important;
    border:1px solid #d1d5db !important;
}

section[data-testid="stSidebar"]{
    background:#f8fafc;
}
</style>
""", unsafe_allow_html=True)

# ---------------- الشريط الجانبي ----------------
with st.sidebar:
    st.title("نبراس")

    if st.button("✏️ محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# ---------------- العنوان ----------------
st.markdown(
    '<div class="title">نبراس</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub">مساعدك الذكي</div>',
    unsafe_allow_html=True
)

# ---------------- المحادثات ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- الإدخال ----------------
prompt = st.chat_input("اسأل نبراس...")

# ---------------- إرسال الرسالة ----------------
if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    messages = [
        {
            "role": "system",
            "content": """
أنت مساعد ذكي اسمك نبراس.

تساعد المستخدمين في:
- البر والكشتات.
- الحلال والمواشي.
- الصيد والطيور المهاجرة.
- الأسئلة العامة.

أجب باختصار.
كن مؤدباً دائماً.
لا تستخدم العنصرية أو التعصب.
إذا لم تعرف معلومة فقل: لا أملك معلومات مؤكدة حالياً.
إذا سئلت عن اسمك فقل: اسمي نبراس.
"""
        }
    ]

    messages.extend(st.session_state.messages)

    with st.spinner("يفكر نبراس..."):

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_completion_tokens=150
        )

        answer = response.choices[0].message.content

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()
