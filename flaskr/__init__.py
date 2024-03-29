import os
from dotenv import load_dotenv

from flask import Flask
from flaskr import db

from flaskr.api import bp as api_bp
from flaskr.models import bp as models_bp

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['MONGO_URI'] = MONGO_URI
    db.init_app(app)

    app.db = db.get_db()

    # register blueprint
    app.register_blueprint(api_bp)
    app.register_blueprint(models_bp)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app