from flask import Blueprint, request, jsonify
	
customers = Blueprint('customers', __name__)
	
@customers.route('/new', methods=['POST'])
def new_customer():
	data = request.get_json()
	return jsonify({"status": "New customer account created successfully"}), 200