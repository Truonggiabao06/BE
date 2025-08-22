from flask import Blueprint

bid_bp = Blueprint("bid", __name__, url_prefix="/bids")

@bid_bp.get("/")
def ping_bids():
    return {"ok": True, "resource": "bids"}
