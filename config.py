import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    load_dotenv()


class Config:
    """Base configuration for the application."""

    @classmethod
    def validate_config(cls) -> None:
        """
        Validate that all required environment variables are set.
        Raises ValueError if any required variables are missing.
        """
        required_vars = [
            # Core application settings
            "SECRET_KEY",
            "DB_HOST",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD",

            # API Keys
            "SQUARE_ACCESS_TOKEN",
            "CONVERTKIT_API_KEY",
            "SENDLAYER_API_KEY",
            "GENDER_API_KEY",

            # Integration tokens
            "CAMPFIRE_WEBHOOK_TOKEN",
            "CAMPFIRE_ROOM_TOKEN",

            # Monitoring
            "SENTRY_DSN"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    # --- Flask Settings ---
    FLASK_ENV: str = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true")
    SECRET_KEY: str = os.environ["SECRET_KEY"]

    # --- Database Configuration ---
    DB_HOST: str = os.environ["DB_HOST"]
    DB_NAME: str = os.environ["DB_NAME"]
    DB_USER: str = os.environ["DB_USER"]
    DB_PASSWORD: str = os.environ["DB_PASSWORD"]
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "connect_args": {
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    }

    # --- Third-Party API Integrations ---
    # Gender API
    GENDER_API_KEY: str = os.environ["GENDER_API_KEY"]

    # Square API
    SQUARE_ACCESS_TOKEN: str = os.environ["SQUARE_ACCESS_TOKEN"]
    SQUARE_LOCATION_ID: str = os.environ["SQUARE_LOCATION_ID"]
    SQUARE_NEW_CUSTOMER_SIGNATURE_KEY: str = os.environ["SQUARE_NEW_CUSTOMER_SIGNATURE_KEY"]
    SQUARE_NEW_CUSTOMER_NOTIFICATION_URL: str = os.environ["SQUARE_NEW_CUSTOMER_NOTIFICATION_URL"]

    # ConvertKit API
    CONVERTKIT_API_KEY: str = os.environ["CONVERTKIT_API_KEY"]
    CONVERTKIT_CHARLOTTE_FORM_ID: str = os.environ["CONVERTKIT_CHARLOTTE_FORM_ID"]
    CONVERTKIT_MILLS_FORM_ID: str = os.environ["CONVERTKIT_MILLS_FORM_ID"]

    # Acuity Scheduling API
    ACUITY_USER_ID: str = os.environ["ACUITY_USER_ID"]
    ACUITY_API_KEY: str = os.environ["ACUITY_API_KEY"]

    # --- Logging and Monitoring ---
    SENTRY_DSN: str = os.environ["SENTRY_DSN"]

    # --- Email Settings ---
    SENDLAYER_API_KEY: str = os.environ["SENDLAYER_API_KEY"]
    DEFAULT_FROM_EMAIL: str = os.environ["DEFAULT_FROM_EMAIL"]
    DEFAULT_REPLY_TO: str = os.environ["DEFAULT_REPLY_TO"]

    # --- URLs ---
    CAMPFIRE_STUDIO_URL: str = os.environ["CAMPFIRE_STUDIO_URL"]
    CAMPFIRE_FINANCE_URL: str = os.environ["CAMPFIRE_FINANCE_URL"]
    CAMPFIRE_TECH_URL: str = os.environ["CAMPFIRE_TECH_URL"]
    CAMPFIRE_ALERT_URL: str = os.environ["CAMPFIRE_ALERT_URL"]
    CAMPFIRE_BOT_URL: str = os.environ["CAMPFIRE_BOT_URL"]
    BOOKING_URL: str = os.environ["BOOKING_URL"]
    TRACKING_BASE_URL: str = os.environ["TRACKING_BASE_URL"]
    NEWSLETTER_SIGNUP_URL: str = os.environ["NEWSLETTER_SIGNUP_URL"]

    # --- Campfire Tokens ---
    CAMPFIRE_WEBHOOK_TOKEN: str = os.environ["CAMPFIRE_WEBHOOK_TOKEN"]
    CAMPFIRE_ROOM_TOKEN: str = os.environ["CAMPFIRE_ROOM_TOKEN"]

    # --- Application-Specific ---
    ROSEDALE_API_KEY: str = os.environ["ROSEDALE_API_KEY"]
    LATEPOINT_IP_ADDRESS: str = os.environ["LATEPOINT_IP_ADDRESS"]
    CAMPFIRE_IP_ADDRESS: str = os.environ["CAMPFIRE_IP_ADDRESS"]


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    FLASK_DEBUG = True

    # Add development-specific settings here
    @classmethod
    def validate_config(cls) -> None:
        super().validate_config()
        # Add development-specific validation if needed


class ProductionConfig(Config):
    """Production-specific configuration."""
    FLASK_DEBUG = False

    @classmethod
    def validate_config(cls) -> None:
        super().validate_config()
        # Add additional production-specific validation
        prod_only_vars = [
            "SENTRY_DSN",
            "SQUARE_ACCESS_TOKEN",
            "CAMPFIRE_WEBHOOK_TOKEN"
        ]
        missing_vars = [var for var in prod_only_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required production variables: {', '.join(missing_vars)}"
            )


# Map environments to configuration classes
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}