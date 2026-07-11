import streamlit as st
from openai import OpenAI
import os
import time
import random
import base64

st.set_page_config(page_title="نبراس Pro", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# ================================================================
# 1. المفتاح والعميل
# ================================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ================================================================
# 2. الذاكرة والإعدادات
# ================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "أنت نبراس Pro، صديق ذكي ومبدع، تجيب بأسلوب فريد."},
                                 {"role": "assistant", "content": "✨ مرحباً، أنا نبراس Pro. كيف يمكنني إلهامك اليوم؟"}]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#ffffff"
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = True

# ================================================================
# 3. دوال إبداعية
# ================================================================
def get_time():
    return time.strftime("%I:%M %p")

def random_quote():
    quotes = [
        "💡 الإبداع هو الذكاء الذي يمرح.",
        "🚀 المستقبل لمن يؤمن بجمال أحلامه.",
        "🌟 كن أنت التغيير الذي تريد رؤيته.",
        "🎯 النجاح ليس نهائياً، والفشل ليس قاتلاً.",
        "🧠 العقل العظيم يطرح الأسئلة العظيمة."
    ]
    return random.choice(quotes)

def analyze_sentiment(text):
    words = text.split()
    positive = ["حلو", "جميل", "رائع", "ممتاز", "سعيد", "أحب", "شكراً"]
    negative = ["سيء", "حزين", "مزعج", "غبي", "كره", "تعبت"]
    pos = sum(1 for w in words if w in positive)
    neg = sum(1 for w in words if w in negative)
    if pos > neg:
        return "😊 إيجابي"
    elif neg > pos:
        return "😞 سلبي"
    return "😐 محايد"

# ================================================================
# 4. مترجم لغة عين (في نافذة منبثقة)
# ================================================================
def عين_مترجم():
    st.markdown("### 🧠 مترجم لغة عين")
    st.caption("اكتب كوداً بلغة عربية (عين) وسيترجم إلى بايثون وينفذ.")
    st.components.v1.html("""
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"></script>
      <style>
        body { font-family: sans-serif; direction: rtl; background: transparent; padding: 10px; }
        textarea { width: 100%; height: 100px; font-family: monospace; }
        #الناتج { background: #fff; padding: 10px; margin-top: 10px; border: 1px solid #ccc; white-space: pre; }
        button { padding: 8px 16px; margin-top: 8px; margin-left: 5px; }
      </style>
    </head>
    <body>
    <textarea id="كود_عين">متغير العدد = 5
إذا (العدد > 3) {
  اطبع "العدد أكبر من 3"
} آخر {
  اطبع "العدد صغير"
}</textarea><br>
    <button onclick="شغل()">▶️ ترجمة وتشغيل</button>
    <button onclick="احفظ()">💾 حفظ الكود</button>
    <div id="الناتج"></div>
    <script>
    let جاهز = loadPyodide();

    async function شغل() {
      const كود = document.getElementById("كود_عين").value;
      let بايثون = كود;
      بايثون = بايثون.replace(/متغير\s+(\w+)\s*=\s*(.+)/g, "$1 = $2");
      بايثون = بايثون.replace(/اطبع\s+\"(.+?)\"/g, 'print("$1")');
      بايثون = بايثون.replace(/إذا\s*\((.+?)\)\s*\{/g, "if ($1):");
      بايثون = بايثون.replace(/\}\s*آخر\s*\{/g, "else:");
      بايثون = بايثون.replace(/\u0643\u0631\u0631 من (\d+) إلى (\d+)\s*\{/g, "for i in range($1, $2+1):");
      بايثون = بايثون.replace(/\}/g, "");
      let أسطر = بايثون.split("\n");
      let مسافة = "";
      let نتيجة = "";
      for (let سطر of أسطر) {
        سطر = سطر.trim();
        if (سطر.endsWith(":")) { نتيجة += مسافة + سطر + "\n"; مسافة += "    "; }
        else { نتيجة += مسافة + سطر + "\n"; }
      }
      const بايثون_جاهز = await جاهز;
      try {
        await بايثون_جاهز.runPythonAsync(`\n${نتيجة}`);
        document.getElementById("الناتج").innerText = "✅ تم التنفيذ بنجاح";
      } catch (خطأ) {
        document.getElementById("الناتج").innerText = "❌ خطأ: " + خطأ;
      }
    }
    function احفظ() {
      const كود = document.getElementById("كود_عين").value;
      const ملف = new Blob([كود], { type: "text/plain" });
      const رابط = document.createElement("a");
      رابط.href = URL.createObjectURL(ملف);
      رابط.download = "الكود.ain";
      رابط.click();
    }
    </script>
    </body>
    </html>
    """, height=400, scrolling=True)

