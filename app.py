from flask import Flask
from dotenv import load_dotenv
from customers.routes import customers_bp
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
	
if os.getenv("FLASK_ENV") == "development":
	load_dotenv(".env.dev")
else:
	load_dotenv()

# Register blueprints
from customers.routes import customers_bp
app.register_blueprint(customers_bp, url_prefix='/customers')

from transactions.routes import transactions_bp
app.register_blueprint(transactions_bp, url_prefix='/transactions')

from appointments.routes import appointments_bp
app.register_blueprint(appointments_bp, url_prefix='/appointments')

from square_api.routes import square_api_bp
app.register_blueprint(square_api_bp, url_prefix='/square')

@app.route("/")
def home():
	return "Welcome to Rosedale Massage API"
	
@app.errorhandler(Exception)
def handle_exception(e):
	# Log the exception
	logger.error("An unexpected error occurred:\n%s", traceback.format_exc())
		
	# Return a generic error message to the user
	return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
	if os.getenv("FLASK_DEBUG") == "1":
		app.run(host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
	else:
		app.run(host='0.0.0.0', port=8080)