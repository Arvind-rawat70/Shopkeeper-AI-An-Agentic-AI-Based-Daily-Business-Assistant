import pandas as pd

from chat_response_utils import build_direct_business_answer


def test_low_stock_name_question_returns_only_targeted_result():
    df = pd.DataFrame([
        {"name": "Rice", "stock_quantity": 15},
        {"name": "Milk", "stock_quantity": 22},
        {"name": "Bread", "stock_quantity": 9},
    ])

    answer = build_direct_business_answer("Give me the name of the lowest stock product", df)

    assert answer == "The product with the lowest stock right now is Bread, with 9 units currently in stock."


def test_low_stock_single_product_question_ignores_extra_rows():
    df = pd.DataFrame([
        {"name": "Tomato", "stock_quantity": 18},
        {"name": "Onion", "stock_quantity": 11},
        {"name": "Potato", "stock_quantity": 7},
    ])

    answer = build_direct_business_answer("What is the name of the lowest stock item?", df)

    assert answer == "The product with the lowest stock right now is Potato, with 7 units currently in stock."
