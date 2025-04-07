from app import ma, db
from models import Achievement, User, Time_achievement_to_user


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session


class AchievementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Achievement
        load_instance = True
        sqla_session = db.session


class Time_achievement_to_user_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Time_achievement_to_user
        load_instance = True
        sqla_session = db.session

    user_id = ma.auto_field()
    achievement_id = ma.auto_field()


all_time_achievement_to_user_schema = Time_achievement_to_user_schema(many=True)

user_schema = UserSchema()
all_users_schema = UserSchema(many=True)


achievement_schema = AchievementSchema()
all_achievements_schema = AchievementSchema(many=True)
