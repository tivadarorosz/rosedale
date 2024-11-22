from flask import Blueprint, request, jsonify
from app.services.orders import process_order_webhook

# Create a Flask blueprint for webhooks
orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/latepoint/new", methods=["POST"])
def latepoint_new_order_webhook():
    """
    Handles webhook requests for creating new orders from LatePoint or Square.

    Query Params:
        source (str): 'latepoint' or 'square'.

    Returns:
        JSON response with order ID or an error message.
    """
    try:
        # LatePoint sends data in x-www-form-urlencoded format
        data = request.form.to_dict()

        # Process the webhook data via the service layer
        order = process_order_webhook(data, source)

        # Return success response
        return jsonify({
            "message": "Order processed successfully",
            "order_id": order.id,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500