import os
import sys
import logging
import traceback
from flask import Flask, jsonify
from dotenv import load_dotenv

# Add parent directory to Python path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_app():
	# Create Flask app
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
		logger.info("Flask Debug is enabled.")
	else:
		load_dotenv()

	def register_blueprints():
		"""Register all blueprints with error handling"""
		try:
			logger.debug("Starting blueprint registration")
			
			from src.api.endpoints.customers.routes import customers_bp
			app.register_blueprint(customers_bp, url_prefix='/customers')
			
			from src.api.endpoints.transactions.routes import transactions_bp
			app.register_blueprint(transactions_bp, url_prefix='/transactions')
			
			from src.api.endpoints.appointments.routes import appointments_bp
			app.register_blueprint(appointments_bp, url_prefix='/appointments')
			
			from src.api.endpoints.square_api.routes import square_api_bp
			app.register_blueprint(square_api_bp, url_prefix='/square')
			
			logger.debug("Completed blueprint registration")
		except Exception as e:
			logger.error(f"Error registering blueprints: {str(e)}")
			logger.error(traceback.format_exc())
			raise

	# Register blueprints
	register_blueprints()

	@app.route("/healthcheck")
	def healthcheck():
		return "OK", 200

	def print_registered_routes():
		print("\nRegistered Routes:")
		for rule in app.url_map.iter_rules():
			print(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")

	# Print routes after registration
	print_registered_routes()

	@app.route("/")
	def home():
		app.logger.debug("Received request for home route")
		return "Welcome to Rosedale Massage API"

	@app.errorhandler(Exception)
	def handle_exception(e):
		logger.error("An unexpected error occurred:\n%s", traceback.format_exc())
		return jsonify({"error": "An unexpected error occurred"}), 500

	return app

# Create the application instance
app = create_app()

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