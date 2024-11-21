from flask import Blueprint, request, jsonify
from services.orders import process_order_webhook

# Create a Flask blueprint for webhooks
orders_webhook_bp = Blueprint("orders_webhook", __name__)

@orders_webhook_bp.route("/new", methods=["POST"])
def handle_new_order_webhook():
    """
    Handles webhook requests for creating new orders from LatePoint or Square.

    Query Params:
        source (str): 'latepoint' or 'square'.

    Returns:
        JSON response with order ID or an error message.
    """
    try:
        # Extract source from query parameters
        source = request.args.get("source")
        if source not in ["latepoint", "square"]:
            return jsonify({"error": "Invalid source"}), 400

        # Handle data based on source
        if source == "latepoint":
            # LatePoint sends data in x-www-form-urlencoded format
            data = request.form.to_dict()
        elif source == "square":
            # Square sends data as JSON
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400

        # Process the webhook data via the service layer
        order = process_order_webhook(data, source)

        # Return success response
        return jsonify({
            "message": "Order processed successfully",
            "order_id": order.id,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500