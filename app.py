from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow


from config import Config

app = Flask(__name__)


app.config.from_object(Config)
app.config.from_object(Config)


db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)


from views import *
