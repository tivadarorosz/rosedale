from flask import Blueprint, request, jsonify
import os
from customers.db import create_db_customer, check_email_exists, update_latepoint_customer, determine_customer_type
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from api_utils import get_gender
from campfire_utils import send_message
from convertkit import ConvertKit
import requests
import logging
import traceback

logger = logging.getLogger(__name__)

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")

@appointments_bp.route('/new', methods=['POST'])
def new_appointment():
	data = request.get_json()
	# Logic to handle marking an appointment as finished
	return jsonify({"status": "Appointment marked as finished"}), 200