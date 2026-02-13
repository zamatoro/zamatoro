import json
import os
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "lawyer_test_secret_key"

# --- КОНФИГУРАЦИЯ ---
ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASS = "admin123"
USERS_FILE = "users.json"
NUM_EXAM_QUESTIONS = 120

# Словарь переводов интерфейса
UI_TEXTS = {
    "ru": {
        "title": "ЮРИДИЧЕСКИЙ ТРЕНАЖЁР",
        "subtitle": "Кыргызская Республика",
        "modes": "Режимы",
        "train": "Тренировка",
        "exam": "Экзамен (120)",
        "errors": "Мои ошибки",
        "logout": "Выйти",
        "change_course": "Сменить курс",
        "admin": "Админка",
        "select_topic": "Выберите темы:",
        "order_seq": "По порядку",
        "order_rnd": "Случайно",
        "start": "Начать",
        "back": "Назад",
        "exit": "Выход",
        "next": "Далее",
        "answer": "Ответить",
        "result": "Результаты",
        "correct": "Верно",
        "wrong": "Ошибки",
        "menu": "Меню",
        "review": "Просмотр ошибок",
        "time_out": "Время вышло!",
        "pass": "Сдал!",
        "fail": "Не сдал",
        "hint_multi": "⚠️ Выберите несколько",
        "q_from": "из",
        "exam_pass_msg": "Экзамен сдан!",
        "exam_fail_msg": "Экзамен не сдан. Необходимо минимум 70% (84 правильных ответа)."
    },
    "kg": {
        "title": "ЮРИДИКАЛЫК ТРЕНАЖЁР",
        "subtitle": "Кыргыз Республикасы",
        "modes": "Режимдер",
        "train": "Машыгуу",
        "exam": "Сынак (120)",
        "errors": "Менин каталарым",
        "logout": "Чыгуу",
        "change_course": "Курсту алмаштыруу",
        "admin": "Админ",
        "select_topic": "Темаларды тандаңыз:",
        "order_seq": "Кезек менен",
        "order_rnd": "Аралаш",
        "start": "Баштоо",
        "back": "Артка",
        "exit": "Чыгуу",
        "next": "Кийинки",
        "answer": "Жооп берүү",
        "result": "Жыйынтыктар",
        "correct": "Туура",
        "wrong": "Каталар",
        "menu": "Меню",
        "review": "Каталарды көрүү",
        "time_out": "Убакыт бүттү!",
        "pass": "Өттү!",
        "fail": "Өткөн жок",
        "hint_multi": "⚠️ Бир нече жооп тандаңыз",
        "q_from": "/",
        "exam_pass_msg": "Сынак тапшырылды!",
        "exam_fail_msg": "Сынак тапшырылган жок. Кеминде 70% (84 туура жооп) керек."
    }
}

# --- РАБОТА С ФАЙЛАМИ ---
def get_questions_file(branch, lang):
    # Карта имен файлов: branch_lang.json
    return f"{branch}_{lang}.json"

