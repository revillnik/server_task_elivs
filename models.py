from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    language = db.Column(db.String(255), nullable=False, default="ru")
    user_achievements = db.relationship(
        "Achievement",
        secondary="times_achievement_to_user",
        backref="achievement_users",
    )

    def __repr__(self):
        return self.username


class Time_achievement_to_user(db.Model):
    __tablename__ = "times_achievement_to_user"
    __table_args__ = (db.PrimaryKeyConstraint("user_id", "achievement_id"),)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.id"))
    date_receipt = db.Column(db.DateTime(), default=datetime.now)


class Achievement(db.Model):
    __tablename__ = "achievements"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    score = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text(), nullable=True)

    def __repr__(self):
        return self.title
