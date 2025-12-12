
from unittest.mock import patch, MagicMock

import cli

@patch("cli.requests.get")
def test_view_all_items(mock_get):
    """Test that view_all_items calls the API and handles a basic response."""

    # Fake response from the API
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [
        {
            "id": 1,
            "product": {
                "product_name": "Test Product",
                "brands": "Test Brand",
                "price": 1.23,
                "stock": 5,
                "barcode": "1234567890"
            }
        }
    ]

    mock_get.return_value = fake_response

    # so the function runs without errors
    cli.view_all_items()


@patch("cli.requests.post")
@patch("builtins.input")
def test_add_item_from_barcode(mock_input, mock_post):
    """Test the CLI function that adds an item from barcode using the external API route."""

    # Mock user input for barcode
    mock_input.return_value = "1234567890"

    # Fake API response
    fake_response = MagicMock()
    fake_response.status_code = 201
    fake_response.json.return_value = {
        "id": 10,
        "product": {
            "product_name": "Barcode Product",
            "brands": "Brand",
            "barcode": "1234567890"
        }
    }

    mock_post.return_value = fake_response

    # so it runs without errors
    cli.add_item_from_barcode()
