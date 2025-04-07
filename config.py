import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "a_really_really_really_really_long_secret_key"
    )
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQLALCHEMY_DATABASE_URI")
        or "postgresql+psycopg2://postgres:2215779638@localhost/my_db"
    )
