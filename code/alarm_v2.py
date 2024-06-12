import json
from pyflink.common import Row, WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.state import ValueStateDescriptor, ValueState

state_value = None

def transaction_monitor():
    # 1. Utwórz StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars("file:///home/kafka/flink-sql-connector-kafka-3.1.0-1.18.jar")
    # env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1)

    # 2. Utwórz źródłowy DataStream
    kafka_source = FlinkKafkaConsumer(
        topics="Transactions",
        deserialization_schema=SimpleStringSchema(),
        properties={"bootstrap.servers": "localhost:9092"},
    )

    ds = env.add_source(kafka_source)

    # 3. Zdefiniuj logikę przetwarzania
    def process_transaction(json_str):
        global state_value
        data = json.loads(json_str)
        transaction_value = float(data["transaction_value"])

        if state_value is None or state_value["count"]>=30:
            state_value = {"count": 0, "sum": 0.0, "sum_sq": 0.0}
            

        count = state_value["count"] + 1
        sum_val = state_value["sum"] + transaction_value
        sum_sq = state_value["sum_sq"] + transaction_value**2

        state_value["count"] = count
        state_value["sum"] = sum_val
        state_value["sum_sq"] = sum_sq

        # Calculate mean and standard deviation
        mean = sum_val / count
        variance = (sum_sq / count) - (mean**2)
        std_dev = variance**0.5

        # Anomaly detection rule (e.g., 3 standard deviations from mean)
        if abs(transaction_value - mean) > 3 * std_dev:
            anomaly_message = {
                "user_id": data["user_id"],
                "card_id": data["card_id"],
                "card_limit": data["card_limit"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "transaction_value": data["transaction_value"],
                "timestamp": data["timestamp"],
                "message": "Anomalous transaction detected",
            }
            return json.dumps(anomaly_message)
        else:
            return None

    
    ds = ds.map(
        lambda json_str: process_transaction(json_str),
        output_type=Types.STRING(),
    ).filter(lambda x: x is not None)
    
    # 4. Utwórz sink i emituj rezultat do niego
    kafka_sink = FlinkKafkaProducer(
        topic="Alarm",
        serialization_schema=SimpleStringSchema(),
        producer_config={"bootstrap.servers": "localhost:9092"},
    )
    ds.add_sink(kafka_sink)

    # 5. Uruchom zadanie
    env.execute("transaction_monitor")


if __name__ == "__main__":
    transaction_monitor()
