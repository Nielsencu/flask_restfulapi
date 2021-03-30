from flask import Flask

from .backend.views import backend
from .models import db, migrate
from functools import wraps

BLUEPRINTS = (backend,)

def create_app(app_name="project", blueprints=None):
    app = Flask(__name__)
        
    print("Creating app")

    app.config.from_object("project.config")
    app.app_context().push()

    if blueprints is None:
        create_blueprints(app, BLUEPRINTS)

    init_app(app)

    db.drop_all() # Use for dev env
    db.create_all()
    db.session.commit()

    return app

def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    

def create_blueprints(app,blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


if __name__ == '__main__':
    create_app()

