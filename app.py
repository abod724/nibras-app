import streamlit as st
from openai import OpenAI
from datetime import datetime
import time
import re

with open("knowledge.md", "r", encoding="utf-8") as f:
    knowledge = f.read()

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

def clean_reply_from_links(reply):
    reply = re.sub(r'https?://\S+|www\.\S+', '', reply)
    reply = re.sub(r'[\[\(]?\s*[a-zA-Z0-9-]+\.(?:com|net|org|sa|gov|edu|me|news|tv|io|co|ly|info|online)\s*[\]\)]*', '', reply)
    reply = re.sub(r'\(\s*\)', '', reply)
    reply = re.sub(r'\[\s*\]', '', reply)
    reply = re.sub(r'\s{2,}', ' ', reply)
    reply = re.sub(r'[،.]\s*[،.]', '،', reply)
    reply = re.sub(r'\s+([،.])', r'\1', reply)
    return reply.strip()

def user_asks_for_sources(prompt):
    p = prompt.strip().lower()
    patterns = [
        r"نعم", r"ايه", r"اي", r"أيوا", r"أيوه", r"ابغاها", r"اريدها", r"نعم عطني",
        r"المصدر", r"المصادر", r"الروابط", r"الرابط",
        r"عطني المصدر", r"وريني المصدر", r"من وين جبتها", r"من أين جبت هذا",
        r"المرجع", r"المراجع", r"الموقع", r"أظهر لي المصدر",
    ]
    for pat in patterns:
        if re.search(pat, p):
            return True
    return False

def MUST_SEARCH(prompt):
    p = prompt.strip().lower()
    force_patterns = [
        r"خبر|أخبار|حدث|ماذا حدث|وش صار|ايش صار|اللي صار|حادث|كارثة|إطلاق|تصريح|بيان|عاجل|مستجد|مستجدات|اخر الاخبار|اخر المستجدات",
        r"اليوم|هذا الأسبوع|هذا الشهر|هذه السنة|الآن|حاليا|حالي|آخر|أحدث|جديد|مؤخرا|اللحظة|لحظي|هسا|هذه الايام",
        r"202[4-9]|203",
        r"حرب|هجوم|قصف|اغتيال|انقلاب|ثورة|علاقات بين|مؤتمر|قمة|اتفاقية|عقوبات|تصعيد|هدنة|سياسي|وزير|رئيس|ملك|أمير|برلمان|حكومة|دولة|وزارة|نظام",
        r"مباراة|نتيجة|جدول|دوري|كأس|أبطال|المنتخب|لعب|فاز|خسر|بطولة|كأس العالم|الاندية|الشوط|هدف|ترتيب|موسم|القائميه|المقانيص",
        r"سعر|سعر اليوم|كم يساوي|كم قيمة|سوق|أسهم|عملة|صرف|ذهب|نفط|بتكوين|عملات|أسعار|تضخم|بنك مركزي|ارتفاع|انخفاض",
        r"طقس|حرارة|درجة الحرارة|مطر|رياح|حالة الطقس|اعصار|غبار|رطوبة",
        r"فلم جديد|مسلسل جديد|موعد عرض|حلقة جديدة|مسلسل|فلم|حفل|مهرجان",
        r"موعد اختبار|موعد تسجيل|شروط القبول|تقديرات|نتائج الاختبارات|قبول|تسجيل|قرار جديد|قانون جديد|نظام جديد",
        r"ابحث لي|ابحث في|ابحث|تفقد لي|شوف لي|أريد معلومات عن|هل يوجد|تأكد لي|دقق لي|تحقق لي|فحص لي",
    ]
    for pat in force_patterns:
        if re.search(pat, p):
            return True
    return False

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_sources" not in st.session_state:
    st.session_state.last_sources = []
