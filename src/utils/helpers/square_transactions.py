import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN")
LOCATION_ID = os.getenv("SQUARE_LOCATION_ID")

# Ensure the environment variables are set
if not ACCESS_TOKEN or not LOCATION_ID:
    raise ValueError("SQUARE_ACCESS_TOKEN and SQUARE_LOCATION_ID must be set in the .env file.")

# Square API URL
BASE_URL = "https://connect.squareup.com/v2"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


def list_transactions():
    """Fetches all transactions for the specified location."""
    url = f"{BASE_URL}/payments"
    params = {
        "location_id": LOCATION_ID,
        "limit": 100  # Maximum number of transactions per request
    }

    transactions = []
    cursor = None  # For pagination

    while True:
        if cursor:
            params["cursor"] = cursor
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch transactions: {response.status_code}, {response.text}")
            break

        data = response.json()
        transactions.extend(data.get("payments", []))

        # Check for next page
        cursor = data.get("cursor")
        if not cursor:
            break

    return transactions


def save_transactions(transactions):
    """Saves each transaction as a JSON file."""
    if not transactions:
        print("No transactions to save.")
        return

    output_dir = "transactions"
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

    for transaction in transactions:
        transaction_id = transaction["id"]
        file_path = os.path.join(output_dir, f"{transaction_id}.json")
        with open(file_path, "w") as file:
            json.dump(transaction, file, indent=4)
        print(f"Saved transaction {transaction_id} to {file_path}")


def main():
    """Main script execution."""
    print("Fetching transactions...")
    transactions = list_transactions()
    print(f"Retrieved {len(transactions)} transactions.")

    print("Saving transactions to files...")
    save_transactions(transactions)
    print("All transactions saved.")


if __name__ == "__main__":
    main()