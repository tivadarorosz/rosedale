from flask import Blueprint, request, jsonify
import requests
import os

# square_api_bp = Blueprint("square_api", __name__)
square_api_bp = Blueprint("square_api", __name__, url_prefix="/square_api")

SQUARE_API_BASE = "https://connect.squareup.com/v2"

@square_api_bp.route('/gift-card-purchase', methods=['GET'])
def gift_card_purchase():
	# Logic to pull new gift card purchases
	response = requests.get(f"{SQUARE_API_BASE}/giftcards/orders", headers={
		"Authorization": f"Bearer {os.getenv('SQUARE_API_KEY')}"
	})
	return jsonify(response.json()), response.status_code

@square_api_bp.route('/refund', methods=['POST'])
def issue_refund():
	data = request.get_json()
	# Logic to issue a refund via Square API
	response = requests.post(f"{SQUARE_API_BASE}/refunds", json=data, headers={
		"Authorization": f"Bearer {os.getenv('SQUARE_API_KEY')}"
	})
	return jsonify(response.json()), response.status_code

@square_api_bp.route('/new-transaction', methods=['GET'])
def new_transaction():
	# Logic to pull new transactions
	response = requests.get(f"{SQUARE_API_BASE}/payments", headers={
		"Authorization": f"Bearer {os.getenv('SQUARE_API_KEY')}"
	})
	return jsonify(response.json()), response.status_code