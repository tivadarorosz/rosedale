from datetime import datetime, UTC
import logging
from logging.handlers import RotatingFileHandler
import traceback
import uuid
from flask import Flask, jsonify, request, Config as FlaskConfig, Response
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import QueuePool
from src.core.monitoring import initialize_sentry, handle_error
from config import config
from src.extensions import db, migrate
import os

from src.models import load_models

def register_models():
    """Register all models with SQLAlchemy"""
    return load_models()

def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance
    """
    print("Starting app creation...")
    app = Flask(__name__)

    # Load environment-specific configuration
    print("Loading config...")
    env = os.getenv("FLASK_ENV", "production")
    app.config.from_object(config[env])

    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize SQLAlchemy with the app
    print("Initializing SQLAlchemy...")
    db.init_app(app)

    # Register models
    print("Registering models...")
    models = register_models()

    # Initialize Flask-Migrate
    print("Initializing Migrate...")
    migrate.init_app(app, db)

    # Validate critical configuration
    config[env].validate_config()
    validate_configuration(app.config)

    # Configure logging with rotation
    setup_logging(app)

    # Initialize error tracking
    initialize_sentry()

    # Register all blueprints
    register_blueprints(app)

    @app.route("/healthcheck")
    def healthcheck() -> tuple[Response, int]:
        """
        Enhanced healthcheck endpoint to verify application health.

        Returns:
            tuple: JSON response and status code
        """
        status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "environment": app.config["FLASK_ENV"],
            "debug_mode": app.debug
        }

        try:
            # Database connection check using engine from config
            with app.config['db_engine'].connect() as conn:
                conn.execute("SELECT 1")
            status["database"] = "connected"
        except Exception as e:
            logger.error(f"Database healthcheck failed: {str(e)}")
            status["database"] = "error"
            status["status"] = "degraded"

        status_code = 200 if status["status"] == "healthy" else 503
        return jsonify(status), status_code

    @app.route("/")
    def home() -> tuple[Response, int]:
        """
        Home route.

        Returns:
            tuple: JSON response and status code
        """
        return jsonify({
            "name": "Rosedale Massage API",
            "version": "1.0",
            "status": "running"
        }), 200

    @app.errorhandler(404)
    def not_found_error(error: Exception) -> tuple[Response, int]:
        """
        Handle 404 errors.

        Args:
            error: The exception that triggered this handler
        Returns:
            tuple: JSON response and status code
        """
        error_id = generate_error_id()

        logger.info(
            f"404 Error (ID: {error_id}) - "
            f"Method: {request.method} - "
            f"Path: {request.path} - "
            f"Error: {str(error)}"
        )

        return create_error_response(
            error_id,
            "Resource not found",
            404,
            app=app
        )

    @app.errorhandler(Exception)
    def handle_exception(error: Exception) -> tuple[Response, int]:
        """
        Global exception handler.

        Args:
            error: The exception that triggered this handler
        Returns:
            tuple: JSON response and status code
        """
        error_id = generate_error_id()

        logger.error(
            f"Unhandled exception (ID: {error_id}): {str(error)}\n"
            f"{traceback.format_exc()}"
        )

        handle_error(error, f"Unhandled exception (ID: {error_id})")

        return create_error_response(
            error_id,
            "An unexpected error occurred",
            500,
            include_details=True,
            app=app
        )

    return app

def setup_logging(app: Flask) -> logging.Logger:
    """
    Configure application logging.

    Args:
        app: Flask application instance
    Returns:
        logging.Logger: Configured logger instance
    """
    log_level = logging.DEBUG if app.config["FLASK_DEBUG"] else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s - %(name)s:%(lineno)d",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                'app.log',
                maxBytes=1024 * 1024,  # 1MB
                backupCount=10
            )
        ]
    )
    return logging.getLogger(__name__)

def setup_database(config: FlaskConfig) -> Engine:
    """
    Initialize database connection pool optimized for Gunicorn workers.

    Args:
        config: Flask application configuration
    Returns:
        Engine: SQLAlchemy engine instance with optimized pool settings
    """
    return create_engine(
        config["SQLALCHEMY_DATABASE_URI"],
        poolclass=QueuePool,
        pool_size=10,         # (2 workers * 4 threads) + 2 extra
        max_overflow=20,      # Allow temporary extra connections
        pool_timeout=30,      # Match Gunicorn timeout
        pool_recycle=1800,    # Recycle connections every 30 minutes
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    )

def validate_configuration(config: FlaskConfig) -> None:
    """
    Validate application configuration.

    Args:
        config: Flask application configuration
    Raises:
        ValueError: If URL format is invalid or not HTTPS
    """
    url_configs = [
        "CAMPFIRE_TECH_URL",
        "CAMPFIRE_ALERT_URL",
        "BOOKING_URL",
        "TRACKING_BASE_URL"
    ]

    for config_key in url_configs:
        url = config.get(config_key)
        if url and not url.startswith("https://"):
            raise ValueError(
                f"Invalid URL format for {config_key}. "
                f"Only HTTPS URLs are allowed"
            )

def generate_error_id() -> str:
    """
    Generate a unique error ID for tracking.

    Returns:
        str: Unique error identifier
    """
    return str(uuid.uuid4())

def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints with error handling.

    Args:
        app: Flask application instance
    Raises:
        Exception: If blueprint registration fails
    """
    blueprint_logger = logging.getLogger(__name__)

    try:
        blueprint_logger.info("Registering blueprints...")

        # API v1 blueprints
        from src.services.giftcards import code_generator
        app.register_blueprint(code_generator, url_prefix="/api/v1/code-generator")

        # Webhook blueprints
        from src.api.webhooks.customers import customers_bp
        # from src.api.webhooks.orders import orders_bp
        from src.api.webhooks.campfire import campfire_webhook

        app.register_blueprint(customers_bp, url_prefix="/customers")
        # app.register_blueprint(orders_bp, url_prefix="/api/v1/webhooks/orders")
        app.register_blueprint(campfire_webhook, url_prefix="/api/v1/webhooks/campfire")

        blueprint_logger.info("Successfully registered all blueprints")

    except Exception as e:
        blueprint_logger.error(f"Failed to register blueprints: {str(e)}")
        blueprint_logger.error(traceback.format_exc())
        handle_error(e, "Blueprint registration failed")
        raise

def create_error_response(
        error_id: str,
        message: str,
        status_code: int,
        include_details: bool = False,
        app: Flask = None
) -> tuple[Response, int]:
    """
    Create a standardized error response.

    Args:
        error_id: Unique identifier for the error
        message: Error message to display
        status_code: HTTP status code
        include_details: Whether to include debug information
        app: Flask application instance
    Returns:
        tuple: JSON response and status code
    """
    response = {
        "error": message,
        "error_id": error_id,
        "timestamp": datetime.now(UTC).isoformat()
    }

    if include_details and app and app.config.get("FLASK_DEBUG"):
        response["debug_info"] = traceback.format_exc()

    return jsonify(response), status_code

# Initialize logger
logger = logging.getLogger(__name__)