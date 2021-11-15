from flask import (
    Blueprint, render_template, request, flash)

from app.db import get_db, get_quizzes

bp = Blueprint('quiz', __name__, url_prefix='/quiz')


@bp.route("/createQuiz", methods=('GET', 'POST'))
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quizName']
        question = request.form['question']
        answers = []
        error = ''
        for i in range(1, 6):
            answer = request.form['answer' + str(i)]
            if answer != '':  # an answer field that hasn't been filled in will be ''
                answers.append(answer)
        if len(answers) < 3:
            error += 'Please provide at least 3 answers. '
        if quiz_name == '':
            error += 'Please provide a quiz name. '
        db = get_db()
        db.execute(
            'insert or ignore into quizzes (name) values (?)',
            (quiz_name,)
        )
        # TODO - prevent duplicate questions
        db.execute(
            'insert into questions (question, quiz) values (?, (select id from quizzes where name is ?))',
            (question, quiz_name)
        )
        for answer in answers:
            db.execute(
                'insert into answers (answer, question) values (?, (select id from questions where question is ?'
                'and quiz is (select id from quizzes where name is ?)))',
                (answer, question, quiz_name)
            )
        if error is None:
            db.commit()
        else:
            flash(error)
    return render_template('quiz/createQuiz.html')


def get_answer_letters():
    return ['A', 'B', 'C', 'D', 'E']


def get_quiz_id_from_quiz_name(quiz_name):
    db = get_db()
    quiz_id = db.execute(
        'select id from quizzes where name is ?',
        (quiz_name,)
    ).fetchone()[0]
    return quiz_id


def get_questions_from_quiz_id(quiz_id):
    db = get_db()
    questions = []
    question_rows = db.execute(
        'select * from questions where quiz is ?',
        (quiz_id,)).fetchall()
    for item in question_rows:
        questions.append(item[1])
    return questions


def get_answers_from_question_name(question_name):
    db = get_db()
    answers = []
    answer_rows = db.execute(
        'select answer from answers where question is (select id from questions where question is ?)',
        (question_name,)).fetchall()
    for item in answer_rows:
        answers.append(item[0])
    return answers


def get_questions_and_answers(quiz_id):
    questions = get_questions_from_quiz_id(quiz_id)

    questions_and_answers = []
    for question in questions:
        answers = get_answers_from_question_name(question)
        questions_and_answers.append([question, answers])
    return questions_and_answers


@bp.route('<quizname>', methods=('GET',))
def view_quiz(quizname):
    quiz_id = get_quiz_id_from_quiz_name(quizname)

    input = {'quiz_name': quizname, 'questions_and_answers': get_questions_and_answers(quiz_id),
             'answer_letters': get_answer_letters()}
    return render_template('quiz/view_quiz.html', input=input)


@bp.route('/delete/<quiz_name>', methods=['POST'])
def delete_quiz(quiz_name):
    db = get_db()
    quiz_id = get_quiz_id_from_quiz_name(quiz_name)
    questions = get_questions_from_quiz_id(quiz_id)
    for question in questions:
        db.execute('delete from answers where question is (select id from questions where question is ?)',
                   (question,))
    db.execute('delete from questions where quiz is (select id from quizzes where name is ?)',
               (quiz_name,))
    db.execute('delete from quizzes where name is ?',
               (quiz_name,))
    db.commit()
    return render_template('home/home.html', input={'quizzes': get_quizzes()})


@bp.route('/delete/<quiz_name>/<question>', methods=['POST'])
def delete_question(quiz_name, question):
    db = get_db()
    db.execute('delete from questions where question is ? and (select id from quizzes where name is ?)',
               (question, quiz_name))
    db.commit()
    return view_quiz(quiz_name)
