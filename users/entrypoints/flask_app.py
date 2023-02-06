from datetime import datetime
from flask import Flask, json, request, Response

from users.adapters import orm
from users.service_layer import services, unit_of_work

app = Flask(__name__)
orm.start_mappers()


@app.route("/users", methods=["POST"])
def add_user():
    try:
        services.add_user(
            request.json["ssn"],
            request.json["first_name"],
            request.json["last_name"],
            datetime.fromisoformat(request.json["date_of_birth"]).date(),
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except services.UserIsUnderage:
        return {"error": "User is underage."}, 400
    return "OK", 201


@app.route("/users/<ssn>", methods=["GET"])
def get_user(ssn):
    try:
        user = services.get_user(ssn, unit_of_work.SqlAlchemyUnitOfWork())
    except services.UserDoesNotExist:
        return {"error": "User does not exist."}, 404

    resp = Response(json.dumps(user))
    resp.headers['Content-Type'] = 'application/json'
    resp.status = 201
    return resp


@app.route("/users", methods=["GET"])
def get_users():
    filter_by = {}
    if first_name := request.json.get('first_name'):
        filter_by['first_name'] = first_name
    if last_name := request.json.get('last_name'):
        filter_by['last_name'] = last_name
    if date_of_birth := request.json.get('date_of_birth'):
        filter_by['date_of_birth'] = date_of_birth

    result = services.get_users(
        request.json.get('current_page', 1),
        request.json.get('page_size', 20),
        unit_of_work.SqlAlchemyUnitOfWork(),
        **filter_by
    )

    resp = Response(json.dumps(result))
    resp.headers['Cache-Control'] = 'public, max-age=60'
    resp.headers['Content-Type'] = 'application/json'
    resp.status = 201
    return resp
