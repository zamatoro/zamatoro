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
    <title>Тренажёр для юристов</title>
    <style>
body {
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    background: #f7f7f7;
}
h1, h2 { text-align: center; }
.question-block {
    background: #fff;
    padding: 24px;
    border-radius: 16px;
    margin-top: 24px;
    box-sizing: border-box;
}
.option {
    margin: 8px 0;
    padding: 12px 12px;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    font-size: 1.13em;
}
.option.correct { background: #b1ffcb; }
.option.incorrect { background: #ffd4d4; }
.btn {
    margin: 8px 2px;
    padding: 12px 22px;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    cursor: pointer;
    font-size: 1.08em;
}
.btn-main { background: #008080; color: #fff; }
.btn-gray { background: #ccc; color: #333; }
.topics-list > div {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 1em;
}
.result {
    font-size: 1.17em;
    margin-top: 24px;
    text-align: center;
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
    min-width: 34px;
    height: 34px;
    border-radius: 17px;
    background: #f3f4f6;
    color: #333;
    text-align: center;
    line-height: 34px;
    cursor: pointer;
    font-weight: bold;
    border: none;
    display: inline-block;
    transition: all 0.15s;
    user-select: none;
    margin-right: 2px;
}
.qnav-page.current {
    background: #118387;
    color: #fff;
    font-weight: bold;
}
.qnav-page.done {
    background: #d1fae5;
    color: #008080;
}
.qnav-page.wrong {
    background: #ffeaea;
    color: #d11a1a;
    border: 1.5px solid #ffb6b6;
}
.qnav-dots {
    font-size: 1.2em;
    padding: 0 4px;
    color: #888;
    user-select: none;
}
.option b {
    margin-right: 10px;
    font-size: 1.08em;
    min-width: 22px;
    text-align: center;
    display: inline-block;
}
@media (max-width: 600px) {
    body {
        max-width: 100vw;
        font-size: 1em;
        padding: 0;
        margin: 0;
        background: #f7f7f7;
    }
    .question-block {
        padding: 12px 6px 18px 6px;
        margin-top: 5vw;
        border-radius: 10px;
    }
    .btn, .btn-main, .btn-gray {
        width: 100%;
        margin: 9px 0;
        padding: 15px 0;
        font-size: 1.06em;
    }
    .topics-list > div {
        font-size: 0.98em;
    }
    .qnav-row {
        gap: 4px;
        margin-bottom: 10px;
        padding-bottom: 3px;
    }
    .qnav-page, .qnav-page.current, .qnav-page.done, .qnav-page.wrong {
        min-width: 28px;
        height: 28px;
        font-size: 0.99em;
        border-radius: 14px;
        line-height: 28px;
        margin-right: 1.5px;
    }
    .option { font-size: 1em; padding: 10px 7px; }
}
    </style>
</head>
<body>
    <h1>Тренажёр для юристов</h1>
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
let wrongAnswers = [];  // Массив с ошибками по вопросам текущей сессии

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
        <div class="question-block">
            <h2>Выберите режим:</h2>
            <button class="btn btn-main" onclick="trainingMenu()">Тренировка</button>
            <button class="btn btn-main" onclick="startExam()">Экзамен</button>
            <button class="btn btn-main" onclick="startErrors()" id="errors-btn">Работа над ошибками (${errors.length})</button>
            <button class="btn btn-gray" style="float:right" onclick="if(confirm('Сбросить прогресс по темам?')){resetTopicStats();trainingMenu(false);}">Сбросить счётчики</button>
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
            <h2>Тренировка — Выберите темы</h2>
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
            let correctIdx = q.options.findIndex(opt => opt.startswith('+'));
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
