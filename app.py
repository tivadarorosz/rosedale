import os
import psycopg2
from datetime import datetime
import sys
import logging
import traceback
from flask import Flask, jsonify
from dotenv import load_dotenv
from src.utils.error_monitoring import initialize_sentry, handle_error

# Create Flask app first
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("FLASK_DEBUG") == "1" else logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
if os.getenv("FLASK_DEBUG") == "1":
    app.debug = True
    logger.info("Flask Debug is enabled.")
else:
    load_dotenv()
    initialize_sentry()  # Initialise Sentry in production


def register_blueprints():
    """Register all blueprints with error handling"""
    try:
        logger.debug("Starting blueprint registration")

        from src.api.endpoints.customers.routes import customers_bp
        app.register_blueprint(customers_bp, url_prefix='/customers')

        from src.api.endpoints.transactions.routes import transactions_bp
        app.register_blueprint(transactions_bp, url_prefix='/transactions')

        from src.api.endpoints.appointments.routes import appointments_bp
        app.register_blueprint(appointments_bp, url_prefix='/appointments')

        from src.api.endpoints.square_api.routes import square_api_bp
        app.register_blueprint(square_api_bp, url_prefix='/square')

        from src.api.code_generator.routes import code_generator
        app.register_blueprint(code_generator, url_prefix='/api/v1/code-generator')

        logger.debug("Completed blueprint registration")
    except Exception as e:
        logger.error(f"Error registering blueprints: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error registering blueprints")
        raise


# Register blueprints after app creation
register_blueprints()


@app.route("/healthcheck")
def healthcheck():
    """
    Enhanced healthcheck endpoint that verifies:
    1. Application is running
    2. Database connection is working
    3. Basic environment configuration
    """
    try:
        # Basic check
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("FLASK_ENV", "production")
        }

        # Optional: Quick DB connection check
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT"),
                connect_timeout=3  # Short timeout for healthcheck
            )
            conn.close()
            status["database"] = "connected"
        except Exception as e:
            status["database"] = "error"
            status["status"] = "degraded"

        # Check essential environment variables
        required_vars = [
            "SENTRY_DSN",
            "CAMPFIRE_TECH_URL",
            "CAMPFIRE_ALERT_URL"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            status["status"] = "degraded"
            status["missing_config"] = missing_vars

        return jsonify(status), 200 if status["status"] == "healthy" else 503

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 503


def print_registered_routes():
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")


# Call it right after all blueprints are registered
print_registered_routes()


@app.route("/")
def home():
    app.logger.debug("Received request for home route")
    return "Welcome to Rosedale Massage API"


@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    error_details = traceback.format_exc()
    logger.error("An unexpected error occurred:\n%s", error_details)
    handle_error(e, "Unhandled exception in application")
    return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    if os.getenv("FLASK_DEBUG") == "1":
        print("Flask Debug is enabled.")
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(host='0.0.0.0', port=port)
