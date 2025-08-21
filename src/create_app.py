# create_app.py
from flask import Flask
from config import Config
from app_logging import setup_logging
from cors import init_cors
from error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # logging
    setup_logging()

    # CORS
    init_cors(app)

    # Error handlers
    register_error_handlers(app)

    # TODO: đăng ký DB và routes khi có module thật
    # from infrastructure.databases import init_db
    # init_db(app)
    #
    # from api.routes import register_routes
    # register_routes(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=6868, debug=True)
