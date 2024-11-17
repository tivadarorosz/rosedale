from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import logging
import traceback

# Create Flask app first
app = Flask(__name__)

# Configure logging
logging.basicConfig(
	level=logging.DEBUG if os.getenv("FLASK_DEBUG") == "1" else logging.INFO,
	format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
if os.getenv("FLASK_DEBUG") == "1":
	app.debug = True
	print("Flask Debug is enabled.")
	# load_dotenv(".env.dev")
else:
	load_dotenv()

# Register blueprints
from src.api.endpoints.customers.routes import customers_bp
app.register_blueprint(customers_bp, url_prefix='/customers')

from src.api.endpoints.transactions.routes import transactions_bp
app.register_blueprint(transactions_bp, url_prefix='/transactions')

from src.api.endpoints.appointments.routes import appointments_bp
app.register_blueprint(appointments_bp, url_prefix='/appointments')

from src.api.endpoints.square_api.routes import square_api_bp
app.register_blueprint(square_api_bp, url_prefix='/square')

# Health check endpoint
@app.route("/healthcheck")
def healthcheck():
	return "OK", 200

# Replace before_first_request with a function that runs at startup
def print_registered_routes():
	print("\nRegistered Routes:")
	for rule in app.url_map.iter_rules():
		print(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")

# Call it right after all blueprints are registered
print_registered_routes()
print(app.url_map)

@app.route("/")
def home():
	app.logger.debug("Received request for home route")
	return "Welcome to Rosedale Massage API"

@app.errorhandler(Exception)
def handle_exception(e):
	# Log the exception
	logger.error("An unexpected error occurred:\n%s", traceback.format_exc())
	
	# Return a generic error message to the user
	return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
	port = int(os.getenv("PORT", 8080))
	if os.getenv("FLASK_DEBUG") == "1":
		print("Flask Debug is enabled.")
		#cert_path = os.path.join('ssl', 'cert.pem')
		#key_path = os.path.join('ssl', 'key.pem')
		
		#if os.path.exists(cert_path) and os.path.exists(key_path):
		#    app.run(host='0.0.0.0', port=port, ssl_context=(cert_path, key_path))
		#else:
		#    logger.warning("SSL certificates not found, running without SSL")
		app.run(host='0.0.0.0', port=port)
	else:
		app.run(host='0.0.0.0', port=port)