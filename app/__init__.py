# Internal imports
from app.config import Config

# External imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)

    from app.main.routes import main
    from app.agent.routes import agent
    from app.admin.routes import admin
    from app.customer.routes import customer
    
    app.register_blueprint(main)
    app.register_blueprint(agent)
    app.register_blueprint(admin)
    app.register_blueprint(customer)

    return app
