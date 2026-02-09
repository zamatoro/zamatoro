import json
from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)
app.secret_key = "lawyer_test_secret_key"

# Загрузка вопросов
with open("quiz_questions.json", encoding="utf-8") as f:
    all_questions = json.load(f)

topics = sorted(set(q["topic"] for q in all_questions))
NUM_EXAM_QUESTIONS = 120

MAIN_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Юридический тренажёр</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
body {
    background: #c68b3e;
    background-image: repeating-linear-gradient(45deg,#e7b46b 0 8px,transparent 8px 16px), repeating-linear-gradient(-45deg,#e0a858 0 10px,transparent 10px 20px);
    min-height: 100vh;
    font-family: Arial, sans-serif;
    margin: 0;
}
h1, h2, h3 { text-align: center; }
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
    max-width: 600px;
    width: 95%;
    display: flex;
    flex-direction: column;
    position: relative;
}
.timer-display {
    position: sticky;
    top: 0;
    background: #a25628;
    color: #fff;
    padding: 5px 15px;
    border-radius: 0 0 10px 10px;
    margin: -25px auto 10px auto;
    font-weight: bold;
    z-index: 10;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
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
    border: 2px solid transparent;
    transition: background 0.14s, border 0.14s;
}
/* Стили для выбранных ответов в процессе выбора */
.option.selected {
    border: 2px solid #b2652d;
    background: #fff;
}
.option.correct { background: #d1ffde; border: 2px solid #69dd87;}
.option.incorrect { background: #ffdede; border: 2px solid #f99393;}
.option.missed { border: 2px dashed #69dd87; }

.option b {
    margin-right: 12px;
    font-size: 1.08em;
    min-width: 23px;
    text-align: center;
    display: inline-block;
}
.checkbox-indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #b2652d;
    border-radius: 4px;
    margin-right: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
}
.selected .checkbox-indicator {
    background: #b2652d;
}
.selected .checkbox-indicator::after {
    content: '✓';
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
    padding: 5px 0;
    border-bottom: 1px solid #0001;
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
    padding-bottom: 5px;
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
    flex-shrink: 0;
}
.qnav-page.current { background: #d78739; color: #fff; font-weight: bold; }
.qnav-page.done { background: #d1fae5; color: #b2652d; }
/* Класс ошибки показываем только если не скрыт результат */
.qnav-page.wrong { background: #ffeaea; color: #d11a1a; border: 1.5px solid #ffb6b6; }
.qnav-dots { font-size: 1.16em; padding: 0 4px; color: #a77e41; user-select: none; }

.topic-stats-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    font-size: 0.9em;
    text-align: left;
}
.topic-stats-table th, .topic-stats-table td {
    border: 1px solid #0002;
    padding: 6px;
}
.topic-stats-table th { background: #0001; }

@media (max-width: 600px) {
    .main-card {
        min-width: 90vw;
        padding: 13vw 3vw 18vw 3vw;
        border-radius: 14px;
    }
    .main-modes { width: 100%; padding: 13px 3vw 13px 3vw;}
    .main-title { font-size: 1.22em; }
    .main-version { left: 9vw; font-size: 1em;}
    .question-block { max-width:98vw; padding: 11vw 2vw 7vw 2vw; margin-top: 15px;}
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
const NUM_EXAM_QUESTIONS = {{ NUM_EXAM_QUESTIONS|tojson }};
let allQuestions = [];
let currentQuestions = [];
let userAnswers = [];
let currentIdx = 0;
let mode = null;
let errors = [];
let navHistory = [];
let wrongAnswers = [];
let examTimer = null;
let examEndTime = null;
let examFinished = false; 
let tempSelection = [];

function getTopicStats() {
    return JSON.parse(localStorage.getItem("topicStats") || "{}");
}
function setTopicStats(stats) {
    localStorage.setItem("topicStats", JSON.stringify(stats));
}
function incrementTopic(topic, isCorrect) {
    let stats = getTopicStats();
    if (!stats[topic]) stats[topic] = { total: 0, correct: 0 };
    if(isCorrect) stats[topic].correct = (stats[topic].correct || 0) + 1;
    stats[topic].total = (stats[topic].total || 0) + 1;
    setTopicStats(stats);
}

function fetchQuestions() {
    fetch("/questions").then(r => r.json()).then(data => { allQuestions = data; });
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function prepareQuestions(qs) {
    return qs.map(q => {
        let optsObj = q.options.map((optText, idx) => ({
            text: optText.replace(/^[-+]/, ''),
            isCorrect: optText.startsWith('+'),
            originalIdx: idx
        }));
        let shuffled = shuffleArray([...optsObj]);
        let correctCount = shuffled.filter(o => o.isCorrect).length;
        return {
            ...q,
            processedOptions: shuffled,
            isMulti: correctCount > 1,
            correctCount: correctCount
        };
    });
}

function mainMenu(push=true) {
    if (push) navHistory.push("mainMenu");
    stopTimer();
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
                <span class="main-btn-icon">✅</span> Экзамен (120 вопр.)
            </button>
            <button class="main-btn" onclick="startErrors()" id="errors-btn">
                <span class="main-btn-icon">❌</span> Мои ошибки
            </button>
        </div>
        <div class="main-version">v1.6</div>
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
        let stat = topicStats[t] || {correct:0};
        return `<div>
            <label style="flex:1; display:flex; align-items:center; gap:8px;">
                <input type="checkbox" id="topic${i}" style="transform:scale(1.3)"> ${t}
            </label>
            <span style="min-width:60px;text-align:right;font-weight:bold;font-size:0.9em;color:#555;">${stat.correct}/${total}</span>
        </div>`;
    }).join('');
    document.getElementById('app').innerHTML = `
        <div class="question-block">
            <h2>Тренировка</h2>
            <div style="margin-bottom:10px; font-size:0.9em; color:#666;">Выберите темы:</div>
            <div class="topics-list" style="max-height:50vh; overflow-y:auto;">${topicsHtml}</div>
            <div style="margin-top:15px; background:#fff8; padding:10px; border-radius:8px;">
                <label style="margin-right:15px;"><input type="radio" name="order" value="sequential" checked> По порядку</label>
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
        
        mode = "train"; 
        examFinished = false;
        currentQuestions = prepareQuestions(qs);
        userAnswers = Array(qs.length).fill(null); 
        currentIdx = 0;
        wrongAnswers = Array(qs.length).fill(false);
        showQuestion(true);
    });
}

function startExam() {
    fetch("/questions").then(r => r.json()).then(data => {
        // Группировка вопросов по темам
        let questionsByTopic = {};
        data.forEach(q => {
            if(!questionsByTopic[q.topic]) questionsByTopic[q.topic] = [];
            questionsByTopic[q.topic].push(q);
        });
        
        let examQs = [];
        let remainingPool = [];
        
        // 1. Выборка согласно логике (6-8 для больших, 1-4 для малых)
        for(let t in questionsByTopic) {
             let qs = questionsByTopic[t];
             // Перемешиваем вопросы внутри темы
             qs = qs.sort(() => Math.random() - 0.5);
             
             let count = qs.length;
             let take = 0;
             
             if (count > 140) {
                 // Большая тема: берем от 6 до 8
                 take = Math.floor(Math.random() * (8 - 6 + 1)) + 6;
             } else {
                 // Маленькая тема (<=140): берем от 1 до 4
                 take = Math.floor(Math.random() * (4 - 1 + 1)) + 1;
             }
             
             // Защита: нельзя взять больше, чем есть
             take = Math.min(take, count);
             
             // Добавляем выбранные
             for(let i=0; i<take; i++) examQs.push(qs[i]);
             // Остальные кидаем в общий котел на случай добора
             for(let i=take; i<count; i++) remainingPool.push(qs[i]);
        }
        
        // 2. Добиваем до 120, если набралось меньше (из общего котла)
        remainingPool = remainingPool.sort(() => Math.random() - 0.5);
        let needed = NUM_EXAM_QUESTIONS - examQs.length;
        
        if (needed > 0) {
            if (remainingPool.length >= needed) {
                examQs = examQs.concat(remainingPool.slice(0, needed));
            } else {
                // Если вдруг вопросов вообще не хватает (маловероятно)
                examQs = examQs.concat(remainingPool);
            }
        } else if (needed < 0) {
            // Если вдруг набрали больше 120 (очень много больших тем), подрезаем
            // Но лучше перемешать перед подрезкой
            examQs = examQs.sort(() => Math.random() - 0.5);
            examQs = examQs.slice(0, NUM_EXAM_QUESTIONS);
        }
        
        // 3. Финальное перемешивание всего списка вопросов экзамена
        examQs = examQs.sort(() => Math.random() - 0.5);

        mode = "exam"; 
        examFinished = false; 
        currentQuestions = prepareQuestions(examQs); 
        userAnswers = Array(examQs.length).fill(null); 
        currentIdx = 0;
        wrongAnswers = Array(examQs.length).fill(false);
        
        examEndTime = Date.now() + 2 * 60 * 60 * 1000;
        startTimer();
        
        showQuestion(true);
    });
}

function startErrors() {
    if(errors.length === 0) { alert("Нет ошибок для повторения!"); return; }
    mode = "errors"; 
    examFinished = false;
    let rawErrors = errors.map(errQ => {
        return allQuestions.find(q => q.question === errQ.question && q.topic === errQ.topic) || errQ;
    });

    currentQuestions = prepareQuestions(rawErrors); 
    userAnswers = Array(currentQuestions.length).fill(null); 
    currentIdx = 0;
    wrongAnswers = Array(currentQuestions.length).fill(false);
    showQuestion(true);
}

function startTimer() {
    if(examTimer) clearInterval(examTimer);
    examTimer = setInterval(() => {
        let now = Date.now();
        let diff = examEndTime - now;
        if(diff <= 0) {
            clearInterval(examTimer);
            alert("Время экзамена истекло!");
            showResult(true);
            return;
        }
        let el = document.getElementById('timer');
        if(el) {
            let h = Math.floor(diff / (1000 * 60 * 60));
            let m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            let s = Math.floor((diff % (1000 * 60)) / 1000);
            el.innerText = `⏱️ ${h}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        }
    }, 1000);
}

function stopTimer() {
    if(examTimer) clearInterval(examTimer);
    examTimer = null;
}

function showQuestion(push=true) {
    if (push) navHistory.push("showQuestion");
    if(currentIdx >= currentQuestions.length) { showResult(true); return; }
    let q = currentQuestions[currentIdx];

    let total = currentQuestions.length;
    let current = currentIdx;
    let pagination = '';
    let maxShown = 10; 

    pagination += `<span class="qnav-page" onclick="gotoQuestion(${Math.max(0, current-1)})" ${current===0?'style="opacity:0.5;pointer-events:none"':''}>&lt;</span>`;
    
    let shown = [];
    if (total <= maxShown) {
        shown = Array.from({length: total}, (_, i) => i);
    } else {
        if (current <= 4) {
            shown = [...Array(7).keys(), 'dots', total-1];
        } else if (current >= total-5) {
            shown = [0, 'dots', ...Array.from({length:7}, (_,i)=>total-7+i)];
        } else {
            shown = [0, 'dots', ...Array.from({length:3},(_,i)=>current-1+i), 'dots', total-1];
        }
    }

    let canShowResult = true;
    if (mode === 'exam' && !examFinished) {
        canShowResult = false;
    }

    for (let idx of shown) {
        if (idx === 'dots') {
            pagination += `<span class="qnav-dots">...</span>`;
        } else {
            let cls = "qnav-page";
            if (idx === current) cls += " current";
            else if (canShowResult && wrongAnswers[idx]) cls += " wrong";
            else if (userAnswers[idx] !== null) cls += " done";
            pagination += `<span class="${cls}" onclick="gotoQuestion(${idx})">${idx+1}</span>`;
        }
    }
    pagination += `<span class="qnav-page" onclick="gotoQuestion(${Math.min(total-1, current+1)})" ${current===total-1?'style="opacity:0.5;pointer-events:none"':''}>&gt;</span>`;

    let letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З'];
    
    let opts = q.processedOptions.map((opt, i) => {
        let cls = "option";
        let isSelected = false;
        let showResultColors = (userAnswers[currentIdx] !== null) && canShowResult;

        if (userAnswers[currentIdx] && userAnswers[currentIdx].includes(i)) {
            isSelected = true;
            cls += " selected";
        }

        if (showResultColors) {
            if (opt.isCorrect) {
                cls += " correct"; 
            } else if (isSelected && !opt.isCorrect) {
                cls += " incorrect"; 
            } else if (!isSelected && opt.isCorrect) {
                 cls += " missed"; 
            }
        }
        
        let prefix = "";
        if (q.isMulti) {
            prefix = `<div class="checkbox-indicator"></div>`;
        } else {
            prefix = `<b>${letters[i]})</b>`;
        }

        return `<div class="${cls}" onclick="chooseOption(${i})">${prefix} ${opt.text}</div>`;
    }).join('');

    let multiHint = q.isMulti ? `<div style="color:#b2652d; font-weight:bold; margin-bottom:5px;">⚠️ Выберите несколько вариантов</div>` : '';

    let timerHtml = mode === 'exam' ? `<div id="timer" class="timer-display">Загрузка...</div>` : '';

    let nav = `<div style="display:flex;justify-content:space-between;gap:10px;margin-top:20px">
        <button class="btn btn-gray" onclick="goBack()">Назад</button>
        <button class="btn btn-main" onclick="nextOrSubmit()">${userAnswers[currentIdx]!==null ? 'Далее' : 'Ответить'}</button>
    </div>`;

    document.getElementById('app').innerHTML = `
    <div style="display:flex; gap:20px; flex-wrap:wrap; justify-content:center;">
      <div class="question-block">
        ${timerHtml}
        <div style="display:flex; justify-content:space-between; font-size:0.9em; color:#666;">
            <span>Вопрос ${currentIdx+1} из ${total}</span>
            <span>${q.topic}</span>
        </div>
        <div class="qnav-row">${pagination}</div>
        <div style="margin:10px 0 15px"><b>${q.question}</b></div>
        ${multiHint}
        <div>${opts}</div>
        ${nav}
      </div>
    </div>
    `;
}

function gotoQuestion(idx) {
    tempSelection = []; 
    currentIdx = idx;
    showQuestion(false);
}

function chooseOption(i) {
    if (userAnswers[currentIdx] !== null) return; 

    let q = currentQuestions[currentIdx];
    
    if (q.isMulti) {
        if (tempSelection.includes(i)) {
            tempSelection = tempSelection.filter(x => x !== i);
        } else {
            tempSelection.push(i);
        }
    } else {
        tempSelection = [i];
    }
    updateSelectionUI();
}

function updateSelectionUI() {
    let opts = document.querySelectorAll('.option');
    opts.forEach((el, idx) => {
        if(tempSelection.includes(idx)) el.classList.add('selected');
        else el.classList.remove('selected');
    });
}

function nextOrSubmit() {
    if (userAnswers[currentIdx] !== null) {
        if(currentIdx < currentQuestions.length-1) { 
            tempSelection = [];
            currentIdx++; 
            showQuestion(false); 
        } else { 
            showResult(true); 
        }
        return;
    }

    if (tempSelection.length === 0) { alert("Выберите вариант ответа!"); return; }
    
    userAnswers[currentIdx] = [...tempSelection]; 
    tempSelection = []; 

    let q = currentQuestions[currentIdx];
    let correctIndices = q.processedOptions.map((o, i) => o.isCorrect ? i : -1).filter(i => i !== -1);
    let userSorted = userAnswers[currentIdx].sort();
    let correctSorted = correctIndices.sort();
    let isCorrect = JSON.stringify(userSorted) === JSON.stringify(correctSorted);
    
    wrongAnswers[currentIdx] = !isCorrect;

    if (!isCorrect && mode !== "errors") {
        let originalQ = allQuestions.find(x => x.question === q.question && x.topic === q.topic);
        if(originalQ && !errors.includes(originalQ)) errors.push(originalQ);
    }
    
    if (mode === "train") {
        incrementTopic(q.topic, isCorrect);
    }

    if (mode === 'exam') {
        if(currentIdx < currentQuestions.length-1) {
             currentIdx++;
             showQuestion(false);
        } else {
             showResult(true);
        }
    } else {
        showQuestion(false);
    }
}

function showResult(push=true) {
    if (push) navHistory.push("showResult");
    stopTimer();
    
    examFinished = true;

    let correctCount = 0;
    let examTopicStats = {};

    currentQuestions.forEach((q, idx) => {
        let correctIndices = q.processedOptions.map((o, i) => o.isCorrect ? i : -1).filter(i => i !== -1);
        let userSel = userAnswers[idx] || [];
        
        let userSorted = [...userSel].sort();
        let correctSorted = correctIndices.sort();
        let isCorrect = JSON.stringify(userSorted) === JSON.stringify(correctSorted);

        if (isCorrect) correctCount++;

        if (mode === 'exam') {
            if (!examTopicStats[q.topic]) examTopicStats[q.topic] = { total: 0, correct: 0 };
            examTopicStats[q.topic].total++;
            if (isCorrect) examTopicStats[q.topic].correct++;
        }
    });

    let percent = currentQuestions.length > 0 ? Math.round(correctCount / currentQuestions.length * 100) : 0;
    let msg = "";
    
    if(mode === "exam") {
        msg = percent >= 70 ? "<h3 style='color:green'>Экзамен сдан!</h3>" : "<h3 style='color:red'>Экзамен не сдан.</h3><div>Необходимо минимум 70% (84 правильных ответа).</div>";
    } else if(mode === "errors") {
        msg = "<b>Работа над ошибками завершена!</b>";
        currentQuestions.forEach((q, idx) => {
             let correctIndices = q.processedOptions.map((o, i) => o.isCorrect ? i : -1).filter(i => i !== -1);
             let userSel = userAnswers[idx] || [];
             let isCorrect = JSON.stringify(userSel.sort()) === JSON.stringify(correctIndices.sort());
             
             if(isCorrect) {
                 let originalIdx = errors.findIndex(e => e.question === q.question);
                 if(originalIdx !== -1) errors.splice(originalIdx, 1);
             }
        });
    } else {
        msg = "<b>Тренировка завершена!</b>";
    }

    let statsHtml = "";
    if (mode === 'exam') {
        let rows = Object.keys(examTopicStats).sort().map(topic => {
            let s = examTopicStats[topic];
            let rowP = Math.round(s.correct/s.total*100);
            let color = rowP < 50 ? '#ffeaea' : '#f0fff4';
            return `<tr style="background:${color}">
                <td>${topic}</td>
                <td style="text-align:center"><b>${s.correct}</b> / ${s.total} (${rowP}%)</td>
            </tr>`;
        }).join('');
        statsHtml = `
        <div style="max-height: 300px; overflow-y: auto; margin-top:15px; border:1px solid #ccc;">
            <table class="topic-stats-table">
                <thead><tr><th>Тема</th><th>Результат</th></tr></thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
        `;
    }

    document.getElementById('app').innerHTML = `
        <div class="question-block result">
            <h2>Результаты</h2>
            <div style="font-size:3em; color:#b2652d; margin:10px 0;">${percent}%</div>
            <div style="display:flex; justify-content:space-around; width:100%; margin-bottom:15px;">
                <div style="color:green">Верно: <b>${correctCount}</b></div>
                <div style="color:red">Ошибки: <b>${currentQuestions.length - correctCount}</b></div>
            </div>
            <div>${msg}</div>
            ${statsHtml}
            <div style="margin-top:20px; width:100%">
                <button class="btn btn-main" style="width:100%" onclick="onErrorsResult()">Главное меню</button>
            </div>
        </div>
    `;
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
    return render_template_string(MAIN_HTML, topics=topics, NUM_EXAM_QUESTIONS=NUM_EXAM_QUESTIONS)

@app.route("/questions")
def questions():
    return jsonify(all_questions)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