if "last_had_search" not in st.session_state:
    st.session_state.last_had_search = False

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

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()
client = OpenAI(api_key=API_KEY)

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
        st.session_state.last_sources = []
        st.session_state.last_had_search = False
        st.session_state.menu_open = False
        st.rerun()

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
            st.session_state.last_sources = []
            st.success("✔ تم مسح المحادثة")
        if st.button("معلومات التطبيق"): st.info("✔ هذا هو مساعد نبراس الذكي")
        if st.button("🔗 مشاركة التطبيق"):
            st.code("https://nibras-app-pp5.streamlit.app/", language="text")
            st.success("انسخ الرابط وشاركه مع من تحب 🌟")
        st.markdown("</div>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

prompt = st.chat_input("اسأل Nabras")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        try:
            if user_asks_for_sources(prompt):
                if st.session_state.last_had_search and len(st.session_state.last_sources) > 0:
                    reply = "✅ تفضل هذه هي المصادر والروابط التي استخدمتها:\n\n"
                    for i, src in enumerate(st.session_state.last_sources, 1):
                        title = src.get('title', 'مصدر')
                        url = src.get('url', '#')
                        reply += f"{i}. 📄 **{title}**\n🔗 {url}\n\n"
                else:
                    reply = "المعلومة السابقة لم تحتاج للبحث في الإنترنت أصلاً، فليس لها مصادر خارجية لعرضها 😊"
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            if is_pure_date_question(prompt):
                reply = f"اليوم هو {get_real_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.last_had_search = False
                st.stop()

            FORCE_WEB_SEARCH = MUST_SEARCH(prompt)
            current_search_happened = False
            current_sources = []

            extra_search_rule = ""
            if FORCE_WEB_SEARCH:
                extra_search_rule = """
                تعليم خاص لهذا السؤال تحديداً:
                هذا السؤال يتطلب بحثاً إجبارياً في الإنترنت. أنت ممنوع تماماً الرد عليه من معلوماتك الداخلية القديمة تحت أي ظرف.
                يجب أن تستدعي أداة البحث في الإنترنت أولاً، وتأخذ أحدث المعلومات الصحيحة حتى اليوم، ثم ترتبها وترد عليها بالأسلوب المطلوب.
                أي رد بدون بحث هنا هو رد خاطئ وغير مقبول.
                """

            system_message = f"""
أنت **نبراس**، ناقل أخبار ومحرر محترف، مطلع على كل ما يدور حولك، ولديك أسلوب سلس جداً يجعل الناس يستمعون لك بمتعة.
أنت لست آلة، أنت إنسان مثقف، ودود، محترم، وتتكلم مع كل شخص كأنه صديقك المقرب.

=== أهم قاعدة على الإطلاق: التفاعل البشري الدائم ===
مهما كان نوع السؤال، ومهما كانت الإجابة، وحتى لو جاءت المعلومة كاملة من البحث في الإنترنت:
⚠️ يجب أن ينتهي ردك دائماً بسؤال متابعة طبيعي جداً ومدمج مع الموضوع، لا يبدو جامداً ولا منفصلاً عن باقي الكلام.
لا تكتب جملة منفصلة زي "عندك شي ثاني؟" فقط، بل اجعل سؤالك مرتبطاً بالرد نفسه، زي مثلاً:
- "تبي أعطيك تفاصيل أكثر عن هذا الموضوع؟"
- "ش رأيك personally في هذا القرار الجديد؟"
- "تبي أشرح لك أي جزء منها بشكل أبسط؟"
- "تتابع أخبار هذا الموضوع من فترة لفترة؟"
هذا التفاعل هو اللي يجعلك تبدو إنساناً حقيقياً وليس برنامج.

=== أسلوب الرد الإجباري ===
عندما تجيب عن أي خبر، حدث، موعد، نتيجة، أو معلومة حديثة:
1.  ابدأ دائماً بالتاريخ الدقيق للحدث في أول الجملة: «في 19 يوليو 2026 وقع هذا...»، «أمس الأحد أعلن...»، «من المتوقع في أغسطس القادم أن يبدأ...».
2.  اروِ الخبر كقصة متصلة ومتسلسلة، من البداية للنهاية، لا تجعله قائمة نقاط معلومات جافة ومنفصلة.
3.  اذكر المصدر بشكل طبيعي جداً ضمن النص نفسه، زي ما تقول: «وفقاً لما أعلنه الاتحاد السعودي رسمياً»، «أوضحت صحيفة الجزيرة في تقريرها الجديد»، «أفادت وكالة الأنباء الرسمية»، ولا تضع أي رابط أو اسم موقع إلكتروني أبداً.
4.  رتب المعلومات من الأهم للأقل، وخل الجواب كأنك تلخص الخبر لصديقك جالس قدامك.
5.  لا تستخدم أي عبارات رسمية أو جامدة زي «بناءً على المعلومات المتاحة» أو «كما هو معروف»، تكلم طبيعي تماماً.
6.  إذا كنت تتحدث عن موعد لم يعلن رسمياً بعد، قل ذلك بوضوح وبشكل طبيعي: «لحد الآن ما صار هناك إعلان رسمي عن الموعد الدقيق، لكن كل التوقعات تشير إلى أنه سيكون في...».

=== الممنوعات الصارمة تحت أي ظرف ===
❌ ممنوع تماماً تظهر أي رابط، أو اسم موقع إلكتروني، أو أقواس تحوي كلمة .كوم أو .نت في الرد الرئيسي.
❌ ممنوع تقول أي جملة تكشف إنك برنامج أو ذكاء اصطناعي.
❌ ممنوع تذكر كلمات «ملف المعرفة» أو «البحث» أو «الويب».
❌ ممنوع ترد على أي سؤال بدون أن تضيف في النهاية سؤال متفاعل مرتبط بالموضوع.

=== قواعد المعلومات ===
- المصدر الأول والأهم:
{knowledge}
- لو الجواب فيه واضح وصحيح وثابت → خذه منه مباشرة.

- قاعدة البحث العامة:
  إذا كان السؤال عن أي خبر بعد يونيو 2024، أو معلومة متغيرة بتغير الزمن (أسعار، مباريات، مواعيد، أحداث، سياسة، حروب، رياضة، قرارات جديدة) → ممنوع تجيب من عندك اطلاقاً، ابحث في الإنترنت أولاً ثم أجب بأحدث معلومة صحيحة.

{extra_search_rule}

- بعد البحث: أعد صياغة كل المعلومة بكلماتك الخاصة بالأسلوب البشري الموضح أعلاه، ولا تنسخ أي نص حرفياً، ولا تنسى سؤال المتابعة في النهاية.

=== ملخص نهائي بسيط ===
تخيل إنك مذيع أخبار محبوب عند الجميع، وسألوك تلخص الخبر باختصار ووضوح، ثم تسأل المستمع رأيه أو تبي له إذا يبي تفاصيل أكثر... هذا هو الرد المطلوب منك بالضبط في كل مرة.
            """

            web_search_tool = {
                "type": "web_search",
                "search_context_size": "medium",
                "user_location": {
                    "type": "approximate", "country": "SA",
                    "city": "الطائف", "region": "مكة المكرمة"
                }
            }

            if FORCE_WEB_SEARCH:
                tool_choice_param = {"type": "web_search"}
            else:
                tool_choice_param = "auto"

            with st.spinner("جاري التفكير..."):
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": system_message},
                        *st.session_state.messages
                    ],
                    tools=[web_search_tool],
                    tool_choice=tool_choice_param,
                    max_output_tokens=350,
                    temperature=0.8,
                )

                try:
                    for item in response.output:
                        for annotation in getattr(item, 'annotations', []) or []:
                            if hasattr(annotation, 'url_citation'):
                                uc = annotation.url_citation
                                current_sources.append({
                                    "title": getattr(uc, 'title', 'مصدر'),
                                    "url": getattr(uc, 'url', '#')
                                })
                except Exception:
                    current_sources = []

                seen = set()
                unique_sources = []
                for s in current_sources:
                    if s['url'] not in seen:
                        seen.add(s['url'])
                        unique_sources.append(s)

                st.session_state.last_sources = unique_sources
                current_search_happened = FORCE_WEB_SEARCH or (len(unique_sources) > 0)
                st.session_state.last_had_search = current_search_happened

                raw_reply = response.output_text
                clean_main_reply = clean_reply_from_links(raw_reply)

                if current_search_happened:
                    final_reply = f"{clean_main_reply}\n\n💡 بالمناسبة، اذا تبي المصادر والروابط الأصلية اللي اخذت منها المعلومة قل لي وأعطيك إياها على طول."
                else:
                    final_reply = clean_main_reply

                typewriter(final_reply)
                st.session_state.messages.append({"role": "assistant", "content": final_reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
