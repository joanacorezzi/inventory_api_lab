
import requests  # used to call the Flask API

# Base URL of the Flask server
BASE_URL = "http://127.0.0.1:5000"


def print_menu():
    """Show the options the user can choose from."""
    print("\n=== Inventory Management CLI ===")
    print("1. View all inventory items")
    print("2. View a single item by ID")
    print("3. Add a new inventory item")
    print("4. Update item price or stock")
    print("5. Delete an item")
    print("6. Add item from OpenFoodFacts by barcode")
    print("0. Exit")


def view_all_items():
    """Call GET /inventory to see all items."""
    try:
        response = requests.get(f"{BASE_URL}/inventory")
        # If the response status code is 200, show the items
        if response.status_code == 200:
            items = response.json()
            print("\n--- Inventory Items ---")
            for item in items:
                print(f"ID: {item['id']}")
                print(f"  Name: {item['product'].get('product_name')}")
                print(f"  Brand: {item['product'].get('brands')}")
                print(f"  Price: {item['product'].get('price')}")
                print(f"  Stock: {item['product'].get('stock')}")
                print(f"  Barcode: {item['product'].get('barcode')}")
                print("------------------------")
        else:
            print("Error: Could not fetch inventory.")
    except requests.RequestException:
        # if the server is not running or there is a connection problem
        print("Error: Could not connect to the API. Is the Flask app running?")


def view_single_item():
    """Call GET /inventory/<id> to see one item."""
    item_id = input("Enter the item ID: ")

    # Build the URL with the item ID
    try:
        response = requests.get(f"{BASE_URL}/inventory/{item_id}")
        if response.status_code == 200:
            item = response.json()
            print("\n--- Item Details ---")
            print(f"ID: {item['id']}")
            print(f"Name: {item['product'].get('product_name')}")
            print(f"Brand: {item['product'].get('brands')}")
            print(f"Price: {item['product'].get('price')}")
            print(f"Stock: {item['product'].get('stock')}")
            print(f"Barcode: {item['product'].get('barcode')}")
            print(f"Ingredients: {item['product'].get('ingredients_text')}")
            print("---------------------")
        elif response.status_code == 404:
            print("Item not found.")
        else:
            print("Error: Could not fetch item.")
    except requests.RequestException:
        print("Error: Could not connect to the API.")


def add_new_item():
    """Call POST /inventory to add a manually created item."""
    print("\nEnter item information:")

    # Ask the user for basic product info
    name = input("Product name: ")
    brand = input("Brand: ")
    ingredients = input("Ingredients text: ")
    price_str = input("Price (example: 3.99): ")
    stock_str = input("Stock (example: 10): ")
    barcode = input("Barcode: ")

    # Convert price and stock to numbers
    try:
        price = float(price_str)
    except ValueError:
        price = 0.0  # default if user input is invalid

    try:
        stock = int(stock_str)
    except ValueError:
        stock = 0  # default if user input is invalid

    # Build the JSON body to send to the API
    data = {
        "product_name": name,
        "brands": brand,
        "ingredients_text": ingredients,
        "price": price,
        "stock": stock,
        "barcode": barcode
    }

    try:
        response = requests.post(f"{BASE_URL}/inventory", json=data)
        if response.status_code == 201:
            item = response.json()
            print("\nNew item added:")
            print(f"ID: {item['id']}")
            print(f"Name: {item['product'].get('product_name')}")
        else:
            print("Error: Could not add new item.")
    except requests.RequestException:
        print("Error: Could not connect to the API.")


def update_item_price_or_stock():
    """Call PATCH /inventory/<id> to update price or stock."""
    item_id = input("Enter the item ID to update: ")

    # Ask what the user wants to update
    print("What would you like to update?")
    print("1. Price")
    print("2. Stock")
    choice = input("Enter choice (1 or 2): ")

    data = {}

    if choice == "1":
        new_price_str = input("Enter new price: ")
        try:
            new_price = float(new_price_str)
        except ValueError:
            print("Invalid price. Update cancelled.")
            return
        data["price"] = new_price
    elif choice == "2":
        new_stock_str = input("Enter new stock: ")
        try:
            new_stock = int(new_stock_str)
        except ValueError:
            print("Invalid stock. Update cancelled.")
            return
        data["stock"] = new_stock
    else:
        print("Invalid choice. Update cancelled.")
        return

    # Send PATCH request to the API
    try:
        response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=data)
        if response.status_code == 200:
            item = response.json()
            print("\nItem updated:")
            print(f"ID: {item['id']}")
            print(f"Name: {item['product'].get('product_name')}")
            print(f"Price: {item['product'].get('price')}")
            print(f"Stock: {item['product'].get('stock')}")
        elif response.status_code == 404:
            print("Item not found.")
        else:
            print("Error: Could not update item.")
    except requests.RequestException:
        print("Error: Could not connect to the API.")


def delete_item():
    """Call DELETE /inventory/<id> to remove an item."""
    item_id = input("Enter the item ID to delete: ")

    try:
        response = requests.delete(f"{BASE_URL}/inventory/{item_id}")
        if response.status_code == 200:
            print("Item deleted successfully.")
        elif response.status_code == 404:
            print("Item not found.")
        else:
            print("Error: Could not delete item.")
    except requests.RequestException:
        print("Error: Could not connect to the API.")


def add_item_from_barcode():
    """Call POST /inventory/fetch/<barcode> to add an item using OpenFoodFacts."""
    barcode = input("Enter barcode to search in OpenFoodFacts: ")

    # send a POST request to the special route that uses the external API
    try:
        response = requests.post(f"{BASE_URL}/inventory/fetch/{barcode}")
        if response.status_code == 201:
            item = response.json()
            print("\nItem added from OpenFoodFacts:")
            print(f"ID: {item['id']}")
            print(f"Name: {item['product'].get('product_name')}")
            print(f"Brand: {item['product'].get('brands')}")
            print(f"Barcode: {item['product'].get('barcode')}")
        elif response.status_code == 404:
            print("Product not found in external API.")
        else:
            print("Error: Could not add item from external API.")
    except requests.RequestException:
        print("Error: Could not connect to the API.")


def main():
    """Main loop of the CLI application."""
    while True:
        print_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            view_all_items()
        elif choice == "2":
            view_single_item()
        elif choice == "3":
            add_new_item()
        elif choice == "4":
            update_item_price_or_stock()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            add_item_from_barcode()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


# Run the CLI only if this file is executed directly
if __name__ == "__main__":
    main()
