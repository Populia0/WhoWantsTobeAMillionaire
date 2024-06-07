from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, csv
from random import randint, shuffle
from threading import Timer

class csvrd:
    def csvFile(self, filename):
        self.readFile(filename)
    def readFile(self, filename):
        csvrd.open()
        sql_create = '''CREATE TABLE IF NOT EXISTS questions(
        text TEXT PRIMARY KEY,
        answer1 TEXT,
        answer2 TEXT,
        answer3 TEXT,
        answer4 TEXT,
        right_answer INTEGER,
        level INTEGER);'''

        cursor.execute(sql_create)

        filename.encode('utf-8')
        with open(filename) as f:
            data = list(csv.reader(f, delimiter=";"))
            for row in data:
                cursor.execute("SELECT text FROM questions WHERE text = ?", (row[0],))
                if cursor.fetchone() is None:
                    cursor.execute('INSERT INTO questions (text,answer1,answer2,answer3,answer4,right_answer,level) VALUES (?, ?, ?, ?, ?, ?, ?)', row)
        conn.commit()
        cursor.close()
        conn.close()

    def open():
        global conn, cursor
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()

    def do(query):
        cursor.execute(query)
        conn.commit()
    
    def close():
        cursor.close()
        conn.close()

class login:
    def createDB(self):
        db_q = sqlite3.connect('users.db')
        cursor_db = db_q.cursor()
        sql_create = '''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        name TEXT
        record INTEGER);'''
        cursor_db.execute(sql_create)
        db_q.commit()
        cursor_db.close()
        db_q.close()
    def get_db_connection():
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        return conn
    def close_db_connection(conn):
        conn.close()


app = Flask(__name__)

csvrd().csvFile('Вопросы.csv')
login().createDB()

last_question = 0
correct = 0
quest = ""
q_id = ""
sum = 0
used_help50 = False
used_help_mist = False
used_help_change = False

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       Login = request.form.get('Login')
       db_lp = sqlite3.connect('users.db')
       cursor_db = db_lp.cursor()

       cursor_db.execute('INSERT INTO users (name, record) VALUES(?, ?)', (Login, 0))
       db_lp.commit()

       cursor_db.close()
       db_lp.close()

       return redirect(url_for('choice'))
    return render_template('login.html')

def check_answer(q_id, ans_text):
    csvrd.open()
    db_q = sqlite3.connect('questions.db')
    cursor = db_q.cursor()
    query = """
    SELECT right_answer
    FROM questions
    WHERE text == (?)
    """
    cursor.execute(query, (q_id,))
    result = cursor.fetchone()

    query = """
    SELECT answer1,answer2,answer3,answer4
    FROM questions
    WHERE text == (?)
    """
    cursor.execute(query, (q_id,))
    answers = cursor.fetchone()
    csvrd.close()
    answers = list(answers)
    if ans_text is not None:
        i = answers.index(ans_text)
    else:
        return False
    if result is None:
        return False
    if result[0] == i+1:
        return True
    return False

def save_answers():
    answer = request.form.get('ans_text')
    global q_id
    global last_question
    global correct
    global sum
    last_question += 1
    if check_answer(q_id, answer):
        correct += 1
        return True
    else:
        return False

def get_question_after(last_question):
    csvrd.open()
    query = """
    SELECT text,answer1,answer2,answer3,answer4
    FROM questions
    WHERE level == (?)
    ORDER BY RANDOM()
    LIMIT 1
    """
    cursor.execute(query, (last_question+1,))
    result = cursor.fetchone()
    csvrd.close()
    return result

def sqore(correct):
    l = [0, 500, 1000, 2000, 3000, 5000, 10000, 15000, 25000, 50000, 100000, 200000, 400000, 800000, 1500000, 3000000]
    return l[correct]

def question_form(question):
    question, *answers_list = question
    global correct
    global q_id
    global used_help50
    global used_help_mist
    global used_help_change
    q_id = question
    print(correct)
    return render_template('game.html', question=question, answers_list=answers_list, sqore = sqore(correct), used_help50=used_help50, used_help_mist=used_help_mist, used_help_change=used_help_change)

def mistake():
    global q_id
    csvrd.open()
    query = """
    SELECT right_answer
    FROM questions
    WHERE text == (?)
    """
    cursor.execute(query, (q_id,))
    result = cursor.fetchone()
    query = """
    SELECT answer1,answer2,answer3,answer4
    FROM questions
    WHERE text == (?)
    """
    cursor.execute(query, (q_id,))
    answers = cursor.fetchone()
    csvrd.close()
    answers = list(answers)

    answer = request.form.get('ans_text')
    global last_question
    global correct
    last_question += 1
    if check_answer(q_id, answer):
        correct += 1
        question = get_question_after(last_question)
        return question
    else:
        question = q_id, *answers
        return question 


def f50():
    global q_id
    csvrd.open()
    query = """
    SELECT right_answer
    FROM questions
    WHERE text == (?)
    """
    cursor.execute(query, (q_id,))
    result = cursor.fetchone()
    query = """
    SELECT answer1,answer2,answer3,answer4
    FROM questions
    WHERE text == (?)
    """
    cursor.execute(query, (q_id,))
    answers = cursor.fetchone()
    csvrd.close()
    k = 0
    answers = list(answers)
    for x in answers:
        if x != result:
            answers.remove(x)
            k += 1
        if k == 2:
            break
    question = q_id, *answers
    return question

def change(last_question):
    csvrd.open()
    global q_id 
    query = """
    SELECT text,answer1,answer2,answer3,answer4
    FROM questions
    WHERE level == (?)
    AND text != (?)
    ORDER BY RANDOM()
    LIMIT 1
    """
    cursor.execute(query, (last_question, q_id,))
    result = cursor.fetchone()
    csvrd.close()
    return result

def call():
    csvrd.open()
    global q_id 
    query = """
    SELECT text,answer1,answer2,answer3,answer4
    FROM questions
    WHERE text == (?)
    """
    cursor.execute(query, (q_id,))
    result = cursor.fetchone()
    csvrd.close()
    return result

@app.route('/game', methods=['GET', 'POST'])
def game():
    global used_help50
    global used_help_mist
    global used_help_change
    f = True
    if request.method == "POST":
        f = save_answers()
    btn = request.form.get('btn')
    if btn == "50 на 50":
        question = f50()
        used_help50 = True
        return question_form(question)
    elif btn == "Замена вопроса":
        question = change(last_question)
        used_help_change = True
        return question_form(question)
    #elif btn == "Звонок другу":
    #    return redirect(url_for('call'))
    elif btn == "Право на ошибку":
        question = mistake()
        used_help_mist = True
        return question_form(question)
    else:
        global sum 
        global correct
        question = get_question_after(last_question) 
        if last_question < 15 and f:
            return question_form(question)
        else:
            if not f:
                if sqore(correct) < sum:
                    correct = 0
                else:
                    l = [0, 500, 1000, 2000, 3000, 5000, 10000, 15000, 25000, 50000, 100000, 200000, 400000, 800000, 1500000, 3000000]
                    correct = l.index(sum) 
            return redirect(url_for('win'))

@app.route('/win', methods=['GET', 'POST'])
def win():
    return render_template('win.html', sqore = sqore(correct))

@app.route('/choice', methods=['GET', 'POST'])
def choice():
    if request.method == 'POST':
        global sum
        sum = int(request.form['nesgoraemaya_summa'])
        return redirect(url_for('game'))
    return render_template('sum.html')

if __name__ == "__main__":
    app.run(debug=True)
