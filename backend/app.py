"""NutriPlan Flask backend — app entry point.

Run:
    python app.py
    OR
    flask --app app run --port 5000
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

# Import blueprints
from routes.foods import foods_bp
from routes.menu import menu_bp
from routes.analyzer import analyzer_bp
from routes.balancer import balancer_bp
from routes.ai import ai_bp
from routes.chat import chat_bp


def create_app():
    """Application factory."""
    app = Flask(__name__)

    # CORS — allow the React dev server
    CORS(app, origins=[Config.FRONTEND_ORIGIN])

    # Register blueprints
    app.register_blueprint(foods_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(balancer_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(chat_bp)

    # Seed reset endpoint
    @app.route("/api/seed/reset", methods=["POST"])
    def reset_seed():
        """Re-seed the database with demo data."""
        try:
            from seed import seed
            seed()
            return jsonify({"success": True, "data": {"message": "Database re-seeded with demo data."}})
        except Exception as e:
            return jsonify({"success": False, "error": {"message": str(e)}}), 500

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": {"message": "Endpoint not found."}}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": {"message": "Internal server error."}}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"\n🚀 NutriPlan API starting on http://localhost:{Config.FLASK_PORT}")
    print(f"   CORS allowed: {Config.FRONTEND_ORIGIN}")
    print(f"   AI primary: {Config.AI_PRIMARY_PROVIDER}")
    print(f"   AI fallback: {Config.AI_FALLBACK_PROVIDER}\n")
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=True)
