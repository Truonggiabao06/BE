from flask import Flask

def register_routes(app: Flask):
    # Import trong hàm để tránh vòng lặp import
    from .controllers.auth_controller import auth_bp
    from .controllers.auction_item_controller import auction_item_bp  # đúng tên biến trong file hiện có
    from .controllers.user_controller import user_bp
    from .controllers.auction_session_controller import auction_session_bp
    from .controllers.bid_controller import bid_bp
    from .controllers.payment_controller import payment_bp

    # Đăng ký
    app.register_blueprint(auth_bp)
    app.register_blueprint(auction_item_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auction_session_bp)
    app.register_blueprint(bid_bp)
    app.register_blueprint(payment_bp)