# ================================================================
# 5. الشريط الجانبي (اللوحة الإبداعية)
# ================================================================
with st.sidebar:
    st.markdown("### ✨ نبراس Pro")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": "أنت نبراس Pro، صديق ذكي ومبدع."},
                                     {"role": "assistant", "content": "✨ مرحباً، أنا نبراس Pro. كيف يمكنني إلهامك اليوم؟"}]
        st.rerun()
    
    st.markdown("### 📋 المحادثات السابقة")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history[::-1]):
            if st.button(f"💬 محادثة {i+1}", key=f"side_{i}"):
                st.session_state.messages = chat
                st.rerun()
    else:
        st.info("لا توجد محادثات")
    
    st.markdown("---")
    
    # إبداعات جانبية
    st.markdown("### 🎨 إبداعات")
    if st.button("🎲 اقتباس تحفيزي", use_container_width=True):
        st.info(random_quote())
    
    if st.button("📊 تحليل المشاعر", use_container_width=True):
        if len(st.session_state.messages) > 1:
            last_user = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
            if last_user:
                st.info(f"المشاعر: {analyze_sentiment(last_user)}")
            else:
                st.warning("اكتب شيئاً أولاً")
        else:
            st.warning("لا توجد رسائل")
    
    st.markdown("### ⚙️ التخصيص")
    st.session_state.bg_color = st.selectbox("لون الخلفية", ["#ffffff", "#f5f0eb", "#f0f4f8"])
    st.session_state.sound_enabled = st.checkbox("🔊 تفعيل الصوت", value=st.session_state.sound_enabled)
    
    st.markdown("---")
    with st.expander("🧠 مترجم لغة عين", expanded=False):
        عين_مترجم()

# ================================================================
# 6. CSS الإبداعي
# ================================================================
st.markdown(f"""
<style>
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stApp {{ background: {st.session_state.bg_color}; transition: background 0.5s ease; }}
    .chat-container {{ max-width: 800px; margin: 20px auto; padding: 0 20px; }}
    
    .msg-user {{
        padding: 12px 18px;
        margin: 6px 0 6px auto;
        background: #e9ecef;
        border-radius: 20px 20px 4px 20px;
        max-width: 75%;
        width: fit-content;
        animation: slideInRight 0.3s ease;
    }}
    .msg-bot {{
        padding: 12px 18px;
        margin: 6px auto 6px 0;
        background: #ffffff;
        border-radius: 20px 20px 20px 4px;
        max-width: 75%;
        width: fit-content;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        animation: slideInLeft 0.3s ease;
    }}
    
    @keyframes slideInRight {{
        from {{ opacity: 0; transform: translateX(30px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    @keyframes slideInLeft {{
        from {{ opacity: 0; transform: translateX(-30px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    .stChatInput {{
        border-radius: 40px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 4px 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02) !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 760px !important;
        max-width: 94% !important;
        z-index: 999 !important;
        transition: all 0.3s ease;
    }}
    .stChatInput:focus-within {{
        box-shadow: 0 4px 30px rgba(0,0,0,0.06) !important;
    }}
    .stChatInput input {{
        border-radius: 40px !important;
        padding: 14px 18px !important;
        font-size: 15px !important;
        background: transparent !important;
    }}
    .stChatInput button {{
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 6px 14px !important;
        color: white !important;
        transition: 0.2s;
    }}
    .stChatInput button:hover {{
        transform: scale(1.05);
        background: #333 !important;
    }}
    
    .suggestion-chips {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: center;
        margin: 10px 0 20px 0;
    }}
    .suggestion-chip {{
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 30px;
        padding: 6px 16px;
        font-size: 13px;
        cursor: pointer;
        transition: 0.2s;
        color: #1a1a1a;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }}
    .suggestion-chip:hover {{
        background: #f0f0f0;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }}
    
    .time-badge {{
        font-size: 10px;
        color: #aaa;
        margin-top: 4px;
        display: block;
    }}
    
    .copy-btn {{
        background: transparent;
        border: none;
        font-size: 14px;
        cursor: pointer;
        color: #aaa;
        padding: 2px 8px;
        border-radius: 12px;
        transition: 0.2s;
        float: left;
    }}
    .copy-btn:hover {{
        background: #f0f0f0;
        color: #1a1a1a;
    }}
</style>
""", unsafe_allow_html=True)

# ================================================================
# 7. عرض المحادثة مع وقت وزر نسخ
# ================================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"""
        <div class="msg-bot">
            {msg["content"]}
            <span class="time-badge">{get_time()}</span>
            <button class="copy-btn" onclick="navigator.clipboard.writeText(`{msg["content"]}`)">📋 نسخ</button>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================================================================
# 8. اقتراحات ذكية تحت مربع الكتابة
# ================================================================
suggestions = ["💡 كيف أبدأ مشروعي؟", "🚀 ما هي أحدث أخبار التقنية؟", "🎨 أعطني فكرة إبداعية", "📚 كيف أتعلم البرمجة؟", "🧠 ما هو الذكاء الاصطناعي؟"]
cols = st.columns(len(suggestions))
for i, col in enumerate(cols):
    with col:
        if st.button(suggestions[i], key=f"sug_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestions[i]})
            st.rerun()

# ================================================================
# 9. أيقونة تفاعلية فوق مربع الكتابة
# ================================================================
col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    if st.button("✨", key="sparkle_icon", help="لمسة إبداعية"):
        st.info(random_quote())

# ================================================================
# 10. مربع الإدخال الرئيسي
# ================================================================
prompt = st.chat_input("اكتب سؤالك الإبداعي هنا...", key="main_chat")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("نبراس Pro يفكر بإبداع..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=600
                )
                reply = response.output_text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.chat_history.append(st.session_state.messages.copy())
                
                if st.session_state.sound_enabled:
                    try:
                        speech = client.audio.speech.create(
                            model="tts-1",
                            voice="alloy",
                            input=reply[:300],
                            response_format="mp3"
                        )
                        audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                        st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                    except:
                        pass
                
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
