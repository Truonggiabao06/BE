from flask import Blueprint

user_bp = Blueprint("user", __name__, url_prefix="/users")

@user_bp.get("/")
def ping_users():
    return {"ok": True, "resource": "users"}
