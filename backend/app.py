from flask import Flask, jsonify
from flask_cors import CORS

from routes.ocr import ocr_bp
from routes.predict import predict_bp
from routes.simplify import simplify_bp
from routes.translate import translate_bp
from routes.voice import voice_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(predict_bp)
    app.register_blueprint(simplify_bp)
    app.register_blueprint(translate_bp)
    app.register_blueprint(voice_bp)
    app.register_blueprint(ocr_bp)

    @app.get("/")
    def home():
        return jsonify(
            {
                "service": "Multilingual Rural Healthcare Assistant",
                "status": "running",
                "frontend": "Run the React app from the frontend folder with npm run dev.",
                "endpoints": [
                    "GET /health",
                    "POST /predict",
                    "POST /simplify",
                    "POST /translate",
                    "POST /voice",
                    "POST /ocr",
                    "POST /report-image",
                ],
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "multilingual-rural-healthcare-assistant"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
