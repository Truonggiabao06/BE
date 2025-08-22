from flask import Blueprint

payment_bp = Blueprint("payment", __name__, url_prefix="/payments")

@payment_bp.get("/")
def ping_payments():
    return {"ok": True, "resource": "payments"}
