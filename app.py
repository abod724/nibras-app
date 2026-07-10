import streamlit as st
import base64
from datetime import datetime
import json
import os
import re
from openai import OpenAI
import requests
from PIL import Image
import io

# ============================================================
# 1. التكوين الأساسي
# ============================================================
st.set_page_config(
    page_title="نبراس - صديقك الذكي",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. إدارة الذاكرة
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

# ============================================================
# 3. إعدادات الجلسة
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

memory = load_memory()

# ============================================================
# 4. المفتاح والعميل
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🚨 الرجاء إضافة مفتاح OpenAI في الإعدادات")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ============================================================
# 5. التصميم العصري
# ============================================================
st.markdown("""
<style>
    /* إعادة تعيين الخلفيات */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* شريط علوي شفاف */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        padding: 12px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 2px 20px rgba(0,0,0,0.03);
    }
    
    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .brand-icon {
        font-size: 28px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 8px 12px;
        border-radius: 14px;
        color: white;
    }
    
    .brand-name {
        font-size: 22px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    
    .brand-sub {
        font-size: 14px;
        color: #6b7280;
        font-weight: 400;
        -webkit-text-fill-color: #6b7280;
    }
    
    .header-actions {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    .header-actions button {
        background: rgba(0,0,0,0.03);
        border: none;
        padding: 8px 14px;
        border-radius: 30px;
        font-size: 15px;
        cursor: pointer;
        transition: all 0.2s;
        color: #1a1a1a;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .header-actions button:hover {
        background: rgba(102, 126, 234, 0.1);
        transform: scale(1.02);
    }
    
    /* منطقة المحادثة */
    .chat-container {
        max-width: 820px;
        margin: 80px auto 100px;
        padding: 0 24px;
    }
    
    /* فقاعات المحادثة */
    .msg-wrapper {
        display: flex;
        margin: 12px 0;
        animation: fadeIn 0.3s ease;
    }
    
    .msg-wrapper.user {
        justify-content: flex-end;
    }
    
    .msg-wrapper.assistant {
        justify-content: flex-start;
    }
    
    .msg-bubble {
        max-width: 75%;
        padding: 14px 20px;
        border-radius: 18px;
        line-height: 1.6;
        font-size: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .msg-wrapper.user .msg-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .msg-wrapper.assistant .msg-bubble {
        background: white;
        color: #1a1a1a;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(0,0,0,0.04);
    }
    
    /* ملفات مرفوعة */
    .file-preview {
        background: rgba(102, 126, 234, 0.06);
        border-radius: 12px;
        padding: 8px 14px;
        margin: 4px 0;
        border: 1px dashed rgba(102, 126, 234, 0.2);
        font-size: 13px;
        display: inline-block;
    }
    
    /* مؤشر الكتابة */
    .typing-indicator {
        display: inline-block;
        background: white;
        padding: 12px 20px;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin: 0 3px;
        background: #667eea;
        border-radius: 50%;
        animation: pulse 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes pulse {
        0%, 60%, 100% { transform: scale(0.6); opacity: 0.4; }
        30% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* إخفاء عناصر Streamlit */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* مربع الإدخال */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04) !important;
        padding: 4px 16px !important;
        background: white !important;
    }
    
    .stChatInput input {
        border-radius: 30px !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        background: transparent !important;
    }
    
    .stChatInput button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 50% !important;
        padding: 8px 12px !important;
        color: white !important;
        border: none !important;
    }
    
    /* تذييل */
    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 12px;
        padding: 20px 0;
        border-top: 1px solid rgba(0,0,0,0.04);
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 6. الشريط العلوي
# ============================================================
st.markdown("""
<div class="top-bar">
    <div class="brand">
        <span class="brand-icon">✨</span>
        <div>
            <span class="brand-name">نبراس</span>
            <span class="brand-sub">صديقك الذكي</span>
        </div>
    </div>
    <div class="header-actions">
        <button onclick="location.reload()">🔄 جديد</button>
        <button onclick="alert('📋 المحادثات السابقة')">📋</button>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 7. استخراج اسم المستخدم
# ============================================================
if st.session_state.user_name is None:
    if st.session_state.messages and st.session_state.messages[-1].get("role") == "user":
        last_msg = st.session_state.messages[-1].get("content", "")
        match = re.search(r"اسمي\s+(\w+)", last_msg)
        if match:
            st.session_state.user_name = match.group(1)
            if st.session_state.user_name not in memory["users"]:
                memory["users"][st.session_state.user_name] = {
                    "first_seen": datetime.now().isoformat(),
                    "interests": []
                }
                save_memory(memory)
            st.rerun()

# ============================================================
# 8. عرض المحادثة
# ============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg.get("role", "assistant")
    content = msg.get("content", "")
    if role == "user":
        st.markdown(f'''
        <div class="msg-wrapper user">
            <div class="msg-bubble">{content}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="msg-wrapper assistant">
            <div class="msg-bubble">{content}</div>
        </div>
        ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 9. مربع الإدخال مع رفع الملفات
# ============================================================
prompt = st.chat_input(
    "اكتب سؤالك... أو ارفع صورة أو ملف",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf", "txt", "csv"]
)

# ============================================================
# 10. معالجة الإدخال
# ============================================================
if prompt:
    query = prompt.text.strip() if hasattr(prompt, 'text') else str(prompt).strip()
    
    # معالجة الملفات المرفوعة
    files_info = []
    if hasattr(prompt, 'files') and prompt.files:
        for file in prompt.files:
            ext = file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png']:
                try:
                    img = Image.open(file)
                    files_info.append(f"🖼️ صورة: {file.name} ({img.size[0]}×{img.size[1]})")
                except:
                    files_info.append(f"📎 ملف: {file.name}")
            else:
                files_info.append(f"📄 ملف: {file.name}")
    
    if query or files_info:
        # بناء الرسالة
        full_message = query
        if files_info:
            full_message += "\n" + "\n".join(files_info)
        
        # إضافة للمحادثة
        st.session_state.messages.append({"role": "user", "content": full_message})
        
        # عرض رسالة المستخدم
        with st.chat_message("user"):
            st.markdown(full_message)
        
        # مؤشر التفكير
        with st.chat_message("assistant"):
            with st.spinner("✨"):
                try:
                    # تحضير السياق
                    context = ""
                    if st.session_state.user_name:
                        context = f"المستخدم: {st.session_state.user_name}"
                    
                    system_prompt = f"""
                    أنت نبراس، صديق ذكي ودود.
                    
                    🎯 شخصيتك:
                    - تتحدث كصديق قريب، بأسلوب سعودي حبي.
                    - تستخدم اسم المستخدم إذا عرفته.
                    - تختصر المعلومة وتوضحها بأمثلة.
                    - إذا سألك عن شيء لا تعرفه، تقول بصراحة.
                    
                    📌 عن المستخدم:
                    {context}
                    
                    🔥 مهمتك:
                    - جاوب على السؤال بأسلوبك البسيط.
                    - إذا كان هناك ملفات مرفوعة، أشر إليها في ردك.
                    - استخدم معلوماتك العامة مع الإشارة إلى المصدر إذا أمكن.
                    """
                    
                    # استدعاء الذكاء الاصطناعي
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]],
                            {"role": "user", "content": query or "اطلع على الملفات المرفوعة ورد عليها"}
                        ],
                        max_tokens=600
                    )
                    
                    answer = response.choices[0].message.content
                    
                    # تخزين الرد
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # عرض الرد
                    st.markdown(answer)
                    
                    # صوت
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
                    
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ: {str(e)}")

# ============================================================
# 11. تذييل
# ============================================================
st.markdown("""
<div class="footer">
    ✨ نبراس © 2026 — صديقك الذكي
</div>
""", unsafe_allow_html=True)
