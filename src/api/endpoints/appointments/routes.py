from flask import Blueprint, request, jsonify
import os
from src.api.utils.db_utils_customers import create_db_customer, check_email_exists, update_latepoint_customer, determine_customer_type
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from src.utils.api_utils import get_gender
from src.utils.campfire_utils import send_message
from convertkit import ConvertKit
import requests
import logging
import traceback

logger = logging.getLogger(__name__)

appointments_bp = Blueprint("appointments", __name__)
# appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")

@appointments_bp.route('/new', methods=['POST'])
def new_appointment():
	data = request.get_json()
	# Logic to handle marking an appointment as finished
	return jsonify({"status": "Appointment marked as finished"}), 200