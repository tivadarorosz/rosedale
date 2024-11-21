import os
import psycopg2
from datetime import datetime
import logging
import traceback
from flask import Flask, jsonify, request
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

# Load environment variables
load_dotenv()

# Environment configuration
ENVIRONMENT = os.getenv("FLASK_ENV", "production")
DEBUG_MODE = os.getenv("FLASK_DEBUG") == "1"

# Initialize Sentry regardless of environment
initialize_sentry()

# Configure app based on environment
if DEBUG_MODE:
    app.debug = True
    logger.info("Flask Debug is enabled.")

logger.info(f"Running in {ENVIRONMENT} environment")

# Configure SSL for development environment
ssl_context = None
if ENVIRONMENT == "development":
    cert_path = "cert.pem"
    key_path = "key.pem"

    if os.path.exists(cert_path) and os.path.exists(key_path):
        ssl_context = (cert_path, key_path)
        logger.info("SSL certificates found and will be used.")
    else:
        logger.warning("SSL certificates not found. Running without SSL.")


def register_blueprints():
    """Register all blueprints with error handling"""
    try:
        logger.debug("Starting blueprint registration")

        from src.api.endpoints.customers.routes import customers_bp
        app.register_blueprint(customers_bp, url_prefix='/customers')

        from src.api.endpoints.orders.routes import orders_bp
        app.register_blueprint(orders_bp, url_prefix='/orders')

        from src.api.endpoints.transactions.routes import transactions_bp
        app.register_blueprint(transactions_bp, url_prefix='/transactions')

        from src.api.endpoints.appointments.routes import appointments_bp
        app.register_blueprint(appointments_bp, url_prefix='/appointments')

        from src.api.endpoints.square_api.routes import square_api_bp
        app.register_blueprint(square_api_bp, url_prefix='/square')

        from src.api.code_generator.routes import code_generator
        app.register_blueprint(code_generator, url_prefix='/api/v1/code-generator')

        from src.api.webhooks.campfire.routes import campfire_webhook
        app.register_blueprint(campfire_webhook, url_prefix='/webhooks/campfire')

        logger.debug("Completed blueprint registration")
    except Exception as e:
        logger.error(f"Error registering blueprints: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error registering blueprints")
        raise


# Register blueprints
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
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": ENVIRONMENT,
            "debug_mode": DEBUG_MODE
        }

        # Database connection check
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT"),
                connect_timeout=3
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
            "CAMPFIRE_ALERT_URL",
            "CAMPFIRE_WEBHOOK_TOKEN",
            "CAMPFIRE_ROOM_TOKEN"
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


# Print registered routes
print_registered_routes()

# 404 Error Handler
@app.errorhandler(404)
def not_found_error(e):
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    logger.error(
        f"404 Error: {e.description} - URL: {request.url} - "
        f"IP: {client_ip} - Method: {request.method} - "
        f"User-Agent: {request.headers.get('User-Agent')}"
    )

    ignored_paths = ["/phpmyadmin", "/wp-admin"]
    if request.path in ignored_paths:
        return jsonify({"error": "URL not found"}), 404

    return jsonify({"error": "Resource not found"}), 404

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
    if ENVIRONMENT == "development" and ssl_context:
        app.run(host='0.0.0.0', port=port, ssl_context=ssl_context, debug=DEBUG_MODE)
    else:
        app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)