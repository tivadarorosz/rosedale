from flask import Flask, request, redirect
from flask_talisman import Talisman
from customers import customers
from transactions import transactions
from appointments import appointments
from square_api import square_api
import os
from dotenv import load_dotenv

app = Flask(__name__)

if os.getenv("FLASK_DEBUG") == "1":
	app.debug = True

# Enforce HTTPS
#Talisman(app)
#Talisman(app, force_https=False)  # Disable HTTPS enforcement

# Load .env file only if not in production
#if os.getenv("FLASK_DEBUG") != "production":
#	load_dotenv()

@app.route("/")
def home():
	return "Welcome to Rosedale Massage API"
	
@app.before_request
	def enforce_https():
		if not request.is_secure:
			url = request.url.replace("http://", "https://", 1)
			return redirect(url, code=301)

# Register blueprints
app.register_blueprint(customers, url_prefix='/customers')
app.register_blueprint(transactions, url_prefix='/transactions')
app.register_blueprint(appointments, url_prefix='/appointments')
app.register_blueprint(square_api, url_prefix='/square')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)