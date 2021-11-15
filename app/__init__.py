import os

from flask import Flask, render_template

def create_app():
    #  Creates app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "recipe_site.db")
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth, home, quiz
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(quiz.bp)

    return app