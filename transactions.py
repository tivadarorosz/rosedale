from flask import Blueprint, request, jsonify

transactions = Blueprint('transactions', __name__)

@transactions.route('/new', methods=['POST'])
def new_transaction():
	data = request.get_json()
	# Logic to handle new transactions
	return jsonify({"status": "New transaction processed successfully"}), 200