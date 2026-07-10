import os
from flask import Flask, render_template, request, jsonify, send_file
import openai
from gtts import gTTS
from flask_cors import CORS
from io import BytesIO

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("⚠️ مفتاح OpenAI غير موجود! أضفه في ملف .env")

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    
    if user_message.strip().lower().startswith(("ارسم لي", "ارسم", "draw")):
        prompt = user_message.replace("ارسم لي", "").replace("ارسم", "").replace("draw", "")
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
        )
        img_url = response['data'][0]['url']
        return jsonify({"type": "image", "content": img_url})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "أنت مساعد ذكي ودود يتكلم العربية ببساطة."},
            {"role": "user", "content": user_message}
        ]
    )
    reply = response.choices[0].message.content.strip()
    return jsonify({"type": "text", "content": reply})

@app.route("/speech", methods=["POST"])
def speech():
    data = request.json
    text = data.get("text")
    tts = gTTS(text, lang='ar')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return send_file(fp, mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(debug=True)
