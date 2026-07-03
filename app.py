import streamlit as st
from openai import OpenAI

# إعدادات نهائية ثابتة
st.set_page_config(
    page_title="نبراس - Nibras",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# واجهة مريحة وثابتة
st.markdown("""
<style>
* {direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;}
#MainMenu, footer, header {display: none !important;}
.stApp {background: #f7f9fc; max-width: 900px; margin: 0 auto;}
.header {background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin: 20px 0;}
.header h1 {color: #2563eb; margin: 0; font-size: 28px;}
.chat {margin: 30px 10px 120px;}
.msg {padding: 16px 20px; margin: 12px 0; border-radius: 18px; max-width: 85%; line-height: 1.7; font-size: 16px;}
.user {background: #2563eb; color: white; margin-left: auto;}
.bot {background: white; border: 1px solid #e2e8f0; margin-right: auto; box-shadow: 0 1px 5px rgba(0,0,0,0.03);}
.input-box {position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 95%; max-width: 850px; background: white; border-radius: 12px; padding: 20px; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);}
.stButton>button {background: #2563eb; color: white; border: none; border-radius: 8px; padding: 10px 30px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# اتصال آمن
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("⚠️ أضف مفتاحك في إعدادات Streamlit أولاً")
    st.stop()
client = OpenAI(api_key=API_KEY)

# محتوى التطبيق
st.markdown('<div class="header"><h1>💬 نبراس — مساعدك الذكي</h1><p>اسألني أي شيء وسأجيبك بوضوح تام</p></div>', unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = [{"role":"assistant", "content":"أهلاً وسهلاً بك! أنا نبراس، سأجيبك دائماً بكل دقة ووضوح، ولن أتردد في الإجابة أبداً."}]

st.markdown('<div class="chat">', unsafe_allow_html=True)
for m in st.session_state.chat:
    st.markdown(f'<div class="msg {m["role"]}">{m["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="input-box">', unsafe_allow_html=True)
inp = st.text_input("", placeholder="اكتب سؤالك هنا بكل سهولة...", label_visibility="collapsed")
if st.button("إرسال السؤال") and inp.strip():
    st.session_state.chat.append({"role":"user", "content":inp.strip()})
    with st.spinner("أجهز إجابتي لك..."):
        res = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role":"system","content":"أنت نبراس، مساعد ذكي شامل. أجب دائماً باللغة العربية الواضحة. ممنوع تماماً قول «لا أعرف» أو «راجع المصادر». أجب بثقة واكتمال عن أي سؤال في أي مجال."}, *st.session_state.chat],
            temperature=0.7,
            max_tokens=500
        )
        st.session_state.chat.append({"role":"assistant", "content":res.choices[0].message.content})
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
