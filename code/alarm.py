import json
from pyflink.common import Row, WatermarkStrategy
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema


def transaction_monitor():
    # 1. Utwórz StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars("file:///home/kafka/flink-sql-connector-kafka-3.1.0-1.18.jar")
    # env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    #env.set_parallelism(1)

    # 2. Utwórz źródłowy DataStream
    kafka_source = FlinkKafkaConsumer(
        topics="Transactions",
        deserialization_schema=SimpleStringSchema(),
        properties={"bootstrap.servers": "localhost:9092"},
    )

    ds = env.add_source(kafka_source)
    

    # 3. Zdefiniuj logikę przetwarzania
    def process_json(json_str):
        data = json.loads(json_str)
        if float(data["transaction_value"]) > 100:
            x = json.dumps(
                {
                    "user_id": data["user_id"],
                    "card_id": data["card_id"],
                    "card_limit": data["card_limit"],
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "transaction_value": data["transaction_value"],
                    "timestamp": data["timestamp"],
                    "message": "Transaction bigger than  100",
                }
            )
            print(x)
            return x
        else:
            return None

    ds = ds.map(
        lambda json_str: process_json(json_str), output_type=Types.STRING()
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
