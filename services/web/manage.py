from flask.cli import FlaskGroup

from project.app import app
from project.models import db,User

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

def seed_db():
    db.session.add(User(name="wangwang", password="12345"))
    db.session.commit()

if __name__ == '__main__':
    cli()
    
    
    