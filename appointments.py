from flask import Blueprint, request, jsonify

appointments = Blueprint('appointments', __name__)

@appointments.route('/finished', methods=['POST'])
def appointment_finished():
	data = request.get_json()
	# Logic to handle marking an appointment as finished
	return jsonify({"status": "Appointment marked as finished"}), 200