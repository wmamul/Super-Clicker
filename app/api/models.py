from flask_restx import fields
from app.api import api

message = api.model("Message", {
    "message": fields.String(max_length=255)
    })

token = api.model("Token", {
    "token": fields.String(max_length=40),
    "exp": fields.DateTime()
    })

user_register = api.model("Registration", {
    "username": fields.String(min_length=6, max_length=20),
    "password": fields.String(min_length=8, max_length=20),
    "email": fields.String(max_length=120)
    })

user_update = api.inherit("Update user", user_register, {
    "image": fields.String(max_length=80, desctiption="Profile picture path on the server")
    })

user_info = api.inherit("Full user info", user_update, {
    "last_login": fields.DateTime()
    })
