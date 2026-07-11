import streamlit as st
from openai import OpenAI
import os
import time
import base64

# ===== إعدادات الصفحة =====
st.set_page_config(page_title="نبراس X", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ===== المفتاح =====
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ===== الذاكرة =====
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = True

# ===== دوال مساعدة =====
def get_time():
    return time.strftime("%I:%M %p")

# ===== مترجم لغة عين =====
def عين_مترجم():
    st.markdown("### 🧠 مترجم لغة عين")
    st.components.v1.html("""
    <html>
    <head><script src="https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"></script>
    <style>body{direction:rtl;background:transparent;padding:10px;}
    textarea{width:100%;height:100px;font-family:monospace;}
    #الناتج{background:#fff;padding:10px;margin-top:10px;border:1px solid #ccc;white-space:pre;}
    button{padding:8px 16px;margin-top:8px;margin-left:5px;}</style>
    </head>
    <body>
    <textarea id="كود_عين">متغير العدد = 5
إذا (العدد > 3) {
  اطبع "العدد أكبر من 3"
} آخر {
  اطبع "العدد صغير"
}</textarea><br>
    <button onclick="شغل()">▶️ ترجمة</button>
    <button onclick="احفظ()">💾 حفظ</button>
    <div id="الناتج"></div>
    <script>
    let جاهز = loadPyodide();
    async function شغل() {
      let ك = document.getElementById("كود_عين").value;
      let ب = ك.replace(/متغير\s+(\w+)\s*=\s*(.+)/g,"$1 = $2")
               .replace(/اطبع\s+\"(.+?)\"/g,'print("$1")')
               .replace(/إذا\s*\((.+?)\)\s*\{/g,"if ($1):")
               .replace(/\}\s*آخر\s*\{/g,"else:")
               .replace(/\u0643\u0631\u0631 من (\d+) إلى (\d+)\s*\{/g,"for i in range($1, $2+1):")
               .replace(/\}/g,"");
      let أس = ب.split("\n"), م="", ن="";
      for (let س of أس) {
        س = س.trim();
        if (س.endsWith(":")) { ن += م + س + "\n"; م += "    "; }
        else { ن += م + س + "\n"; }
      }
      const ج = await جاهز;
      try { await ج.runPythonAsync(`\n${ن}`); document.getElementById("الناتج").innerText="✅ تم التنفيذ"; }
      catch (خ) { document.getElementById("الناتج").innerText="❌ "+خ; }
    }
    function احفظ() {
      const ك = document.getElementById("كود_عين").value;
      const ف = new Blob([ك], {type:"text/plain"});
      const ر = document.createElement("a");
      ر.href = URL.createObjectURL(ف);
      ر.download = "الكود.ain";
      ر.click();
    }
    </script>
    </body>
    </html>
    """, height=380, scrolling=True)

# ===== الشريط الجانبي =====
with st.sidebar:
    st.markdown("### ⚡ نبراس X")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history.append(st.session_state.messages.copy())
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
    st.session_state.sound_enabled = st.checkbox("🔊 الصوت", value=st.session_state.sound_enabled)
    with st.expander("🧠 مترجم لغة عين", expanded=False):
        عين_مترجم()

# ===== الشريط العلوي (بدون اسم نبراس) =====
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #ffffff; }
.chat-container { max-width: 800px; margin: 20px auto; padding: 0 20px; }
.msg-user {
    padding: 10px 16px; margin: 6px 0 6px auto; background: #e9ecef;
    border-radius: 18px 18px 4px 18px; max-width: 75%; width: fit-content;
}
.msg-bot {
    padding: 10px 16px; margin: 6px auto 6px 0; background: #f8f9fa;
    border-radius: 18px 18px 18px 4px; max-width: 75%; width: fit-content;
    border: 1px solid #e5e5e5;
}
.time-badge { font-size: 10px; color: #aaa; margin-top: 4px; display: block; }
.stChatInput {
    border-radius: 30px !important; border: 1px solid #e5e5e5 !important;
    background: #ffffff !important; padding: 4px 16px !important;
    position: fixed !important; bottom: 20px !important; left: 50% !important;
    transform: translateX(-50%) !important;
    width: 760px !important; max-width: 94% !important; z-index: 999 !important;
}
.stChatInput input { border-radius: 30px !important; padding: 12px 16px !important; font-size: 15px !important; }
.stChatInput button { background: #1a1a1a !important; border-radius: 50% !important; padding: 6px 14px !important; color: white !important; }
.suggestion-chips { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin: 6px 0 16px 0; }
.suggestion-chip {
    background: white; border: 1px solid #e5e5e5; border-radius: 30px;
    padding: 4px 14px; font-size: 13px; cursor: pointer; transition: 0.2s;
    color: #1a1a1a;
}
.suggestion-chip:hover { background: #f0f0f0; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# ===== عرض المحادثة =====
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== الخيارات =====
suggestions = ["💡 مشروع جديد", "🚀 أخبار التقنية", "🎨 فكرة إبداعية", "📚 تعلم البرمجة", "🧠 الذكاء الاصطناعي"]
st.markdown('<div class="suggestion-chips">', unsafe_allow_html=True)
cols = st.columns(len(suggestions))
for i, col in enumerate(cols):
    with col:
        if st.button(suggestions[i], key=f"chip_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": suggestions[i]})
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ===== مربع الكتابة =====
prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("نبراس يفكر..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=500
                )
                reply = response.output_text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                if st.session_state.sound_enabled:
                    try:
                        speech = client.audio.speech.create(model="tts-1", voice="alloy", input=reply[:300], response_format="mp3")
                        audio_b64 = base64.b64encode(speech.content).decode()
                        st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                    except: pass
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ {str(e)}")
