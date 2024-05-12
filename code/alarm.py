import json
from pyflink.common import Row
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema

def temperature_monitor():
    # 1. Utwórz StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars("file:///home/kafka/flink-sql-connector-kafka-3.1.0-1.18.jar")
    #env.set_runtime_mode(RuntimeExecutionMode.BATCH)
    env.set_parallelism(1)

    # 2. Utwórz źródłowy DataStream
    kafka_source = FlinkKafkaConsumer(
        topics='Temperature',
        deserialization_schema=SimpleStringSchema(),
        properties={'bootstrap.servers': 'localhost:9092'})

    ds = env.add_source(kafka_source)

    # 3. Zdefiniuj logikę przetwarzania
    def process_json(json_str):
        data = json.loads(json_str)
        if float(data["temperature"]) < 0:
            x = json.dumps({"thermometer_id": data["thermometer_id"],
                               "temperature": data["temperature"],
                               "timestamp": data["timestamp"],
                               "message": "Temperature below zero!"})
            print(x)
            return x
        else:
            return None

    ds = ds.map(lambda json_str: process_json(json_str),
                output_type=Types.STRING()).filter(lambda x: x is not None)

    # 4. Utwórz sink i emituj rezultat do niego
    kafka_sink = FlinkKafkaProducer(
        topic='Alarm',
        serialization_schema=SimpleStringSchema(),
        producer_config={'bootstrap.servers': 'localhost:9092'})
    ds.add_sink(kafka_sink)

    # 5. Uruchom zadanie
    env.execute('temperature_monitor')


if __name__ == '__main__':
    temperature_monitor()
