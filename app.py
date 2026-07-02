import streamlit as st
from openai import OpenAI

# إعداد واجهة الصفحة
st.set_page_config(page_title="سند", page_icon="🌵")

# سحب المفتاح من الأسرار (Secrets) التي سنقوم بحفظها في إعدادات Streamlit
# تأكد أن اسم المفتاح في الأسرار هو "OPENAI_API_KEY"
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# هنا يمكنك البدء بإضافة واجهة التطبيق
st.title("تطبيق سند")
