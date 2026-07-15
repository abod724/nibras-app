# مـبـرمـج الـنـظـام : عـبـدالله
# مـسـاعـد ذكـي مـع بـحـث بـالـويـب

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# صـنـدوق الـمـفـتـاح
API_KEY = "ضع_مفتاحك_هنا"

# دالـة الـبـحـث بـالـويـب
def web_search(query):
    url = f"https://api.bing.microsoft.com/v7.0/search?q={query}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    response = requests.get(url, headers=headers)

    try:
        data = response.json()
        result = data["webPages"]["value"][0]["snippet"]
        return result
    except:
        return "لم يتم العثور على نتائج."

# نـبـذة تـظـهـر فـقـط إذا أحـد سـأل (مـن بـرمـجـك)
def programmer_info():
    return (
        "نبذة عني:\n"
        "• أنا مساعد ذكي تم تطويري وبرمجتي بواسطة عبدالله.\n"
        "• تم إنشائي للإجابة والبحث في الويب.\n"
        "• أبو مشعل المطيري يعمل في التأهيل الشامل — قسم الاتصالات الإدارية.\n"
    )

# الـصـفـحـة الـرئـيـسـيـة
@app.route("/")
def home():
    return render_template("index.html")

# مـعـالـجـة الـسـؤال
@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question")

    # إذا أحد سأل (من برمجك)
    if "من برمجك" in question:
        return render_template("index.html", answer=programmer_info())

    # بـحـث بـالـويـب
    answer = web_search(question)

    return render_template("index.html", answer=answer)

# تـشـغـيـل الـتـطـبـيـق
if __name__ == "__main__":
    app.run(debug=True)
