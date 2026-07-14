import streamlit as st
from openai import OpenAI
from datetime import datetime
import pytz

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_real_date():
    tz = pytz.timezone('Asia/Riyadh')
    return datetime.now(tz).strftime("%A، %d %B %Y")

st.title("Nabras")

# حفظ المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# إدخال المستخدم
user_input = st.chat_input("اكتب رسالتك هنا...")

if user_input:
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # النظام (تحسين بسيط فقط)
    system_prompt = """
    لا تذكر التاريخ أو اليوم أو الوقت إلا إذا طلب المستخدم ذلك بشكل مباشر وصريح.
    إذا ظهرت كلمات مثل (اليوم، التاريخ، الوقت، الشهر، السنة) داخل سؤال لا يطلب فيه المستخدم التاريخ بشكل واضح، فلا تذكر التاريخ.
    لا تعتبر كلمة "اليوم" أو "التاريخ" طلبًا مستقلًا ما لم يقل المستخدم صراحة:
    - وش التاريخ
    - كم التاريخ
    - وش اليوم
    - أعطني التاريخ
    - أعطني اليوم
    ركّز دائمًا على سياق السؤال قبل الرد على أي كلمة لها علاقة بالوقت.
    إذا كان السؤال عن مباراة، حدث، موعد، أو شيء مستقبلي، فلا تذكر تاريخ اليوم الحالي إلا إذا كان جزءًا من الإجابة المطلوبة.
    """

    # إرسال الطلب للنموذج
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    bot_reply = response.output[0].content[0].text

    # عرض رد نبراس
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)
