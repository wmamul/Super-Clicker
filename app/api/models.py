from flask_restx import fields
from app.api import api

message = api.model("Message", {
    "message": fields.String(max_length=255)
    })

token = api.model("Token", {
    "token": fields.String(min_length=36, max_length=36)
    })

user = api.model("User", {
    "username": fields.String(min_length=6, max_length=20),
    "email": fields.String(max_length=120),
    "image": fields.String(max_length=80, desctiption="Profile picture path on the server"),
    "last_login": fields.DateTime(),
    })

register = api.model("User registration requirements", {
    "username": fields.String(min_length=6, max_length=20),
    "password": fields.String(min_length=8, max_length=20),
    "email": fields.String(max_length=120)
    })
