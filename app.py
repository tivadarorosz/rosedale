from flask import Flask
from customers import customers
from transactions import transactions
from appointments import appointments
from square_api import square_api

app = Flask(__name__)

@app.route("/")
def home():
	return "Welcome to Rosedale Massage API"

# Register blueprints
app.register_blueprint(customers, url_prefix='/customers')
app.register_blueprint(transactions, url_prefix='/transactions')
app.register_blueprint(appointments, url_prefix='/appointments')
app.register_blueprint(square_api, url_prefix='/square')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)