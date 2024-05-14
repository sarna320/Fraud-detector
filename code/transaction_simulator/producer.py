import time
import json
import random
from datetime import datetime
from gen_transaction import generate_message
from kafka import KafkaProducer


# Messages will be serialized as JSON
def serializer(message):
    return json.dumps(message).encode("utf-8")


# Kafka Producer
producer = KafkaProducer(bootstrap_servers=["localhost:9092"], value_serializer=serializer)
topic = "Transactions"





def send_fraud_location_message():
    
    num = random.randint(1, 8)
    messages = generate_message(type=2, number_of_transactions=num)
    messages += generate_message(fraud_location=1,type=2)
    messages += generate_message(type=2, number_of_transactions=10 - 1 - num)
    for message in messages:
        producer.send(topic, message)


def send_fraud_sequence():
    # Nomrmal trans, Small trans, Big trans
    
    # Max 7 because we send 3 in sequence and we want sent in batch of 10
    num = random.randint(1, 7)
    messages = generate_message(type=2, number_of_transactions=num)
    messages += generate_message(type=1)
    messages += generate_message(type=3)
    messages += generate_message(type=2, number_of_transactions=10 - 2 - num)
    for message in messages:
        producer.send(topic, message)


def send_similiar_to_fraud_sequence():
    # Nomrmal trans, Small trans, Normal trans,  Big trans
    # Max 6 because we send 3 in sequence and we want sent in batch of 10
    num = random.randint(1, 6)
    messages = generate_message(type=2, number_of_transactions=num)
    messages += generate_message(type=1)
    messages += generate_message(type=2)
    messages += generate_message(type=3)
    messages += generate_message(type=2, number_of_transactions=10 - 3 - num)
    for message in messages:
        producer.send(topic, message)


def send_very_big_in_normal_fraud_sequence():
    # Normal trans, Big  trans, Normal trans
    num = random.randint(1, 6)
    messages = generate_message(type=2, number_of_transactions=num)
    messages += generate_message(type=4)
    messages += generate_message(type=2, number_of_transactions=10 - 1 - num)
    for message in messages:
        producer.send(topic, message)   
        
def send_normal_sequence():    
    num = random.randint(1, 9)
    messages = generate_message(type=2, number_of_transactions=num)
    messages += generate_message(type=3, number_of_transactions=10 - num)
    random.shuffle(messages)
    for message in messages:
        producer.send(topic, message)   

if __name__ == "__main__":
    fraud_functions = [
        {"function": send_fraud_location_message, "print_message": "!!!Sending fraud location message!!!"},
        {"function": send_fraud_sequence, "print_message": "!!!Sending fraud sequence!!!"},
        {"function": send_similiar_to_fraud_sequence, "print_message": "!!!Sending similar to fraud sequence!!!"},
        {"function": send_very_big_in_normal_fraud_sequence, "print_message": "!!!Sending very big in normal fraud sequence!!!"}
    ]
    with open("users_with_cards.json", "r") as f:
        users_with_cards = json.load(f)
    number_of_cards=0
    for user in users_with_cards:
    # Policz ilość kart dla każdego użytkownika
        number_of_cards += len(user["cards"])
    print(f"Number of cards: {number_of_cards}")
    while True:
        if random.random()<0.2:
            selected_function = random.choice(fraud_functions)
            print(selected_function["print_message"])
            selected_function = selected_function["function"]
            selected_function()  
        else:
            send_normal_sequence()
            print("Sending normal sequence")
        time.sleep(random.random()*3)
            
         
