import random
from datetime import datetime
import json


def generate_small_value():
    return round(random.uniform(0.01, 0.09), 2)


def generate_normal_value():
    return round(random.uniform(1, 300), 2)


def generate_large_value():
    return round(random.uniform(500, 1000), 2)


def generate_very_large_value():
    return round(random.uniform(10000, 100000), 2)


def generate_transaction_value():
    value_functions = [
        generate_small_value(),
        generate_normal_value(),
        generate_large_value(),
        generate_very_large_value(),
    ]
    return random.choice(value_functions)


def generate_timestamp():
    return datetime.now().isoformat()


def generate_fraud_location():
    latitude = round(random.uniform(-90, 90), 6)
    longitude = round(random.uniform(-180, 180), 6)
    return latitude, longitude

def random_user_card():
    with open("users_with_cards.json", "r") as f:
        users_with_cards = json.load(f)
    selected_user = random.choice(users_with_cards)
    selected_card = random.choice(selected_user["cards"])
    return selected_user, selected_card

def generate_message(user,card,type=None, fraud_location=0,number_of_transactions=1,) -> dict:
    """
    Generates random transactions for selected users from a JSON file.

    Args:
        type (int, optional): Type of transaction. Default is None . Possible values:
            1 - Small transaction value
            2 - Normal transaction value
            3 - Large transaction value
            4 - Very large transaction value
            None - Random transaction value
        fraud_location (int, optional): Specifies whether the transaction should be generated with a fake location.
            Default is 0 (no fake location). Possible values:
            0 - No fake location
            1 - Use fake location
        number_of_transactions (int, optional): Number of transactions to generate. Default is 1.

    Returns:
        list: A list containing transaction details.
    """
    selected_user=user 
    selected_card=card
    transactions = []
    for _ in range(number_of_transactions):
    # Location fraud
        if fraud_location == 1:
            latitude, longitude = generate_fraud_location()
        else:
            latitude = selected_user["latitude"]
            longitude = selected_user["longitude"]

        # Type of transaction
        if type == 1:
            transaction_value = generate_small_value()
        elif type == 2:
            transaction_value = generate_normal_value()
        elif type == 3:
            transaction_value = generate_large_value()
        elif type == 4:
            transaction_value = generate_very_large_value()
        else:
            transaction_value = generate_transaction_value()

        transaction = {
            "user_id": selected_user["user_id"],
            "card_id": selected_card["card_id"],
            "card_limit": selected_card["available_limit"],
            "latitude": latitude,
            "longitude": longitude,
            "transaction_value": transaction_value,
            "timestamp": generate_timestamp(),
        }

        transactions.append(transaction)

    return transactions

