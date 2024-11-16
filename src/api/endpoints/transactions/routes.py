from flask import Blueprint, request, jsonify

transactions_bp = Blueprint("transactions", __name__)
# transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")

@transactions_bp.route('/new', methods=['POST'])
def new_transaction():
	data = request.get_json()
	# Logic to handle new transactions
	return jsonify({"status": "New transaction processed successfully"}), 200