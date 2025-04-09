from flask import abort, request
from sqlalchemy import func, desc
from googletrans import Translator
from app import app, db
from models import User, Achievement, Time_achievement_to_user
from serializers import (
    all_time_achievement_to_user_schema,
    all_achievements_schema,
    achievement_schema,
    all_users_schema,
    user_schema,
)
import json


@app.route("/")
def index():
    return "Start url"


# маршрут для выдачи достижений пользователям с сохранением даты через доп.таблицу m2m
@app.route("/give_achievement_to_user", methods=["post"])
def give_achievement_to_user():
    achievement_to_user_data = request.get_json()
    try:
        user_for_achievement = db.session.query(User).get_or_404(
            achievement_to_user_data.get("user_id")
        )
        achievement_for_user = db.session.query(Achievement).get_or_404(
            achievement_to_user_data.get("achievement_id")
        )
        user_for_achievement.user_achievements.append(achievement_for_user)
        db.session.add(user_for_achievement)
        db.session.commit()
        return "user_for_achievement"
    except:
        return "Error give achievement to user"


# маршрут, чтобы показать все достижения выданные пользователям вместе с датами (показ таблицы m2m)
@app.route("/all_time_achievement_to_user")
def get_all_time_achievement_to_user():
    all_time_achievement_to_user_data = db.session.query(
        Time_achievement_to_user.achievement_id,
        Time_achievement_to_user.user_id,
        Time_achievement_to_user.date_receipt,
    ).all()
    return all_time_achievement_to_user_schema.dump(all_time_achievement_to_user_data)


# маршут, чтобы показать все достижения
@app.route("/all_achievements")
def get_all_achievements():
    all_achievements_data = db.session.query(Achievement).all()
    return all_achievements_schema.dump(all_achievements_data)


# маршрут для отображения и добавления конкретных достижений по pk
@app.route("/achievement/<int:achievement_pk>", methods=["get", "post"])
def get_achievement(achievement_pk):
    if request.method == "GET":
        one_achievement = db.session.query(Achievement).get_or_404(achievement_pk)
        if one_achievement is not None:
            return achievement_schema.dump(one_achievement)
        else:
            abort(404, f"Achievement with pk={achievement_pk} not found")
    elif request.method == "POST":
        achievement_data = request.get_json()
        try:
            new_achievement = Achievement(**achievement_data)
            db.session.add(new_achievement)
            db.session.commit()
            return f'Success load achievement with title = {achievement_data["title"]}'
        except:
            return "Error load achievement"


# маршрут для отображения всех пользователей
@app.route("/all_users", methods=["get", "post"])
def get_all_users():
    if request.method == "GET":
        all_users_data = db.session.query(User).all()
        return all_users_schema.dump(all_users_data)
    elif request.method == "POST":
        data_for_create_user = request.get_json()
        try:
            new_user = User(
                id=data_for_create_user.get("id"),
                username=data_for_create_user.get("username"),
                language=data_for_create_user.get("language"),
                user_achievements=data_for_create_user.get("user_achievements", list()),
            )
            db.session.add(new_user)
            db.session.commit()
            return f"user - {data_for_create_user.get("username")} был создан!"
        except:
            return "Создать пользователя с такими данными невозможно"


# маршрут для отображения конкретных пользователей по pk
@app.route("/user/<int:user_pk>")
def get_user(user_pk):
    one_user = db.session.query(User).get_or_404(user_pk)
    if one_user is not None:
        return user_schema.dump(one_user)
    else:
        abort(404, f"User with pk={user_pk} not found")


