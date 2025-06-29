import json
from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)
app.secret_key = "lawyer_test_secret_key"

with open("quiz_questions.json", encoding="utf-8") as f:
    all_questions = json.load(f)

topics = sorted(set(q["topic"] for q in all_questions))

MAIN_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Юридический тренажёр</title>
    <style>
body {
    background: #b0732d;
    background-image: repeating-linear-gradient(45deg,#c99354 0 9px,transparent 9px 18px), repeating-linear-gradient(-45deg,#ad7b35 0 11px,transparent 11px 22px);
    min-height: 100vh;
    font-family: 'Arial Rounded MT Bold', Arial, sans-serif;
}
.main-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 99vh;
}
.main-block {
    background: #be7c32e2;
    border-radius: 40px;
    display: flex;
    flex-direction: row;
    box-shadow: 0 6px 34px #92531a52;
    padding: 38px 32px 36px 48px;
}
.main-title-area {
    flex: 2;
    padding-right: 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 350px;
}
.main-logo {
    font-size: 4.5em;
    color: #fff;
    margin-bottom: 18px;
    margin-left: -12px;
}
.main-big-title {
    font-size: 2.9em;
    font-weight: bold;
    color: #fff;
    text-shadow: 0 2px 5px #98632a33;
    margin-bottom: 16px;
    line-height: 1.04em;
    letter-spacing: 2px;
}
.main-subtitle {
    font-size: 1.16em;
    color: #fff9;
    margin-bottom: 32px;
    line-height: 1.28em;
    letter-spacing: 1px;
    font-weight: 500;
}
.main-version {
    color: #fff9;
    font-size: 1.12em;
    margin-top: 45px;
    letter-spacing: 2px;
}
.main-modes-block {
    background: #7d421b;
    border-radius: 25px;
    padding: 32px 24px 34px 24px;
    min-width: 260px;
    max-width: 330px;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    box-shadow: 0 2px 15px #66422122;
}
.main-modes-title {
    color: #fff;
    font-size: 1.32em;
    font-weight: bold;
    margin-bottom: 28px;
    text-align: left;
    letter-spacing: 0.5px;
}
.mode-btn {
    background: #b2652d;
    color: #fff;
    border: none;
    font-size: 1.19em;
    border-radius: 13px;
    padding: 16px 20px 15px 19px;
    margin-bottom: 20px;
    font-weight: bold;
    box-shadow: 0 2px 10px #42250616;
    transition: background 0.13s;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
}
.mode-btn:last-child { margin-bottom: 0;}
.mode-btn:hover { background: #cf8a42; }
.mode-icon { font-size: 1.33em; }
.mode-text { font-size: 1em; }
@media (max-width: 950px) {
    .main-block { flex-direction: column; align-items: center; padding: 21px 9px 32px 9px; }
    .main-title-area { padding-right:0; align-items:center; }
    .main-modes-block { margin-top:30px;}
}
    </style>
</head>
<body>
<div class="main-wrapper">
    <div class="main-block">
        <div class="main-title-area">
            <div class="main-logo">
                <span class="scale-icon">⚖️</span>
            </div>
            <div class="main-big-title">ЮРИДИЧЕСКИЙ<br>ТРЕНАЖЁР</div>
            <div class="main-subtitle">
                Готовься к экзамену<br>по законам Кыргызской<br>Республики!
            </div>
            <div class="main-version">v1.0</div>
        </div>
        <div class="main-modes-block">
            <div class="main-modes-title">Режимы</div>
            <button class="mode-btn" onclick="trainingMenu()">
                <span class="mode-icon">🧑‍⚖️</span>
                <span class="mode-text">Тренировка</span>
            </button>
            <button class="mode-btn" onclick="startExam()">
                <span class="mode-icon">✅</span>
                <span class="mode-text">Экзамен</span>
            </button>
            <button class="mode-btn" onclick="startErrors()">
                <span class="mode-icon">❌</span>
                <span class="mode-text">Мои ошибки</span>
            </button>
        </div>
    </div>
</div>
<!-- Ниже подключайте JS-логику теста! -->
<script>
const topics = {{ topics|tojson }};
let allQuestions = [];
function fetchQuestions() {
    fetch("/questions").then(r => r.json()).then(data => { allQuestions = data; });
}
// Ниже заглушки для примера — замените на вашу JS-логику!
function trainingMenu() { alert("Тренировка: выбрать темы!"); }
function startExam()    { alert("Экзамен: по всем темам!"); }
function startErrors()  { alert("Мои ошибки: только ваши ошибки!"); }
window.onload = fetchQuestions;
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(MAIN_HTML, topics=topics)

@app.route("/questions")
def questions():
    return jsonify(all_questions)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
