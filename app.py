
from flask import Flask, jsonify, request  
import requests  # to call the external OpenFoodFacts API

app = Flask(__name__)

# Fake "database" (inventory array)
# Each item has:
# - id: unique ID for our system
# - status: like OpenFoodFacts status (1 = found)
# - product: dictionary with product details
inventory = [
    {
        "id": 1,
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar",
            "price": 3.99,
            "stock": 10,
            "barcode": "1234567890"
        }
    },
    {
        "id": 2,
        "status": 1,
        "product": {
            "product_name": "Granola Bar",
            "brands": "Nature Valley",
            "ingredients_text": "Oats, sugar, honey",
            "price": 1.50,
            "stock": 25,
            "barcode": "0987654321"
        }
    }
]


# Helper function to find an item by id in the inventory list
def find_item_by_id(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None

# Helper function to call OpenFoodFacts by barcode

def fetch_openfoodfacts_product(barcode):
    """
    Call the OpenFoodFacts API using a barcode.
    If the product is found, return a simple dict with some fields.
    If not found or error, return None.
    """
    # endpoint for product by barcode 
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        # timeout=5 means: wait max 5 seconds for response
        response = requests.get(url, timeout=5)
    except requests.RequestException:
        # Network error
        return None

    if response.status_code != 200:
        # Bad HTTP status
        return None

    data = response.json()

    # OpenFoodFacts uses "status" 1 when product is found
    if data.get("status") != 1:
        return None

    product = data.get("product", {})

    # only pick basic fields like the example
    return {
        "product_name": product.get("product_name"),
        "brands": product.get("brands"),
        "ingredients_text": product.get("ingredients_text"),
    }


# Basic test route 
@app.route("/")
def home():
    # text to see that the app runs
    return "Inventory API is running."

# GET /inventory  -> Fetch all items
@app.route("/inventory", methods=["GET"])
def get_inventory():
    # Return the whole inventory list as JSON
    return jsonify(inventory), 200



# GET /inventory/<id>  -> Fetch one item by id
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    # find the item by id
    item = find_item_by_id(item_id)
    if item is None:
        # If not found, return 404 (Not Found)
        return jsonify({"error": "Item not found"}), 404

    # If found, return the item
    return jsonify(item), 200


# POST /inventory  -> Add a new item 
@app.route("/inventory", methods=["POST"])
def add_inventory_item():
    # Get JSON data sent by the client
    data = request.get_json()

    # validation
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Create a new id (max existing id + 1 or 1 if list is empty)
    if inventory:
        new_id = max(item["id"] for item in inventory) + 1
    else:
        new_id = 1

    # Build the new item with a structure similar to OpenFoodFacts
    new_item = {
        "id": new_id,
        "status": 1,  # pretend it is "found"
        "product": {
            "product_name": data.get("product_name", "Unknown Product"),
            "brands": data.get("brands", "Unknown Brand"),
            "ingredients_text": data.get("ingredients_text", ""),
            "price": data.get("price", 0.0),
            "stock": data.get("stock", 0),
            "barcode": data.get("barcode", "")
        }
    }

    # Add to "database" (list)
    inventory.append(new_item)

    # Return the new item with status code 201 
    return jsonify(new_item), 201


# PATCH /inventory/<id>  -> Update part of an item
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    #only update fields inside "product"
    product = item["product"]

    # Loop through the keys sent in the request and update if they exist
    for key, value in data.items():
        # Example: if data = {"price": 4.50}, set product["price"] = 4.50
        product[key] = value

    # Return the updated item
    return jsonify(item), 200


# DELETE /inventory/<id>  -> Remove an item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    # Remove the item from the list
    inventory.remove(item)

    # Return a message
    return jsonify({"message": "Item deleted"}), 200


# POST /inventory/fetch/<barcode>
# Use OpenFoodFacts to create a new item in our inventory

@app.route("/inventory/fetch/<barcode>", methods=["POST"])
def add_item_from_barcode(barcode):

    # Call the external API
    api_product = fetch_openfoodfacts_product(barcode)

    if api_product is None:
        # If external API did not find anything or there was an error
        return jsonify({"error": "Product not found in external API"}), 404

    # Create a new id for local inventory
    if inventory:
        new_id = max(item["id"] for item in inventory) + 1
    else:
        new_id = 1

    # Build a new item using the external API data
    new_item = {
        "id": new_id,
        "status": 1,  # product found
        "product": {
            # use values from API; if something missing, use default string
            "product_name": api_product.get("product_name") or "Unknown Product",
            "brands": api_product.get("brands") or "Unknown Brand",
            "ingredients_text": api_product.get("ingredients_text") or "",
            # price and stock are still our own fields 
            "price": 0.0,
            "stock": 0,
            "barcode": barcode
        }
    }

    # Save new item into fake "database"
    inventory.append(new_item)

    # Return the newly created item
    return jsonify(new_item), 201


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
