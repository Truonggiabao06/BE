from flask import Blueprint

auction_session_bp = Blueprint("auction_session", __name__, url_prefix="/auctions")

@auction_session_bp.get("/")
def ping_auction_sessions():
    return {"ok": True, "resource": "auctions"}
