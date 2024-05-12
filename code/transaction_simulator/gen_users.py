import random
import string
import json


def generate_gps_location():
    latitude = round(random.uniform(-90, 90), 6)
    longitude = round(random.uniform(-180, 180), 6)
    return latitude, longitude


# Funkcja do generowania unikalnego ID użytkownika
def generate_unique_user_id(existing_user_ids):
    while True:
        user_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if user_id not in existing_user_ids:
            existing_user_ids.add(user_id)
            return user_id


# Funkcja do generowania losowej liczby kart przypisanych do użytkownika (od 1 do 3)
def generate_number_of_cards():
    return random.randint(1, 3)


# Funkcja do generowania unikalnego ID karty
def generate_unique_card_id(existing_card_ids):
    while True:
        card_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if card_id not in existing_card_ids:
            existing_card_ids.add(card_id)
            return card_id


# Funkcja do generowania losowego limitu dostępnych wydatków na karcie
def generate_available_limit():
    return random.choice([1000, 5000, 10000])


# Generowanie użytkownika wraz z przypisanymi kartami
def generate_user_with_cards(existing_user_ids, existing_card_ids):
    user_id = generate_unique_user_id(existing_user_ids)
    num_of_cards = generate_number_of_cards()
    latitude, longitude = generate_gps_location()
    cards = [
        {
            "card_id": generate_unique_card_id(existing_card_ids),
            "available_limit": generate_available_limit(),
        }
        for _ in range(num_of_cards)
    ]
    return {
        "user_id": user_id,
        "cards": cards,
        "latitude": latitude,
        "longitude": longitude,
    }


# Inicjalizacja zbiorów do przechowywania istniejących ID użytkowników i kart
existing_user_ids = set()
existing_card_ids = set()

# Generowanie 8000 użytkowników z przypisanymi kartami
users_with_cards = [
    generate_user_with_cards(existing_user_ids, existing_card_ids) for _ in range(8000)
]

# Zapisanie danych użytkowników z kartami do pliku JSON
with open("users_with_cards.json", "w") as f:
    json.dump(users_with_cards, f, indent=4)

print(
    "Dane użytkowników z przypisanymi unikalnymi kartami zostały wygenerowane i zapisane do pliku users_with_cards.json"
)
