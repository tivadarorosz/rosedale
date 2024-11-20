from flask import Blueprint, jsonify, request
from src.utils.error_monitoring import handle_error
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import random
import string
import os
import logging
import traceback
import sentry_sdk

logger = logging.getLogger(__name__)
code_generator = Blueprint('code_generator', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

API_KEY = os.getenv("ROSEDALE_API_KEY")


def generate_code(prefix, suffix_length=8):
    try:
        return f"{prefix}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=suffix_length))}"
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        handle_error(e, "Error generating code")
        raise


def validate_duration(duration):
    return duration in ['60', '90', '110']


def validate_discount(discount, discount_type="fixed"):
    """Validate discount percentage based on type
    Args:
        discount: The discount value to validate
        discount_type: One of "fixed" (20/50), "variable" (1-100), "school" (1-100)
    """
    try:
        discount_value = int(discount)
        if discount_type in ["variable", "school"]:
            return 1 <= discount_value <= 100
        return discount in ['20', '50']  # fixed type
    except (ValueError, TypeError):
        return False


@code_generator.before_request
def authorize_request():
    try:
        api_key = request.headers.get("X-API-KEY")
        if api_key != API_KEY:
            logger.warning("Unauthorized API access attempt")
            sentry_sdk.capture_message("Unauthorized API access attempt", level="warning")
            return jsonify({"error": "Unauthorized"}), 401
    except Exception as e:
        logger.error(f"Authorization error: {str(e)}")
        handle_error(e, "Authorization error")
        return jsonify({"error": "Authorization error"}), 500


@code_generator.route('/generate/unlimited', methods=['GET'])
@limiter.limit("10 per minute")
def generate_unlimited_code():
    try:
        logger.info("Generating unlimited package code")
        duration = request.args.get('duration')
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        expiration = request.args.get('expiration')  # Optional parameter

        if not duration or not validate_duration(duration):
            logger.warning(f"Invalid duration: {duration}")
            return jsonify({"error": "Invalid duration. Must be 60, 90, or 110"}), 400
        if not first_name:
            logger.warning("Missing first_name parameter")
            return jsonify({"error": "Missing first_name parameter"}), 400
        if not last_name:
            logger.warning("Missing last_name parameter")
            return jsonify({"error": "Missing last_name parameter"}), 400

        prefix = f"UL-{duration}-{first_name.upper()}"
        code = generate_code(prefix, suffix_length=6)

        # Create name format
        if expiration:
            try:
                # Parse and format date (assuming incoming format is YYYY-MM-DD)
                expiration_date = datetime.strptime(expiration, "%Y-%m-%d")
                formatted_date = expiration_date.strftime("%d %b %Y")
                name = f"Unlimited-{duration}-{first_name} {last_name}-{formatted_date}"
            except ValueError:
                logger.warning("Invalid expiration date format")
                return jsonify({"error": "Invalid expiration date format. Use YYYY-MM-DD"}), 400
        else:
            name = f"Unlimited-{duration}-{first_name} {last_name}"

        logger.info(f"Generated unlimited code for {first_name} {last_name}")
        return jsonify({
            "code": code,
            "name": name
        })
    except Exception as e:
        logger.error(f"Error generating unlimited code: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error generating unlimited code")
        return jsonify({"error": "Internal Server Error"}), 500


@code_generator.route('/generate/school-code', methods=['GET'])
@limiter.limit("10 per minute")
def generate_school_code():
    try:
        logger.info("Generating school code")
        discount = request.args.get('discount')

        if not discount or not validate_discount(discount, "school"):
            logger.warning("Invalid discount parameter")
            return jsonify({"error": "Invalid discount. Must be between 1 and 100"}), 400

        prefix = f"SCHL-{discount}"
        code = generate_code(prefix, suffix_length=6)
        logger.info(f"Generated school code with discount {discount}")
        return jsonify({"code": code})
    except Exception as e:
        logger.error(f"Error generating school code: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error generating school code")
        return jsonify({"error": "Internal Server Error"}), 500


@code_generator.route('/generate/referral-code', methods=['GET'])
@limiter.limit("10 per minute")
def generate_referral_code():
    try:
        logger.info("Generating referral code")
        first_name = request.args.get('first_name')
        discount = request.args.get('discount')

        if not first_name:
            logger.warning("Missing first_name parameter")
            return jsonify({"error": "Missing first_name parameter"}), 400
        if not discount or not validate_discount(discount, "variable"):
            logger.warning("Invalid discount parameter")
            return jsonify({"error": "Invalid discount. Must be between 1 and 100"}), 400

        prefix = f"REF-{discount}-{first_name.upper()}"
        code = generate_code(prefix, suffix_length=6)
        logger.info(f"Generated referral code for {first_name}")
        return jsonify({"code": code})
    except Exception as e:
        logger.error(f"Error generating referral code: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error generating referral code")
        return jsonify({"error": "Internal Server Error"}), 500


@code_generator.route('/generate/guest-pass', methods=['GET'])
@limiter.limit("10 per minute")
def generate_guest_pass_code():
    try:
        logger.info("Generating guest pass code")
        first_name = request.args.get('first_name')
        duration = request.args.get('duration')

        if not first_name:
            logger.warning("Missing first_name parameter")
            return jsonify({"error": "Missing first_name parameter"}), 400
        if not duration or not validate_duration(duration):
            logger.warning(f"Invalid duration: {duration}")
            return jsonify({"error": "Invalid duration. Must be 60, 90, or 110"}), 400

        prefix = f"FREE-{duration}-{first_name.upper()}"
        code = generate_code(prefix, suffix_length=6)
        logger.info(f"Generated guest pass code for {first_name}")
        return jsonify({"code": code})
    except Exception as e:
        logger.error(f"Error generating guest pass code: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error generating guest pass code")
        return jsonify({"error": "Internal Server Error"}), 500


@code_generator.route('/generate/gift-card', methods=['GET'])
@limiter.limit("10 per minute")
def generate_gift_card_code():
    try:
        logger.info("Generating gift card code")
        amount = request.args.get('amount')
        card_type = request.args.get('type')
        first_name = request.args.get('first_name')

        if not amount:
            logger.warning("Missing amount parameter")
            return jsonify({"error": "Missing amount parameter"}), 400
        if not card_type or card_type.upper() not in ['DIGITAL', 'PREMIUM']:
            logger.warning("Invalid card type")
            return jsonify({"error": "Invalid card type. Must be DIGITAL or PREMIUM"}), 400

        type_code = 'DGTL' if card_type.upper() == 'DIGITAL' else 'PREM'
        prefix = f"GIFT-{type_code}-{amount}"
        if first_name:
            prefix = f"{prefix}-{first_name.upper()}"

        code = generate_code(prefix)
        logger.info(f"Generated gift card code: {code}")
        return jsonify({"code": code})
    except Exception as e:
        logger.error(f"Error generating gift card code: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error generating gift card code")
        return jsonify({"error": "Internal Server Error"}), 500


@code_generator.route('/generate/gift-card/bulk', methods=['GET'])
@limiter.limit("10 per minute")
def generate_bulk_gift_card_codes():
    try:
        logger.info("Generating bulk gift card codes")
        amount = request.args.get('amount')
        quantity = request.args.get('quantity', type=int)

        if not amount:
            logger.warning("Missing amount parameter")
            return jsonify({"error": "Missing amount parameter"}), 400
        if not quantity or quantity < 1 or quantity > 50:
            logger.warning("Invalid quantity")
            return jsonify({"error": "Quantity must be between 1 and 50"}), 400

        codes = []
        prefix = f"GIFT-PREM-{amount}"
        for _ in range(quantity):
            codes.append(generate_code(prefix))

        logger.info(f"Generated {quantity} bulk gift card codes")
        return jsonify({"codes": codes})
    except Exception as e:
        logger.error(f"Error generating bulk gift card codes: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error generating bulk gift card codes")
        return jsonify({"error": "Internal Server Error"}), 500


@code_generator.route('/generate/personal-code', methods=['GET'])
@limiter.limit("10 per minute")
def generate_personal_code():
    try:
        logger.info("Generating personal code")
        duration = request.args.get('duration')
        discount = request.args.get('discount')
        first_name = request.args.get('first_name')

        if not first_name:
            logger.warning("Missing first_name parameter")
            return jsonify({"error": "Missing first_name parameter"}), 400

        if duration and validate_duration(duration):
            prefix = f"PERS-{duration}-{first_name.upper()}"
        elif discount and validate_discount(discount, "variable"):
            prefix = f"PERS-{discount}-{first_name.upper()}"
        else:
            logger.warning("Invalid or missing duration/discount parameter")
            return jsonify({"error": "Must provide either valid duration (60, 90, 110) or discount between 1 and 100"}), 400

        code = generate_code(prefix, suffix_length=6)
        logger.info(f"Generated personal code for {first_name}")
        return jsonify({"code": code})
    except Exception as e:
        logger.error(f"Error generating personal code: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Error generating personal code")
        return jsonify({"error": "Internal Server Error"}), 500