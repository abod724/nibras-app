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

# -------------------------- تصميم الواجهة العربية --------------------------
st.markdown("""
<style>
* {direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, sans-serif;}
.stApp {background: #f8fafc; color: #1e293b;}
.main-title {font-size: 36px; font-weight: bold; color: #165DFF; margin: 20px 0 10px;}
.subtitle {font-size: 16px; color: #64748b; margin-bottom: 30px;}
.box {background: white; padding: 20px; border-radius: 12px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);}
.user {background: #EFF6FF; border-right: 4px solid #3B82F6;}
.btn {background: #165DFF; color: white; font-weight: bold; border-radius: 10px; padding: 10px 20px; border: none;}
.btn:hover {background: #0F4CD0;}
</style>
""", unsafe_allow_html=True)

# -------------------------- رأس الصفحة --------------------------
st.markdown("""
<h1 class="main-title">🤖 مساعد سند</h1>
<p class="subtitle">اسألني وأجيبك بإيجاز ووضوح، أنا مساعدك الخاص</p>
""", unsafe_allow_html=True)

# -------------------------- إدخال السؤال --------------------------
user_text = st.text_input("✍️ اكتب سؤالك هنا:", placeholder="اسألني أي سؤال...")

# -------------------------- تسجيل الصوت --------------------------
st.markdown("### 🎤 أو اسأل بصوتك:")
audio_input = st.audio_input("اضغط لتسجيل سؤالك")

if audio_input:
    with st.spinner("جاري تحويل الصوت لنص..."):
        try:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_input,
                language="ar"
            )
            user_text = result.text
            st.success(f"✅ تم تسجيل سؤالك: {user_text}")
        except Exception as e:
            st.error(f"❌ خطأ في الصوت: {str(e)}")

# -------------------------- إرسال والحصول على الرد --------------------------
if st.button("📤 إرسال", type="primary") and user_text.strip():
    with st.spinner("جاري التفكير..."):
        try:
            # تعليمات ثابتة للمساعد
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
                    أنت مساعد ذكي اسمك **سند**.
                    1. أجب بإيجاز واختصار شديد، لا تطل ولا تكثر الكلام أبداً.
                    2. لا تقل لي اذهب لجوجل ولا لمصادر خارجية، أجب بنفسك دائماً.
                    3. إذا سألتك عن اسمك فقل اسمي سند، مساعدك الخاص.
                    4. تحدث باللغة العربية الفصحى البسيطة، وكن واضحاً ومباشراً.
                    """},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.5,
                max_tokens=500
            )
            answer = response.choices[0].message.content

            # عرض السؤال والرد
            st.markdown(f'<div class="box user"><strong>سؤالك:</strong><br>{user_text}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box"><strong>الرد:</strong><br>{answer}</div>', unsafe_allow_html=True)

            # تحويل الرد لصوت
            with st.spinner("جاري إعداد الرد الصوتي..."):
                speech = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=answer,
                    response_format="mp3"
                )
                audio_b64 = base64.b64encode(speech.content).decode('utf-8')
                st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                st.success("🔊 يمكنك الاستماع للرد")

        except Exception as e:
            st.error(f"❌ خطأ: {str(e)}")

# -------------------------- ملاحظة --------------------------
st.markdown("---")
st.info("🔒 أنا مساعدك سند، أجيبك بسرعة واختصار دائماً.")
