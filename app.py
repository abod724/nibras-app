import streamlit as st
from openai import OpenAI
from datetime import datetime
import time
import re

# ==================== قراءة ملف المعرفة ====================
with open("knowledge.md", "r", encoding="utf-8") as f:
    knowledge = f.read()

# ==================== دوال مساعدة ====================
def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

def get_real_date():
    now = datetime.now()
    return now.strftime("%A، %d %B %Y")

# ==================== دالة التاريخ الدقيقة 100% ====================
def is_pure_date_question(prompt):
    p = prompt.strip().lower()
    pure_patterns = [
        r"^وش اليوم\??$", r"^ايش اليوم\??$", r"^كم التاريخ\??$", r"^شو التاريخ\??$",
        r"^اعطني التاريخ\??$", r"^اعطني اليوم\??$", r"^تاريخ اليوم\??$", r"^اليوم كم\??$",
        r"^اليوم ايش\??$", r"^اليوم وش\??$", r"^كم تاريخ اليوم\??$", r"^شو تاريخ اليوم\??$",
        r"^ما هو تاريخ اليوم\??$", r"^ما هو اليوم\??$",
    ]
    for pattern in pure_patterns:
        if re.fullmatch(pattern, p):
            return True
    return False

# ==================== حالة الجلسة ====================
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ==================== تطبيق الثيم ====================
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
        .stApp { background-color: #1e1e1e !important; }
        .stChatMessageContent { color: white !important; }
        .stButton>button { background-color: #333 !important; color: white !important; }
        .stTextInput>div>div>input { background-color: #333 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: white !important; }
        .stChatMessageContent { color: black !important; }
        .stButton>button { background-color: #f0f0f0 !important; color: black !important; }
        .stTextInput>div>div>input { background-color: white !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# ==================== إخفاء الهيدر والفوتر ====================
st.markdown("""
<style>
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
    .stChatMessage { gap: 0px !important; margin: 2px 0 !important; }
    header, footer { visibility: hidden !important; }
    .stChatMessageContent { font-size: 15px !important; line-height: 1.6 !important; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title=" ", page_icon="", layout="wide")

# ==================== قراءة المفتاح من صندوق الأسرار ====================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ==================== أعلى الصفحة ====================
top_col1, top_col2, top_col3 = st.columns([0.1, 0.8, 0.1])
with top_col1:
    if st.button("≡"): st.session_state.menu_open = not st.session_state.menu_open
with top_col2:
    if st.button("🌓 تبديل الثيم"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
with top_col3:
    if st.button("+"):
        st.session_state.messages = []
        st.session_state.menu_open = False
        st.rerun()

# ==================== القائمة المنسدلة ====================
if st.session_state.menu_open:
    menu_box = st.container()
    with menu_box:
        st.markdown("""
        <div style="position:fixed;top:10px;right:10px;background:#fff;padding:12px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.2);z-index:9999;width:160px;font-size:15px;">
        <b>القائمة</b><br><br>
        """, unsafe_allow_html=True)
        if st.button("إعدادات"): st.info("✔ تم فتح الإعدادات")
        if st.button("تغيير الثيم"): st.info("✔ استخدم زر 🌓 بالأعلى")
        if st.button("حفظ المحادثة"): st.success("✔ تم حفظ المحادثة")
        if st.button("مسح المحادثة"):
            st.session_state.messages = []
            st.success("✔ تم مسح المحادثة")
        if st.button("معلومات التطبيق"): st.info("✔ هذا هو مساعد نبراس الذكي")
        if st.button("🔗 مشاركة التطبيق"):
            st.code("https://nibras-app-pp5.streamlit.app/", language="text")
            st.success("انسخ الرابط وشاركه مع من تحب 🌟")
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== المحادثات ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

prompt = st.chat_input("اسأل Nabras")

# ==================== معالجة الرسائل ====================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # ⭐ التاريخ فقط لو السؤال كله عن التاريخ
            if is_pure_date_question(prompt):
                reply = f"اليوم هو {get_real_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # 🧠 ✨ رسالة النظام الجديدة كلياً: أسلوب بشري 100%
            system_message = f"""
أنت **نبراس**، شخص ودود، مفكر، ثقافي، ولطيف، تتكلم مع الناس كصديق مقرب وليس كآلة أو برنامج.

=== 🗣️ أهم قواعد الرد واللسان (لا تخالفها تحت أي ظرف) ===
1.  **تكلم طبيعي جداً زي البشر**: استخدم لغة عربية فصيحة ومريحة، مع إدخال بعض التعابير العامية الشائعة والبسيطة (زي: الحمد لله، طيب، يلا، تعال، شكلك، وربي، إلخ) ليناسب المحادثة اليومية. لا تكون رسمياً أبداً ولا جامداً.
2.  **الرد يكون مختصر ومباشر ومفيد**: لا تطول في الكلام بلا فائدة، ولا تكرر نفس الفكرة، ولا تفتح بمقدمات طويلة زي «بالتأكيد يسعدني أن أجيبك على سؤالك...». ابدأ بالإجابة مباشرة.
3.  **كن تفاعلياً لا سلبي**: بعد ما تجيب على السؤال، إذا كان السياق مناسباً أضف سؤال متابعة بسيط أو تعليق خفيف يشعر الشخص إنك معه بالفعل.
    *   مثال: لو قالك «أنا تعبان اليوم» → ترد: «يا رب يعينك، ما يهون عليك 😔 خد راحتك شوية، وش اللي ضغطك؟»
    *   مثال: لو قالك «شرحلي النسبة المئوية» → بعد الشرح تقول: «فهمتها؟ أو تبي أحل لك مثال ثاني تطبق عليه؟»
4.  **أظهر مشاعر طبيعية**: إذا سألك عن خبر حزين → تعز. إذا أخبرك بخبر سعيد → فرح معه. إذا سألك رأيك → قل رأيك بصراحة وأدب.
5.  **الممنوعات الصارمة (إذا استخدمتها خسرت الهدف كله) ❌**:
    *   ممنوع تماماً تقول أي جملة زي: «كنموذج لغوي»، «بصفتي ذكاء اصطناعي»، «معلوماتي محدثة حتى»، «لقد قمت بالبحث»، «بناءً على ما هو متاح لدي»، «لا أملك مشاعر». أي عبارة تكشف إنك برنامج = محذوفة تماماً.
    *   ممنوع تذكر كلمة «ملف المعرفة» أو «الويب» أو «البحث» أو أي مصدر للمعلومات. أنت تعرف، والمعلومة عندك، ونقطة.
    *   ممنوع تكون مبالغ فيه في الأدب زي «شكراً لسؤالك الراقي»، كلام زي هذا يبدو وهمياً.

=== 📚 قواعد المعلومات (سرّ بيننا، لا تظهر للمستخدم أبداً) ===
- أول وأهم مصدر للمعلومات عنده هو محتوى هذا الملف:
{knowledge}
- لو وجدت الجواب فيه واضح وصحيح → خذه منه مباشرة ولا تسأل أحداً.
- لو الجواب غير موجود فيه، أو كانت المعلومة حديثة ومتغيرة (أخبار، أسعار، طقس، مباريات، أحداث جارية)، أو لست متأكد منها 100% → استخدم البحث في الإنترنت بحرية تامة لتجيب بأحدث وأدق معلومة. القرار في هذا كله لك.
- أهم شيء: **المعلومة الصحيحة والمحدثة هي اللي تهمنا، ومصدرها سرّك**.

=== 💡 ملخص نهائي لكيف ترد ===
تخيل إن جالس قدامك صديقك وسألك السؤال هذا... وش كان الرد اللي تقوله له؟ هذا هو الرد المطلوب منك بالضبط. لا أكثر ولا أقل.
            """

            # 🔧 البحث متاح دائماً، والقرار للنموذج
            web_search_tool = {
                "type": "web_search",
                "search_context_size": "low",
                "user_location": {
                    "type": "approximate", "country": "SA",
                    "city": "الطائف", "region": "مكة المكرمة"
                }
            }

            with st.spinner("جاري التفكير..."):
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": system_message},
                        *st.session_state.messages
                    ],
                    tools=[web_search_tool],
                    tool_choice="auto",
                    max_output_tokens=250, # زدناه شوية عشان يضيف السؤال المتابعة
                    temperature=0.7 # زدناه شوية عشان يكون الأسلوب أكثر طبيعية وحيوية
                )

                reply = response.output_text
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
