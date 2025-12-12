
import json
from unittest.mock import patch, MagicMock

from app import app, inventory, fetch_openfoodfacts_product


# helper to gives us a test client
def get_test_client():
    return app.test_client()


def test_get_inventory():
    """Test GET /inventory returns a list and status 200."""
    client = get_test_client()
    response = client.get("/inventory")

    assert response.status_code == 200
    data = response.get_json()

    # response will be a list (inventory array)
    assert isinstance(data, list)
    # There should be at least 1 item in inventory
    assert len(data) >= 1


def test_add_inventory_item():
    """Test POST /inventory adds a new item."""
    client = get_test_client()

    # Build a fake product to send
    new_product = {
        "product_name": "Test Product",
        "brands": "Test Brand",
        "ingredients_text": "Test ingredients",
        "price": 9.99,
        "stock": 5,
        "barcode": "1111111111"
    }

    response = client.post(
        "/inventory",
        data=json.dumps(new_product),  # send as JSON string
        content_type="application/json"
    )

    assert response.status_code == 201
    data = response.get_json()

    # The returned item should have an id and a product section
    assert "id" in data
    assert "product" in data
    assert data["product"]["product_name"] == "Test Product"

    # check if the inventory list contains the item 
    ids = [item["id"] for item in inventory]
    assert data["id"] in ids


def test_update_inventory_item():
    """Test PATCH /inventory/<id> updates the price of an item."""
    client = get_test_client()

    # Make sure there is at least one item to update
    first_item_id = inventory[0]["id"]

    update_data = {"price": 4.50}

    response = client.patch(
        f"/inventory/{first_item_id}",
        data=json.dumps(update_data),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()

    # Check that the price was updated
    assert data["product"]["price"] == 4.50


def test_delete_inventory_item():
    """Test DELETE /inventory/<id> removes an item."""
    client = get_test_client()

    # add a simple item that can  be safely deleted
    new_product = {
        "product_name": "Delete Me",
        "brands": "Temp",
        "ingredients_text": "",
        "price": 1.0,
        "stock": 1,
        "barcode": "2222222222"
    }

    post_response = client.post(
        "/inventory",
        data=json.dumps(new_product),
        content_type="application/json"
    )
    post_data = post_response.get_json()
    new_id = post_data["id"]

    # delete the item that was just added
    delete_response = client.delete(f"/inventory/{new_id}")
    assert delete_response.status_code == 200

    # GET should return 404 
    get_response = client.get(f"/inventory/{new_id}")
    assert get_response.status_code == 404

# Tests for external API helper (mocking requests.get)

@patch("app.requests.get")
def test_fetch_openfoodfacts_product_success(mock_get):
    """Test fetch_openfoodfacts_product when external API returns a valid product."""

    # Create a fake response object
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Mocked Product",
            "brands": "Mock Brand",
            "ingredients_text": "Mock ingredients"
        }
    }

    # return the fake_response
    mock_get.return_value = fake_response

    # call the function
    result = fetch_openfoodfacts_product("1234567890")

    # dictionary with those fields
    assert result is not None
    assert result["product_name"] == "Mocked Product"
    assert result["brands"] == "Mock Brand"
    assert result["ingredients_text"] == "Mock ingredients"


@patch("app.requests.get")
def test_fetch_openfoodfacts_product_not_found(mock_get):
    """Test fetch_openfoodfacts_product when external API does not find product."""

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "status": 0,  # 0 means not found according to OpenFoodFacts
        "product": {}
    }

    mock_get.return_value = fake_response

    result = fetch_openfoodfacts_product("0000000000")

    # Should return None if product is not found
    assert result is None
