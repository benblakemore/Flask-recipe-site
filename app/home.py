from flask import (
    Blueprint, render_template)

from app.db import get_quizzes

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route("/")
@bp.route("/home")
def home():

    return render_template('home/home.html', input=input)