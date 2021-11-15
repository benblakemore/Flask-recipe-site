import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username + ' ' + password)
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        print('password is ' + user['password'])
        if user is None:
            error = 'Incorrect username.'
        elif not user['password'] == password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home.home'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/sign_up', methods=('GET', 'POST'))
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if (username or password) is None:
            error = 'One or more required fields left blank'

        db = get_db()
        user = get_user_by_username(username)  # check to see if user exists already
        if user is not None:
            error = 'Username already taken'
        else:
            db.execute('INSERT INTO users (username, password) values (?, ?)',
                       (username, password))
            db.commit()
        if error is None:
            user = get_user_by_username(username)  # get again as user is now added to db
            session['user_id'] = user['id']
            return redirect(url_for('/home'))

        flash(error)

    return render_template('/auth/sign_up.html')


def get_user_by_username(username):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)
                      ).fetchone()
    return user


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