def load_questions_for_session():
    branch = session.get('branch', 'notary')
    lang = session.get('lang', 'ru')
    filename = get_questions_file(branch, lang)
    
    if not os.path.exists(filename):
        # Фолбэк для старого файла, если новые не созданы
        if os.path.exists("quiz_questions.json"):
            filename = "quiz_questions.json"
        else:
            return []
            
    try:
        with open(filename, encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def load_users():
    if not os.path.exists(USERS_FILE):
        users = {ADMIN_USERNAME: generate_password_hash(DEFAULT_ADMIN_PASS)}
        save_users(users)
        return users
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

# --- HTML ШАБЛОНЫ ---

BASE_STYLE = """
<style>
:root {
    --bg-color: #c68b3e; --bg-image: repeating-linear-gradient(45deg,#e7b46b 0 8px,transparent 8px 16px), repeating-linear-gradient(-45deg,#e0a858 0 10px,transparent 10px 20px);
    --card-bg: #fffbeedc; --main-card-bg: #a25628d9; --text-color: #000; --main-title-color: #fff;
    --btn-bg: #b2652d; --btn-text: #fff; --btn-hover: #cd8946;
    --option-bg: #fff8; --option-border: transparent; --option-selected-border: #b2652d;
    --correct-bg: #d1ffde; --correct-border: #69dd87; --incorrect-bg: #ffdede; --incorrect-border: #f99393;
    --timer-bg: #a25628; --font-family: Arial, sans-serif;
}
[data-theme="corporate"] {
    --bg-color: #f4f6f9; --bg-image: none; --card-bg: #ffffff; --main-card-bg: #ffffff;
    --text-color: #333; --main-title-color: #003366; --btn-bg: #003366; --btn-text: #fff; --btn-hover: #004080;
    --option-bg: #f8f9fa; --option-border: #e9ecef; --option-selected-border: #003366;
    --correct-bg: #e6fffa; --correct-border: #38b2ac; --incorrect-bg: #fff5f5; --incorrect-border: #fc8181;
    --timer-bg: #003366; --font-family: 'Roboto', sans-serif; --main-card-shadow: 0 10px 30px rgba(0,0,0,0.08);
}
[data-theme="dark"] {
    --bg-color: #121212; --bg-image: none; --card-bg: #1e1e1e; --main-card-bg: #1e1e1e;
    --text-color: #e0e0e0; --main-title-color: #ffd700; --btn-bg: #333; --btn-text: #ffd700; --btn-hover: #444;
    --option-bg: #2c2c2c; --option-border: #333; --option-selected-border: #ffd700;
    --correct-bg: #1b3a26; --correct-border: #2f855a; --incorrect-bg: #3e1b1b; --incorrect-border: #c53030;
    --timer-bg: #ffd700; --font-family: 'Georgia', serif;
}
[data-theme="game"] {
    --bg-color: #4c1d95; --bg-image: linear-gradient(135deg, #6d28d9 0%, #4c1d95 100%);
    --card-bg: #ffffff; --main-card-bg: #ffffff; --text-color: #333; --main-title-color: #4c1d95;
    --btn-bg: #8b5cf6; --btn-text: #fff; --btn-hover: #7c3aed;
    --option-bg: #f3f4f6; --option-border: #e5e7eb; --option-selected-border: #8b5cf6;
    --correct-bg: #d1fae5; --correct-border: #10b981; --incorrect-bg: #fee2e2; --incorrect-border: #ef4444;
    --timer-bg: #8b5cf6; --font-family: 'Comic Sans MS', sans-serif;
}
body { background-color: var(--bg-color); background-image: var(--bg-image); font-family: var(--font-family); color: var(--text-color); margin: 0; transition: background 0.3s; }
.auth-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; }
.auth-card { background: var(--card-bg); padding: 40px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); width: 350px; text-align: center; }
.auth-title { color: var(--btn-bg); margin-bottom: 20px; font-size: 1.5em; font-weight: bold; }
input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; background: #fff; color: #000; }
button { width: 100%; padding: 12px; background: var(--btn-bg); color: var(--btn-text); border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px; }
.btn-red { background: #d9534f !important; color: #fff !important; }
.btn-red:hover { background: #c9302c !important; }
.main-screen { display: flex; align-items: center; justify-content: center; min-height: 97vh; }
.main-card { background: var(--main-card-bg); border-radius: 32px; padding: 38px; box-shadow: var(--main-card-shadow, 0 4px 24px rgba(0,0,0,0.1)); min-width: 335px; max-width: 96vw; display: flex; flex-direction: column; position: relative; }
.user-info { position: absolute; top: 20px; right: 20px; font-size: 0.9em; text-align: right; z-index: 10; }
[data-theme="classic"] .user-info, [data-theme="classic"] .logout-link, [data-theme="classic"] .main-title { color: #fff; }
[data-theme="dark"] .user-info { color: #e0e0e0; }
.logout-link, .change-course-link { text-decoration: underline; cursor: pointer; font-weight: bold; display: block; margin-top: 5px; }
.main-title { font-size: 2.3em; font-weight: bold; color: var(--main-title-color); margin-bottom: 12px; }
.main-btn { background: var(--btn-bg); color: var(--btn-text); border: none; font-size: 1.13em; border-radius: 12px; padding: 13px; margin-bottom: 12px; width: 100%; text-align: left; font-weight: bold; cursor: pointer; display: flex; align-items: center; }
.theme-switcher { position: fixed; top: 20px; right: 20px; display: flex; gap: 12px; z-index: 2000; padding: 8px; border-radius: 20px; background: rgba(255,255,255,0.2); backdrop-filter: blur(4px); }
.theme-btn { width: 32px; height: 32px; border-radius: 50%; border: 2px solid #fff; cursor: pointer; transition: transform 0.2s; }
.theme-btn:hover { transform: scale(1.15); }
.t-classic { background: #c68b3e; } .t-corp { background: #003366; } .t-dark { background: #121212; border-color: #ffd700; } .t-game { background: #8b5cf6; }
.question-block { background: var(--card-bg); border-radius: 24px; padding: 25px 20px; margin: 26px auto 0; max-width: 600px; width: 95%; display: flex; flex-direction: column; position: relative; color: var(--text-color); }
.timer-display { position: sticky; top: 0; background: var(--timer-bg); color: #fff; padding: 5px 15px; border-radius: 0 0 10px 10px; margin: -25px auto 10px; font-weight: bold; z-index: 10; }
[data-theme="dark"] .timer-display { color: #000; }
.option { margin: 10px 0; padding: 15px 12px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; font-size: 1.13em; background: var(--option-bg); border: 2px solid var(--option-border); min-height: 50px; }
.option.selected { border: 2px solid var(--option-selected-border); background: var(--card-bg); }
.option.correct { background: var(--correct-bg); border-color: var(--correct-border); color: #000; }
.option.incorrect { background: var(--incorrect-bg); border-color: var(--incorrect-border); color: #000; }
.checkbox-indicator { width: 24px; height: 24px; min-width: 24px; border: 2px solid var(--btn-bg); border-radius: 4px; margin-right: 15px; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0; }
.option b { margin-right: 15px; min-width: 24px; text-align: center; flex-shrink: 0; }
.selected .checkbox-indicator { background: var(--btn-bg); } .selected .checkbox-indicator::after { content: '✓'; }
.qnav-row { display: flex; gap: 6px; margin: 10px 0; overflow-x: auto; padding-bottom: 8px; scrollbar-width: thin; -webkit-overflow-scrolling: touch; }
.qnav-page { font-size: 1em; min-width: 32px; height: 32px; border-radius: 8px; background: rgba(0,0,0,0.08); color: var(--text-color); text-align: center; line-height: 32px; cursor: pointer; font-weight: bold; margin-right: 0; flex-shrink: 0; }
.qnav-page.current { background: var(--btn-bg); color: var(--btn-text); transform: scale(1.1); }
.qnav-page.done { background: var(--correct-bg); color: #006400; }
.qnav-page.wrong { background: var(--incorrect-bg); color: #8b0000; }
.topic-row { display: flex; align-items: center; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(0,0,0,0.1); background: rgba(0,0,0,0.02); border-radius: 8px; margin-bottom: 6px; }
.topic-label { display: flex; align-items: center; flex: 1; cursor: pointer; gap: 12px; }
.topic-checkbox { width: 20px; height: 20px; transform: scale(1.2); flex-shrink: 0; }
.topic-stats-table th, .topic-stats-table td { border-color: rgba(0,0,0,0.1); color: #000; } 
/* Styles for Selection Screen */
.selection-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; width: 100%; margin-bottom: 20px; }
.select-card { background: rgba(255,255,255,0.8); padding: 20px; border-radius: 15px; cursor: pointer; text-align: center; border: 3px solid transparent; transition: 0.2s; color: #333; }
.select-card:hover { transform: translateY(-3px); }
.select-card.active { border-color: var(--btn-bg); background: #fff; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
.select-icon { font-size: 40px; display: block; margin-bottom: 10px; }
.lang-toggle { display: flex; background: rgba(0,0,0,0.1); border-radius: 12px; padding: 5px; margin-bottom: 25px; }
.lang-opt { flex: 1; text-align: center; padding: 10px; cursor: pointer; border-radius: 8px; font-weight: bold; transition: 0.2s; }
.lang-opt.active { background: var(--btn-bg); color: var(--btn-text); }
@media (max-width: 600px) { .main-card { padding: 20px; } .main-btn { font-size: 1em; } .selection-grid { grid-template-columns: 1fr; } }
</style>
"""

LOGIN_HTML = """<!DOCTYPE html><html><head><title>Вход</title><meta name="viewport" content="width=device-width, initial-scale=1.0">""" + BASE_STYLE + """</head><body data-theme="classic"><div class="auth-container"><div class="auth-card"><div class="auth-title">🔒 Доступ</div><div style="font-size:0.9em;color:#555;margin-bottom:15px;">Только по подписке</div>{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash-msg">{{ messages[0] }}</div>{% endif %}{% endwith %}<form method="POST"><input type="text" name="username" placeholder="Логин" required><input type="password" name="password" placeholder="Пароль" required><button type="submit">Войти</button></form></div></div></body></html>"""
ADMIN_HTML = """<!DOCTYPE html><html><head><title>Админка</title><meta name="viewport" content="width=device-width, initial-scale=1.0">""" + BASE_STYLE + """</head><body data-theme="classic"><div class="auth-container"><div class="auth-card" style="width:500px;"><div class="auth-title">🛠️ Админка</div>{% with messages = get_flashed_messages() %}{% if messages %}<div class="flash-msg">{{ messages[0] }}</div>{% endif %}{% endwith %}<div style="background:#fff;padding:15px;border-radius:10px;margin-bottom:20px;border:1px solid #ccc;"><b>Добавить</b><form method="POST" action="/admin/add"><input type="text" name="new_username" placeholder="Логин" required><input type="text" name="new_password" placeholder="Пароль" required><button type="submit">Создать</button></form></div><div style="background:#fff;padding:15px;border-radius:10px;max-height:300px;overflow-y:auto;border:1px solid #ccc;"><b>Список ({{ users|length }})</b><table style="width:100%;border-collapse:collapse;margin-top:10px;">{% for user in users %}<tr><td style="padding:5px;border-bottom:1px solid #eee;">{{ user }}</td><td style="padding:5px;border-bottom:1px solid #eee;">{% if user != admin_name %}<form method="POST" action="/admin/delete" style="margin:0;"><input type="hidden" name="user_to_delete" value="{{ user }}"><button type="submit" style="background:#d9534f;margin:0;padding:5px 10px;font-size:0.8em;">X</button></form>{% endif %}</td></tr>{% endfor %}</table></div><div class="link"><a href="/">Тренажер</a> | <a href="/logout">Выйти</a></div></div></div></body></html>"""

SELECTION_HTML = """
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Выбор режима</title><meta name="viewport" content="width=device-width, initial-scale=1.0">""" + BASE_STYLE + """</head>
<body>
    <div class="theme-switcher">
        <div class="theme-btn t-classic" onclick="applyTheme('classic')"></div>
        <div class="theme-btn t-corp" onclick="applyTheme('corporate')"></div>
        <div class="theme-btn t-dark" onclick="applyTheme('dark')"></div>
        <div class="theme-btn t-game" onclick="applyTheme('game')"></div>
    </div>
    <div class="main-screen">
        <div class="main-card">
            <div class="main-title" style="text-align:center;width:100%">Выберите курс /<br>Курсту тандаңыз</div>
            
            <form method="POST" action="/set_context" style="width:100%">
                
                <div class="lang-toggle">
                    <div class="lang-opt active" id="lang-ru" onclick="selLang('ru')">Русский 🇷🇺</div>
                    <div class="lang-opt" id="lang-kg" onclick="selLang('kg')">Кыргызча 🇰🇬</div>
                </div>
                <input type="hidden" name="lang" id="inp-lang" value="ru">

                <div class="selection-grid">
                    <div class="select-card active" id="br-notary" onclick="selBranch('notary')">
                        <span class="select-icon">🏛️</span>
                        <b>Нотариат</b>
                    </div>
                    <div class="select-card" id="br-advocacy" onclick="selBranch('advocacy')">
                        <span class="select-icon">⚖️</span>
                        <b>Адвокатура</b>
                    </div>
                </div>
                <input type="hidden" name="branch" id="inp-branch" value="notary">

                <button type="submit" class="main-btn" style="text-align:center;justify-content:center;">Далее / Кийинки</button>
            </form>
            <div style="text-align:center;width:100%;margin-top:10px;">
                <a href="/logout" class="logout-link" style="color:var(--text-color)">Выйти / Чыгуу</a>
            </div>
        </div>
    </div>
    <script>
        let curTheme = localStorage.getItem('appTheme') || 'classic';
        function applyTheme(t){ document.body.setAttribute('data-theme', t); localStorage.setItem('appTheme', t); }
        applyTheme(curTheme);

        function selLang(l) {
            document.getElementById('inp-lang').value = l;
            document.getElementById('lang-ru').classList.remove('active');
            document.getElementById('lang-kg').classList.remove('active');
            document.getElementById('lang-'+l).classList.add('active');
        }
        function selBranch(b) {
            document.getElementById('inp-branch').value = b;
            document.getElementById('br-notary').classList.remove('active');
            document.getElementById('br-advocacy').classList.remove('active');
            document.getElementById('br-'+b).classList.add('active');
        }
    </script>
</body>
</html>
"""

MAIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Тренажер</title><meta name="viewport" content="width=device-width, initial-scale=1.0">""" + BASE_STYLE + """</head><body><div id="app"></div><script>
const topics = {{ topics|tojson }};
const NUM_EXAM_QUESTIONS = {{ NUM_EXAM_QUESTIONS|tojson }};
const USERNAME = {{ session.get('user', 'Гость')|tojson }};
const IS_ADMIN = {{ (session.get('user') == 'admin')|tojson }};
const LANG = {{ session.get('lang', 'ru')|tojson }};
const BRANCH = {{ session.get('branch', 'notary')|tojson }};
const TXT = {{ UI_TEXTS[session.get('lang', 'ru')]|tojson }};

let allQuestions = [], currentQuestions = [], userAnswers = [], currentIdx = 0, mode = null, errors = [], wrongAnswers = [], examFinished = false, tempSelection = [];
let currentTheme = localStorage.getItem('appTheme') || 'classic';

function applyTheme(t){ document.body.setAttribute('data-theme', t); localStorage.setItem('appTheme', t); }
applyTheme(currentTheme);

function getStats(){ return JSON.parse(localStorage.getItem("topicStats_"+USERNAME+"_"+BRANCH+"_"+LANG) || "{}"); }
function setStats(s){ localStorage.setItem("topicStats_"+USERNAME+"_"+BRANCH+"_"+LANG, JSON.stringify(s)); }
function incTopic(t, ok){ let s=getStats(); if(!s[t])s[t]={total:0,correct:0}; if(ok)s[t].correct=(s[t].correct||0)+1; s[t].total=(s[t].total||0)+1; setStats(s); }
function fetchQ(){ fetch("/questions").then(r=>r.json()).then(d=>{allQuestions=d;}); }
function shuffle(a){ for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a;}
function prepQ(qs){ return qs.map(q=>{ 
    let opts = q.options.map((t,i)=>({text:t.replace(/^[-+]/,''), isCorrect:t.startsWith('+'), idx:i}));
    let shuf = shuffle([...opts]);
    let clean = q.question.replace(/^(Выберите\s+(один\s+)?вариант\s+ответа|Выберите\s+правильный\s+ответ|Төмөнкүлөрдүн\s+ичинен\s+бирөөсүн\s+тандаңыз)[:\.]?\s*/i,"");
    if(clean.length>0) clean=clean.charAt(0).toUpperCase()+clean.slice(1);
    return {...q, question:clean, processedOptions:shuf, isMulti:shuf.filter(o=>o.isCorrect).length>1};
});}
function logout(){ window.location.href="/logout"; }
function changeCourse(){ window.location.href="/reset_context"; }

function mainMenu(){
    clearInterval(window.examTimer);
    let adm = IS_ADMIN ? `<a href="/admin" class="admin-link">🛠️ ${TXT.admin}</a>`:'';
    let brTitle = (BRANCH==='notary') ? (LANG==='ru'?'Нотариат':'Нотариат') : (LANG==='ru'?'Адвокатура':'Адвокатура');
    document.getElementById('app').innerHTML = `
    <div class="theme-switcher">
        <div class="theme-btn t-classic" onclick="applyTheme('classic')"></div>
        <div class="theme-btn t-corp" onclick="applyTheme('corporate')"></div>
        <div class="theme-btn t-dark" onclick="applyTheme('dark')"></div>
        <div class="theme-btn t-game" onclick="applyTheme('game')"></div>
    </div>
    <div class="main-screen"><div class="main-card">
        <div class="user-info">👤 ${USERNAME}<br>${adm}
            <span class="change-course-link" onclick="changeCourse()">🔄 ${TXT.change_course}</span>
            <span class="logout-link" onclick="logout()">${TXT.logout}</span>
        </div>
        <div class="main-icon">${BRANCH==='notary'?'🏛️':'⚖️'}</div>
        <div class="main-title">${TXT.title}<br><span style="font-size:0.6em;opacity:0.8">${brTitle} (${LANG.toUpperCase()})</span></div>
        <div class="main-subtitle">${TXT.subtitle}</div>
        <div class="main-modes"><div class="modes-title">${TXT.modes}</div>
            <button class="main-btn" onclick="trainingMenu()"><span class="main-btn-icon">🧑‍⚖️</span> ${TXT.train}</button>
            <button class="main-btn" onclick="startExam()"><span class="main-btn-icon">✅</span> ${TXT.exam}</button>
            <button class="main-btn" onclick="startErrors()" id="errors-btn"><span class="main-btn-icon">❌</span> ${TXT.errors}</button>
        </div><div class="main-version" style="right:36px;left:auto;">v4.0 (Multi)</div>
    </div></div>`;
    document.getElementById('errors-btn').disabled = errors.length===0;
}

function trainingMenu(){
    let st = getStats();
    let html = topics.map((t,i)=>{
        let tot = allQuestions.filter(q=>q.topic===t).length;
        let cor = (st[t]||{}).correct||0;
        return `<div class="topic-row"><label class="topic-label"><input type="checkbox" id="topic${i}" class="topic-checkbox"><span class="topic-text">${t}</span></label><span class="topic-stats">${cor}/${tot}</span></div>`;
    }).join('');
    document.getElementById('app').innerHTML = `<div class="question-block"><h2>${TXT.train}</h2><div style="margin-bottom:10px;opacity:0.7;">${TXT.select_topic}</div><div class="topics-list" style="max-height:50vh;overflow-y:auto;">${html}</div><div style="margin-top:15px;background:rgba(0,0,0,0.05);padding:10px;border-radius:8px;"><label style="margin-right:15px;"><input type="radio" name="order" value="sequential" checked> ${TXT.order_seq}</label><label><input type="radio" name="order" value="random"> ${TXT.order_rnd}</label></div><button class="btn btn-main" onclick="startTrain()">${TXT.start}</button><button class="btn btn-gray" onclick="mainMenu()">${TXT.back}</button></div>`;
}

function startTrain(){
    let sel = []; topics.forEach((t,i)=>{if(document.getElementById('topic'+i).checked)sel.push(t);});
    if(sel.length===0){alert("Select topic!");return;}
    let order = document.querySelector('input[name="order"]:checked').value;
    fetch("/questions").then(r=>r.json()).then(d=>{
        let qs = d.filter(q=>sel.includes(q.topic));
        if(order==="random") qs=qs.sort(()=>Math.random()-0.5);
        mode="train"; examFinished=false; currentQuestions=prepQ(qs); userAnswers=Array(qs.length).fill(null); currentIdx=0; wrongAnswers=Array(qs.length).fill(false); 
        initQScreen(); showQ();
    });
}

function startExam(){
    fetch("/questions").then(r=>r.json()).then(d=>{
        let byT={}; d.forEach(q=>{if(!byT[q.topic])byT[q.topic]=[];byT[q.topic].push(q);});
        let eqs=[], rem=[];
        for(let t in byT){
            let q=byT[t].sort(()=>Math.random()-0.5);
            let c=q.length, take=(c>140)?Math.floor(Math.random()*3)+6 : Math.floor(Math.random()*4)+1;
            take=Math.min(take,c);
            for(let i=0;i<take;i++)eqs.push(q[i]);
            for(let i=take;i<c;i++)rem.push(q[i]);
        }
        rem=rem.sort(()=>Math.random()-0.5);
        let need=NUM_EXAM_QUESTIONS-eqs.length;
        if(need>0) eqs=eqs.concat(rem.slice(0,need));
        eqs=eqs.sort(()=>Math.random()-0.5).slice(0,NUM_EXAM_QUESTIONS);
        mode="exam"; examFinished=false; currentQuestions=prepQ(eqs); userAnswers=Array(eqs.length).fill(null); currentIdx=0; wrongAnswers=Array(eqs.length).fill(false);
        window.examEndTime = Date.now()+7200000; startTimer(); 
        initQScreen(); showQ();
    });
}

function startErrors(){
    if(errors.length===0){alert("No errors!");return;}
    mode="errors"; examFinished=false;
    let raw=errors.map(e=>allQuestions.find(q=>q.question===e.question&&q.topic===e.topic)||e);
    currentQuestions=prepQ(raw); userAnswers=Array(currentQuestions.length).fill(null); currentIdx=0; wrongAnswers=Array(currentQuestions.length).fill(false); 
    initQScreen(); showQ();
}

function reviewErrors(){
    let wq=[], wa=[];
    currentQuestions.forEach((q,i)=>{
        let c=q.processedOptions.map((o,x)=>o.isCorrect?x:-1).filter(x=>x!==-1);
        let u=userAnswers[i]||[];
        if(JSON.stringify(u.sort())!==JSON.stringify(c.sort())){ wq.push(q); wa.push(u); }
    });
    currentQuestions=wq; userAnswers=wa; currentIdx=0; mode="review";
    wrongAnswers=Array(wq.length).fill(true);
    initQScreen(); showQ();
}

function startTimer(){
    if(window.examTimer)clearInterval(window.examTimer);
    window.examTimer=setInterval(()=>{
        let d=window.examEndTime-Date.now();
        if(d<=0){clearInterval(window.examTimer);alert(TXT.time_out);showRes();return;}
        let h=Math.floor(d/3600000), m=Math.floor((d%3600000)/60000), s=Math.floor((d%60000)/1000);
        let el=document.getElementById('timer'); if(el)el.innerText=`⏱️ ${h}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
    },1000);
}

function initQScreen() {
    let tm = mode==='exam' ? `<div id="timer" class="timer-display">...</div>`:'';
    let pag = currentQuestions.map((_,i)=>`<span class="qnav-page" id="qn-${i}" onclick="gotoQ(${i})">${i+1}</span>`).join('');
    let title = mode==='review' ? `<div style="color:red;font-weight:bold;margin-bottom:10px;">${TXT.review}</div>` : '';
    
    document.getElementById('app').innerHTML = `
    <div style="display:flex;gap:20px;justify-content:center;">
        <div class="question-block">
            ${tm} ${title}
            <div style="display:flex;justify-content:space-between;font-size:0.9em;opacity:0.6;">
                <span id="q-counter"></span><span id="q-topic"></span>
            </div>
            <div class="qnav-row" id="qrow">
                <span class="qnav-page" id="btn-prev" onclick="moveQ(-1)">&lt;</span>
                ${pag}
                <span class="qnav-page" id="btn-next" onclick="moveQ(1)">&gt;</span>
            </div>
            <div style="margin:10px 0 15px"><b id="q-text"></b></div>
            <div id="q-hint" style="color:var(--btn-bg);font-weight:bold;margin-bottom:5px;"></div>
            <div id="q-opts"></div>
            <div style="display:flex;justify-content:space-between;gap:10px;margin-top:20px">
                <button class="btn btn-gray" onclick="mainMenu()">${TXT.exit}</button>
                <button class="btn btn-main" id="btn-action" onclick="subAns()">${TXT.answer}</button>
            </div>
        </div>
    </div>`;
}

function showQ(){
    let q = currentQuestions[currentIdx], tot = currentQuestions.length;
    document.getElementById('q-counter').innerText = `№ ${currentIdx+1} ${TXT.q_from} ${tot}`;
    document.getElementById('q-topic').innerText = q.topic;
    document.getElementById('q-text').innerText = q.question;
    document.getElementById('q-hint').innerText = q.isMulti ? TXT.hint_multi : "";
    document.getElementById('btn-action').innerText = userAnswers[currentIdx]!==null ? TXT.next : TXT.answer;
    
    for(let i=0; i<tot; i++){
        let el = document.getElementById(`qn-${i}`);
        let cls = "qnav-page";
        if(i===currentIdx) cls += " current";
        else if(userAnswers[i]!==null){
            if(mode==='exam'&&!examFinished) cls += " done";
            else cls += wrongAnswers[i] ? " wrong" : " done";
        }
        el.className = cls;
    }
    document.getElementById('btn-prev').style.opacity = currentIdx===0 ? 0.5 : 1;
    document.getElementById('btn-next').style.opacity = currentIdx===tot-1 ? 0.5 : 1;

    let lets=['A','B','C','D','E','F','G']; // Latyn letters for universal
    let opts = q.processedOptions.map((o,i)=>{
        let c="option", sel=userAnswers[currentIdx]&&userAnswers[currentIdx].includes(i);
        let show=(userAnswers[currentIdx]!==null)&&(mode!=='exam'||examFinished||mode==='review');
        if(sel)c+=" selected";
        if(show){
            if(o.isCorrect)c+=" correct";
            else if(sel&&!o.isCorrect)c+=" incorrect";
            else if(!sel&&o.isCorrect)c+=" missed";
        }
        let pre = q.isMulti ? `<div class="checkbox-indicator"></div>` : `<b>${lets[i]})</b>`;
        return `<div class="${c}" onclick="selOpt(${i})">${pre} ${o.text}</div>`;
    }).join('');
    document.getElementById('q-opts').innerHTML = opts;
    let activeEl = document.getElementById(`qn-${currentIdx}`);
    if(activeEl) activeEl.scrollIntoView({behavior: "smooth", inline: "center", block: "nearest"});
}

function moveQ(dir) {
    let newIdx = currentIdx + dir;
    if(newIdx >= 0 && newIdx < currentQuestions.length) gotoQ(newIdx);
}
function gotoQ(i){ tempSelection=[]; currentIdx=i; showQ(); }
function selOpt(i){
    if(userAnswers[currentIdx]!==null)return;
    let q=currentQuestions[currentIdx];
    if(q.isMulti){
        if(tempSelection.includes(i))tempSelection=tempSelection.filter(x=>x!==i); else tempSelection.push(i);
    } else tempSelection=[i];
    let els=document.querySelectorAll('.option'); 
    els.forEach((e,x)=>{
        if(tempSelection.includes(x)) e.classList.add('selected');
        else e.classList.remove('selected');
    });
}
function subAns(){
    if(userAnswers[currentIdx]!==null){
        if(currentIdx<currentQuestions.length-1){tempSelection=[];currentIdx++;showQ();} else showRes();
        return;
    }
    if(tempSelection.length===0){alert("!");return;}
    userAnswers[currentIdx]=[...tempSelection]; tempSelection=[];
    let q=currentQuestions[currentIdx];
    let cor=q.processedOptions.map((o,i)=>o.isCorrect?i:-1).filter(i=>i!==-1);
    let usr=userAnswers[currentIdx].sort(), cr=cor.sort();
    let isOk = JSON.stringify(usr)===JSON.stringify(cr);
    wrongAnswers[currentIdx]=!isOk;
    if(!isOk && mode!=="errors" && mode!=="review"){
        let orig=allQuestions.find(x=>x.question===q.question&&x.topic===q.topic);
        if(orig&&!errors.includes(orig))errors.push(orig);
    }
    if(mode==="train") incTopic(q.topic, isOk);
    if(mode==='exam'){ if(currentIdx<currentQuestions.length-1){currentIdx++;showQ();}else showRes(); } else showQ();
}

function showRes(){
    clearInterval(window.examTimer); examFinished=true;
    if(mode==='review'){ mainMenu(); return; } 

    let cor=0, tStats={};
    currentQuestions.forEach((q,i)=>{
        let c=q.processedOptions.map((o,x)=>o.isCorrect?x:-1).filter(x=>x!==-1);
        let u=userAnswers[i]||[];
        let ok=JSON.stringify(u.sort())===JSON.stringify(c.sort());
        if(ok)cor++;
        if(mode==='exam'){ if(!tStats[q.topic])tStats[q.topic]={tot:0,cor:0}; tStats[q.topic].tot++; if(ok)tStats[q.topic].cor++; }
    });
    let p=Math.round(cor/currentQuestions.length*100)||0;
    
    let msg = "";
    if(mode === "exam") {
        msg = p >= 70 ? `<h3 style='color:green'>${TXT.exam_pass_msg}</h3>` : `<h3 style='color:red'>${TXT.exam_fail_msg}</h3>`;
    } else if(mode === "errors") {
        msg = "<b>Completed!</b>";
    } else {
        msg = "<b>Completed!</b>";
    }

    let tbl="", reviewBtn="";
    if(mode==='exam'){
        let rows=Object.keys(tStats).map(t=>{
            let s=tStats[t], pp=Math.round(s.cor/s.tot*100);
            return `<tr style="background:${pp<50?'#ffeaea':'#f0fff4'}"><td>${t}</td><td style="text-align:center"><b>${s.cor}</b>/${s.tot}</td></tr>`;
        }).join('');
        tbl=`<div style="max-height:300px;overflow-y:auto;margin-top:15px;border:1px solid #ccc;"><table class="topic-stats-table"><thead><tr><th>Тема</th><th>%</th></tr></thead><tbody>${rows}</tbody></table></div>`;
        if(currentQuestions.length - cor > 0) {
            reviewBtn = `<button class="btn btn-red" style="width:100%; margin-top:10px;" onclick="reviewErrors()">${TXT.review}</button>`;
        }
    }
    document.getElementById('app').innerHTML=`<div class="question-block result"><div style="font-size:3em;color:var(--btn-bg);margin:10px 0;">${p}%</div><div>${TXT.correct}: ${cor} | ${TXT.wrong}: ${currentQuestions.length-cor}</div><div>${msg}</div>${tbl}${reviewBtn}<div style="margin-top:20px;"><button class="btn btn-main" style="width:100%" onclick="mainMenu()">${TXT.menu}</button></div></div>`;
}

window.onload=()=>{fetchQ();mainMenu();}
</script></body></html>"""

# --- МАРШРУТЫ FLASK ---

@app.route("/", methods=["GET"])
def index():
    if 'user' not in session: return redirect(url_for('login'))
    # Если контекст еще не выбран, показываем экран выбора
    if 'branch' not in session:
        return render_template_string(SELECTION_HTML)
    
    # Загружаем вопросы согласно контексту
    qs = load_questions_for_session()
    all_topics = sorted(set(q["topic"] for q in qs))
    
    return render_template_string(
        MAIN_HTML, 
        topics=all_topics, 
        NUM_EXAM_QUESTIONS=NUM_EXAM_QUESTIONS,
        UI_TEXTS=UI_TEXTS
    )

@app.route("/set_context", methods=["POST"])
def set_context():
    session['branch'] = request.form.get('branch')
    session['lang'] = request.form.get('lang')
    return redirect(url_for('index'))

@app.route("/reset_context")
def reset_context():
    session.pop('branch', None)
    session.pop('lang', None)
    return redirect(url_for('index'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u, p = request.form.get("username"), request.form.get("password")
        users = load_users()
        if u in users and check_password_hash(users[u], p):
            session['user'] = u
            return redirect(url_for('index'))
        else:
            flash("Неверный логин или пароль")
    return render_template_string(LOGIN_HTML)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/admin", methods=["GET"])
def admin():
    if session.get('user') != ADMIN_USERNAME: return redirect(url_for('index'))
    return render_template_string(ADMIN_HTML, users=load_users(), admin_name=ADMIN_USERNAME)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    if session.get('user') != ADMIN_USERNAME: return redirect(url_for('index'))
    u, p = request.form.get("new_username"), request.form.get("new_password")
    users = load_users()
    if u not in users:
        users[u] = generate_password_hash(p)
        save_users(users)
        flash(f"Добавлен: {u}")
    return redirect(url_for('admin'))

@app.route("/admin/delete", methods=["POST"])
def admin_del():
    if session.get('user') != ADMIN_USERNAME: return redirect(url_for('index'))
    u = request.form.get("user_to_delete")
    users = load_users()
    if u != ADMIN_USERNAME and u in users:
        del users[u]
        save_users(users)
        flash(f"Удален: {u}")
    return redirect(url_for('admin'))

@app.route("/questions")
def get_qs():
    if 'user' not in session: return jsonify([])
    return jsonify(load_questions_for_session())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)