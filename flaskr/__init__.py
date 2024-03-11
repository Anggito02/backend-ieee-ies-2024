import os

from flask import Flask
from . import db
from .api import bp

MONGO_URI = 'mongodb://localhost:27017/db_ieee-ies-2024'

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['MONGO_URI'] = MONGO_URI
    db.init_app(app)

    app.db = db.get_db()

    # register blueprint
    app.register_blueprint(bp)

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