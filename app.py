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
.option {
    margin: 10px 0;
    padding: 15px 12px;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    font-size: 1.13em;
    background: #fff8;
    border: 1.5px solid transparent;
    transition: background 0.14s, border 0.14s;
}
.option.correct { background: #d1ffde; border: 1.5px solid #69dd87;}
.option.incorrect { background: #ffdede; border: 1.5px solid #f99393;}
.option b {
    margin-right: 12px;
    font-size: 1.08em;
    min-width: 23px;
    text-align: center;
    display: inline-block;
}
.btn, .btn-main, .btn-gray {
    margin: 10px 2px 0 0;
    padding: 12px 22px;
    border-radius: 9px;
    border: none;
    font-weight: bold;
    cursor: pointer;
    font-size: 1.10em;
    background: #b2652d;
    color: #fff;
    transition: background 0.14s;
}
.btn-main { background: #b2652d; color: #fff; }
.btn-gray { background: #cfd2d7; color: #835324; }
.btn-main:hover, .btn:hover { background: #c17833; }
.result {
    font-size: 1.12em;
    margin-top: 12px;
    text-align: center;
}
.topics-list > div {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 1em;
}
.qnav-row {
    display: flex;
    gap: 7px;
    margin: 10px 0 13px 0;
    flex-wrap: nowrap;
    align-items: center;
    justify-content: flex-start;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.qnav-page {
    font-size: 1em;
    min-width: 30px;
    height: 30px;
    border-radius: 15px;
    background: #f3f4f6;
    color: #333;
    text-align: center;
    line-height: 30px;
    cursor: pointer;
    font-weight: bold;
    border: none;
    display: inline-block;
    transition: all 0.15s;
    user-select: none;
    margin-right: 2px;
}
.qnav-page.current {
    background: #d78739;
    color: #fff;
    font-weight: bold;
}
.qnav-page.done {
    background: #d1fae5;
    color: #b2652d;
}
.qnav-page.wrong {
    background: #ffeaea;
    color: #d11a1a;
    border: 1.5px solid #ffb6b6;
}
.qnav-dots {
    font-size: 1.16em;
    padding: 0 4px;
    color: #a77e41;
    user-select: none;
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
    .option { font-size: 1em; padding: 10px 7px; }
    .qnav-row { gap: 2px; }
    .qnav-page, .qnav-page.current, .qnav-page.done, .qnav-page.wrong {
        min-width: 26px; height: 26px; font-size: 0.93em; border-radius: 12px; line-height: 26px; margin-right: 1.5px;
    }
    .btn, .btn-main, .btn-gray { width: 100%; margin: 9px 0 0 0; font-size: 1em; padding: 15px 0;}
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
function trainingMenu(push=true) {
    if (push) navHistory.push("trainingMenu");
    let topicStats = getTopicStats();
    let topicsHtml = topics.map((t,i)=>{
        let total = allQuestions.filter(q=>q.topic===t).length;
        let correct = topicStats[t] || 0;
        return `<div>
            <label style="flex:1">
                <input type="checkbox" id="topic${i}">${t}
            </label>
            <span style="min-width:60px;text-align:right;font-weight:bold">${correct} / ${total}</span>
        </div>`;
    }).join('');
    document.getElementById('app').innerHTML = `
        <div class="question-block">
            <h2>Тренировка — выберите темы</h2>
            <div class="topics-list">${topicsHtml}</div>
            <div style="margin-top:10px">
                <label><input type="radio" name="order" value="sequential" checked> По порядку</label>
                <label><input type="radio" name="order" value="random"> Случайно</label>
            </div>
            <button class="btn btn-main" onclick="startTrain()">Начать</button>
            <button class="btn btn-gray" onclick="goBack()">Назад</button>
        </div>
    `;
}
function startTrain() {
    let selectedTopics = [];
    topics.forEach((t,i) => { if(document.getElementById('topic'+i).checked) selectedTopics.push(t); });
    if(selectedTopics.length === 0) { alert("Выберите хотя бы одну тему!"); return; }
    let order = document.querySelector('input[name="order"]:checked').value;
    fetch("/questions").then(r => r.json()).then(data => {
        let qs = data.filter(q => selectedTopics.includes(q.topic));
        if(order==="random") qs = qs.sort(()=>Math.random()-0.5);
        mode = "train"; currentQuestions = qs; userAnswers = Array(qs.length).fill(null); currentIdx = 0;
        wrongAnswers = Array(qs.length).fill(false);
        showQuestion(true);
    });
}
function startExam() {
    fetch("/questions").then(r => r.json()).then(data => {
        let qs = data.sort(()=>Math.random()-0.5).slice(0, Math.min(100, data.length));
        mode = "exam"; currentQuestions = qs; userAnswers = Array(qs.length).fill(null); currentIdx = 0;
        wrongAnswers = Array(qs.length).fill(false);
        showQuestion(true);
    });
}
function startErrors() {
    if(errors.length === 0) { alert("Нет ошибок для повторения!"); return; }
    mode = "errors"; currentQuestions = errors.slice(); userAnswers = Array(errors.length).fill(null); currentIdx = 0;
    wrongAnswers = Array(errors.length).fill(false);
    showQuestion(true);
}

function showQuestion(push=true) {
    if (push) navHistory.push("showQuestion");
    if(currentIdx >= currentQuestions.length) { showResult(true); return; }
    let q = currentQuestions[currentIdx];

    let total = currentQuestions.length;
    let current = currentIdx;
    let pagination = '';
    let maxShown = 15;

    pagination += `<span class="qnav-page" onclick="gotoQuestion(${Math.max(0, current-1)})" ${current===0?'style="opacity:0.5;pointer-events:none"':''}>&lt;</span>`;

    let shown = [];
    if (total <= maxShown) {
        shown = Array.from({length: total}, (_, i) => i);
    } else {
        if (current <= 7) {
            shown = [...Array(11).keys(), 'dots', total-1];
        } else if (current >= total-8) {
            shown = [0, 'dots', ...Array.from({length:11}, (_,i)=>total-11+i)];
        } else {
            shown = [0, 'dots', ...Array.from({length:7},(_,i)=>current-3+i), 'dots', total-1];
        }
    }
    for (let idx of shown) {
        if (idx === 'dots') {
            pagination += `<span class="qnav-dots">...</span>`;
        } else {
            let cls = "qnav-page";
            if (idx === current) cls += " current";
            else if (wrongAnswers[idx]) cls += " wrong";
            else if (userAnswers[idx] !== null) cls += " done";
            pagination += `<span class="${cls}" onclick="gotoQuestion(${idx})">${idx+1}</span>`;
        }
    }
    pagination += `<span class="qnav-page" onclick="gotoQuestion(${Math.min(total-1, current+1)})" ${current===total-1?'style="opacity:0.5;pointer-events:none"':''}>&gt;</span>`;

    let letters = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к', 'л'];
    let opts = q.options.map((opt, i) => {
        let cls = "";
        if(userAnswers[currentIdx]!==null) {
            let correctIdx = q.options.findIndex(opt => opt.startsWith('+'));
            if(i===correctIdx) cls = "option correct";
            else if(i===userAnswers[currentIdx]) cls = "option incorrect";
            else cls = "option";
        } else {
            cls = "option";
        }
        let letter = letters[i] || String.fromCharCode(1072 + i);
        return `<div class="${cls}" onclick="chooseOption(${i})"><b>${letter})</b> ${opt.replace(/^[-+]/,'')}</div>`;
    }).join('');
    let nav = `<div style="display:flex;justify-content:space-between;gap:10px;margin-top:20px">
        <button class="btn btn-gray" onclick="goBack()">Назад</button>
        <button class="btn btn-main" onclick="nextOrSubmit()">${userAnswers[currentIdx]!==null ? 'Далее' : 'Ответить'}</button>
    </div>`;
    document.getElementById('app').innerHTML = `
    <div style="display:flex; gap:20px; flex-wrap:wrap;">
      <div class="question-block" style="flex:1; min-width:0;">
        <div><b>Тема:</b> ${q.topic}</div>
        <div class="qnav-row" style="margin-bottom:13px;">${pagination}</div>
        <div style="margin:16px 0 8px"><b>${q.question}</b></div>
        <div>${opts}</div>
        ${nav}
      </div>
    </div>
    `;
}
function gotoQuestion(idx) {
    currentIdx = idx;
    showQuestion(false);
}
function chooseOption(i) {
    if(userAnswers[currentIdx]!==null) return;
    userAnswers[currentIdx] = i;
    let q = currentQuestions[currentIdx];
    let correctIdx = q.options.findIndex(opt => opt.startsWith('+'));
    wrongAnswers[currentIdx] = (i !== correctIdx);
    if(i !== correctIdx && mode !== "errors") {
        let id = allQuestions.findIndex(x => x.question === q.question && x.topic === q.topic);
        if(!errors.includes(allQuestions[id])) errors.push(allQuestions[id]);
    }
    if(mode === "train" && i === correctIdx) {
        incrementTopic(q.topic);
    }
    showQuestion(false);
}
function nextOrSubmit() {
    if(userAnswers[currentIdx] === null) { alert("Сделайте выбор!"); return; }
    if(currentIdx < currentQuestions.length-1) { currentIdx++; showQuestion(false); }
    else { showResult(true); }
}
function showResult(push=true) {
    if (push) navHistory.push("showResult");
    let correct = 0, wrong = 0;
    let questionsToRemoveFromErrors = [];
    currentQuestions.forEach((q, idx) => {
        let correctIdx = q.options.findIndex(opt => opt.startsWith('+'));
        if(userAnswers[idx] === correctIdx) {
            correct++;
            if (mode === "errors") questionsToRemoveFromErrors.push(idx);
        } else {
            wrong++;
        }
    });
    let percent = Math.round(correct / currentQuestions.length * 100);
    let msg = "";
    if(mode === "exam") msg = percent >= 85 ? "<b>Экзамен сдан!</b>" : "<b>Экзамен не сдан. Необходимо минимум 85%.</b>";
    else if(mode === "errors") msg = "<b>Работа над ошибками завершена!</b>";
    else msg = "<b>Тренировка завершена!</b>";
    document.getElementById('app').innerHTML = `
        <div class="question-block result">
            <div>Правильных: <b>${correct}</b></div>
            <div>Ошибочных: <b>${wrong}</b></div>
            <div>Всего: <b>${currentQuestions.length}</b></div>
            <div>Процент: <b>${percent}%</b></div>
            <div style="margin-top:20px">${msg}</div>
            <button class="btn btn-main" onclick="onErrorsResult()">OK</button>
            <button class="btn btn-gray" onclick="mainMenu(true)">На главную</button>
        </div>
    `;
    if(mode === "errors" && questionsToRemoveFromErrors.length > 0) {
        let idsToRemove = questionsToRemoveFromErrors.map(idx => {
            let q = currentQuestions[idx];
            return allQuestions.findIndex(x => x.question === q.question && x.topic === q.topic);
        });
        errors = errors.filter(q => !idsToRemove.includes(allQuestions.findIndex(x => x.question === q.question && x.topic === q.topic)));
    }
    if(mode === "exam" || mode === "train") {
        errors = [];
        currentQuestions.forEach((q, idx) => {
            let correctIdx = q.options.findIndex(opt => opt.startsWith('+'));
            if(userAnswers[idx] !== correctIdx) {
                let id = allQuestions.findIndex(x => x.question === q.question && x.topic === q.topic);
                if(!errors.includes(allQuestions[id])) errors.push(allQuestions[id]);
            }
        });
    }
}
function onErrorsResult() {
    mainMenu(true);
}
function goBack() {
    if (navHistory.length > 1) navHistory.pop();
    const prev = navHistory.length ? navHistory.pop() : "mainMenu";
    if (prev === "mainMenu") mainMenu(false);
    else if (prev === "trainingMenu") trainingMenu(false);
    else if (prev === "showQuestion") showQuestion(false);
    else if (prev === "showResult") showResult(false);
    else mainMenu(false);
}

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
