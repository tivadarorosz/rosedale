from flask import Flask
from customers import customers
from transactions import transactions
from appointments import appointments
from square_api import square_api
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

if os.getenv("FLASK_DEBUG") == "1":
	app.debug = True

# Load .env file only if not in production
if os.getenv("FLASK_ENV") != "production":
	load_dotenv()

@app.route("/")
def home():
	return "Welcome to Rosedale Massage API"

# Register blueprints
app.register_blueprint(customers, url_prefix='/customers')
app.register_blueprint(transactions, url_prefix='/transactions')
app.register_blueprint(appointments, url_prefix='/appointments') 
app.register_blueprint(square_api, url_prefix='/square')
	
if __name__ == '__main__':
	if os.getenv("FLASK_DEBUG") == "1":
		app.run(host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'))
	else:
		app.run(host='0.0.0.0', port=8080)