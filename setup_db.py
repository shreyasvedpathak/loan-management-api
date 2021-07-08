from app import db, create_app
from app.config import Config
from app.constants import ROLE
from app.customer.models import Users


def setup_db():
    app = create_app(Config)

    with app.app_context():
        db.drop_all()
        db.create_all()

        ADMIN = Users(username=Config.ADMIN_USERNAME,
                      email=Config.ADMIN_EMAIL,
                      contact=Config.ADMIN_CONTACT,
                      password=Config.ADMIN_PASSWORD,
                      role=ROLE['ADMIN'])

        db.session.add(ADMIN)
        db.session.commit()

        print("Database created.")
        print(f"""
ADMIN <{dict(username=Config.ADMIN_USERNAME,
                      email=Config.ADMIN_EMAIL,
                      contact=Config.ADMIN_CONTACT,
                      password=Config.ADMIN_PASSWORD,
                      role=ROLE['ADMIN'])}>""")


if __name__ == "__main__":
    setup_db()
