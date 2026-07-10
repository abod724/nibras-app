import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import re
import json
import os
from PIL import Image
import io
import time

# ============================================================
# 1. إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. المفتاح والعميل
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ============================================================
# 3. الذاكرة والجلسات
# ============================================================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "sessions" not in st.session_state:
    st.session_state.sessions = []

if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

memory = load_memory()

# ============================================================
# 4. CSS - واجهة متطورة مثل ChatGPT
# ============================================================
st.markdown("""
<style>
    /* إخفاء عناصر Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* خلفية الصفحة */
    .stApp {
        background: #f7f7f8;
    }
    
    /* شريط علوي أنيق */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(12px);
        padding: 8px 24px;
        border-bottom: 1px solid rgba(0,0,0,0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        height: 52px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    .top-bar .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 16px;
        font-weight: 500;
        color: #1a1a1a;
    }
    
    .top-bar .brand .icon {
        background: #1a1a1a;
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
    }
    
    .top-bar .actions {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .top-bar .actions button {
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 18px;
        padding: 6px;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #444;
        transition: 0.2s;
    }
    
    .top-bar .actions button:hover {
        background: #f0f0f0;
    }
    
    .top-bar .actions .menu-btn {
        font-size: 20px;
    }
    
    .top-bar .actions .new-btn {
        font-size: 18px;
        font-weight: 300;
        background: #f0f0f0;
        border-radius: 50%;
    }
    
    .top-bar .actions .new-btn:hover {
        background: #e5e5e5;
    }
    
    /* منطقة المحادثة */
    .chat-container {
        max-width: 750px;
        margin: 70px auto 90px;
        padding: 0 20px;
    }
    
    /* الرسائل - مثل ChatGPT تماماً */
    .msg-user {
        padding: 10px 16px;
        margin: 4px 0 8px auto;
        background: #e9ecef;
        border-radius: 18px;
        border-bottom-right-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        text-align: left;
        clear: both;
    }
    
    .msg-bot {
        padding: 10px 16px;
        margin: 4px auto 8px 0;
        background: #ffffff;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        text-align: left;
        clear: both;
    }
    
    .msg-bot code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .msg-bot pre {
        background: #f4f4f4;
        padding: 12px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 8px 0;
    }
    
    /* الصور في المحادثة */
    .chat-image {
        max-width: 280px;
        border-radius: 12px;
        margin: 6px 0;
        border: 1px solid #e5e5e5;
    }
    
    /* مؤشر الكتابة */
    .typing-indicator {
        display: inline-block;
        background: white;
        padding: 10px 18px;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin: 4px 0;
    }
    
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin: 0 3px;
        background: #aaa;
        border-radius: 50%;
        animation: pulse 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes pulse {
        0%, 60%, 100% { transform: scale(0.6); opacity: 0.4; }
        30% { transform: scale(1); opacity: 1; }
    }
    
    /* مربع الإدخال - أنيق */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 2px 12px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.02) !important;
    }
    
    .stChatInput input {
        border-radius: 30px !important;
        padding: 10px 16px !important;
        font-size: 15px !important;
        background: transparent !important;
    }
    
    .stChatInput button {
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 4px 12px !important;
        color: white !important;
        border: none !important;
        transition: 0.2s !important;
    }
    
    .stChatInput button:hover {
        transform: scale(1.03);
        background: #333 !important;
    }
    
    /* زر الصوت المنفصل */
    .audio-btn {
        position: fixed;
        bottom: 28px;
        right: 28px;
        background: #1a1a1a;
        color: white;
        border: none;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: 0.25s;
    }
    
    .audio-btn:hover {
        transform: scale(1.06);
        background: #333;
    }
    
    .audio-btn.recording {
        background: #e74c3c;
        animation: pulse-ring 1.5s infinite;
    }
    
    @keyframes pulse-ring {
        0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(231, 76, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
    }
    
    /* القائمة المنسدلة */
    .dropdown-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.2);
        z-index: 998;
        display: none;
    }
    
    .dropdown-overlay.active {
        display: block;
    }
    
    .dropdown-menu {
        position: fixed;
        top: 60px;
        left: 20px;
        background: white;
        border-radius: 14px;
        padding: 8px;
        z-index: 999;
        min-width: 220px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        display: none;
        border: 1px solid rgba(0,0,0,0.04);
    }
    
    .dropdown-menu.active {
        display: block;
    }
    
    .dropdown-menu .item {
        padding: 10px 14px;
        border-radius: 10px;
        cursor: pointer;
        font-size: 14px;
        transition: 0.15s;
        color: #1a1a1a;
    }
    
    .dropdown-menu .item:hover {
        background: #f5f5f5;
    }
    
    .dropdown-menu .divider {
        height: 1px;
        background: #e5e5e5;
        margin: 6px 10px;
    }
    
    /* تذييل */
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 12px;
        padding: 20px 0 10px;
        border-top: 1px solid #f0f0f0;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 5. الشريط العلوي المتطور
# ============================================================
st.markdown("""
<div class="top-bar">
    <div class="brand">
        <span class="icon">💬</span> نبراس
    </div>
    <div class="actions">
        <button class="menu-btn" onclick="toggleDropdown()">☰</button>
        <button class="new-btn" onclick="location.reload()">＋</button>
    </div>
</div>

<!-- خلفية القائمة -->
<div class="dropdown-overlay" id="overlay" onclick="closeDropdown()"></div>

<!-- القائمة المنسدلة -->
<div class="dropdown-menu" id="dropdown">
    <div class="item" onclick="location.reload()">➕ محادثة جديدة</div>
    <div class="divider"></div>
    <div class="item" id="sessionsList">📋 المحادثات السابقة</div>
</div>

<script>
function toggleDropdown() {
    document.getElementById('dropdown').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}
function closeDropdown() {
    document.getElementById('dropdown').classList.remove('active');
    document.getElementById('overlay').classList.remove('active');
}
</script>
""", unsafe_allow_html=True)

# عرض المحادثات السابقة في القائمة
with st.sidebar:
    st.markdown("### 📋 المحادثات")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]
        st.rerun()
    st.markdown("---")
    if st.session_state.sessions:
        for i, s in enumerate(st.session_state.sessions[::-1]):
            if st.button(f"💬 {s['date']}", key=f"side_{i}", use_container_width=True):
                st.session_state.messages = s["messages"]
                st.rerun()
    else:
        st.info("لا توجد محادثات سابقة")
st.sidebar.empty()

# ============================================================
# 6. عرض المحادثة (بدون أيقونات)
# ============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 7. استخراج الاسم
# ============================================================
if st.session_state.user_name is None:
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]["content"]
        match = re.search(r"اسمي\s+(\w+)", last_msg)
        if match:
            st.session_state.user_name = match.group(1)
            if st.session_state.user_name not in memory["users"]:
                memory["users"][st.session_state.user_name] = {"first_seen": datetime.now().isoformat()}
                save_memory(memory)
            st.session_state.messages.append(
                {"role": "assistant", "content": f"أهلاً {st.session_state.user_name}! سعيد برؤيتك 🤍"}
            )
            st.rerun()

# ============================================================
# 8. مربع الإدخال (مع رفع الصور)
# ============================================================
user_input = st.chat_input(
    "اكتب سؤالك... أو ارفع صورة",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "gif", "webp"]
)

# ============================================================
# 9. زر الصوت (منفصل)
# ============================================================
st.markdown("""
<button class="audio-btn" id="audioBtn" onclick="toggleRecording()">🎤</button>

<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

function toggleRecording() {
    const btn = document.getElementById('audioBtn');
    
    if (isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        btn.classList.remove('recording');
        btn.textContent = '🎤';
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.onload = function(e) {
                    const base64Audio = e.target.result.split(',')[1];
                    
                    fetch('/transcribe', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ audio: base64Audio })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.text) {
                            const input = document.querySelector('.stChatInput input');
                            input.value = data.text;
                            // تشغيل حدث الإدخال
                            const event = new Event('input', { bubbles: true });
                            input.dispatchEvent(event);
                            // محاكاة الضغط على Enter بعد 300ms
                            setTimeout(() => {
                                const btn = document.querySelector('.stChatInput button');
                                if (btn) btn.click();
                            }, 400);
                        }
                    });
                };
                reader.readAsDataURL(audioBlob);
                btn.textContent = '🎤';
                btn.classList.remove('recording');
                isRecording = false;
            };
            
            mediaRecorder.start();
            isRecording = true;
            btn.classList.add('recording');
            btn.textContent = '⏹️';
        })
        .catch(() => {
            alert('الرجاء السماح بالوصول إلى المايكروفون');
        });
}
</script>
""", unsafe_allow_html=True)

# ============================================================
# 10. معالجة الإدخال مع بحث ويب محدث وصور
# ============================================================
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
    # معالجة الملفات المرفوعة (صور)
    uploaded_images = []
    if hasattr(user_input, 'files') and user_input.files:
        for file in user_input.files:
            try:
                img_bytes = file.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode()
                uploaded_images.append({
                    "name": file.name,
                    "data": img_b64
                })
            except:
                pass
    
    # بناء رسالة المستخدم
    user_message = query
    if uploaded_images:
        if query:
            user_message += f"\n\n📷 صورة: {uploaded_images[0]['name']}"
        else:
            user_message = f"📷 صورة: {uploaded_images[0]['name']}"
    
    if user_message.strip():
        # إضافة للمحادثة وعرضها
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # عرض الصور
        for img in uploaded_images:
            st.image(f"data:image/png;base64,{img['data']}", width=250)
        
        # مؤشر الكتابة
        with st.chat_message("assistant"):
            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                # ===== بحث ويب محدث =====
                search_results = ""
                try:
                    search_response = client.responses.create(
                        model="gpt-4o-mini",
                        input=[{"role": "user", "content": f"ابحث عن: {query if query else 'وصف الصورة'}"}],
                        tools=[{"type": "web_search"}],
                        max_output_tokens=300
                    )
                    search_results = search_response.output_text
                except:
                    pass
                
                # ===== تحضير التعليمات =====
                system_prompt = f"""
                أنت نبراس، صديق ذكي ومتحدث لبق.

                ### شخصيتك:
                - ودود، بسيط، يتحدث كصديق مقرب.
                - تستخدم اسم المستخدم إن عرفته: {st.session_state.user_name if st.session_state.user_name else "لم أعرفه"}
                - لا تستخدم أيقونات (✌️، ✅، ❌) في ردودك أبداً.
                - تجيب باختصار ووضوح، لا تبالغ في الإطالة.

                ### المعلومات المحدثة من البحث:
                {search_results if search_results else "لا توجد نتائج بحث محدثة لهذا السؤال."}

                ### تعليمات إضافية:
                - إذا أرسل المستخدم صورة، صفها أو تحدث عنها بأسلوبك.
                - إذا السؤال خارج معرفتك، قل ذلك بصراحة.
                """
                
                # ===== بناء الرسائل =====
                messages = [
                    {"role": "system", "content": system_prompt},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                ]
                
                # ===== إذا كانت هناك صور، استخدم Vision API =====
                if uploaded_images:
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query or "صف هذه الصورة بالتفصيل"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{uploaded_images[0]['data']}"}}
                        ]
                    })
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=600
                    )
                else:
                    messages.append({"role": "user", "content": query})
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=600
                    )
                
                answer = response.choices[0].message.content
                
                # ===== إزالة المؤشر وعرض الرد =====
                typing_placeholder.empty()
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.markdown(f'<div class="msg-bot">{answer}</div>', unsafe_allow_html=True)
                
                # ===== حفظ الجلسة =====
                st.session_state.sessions.append({
                    "date": datetime.now().strftime("%H:%M - %d/%m"),
                    "messages": st.session_state.messages.copy()
                })
                
                # ===== تشغيل الصوت تلقائياً =====
                try:
                    speech = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=answer[:300],
                        response_format="mp3"
                    )
                    audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                    st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                except:
                    pass
                
                st.rerun()
                
            except Exception as e:
                typing_placeholder.empty()
                st.error(f"⚠️ حدث خطأ: {str(e)}")

# ============================================================
# 11. تذييل
# ============================================================
st.markdown("""
<div class="footer">
    نبراس · صديقك الذكي · 2026
</div>
""", unsafe_allow_html=True)