# маршрут для отображения достижений конкретных пользователей на выбранном языке
@app.route("/user_achievements_with_language/<int:user_pk>")
async def get_user_achievements_with_language(user_pk):
    result_list_with_tranlsated_text = list()
    user = db.session.query(User).get_or_404(user_pk)
    user_achievements = (
        db.session.query(Achievement)
        .join(Achievement.achievement_users)
        .filter(User.id == user_pk)
        .all()
    )
    for i in user_achievements:
        translator = Translator()
        translate_text = await translator.translate(i.title, dest=user.language)
        data_give_achievement = (
            db.session.query(Time_achievement_to_user)
            .filter(
                Time_achievement_to_user.user_id == user.id,
                Time_achievement_to_user.achievement_id == i.id,
            )
            .one_or_none()
        )
        user_dict_data = {
            "title": translate_text.text,
            "date_receipt": str(data_give_achievement.date_receipt.date()),
        }
        result_list_with_tranlsated_text.append(user_dict_data)

    return json.dumps(
        {f"{user.username}": result_list_with_tranlsated_text},
        ensure_ascii=False,
    )


# маршрут для вывода статистической информации
@app.route("/statistic_information")
def get_statistic_information():
    # пользователь с макс количеством достижений (штук)
    query_for_user_with_max_count_achievements = (
        db.session.query(User, func.count(Achievement.id))
        .join(User.user_achievements)
        .group_by(User.id)
        .order_by(desc(func.count(Achievement.id)))
        .all()
    )

    max_count_achievements = query_for_user_with_max_count_achievements[0][1]
    users_with_max_count_achievements = list(
        map(
            lambda x: x[0].username,
            filter(
                lambda x: x[1] == max_count_achievements,
                query_for_user_with_max_count_achievements,
            ),
        )
    )

    # пользователь с максимальным количеством очков достижений

    query_for_user_statistic = (
        db.session.query(User, func.sum(Achievement.score))
        .join(User.user_achievements)
        .group_by(User.id)
        .order_by(desc(func.sum(Achievement.score)))
        .all()
    )

    # пользователи с максимальной разностью

    max_dif = [
        query_for_user_statistic[0][0].username,
        (
            query_for_user_statistic[-1][0].username
            if len(query_for_user_statistic) > 1
            else "database have one user"
        ),
    ]

    # пользователи с минимальной разностью

    if len(query_for_user_statistic) > 1:
        for i in range(0, len(query_for_user_statistic) - 1):
            if i == 0:
                min_dif = (
                    query_for_user_statistic[i][1] - query_for_user_statistic[i + 1][1],
                    query_for_user_statistic[i],
                    query_for_user_statistic[i + 1],
                )
            else:
                next_min_dif = (
                    query_for_user_statistic[i][1] - query_for_user_statistic[i + 1][1],
                    query_for_user_statistic[i],
                    query_for_user_statistic[i + 1],
                )
                if min_dif[0] >= next_min_dif[0]:
                    min_dif = next_min_dif
        else:
            min_dif = list(map(lambda x: x[0].username, min_dif[1::]))
    else:
        min_dif = [query_for_user_statistic[0].username, "database have one user"]

    # пользователи, которые получали достижения 7 дней подряд

    users_with_achievements_every_day_of_week = list()

    user_with_seven_achievements = list(
        filter(lambda x: x[1] >= 7, query_for_user_with_max_count_achievements)
    )
    for user in user_with_seven_achievements:
        list_user_achievements_with_data = (
            db.session.query(Time_achievement_to_user.date_receipt)
            .filter(Time_achievement_to_user.user_id == user[0].id)
            .order_by(Time_achievement_to_user.date_receipt)
            .all()
        )
        for date_achievement in range(0, len(list_user_achievements_with_data) - 1):
            difference_date = (
                list_user_achievements_with_data[
                    date_achievement + 1
                ].date_receipt.date()
                - list_user_achievements_with_data[date_achievement].date_receipt.date()
            ).days
            if difference_date != 1:
                break
        else:
            users_with_achievements_every_day_of_week.append(user[0].username)

    return json.dumps(
        {
            "users_with_max_count_achievements": users_with_max_count_achievements,
            "user_max_score": max_dif[0],
            "users_max_differense_score": max_dif,
            "users_min_differense_score": min_dif,
            "users_with_achievements_every_day_of_week": users_with_achievements_every_day_of_week,
        },
        ensure_ascii=False,
    )
