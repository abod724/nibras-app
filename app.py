import streamlit as st
from openai import OpenAI

# -------------------------- إعدادات ثابتة نهائية --------------------------
st.set_page_config(
    page_title="نبراس - Nibras",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------- تصميم واجهة ثابتة وجاهزة للنشر --------------------------
st.markdown("""
<style>
* {direction: rtl; text-align: right; font-family: 'Cairo', 'Segoe UI', sans-serif;}
#MainMenu, footer, header {display: none !important;}
.stApp {background: #f8fafc; max-width: 900px; margin: 0 auto;}

/* العنوان */
.header {padding: 20px; text-align: center; border-bottom: 1px solid #e2e8f0; background: white; border-radius: 0 0 16px 16px;}
.header h1 {margin: 0; color: #1d4ed8; font-size: 28px; font-weight: 700;}
.header p {margin: 5px 0 0; color: #64748b; font-size: 15px;}

/* المحادثة */
.chat {margin: 20px 10px 120px;}
.msg {padding: 15px 20px; margin: 12px 0; border-radius: 20px; max-width: 85%; line-height: 1.7; font-size: 16px;}
.user {background: #2563eb; color: white; margin-left: auto; border-bottom-right-radius: 5px;}
.bot {background: white; border: 1px solid #e2e8f0; margin-right: auto; border-bottom-left-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);}

/* مربع الإدخال */
.input-area {position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 95%; max-width: 850px; background: white; border-radius: 50px; padding: 15px 25px; box-shadow: 0 4px 15px rgba(37,99,235,0.08);}
.stButton>button {background: #2563eb; color: white; border: none; border-radius: 20px; padding: 8px 25px; font-weight: bold; font-size: 15px;}
</style>
""", unsafe_allow_html=True)

# -------------------------- الاتصال الرسمي الآمن --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("⚠️ التطبيق جاهز، سيتم تشغيله بعد إضافة المفتاح")
    st.stop()
client = OpenAI(api_key=API_KEY)

# -------------------------- محتوى الواجهة --------------------------
st.markdown('<div class="header"><h1>نبراس 💬</h1><p>مساعدك الذكي الشامل — اسألني أي شيء</p></div>', unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = [{"role":"assistant", "content":"أهلاً وسهلاً بك في نبراس! أنا مساعدك الذكي، يمكنك سؤالي عن أي معلومة، وسأجيب لك بكل دقة ووضوح."}]

st.markdown('<div class="chat">', unsafe_allow_html=True)
for m in st.session_state.chat:
    st.markdown(f'<div class="msg {m["role"]}">{m["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="input-area">', unsafe_allow_html=True)
inp = st.text_input("", placeholder="اكتب سؤالك هنا...", label_visibility="collapsed")
if st.button("إرسال") and inp.strip():
    st.session_state.chat.append({"role":"user", "content":inp.strip()})
    with st.spinner("أجيبك فوراً..."):
        res = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role":"system","content":"أنت نبراس، مساعد ذكي شامل. أجب دائماً باللغة العربية الواضحة والبسيطة. لا تقل أبداً «لا أعرف» أو «راجع المصادر». تغطي كل المجالات: معلومات عامة، رياضة، تاريخ، تقنية، وغيرها. تحدث بثقة واكتمال."}, *st.session_state.chat],
            temperature=0.7,
            max_tokens=500
        )
        st.session_state.chat.append({"role":"assistant", "content":res.choices[0].message.content})
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
