import json
from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)
app.secret_key = "lawyer_test_secret_key"

with open("quiz_questions.json", encoding="utf-8") as f:
    all_questions = json.load(f)

topics = sorted(set(q["topic"] for q in all_questions))
NUM_EXAM_QUESTIONS = 100

MAIN_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Юридический тренажёр</title>
    <style>
body {
    background: #c68b3e;
    background-image: repeating-linear-gradient(45deg,#e7b46b 0 8px,transparent 8px 16px), repeating-linear-gradient(-45deg,#e0a858 0 10px,transparent 10px 20px);
    min-height: 100vh;
    font-family: Arial, sans-serif;
}
h1, h2 { text-align: center; }
.main-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 97vh;
}
.main-card {
    background: #a25628d9;
    border-radius: 32px;
    padding: 38px 32px 36px 32px;
    box-shadow: 0 4px 24px #2d180812;
    min-width: 335px;
    max-width: 96vw;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    position: relative;
}
.main-icon {
    font-size: 40px;
    color: #fff;
    margin-bottom: 12px;
    align-self: center;
}
.main-title {
    font-size: 2.3em;
    font-weight: bold;
    color: #fff;
    letter-spacing: 1px;
    margin-bottom: 12px;
    line-height: 1.08em;
    text-align: left;
}
.main-subtitle {
    font-size: 1.2em;
    color: #fff9;
    margin-bottom: 24px;
    line-height: 1.24em;
}
.main-modes {
    background: #7e3f15e0;
    border-radius: 16px;
    padding: 20px 24px 20px 24px;
    align-self: flex-end;
    width: 260px;
    margin-bottom: 24px;
    box-shadow: 0 2px 12px #2d18081a;
}
.modes-title {
    color: #fff;
    font-size: 1.25em;
    font-weight: bold;
    margin-bottom: 18px;
    letter-spacing: 0.5px;
}
.main-btn {
    background: #b2652d;
    color: #fff;
    border: none;
    font-size: 1.13em;
    border-radius: 12px;
    padding: 13px 16px 13px 0;
    margin-bottom: 12px;
    width: 100%;
    text-align: left;
    font-weight: bold;
    box-shadow: 0 2px 10px #42250611;
    transition: background 0.13s;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
}
.main-btn:last-child { margin-bottom: 0; }
.main-btn:hover {
    background: #cd8946;
}
.main-btn-icon {
    font-size: 1.28em;
    margin-left: 15px;
}
.main-version {
    position: absolute;
    left: 36px;
    bottom: 16px;
    color: #fff7;
    font-size: 1.11em;
    letter-spacing: 1.5px;
}
.question-block {
    background: #fffbeedc;
    border-radius: 24px;
    padding: 25px 20px 18px 20px;
    box-shadow: 0 2px 12px #42250611;
    margin: 26px auto 0 auto;
    max-width: 490px;
    min-width: 0;
    display: flex;
    flex-direction: column;
}
.train-screen {
    width: 100vw;
    max-width: 520px;
    margin: 0 auto;
}
.train-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 26px 0 9px 0;
}
.train-gear, .train-menu {
    font-size: 1.6em;
    opacity: 0.7;
    padding: 0 7px;
}
.train-title {
    font-size: 2.2em;
    color: #fff;
    font-weight: bold;
    letter-spacing: 1.1px;
}
.train-card {
    background: #a25628d9;
    border-radius: 22px;
    padding: 30px 23px 26px 23px;
    box-shadow: 0 4px 18px #2d18081a;
    margin: 0 0 24px 0;
}
.train-topic-list { margin-bottom: 25px; }
.train-topic-row {
    display: flex;
    align-items: center;
    border-radius: 14px;
    padding: 8px 0 8px 0;
    font-size: 1.19em;
    cursor: pointer;
    transition: background 0.14s;
}
.train-topic-row:hover { background: #ffecbc24; }
.train-topic-row:not(:last-child) { border-bottom: 1px solid #e1af82a8;}
.train-topic-name {
    flex: 1;
    color: #fff;
    font-weight: 400;
}
.train-topic-progress {
    color: #fffbe0;
    font-weight: bold;
    font-size: 1.07em;
    min-width: 63px;
    text-align: right;
}
.train-overall-progress {
    background: #d9a25580;
    color: #fff;
    font-size: 1.13em;
    padding: 10px 0 8px 0;
    border-radius: 13px;
    margin: 25px 0 14px 0;
    text-align: center;
    font-weight: 500;
}
.train-btns {
    display: flex;
    gap: 22px;
}
.main-btn {
    background: #7e3f15e0;
    color: #fff;
    border: none;
    font-size: 1.18em;
    border-radius: 13px;
    padding: 16px 20px;
    margin-bottom: 0;
    min-width: 180px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 2px 10px #42250611;
    transition: background 0.13s;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: center;
}
.main-btn:hover { background: #b2652d;}
.main-btn-icon {
    font-size: 1.23em;
}
@media (max-width: 600px) {
    .main-card {
        min-width: 90vw;
        padding: 13vw 3vw 18vw 3vw;
        border-radius: 14px;
    }
    .main-modes { width: 100%; padding: 13px 3vw 13px 3vw;}
    .main-title { font-size: 1.22em; }
    .main-version { left: 9vw; font-size: 1em;}
    .question-block { max-width:98vw; padding: 11vw 2vw 7vw 2vw; }
    .train-header { margin-top: 4vw; }
    .train-card { padding: 7vw 3vw 7vw 3vw;}
    .main-btn { min-width: 1px; width: 100%; font-size: 1.05em;}
    .train-btns { flex-direction: column; gap: 12px;}
    .train-title { font-size: 1.25em;}
}
    </style>
</head>
<body>
    <div id="app"></div>
<script>
const topics = {{ topics|tojson }};
let allQuestions = [];
let currentQuestions = [];
let userAnswers = [];
let currentIdx = 0;
let mode = null;
let errors = [];
let sessionResult = {};
let navHistory = [];
let wrongAnswers = [];

function getTopicStats() {
    return JSON.parse(localStorage.getItem("topicStats") || "{}");
}
function setTopicStats(stats) {
    localStorage.setItem("topicStats", JSON.stringify(stats));
}
function incrementTopic(topic) {
    let stats = getTopicStats();
    stats[topic] = (stats[topic] || 0) + 1;
    setTopicStats(stats);
}
function resetTopicStats() {
    localStorage.removeItem("topicStats");
}

function fetchQuestions() {
    fetch("/questions").then(r => r.json()).then(data => { allQuestions = data; });
}
function mainMenu(push=true) {
    if (push) navHistory.push("mainMenu");
    document.getElementById('app').innerHTML = `
    <div class="main-screen">
    <div class="main-card">
        <div class="main-icon">⚖️</div>
        <div class="main-title">ЮРИДИЧЕСКИЙ<br>ТРЕНАЖЁР</div>
        <div class="main-subtitle">Готовься к экзамену<br>по законам Кыргызской<br>Республики!</div>
        <div class="main-modes">
            <div class="modes-title">Режимы</div>
            <button class="main-btn" onclick="trainingMenu()">
                <span class="main-btn-icon">🧑‍⚖️</span> Тренировка
            </button>
            <button class="main-btn" onclick="startExam()">
                <span class="main-btn-icon">✅</span> Экзамен
            </button>
            <button class="main-btn" onclick="startErrors()" id="errors-btn">
                <span class="main-btn-icon">❌</span> Мои ошибки
            </button>
        </div>
        <div class="main-version">v1.0</div>
    </div>
    </div>
    `;
    document.getElementById('errors-btn').disabled = errors.length === 0;
}

// --- РЕЖИМ ТРЕНИРОВКИ ---

function trainingMenu(push=true) {
    if (push) navHistory.push("trainingMenu");
    let topicStats = getTopicStats();
    let topicsHtml = topics.map((t,i)=>{
        let total = allQuestions.filter(q=>q.topic===t).length;
        let correct = topicStats[t] || 0;
        // Вся строка кликабельна, тренировка только по теме!
        return `<div class="train-topic-row" style="cursor:pointer" onclick="startTrainOneTopic('${encodeURIComponent(t)}')">
                <span class="train-topic-name">${t}</span>
                <span class="train-topic-progress">${correct} / ${total}</span>
            </div>`;
    }).join('');
    let allQuestionsCount = allQuestions.length;
    let correctSum = topics.reduce((sum, t) => sum + (topicStats[t]||0), 0);
    let percent = allQuestionsCount ? Math.round(correctSum/allQuestionsCount*100) : 0;
    document.getElementById('app').innerHTML = `
    <div class="train-screen">
        <div class="train-header">
            <span class="train-gear">⚙️</span>
            <span class="train-title">Тренировка</span>
            <span class="train-menu">⋮</span>
        </div>
        <div class="train-card">
            <div class="train-topic-list">
                ${topicsHtml}
            </div>
            <div class="train-overall-progress">
                Пройдено <b>${correctSum}</b> из <b>${allQuestionsCount}</b> вопросов (${percent}%)
            </div>
            <div class="train-btns">
                <button class="main-btn" onclick="startErrors()">
                    Мои ошибки
                </button>
                <button class="main-btn" onclick="startExam()">
                    Сдать экзамен
                </button>
            </div>
        </div>
    </div>
    `;
}

// --- Функция старта тренировки по одной теме ---
function startTrainOneTopic(topicName) {
    topicName = decodeURIComponent(topicName);
    let qs = allQuestions.filter(q => q.topic === topicName);
    mode = "train";
    currentQuestions = qs;
    userAnswers = Array(qs.length).fill(null);
    currentIdx = 0;
    wrongAnswers = Array(qs.length).fill(false);
    showQuestion(true);
}

// --- остальные функции экзамена/ошибок/опроса — как в вашей логике! ---

window.onload = function() {
    fetchQuestions();
    mainMenu();
}
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
