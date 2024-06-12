from datetime import datetime, timedelta
from typing import Iterable
from pyflink.common import Types, Row
from pyflink.common.time import Time, Duration
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.formats.json import (
    JsonRowDeserializationSchema,
    JsonRowSerializationSchema,
)
from pyflink.datastream.functions import (
    KeyedProcessFunction,
    ProcessWindowFunction,
    RuntimeContext,
)
from pyflink.datastream.state import MapStateDescriptor
from pyflink.datastream.state import ValueStateDescriptor, ValueState
from pyflink.datastream.window import TumblingEventTimeWindows
from collections import deque


class DetectLimitBreaches(ProcessWindowFunction):

    def process(
        self, key: int, context: ProcessWindowFunction.Context, elements: Iterable[dict]
    ) -> Iterable[dict]:
        transactions = list(elements)

        limit = float(transactions[0]["card_limit"])
        over_limit_transactions = [
            trans for trans in transactions if float(trans["transaction_value"]) > limit
        ]

        if len(over_limit_transactions) >= 3:
            for transaction in over_limit_transactions:
                transaction["anomaly"] = "Limit breach detected"
                yield transaction

        


class DetectMovingAverageAnomalies(KeyedProcessFunction):

    def __init__(self):
        self.transaction_window_state = None

    def open(self, runtime_context: RuntimeContext):
        self.transaction_window_state = runtime_context.get_state(
            ValueStateDescriptor("transaction_window", Types.PICKLED_BYTE_ARRAY())
        )

    def process_element(self, value: dict, ctx: KeyedProcessFunction.Context):
        # Retrieve the current state or initialize a new deque
        transaction_window = self.transaction_window_state.value()
        if transaction_window is None:
            transaction_window = deque(maxlen=100)
        else:
            transaction_window = deque(transaction_window, maxlen=100)

        # Add the new transaction value
        transaction_window.append(float(value["transaction_value"]))

        # Update the state with the latest transaction window
        self.transaction_window_state.update(transaction_window)

        # Calculate the moving average
        moving_avg = sum(transaction_window) / len(transaction_window)

        # Check for anomalies
        if float(value["transaction_value"]) > 3 * moving_avg and len(transaction_window)>50:
            value["anomaly"] = "Much different from average"
            print(f"Transaction differs a lot from average{value}")
            yield value


class DetectLocationChangeAnomalies(KeyedProcessFunction):

    def __init__(self):
        self.last_location_state = None

    def open(self, runtime_context: RuntimeContext):
        self.last_location_state = runtime_context.get_state(
            ValueStateDescriptor("last_location", Types.PICKLED_BYTE_ARRAY())
        )

    def process_element(self, value: dict, ctx: KeyedProcessFunction.Context):
        # Retrieve the current state or initialize to None
        last_location = self.last_location_state.value()
        current_location = (value["latitude"], value["longitude"])

        # Check for location change
        if last_location and last_location != current_location:
            value["anomaly"] = "location change"
            yield value

        # Update the state with the new location
        self.last_location_state.update(current_location)

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

    env.add_jars("file:///home/kafka/flink-sql-connector-kafka-3.1.0-1.18.jar")

    input_type_info = Types.ROW_NAMED(
        [
            "card_id",
            "user_id",
            "card_limit",
            "latitude",
            "longitude",
            "transaction_value",
            "timestamp",
            "anomaly",
        ],
        [
            Types.STRING(),
            Types.STRING(),
            Types.DOUBLE(),
            Types.DOUBLE(),
            Types.DOUBLE(),
            Types.DOUBLE(),
            Types.STRING(),
            Types.STRING(),
        ],
    )

    deserialization_schema = (
        JsonRowDeserializationSchema.builder()
        .type_info(type_info=input_type_info)
        .build()
    )

    kafka_source = FlinkKafkaConsumer(
        topics="Transactions",
        deserialization_schema=deserialization_schema,
        properties={"bootstrap.servers": "localhost:9092"},
    )

    ds = env.add_source(kafka_source)

    watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
        Duration.of_minutes(1)
    )

    ds = ds.assign_timestamps_and_watermarks(watermark_strategy)

    output_type_info = Types.ROW_NAMED(
        [
            "card_id",
            "user_id",
            "card_limit",
            "latitude",
            "longitude",
            "transaction_value",
            "timestamp",
            "anomaly",
        ],
        [
            Types.STRING(),
            Types.STRING(),
            Types.DOUBLE(),
            Types.DOUBLE(),
            Types.DOUBLE(),
            Types.DOUBLE(),
            Types.STRING(),
            Types.STRING(),
        ],
    )

    anomalies_limit = (
        ds.key_by(lambda row: row["card_id"])
        .window(TumblingEventTimeWindows.of(Time.minutes(5)))
        .process(DetectLimitBreaches(), output_type=output_type_info)
    )

    anomalies_average = (
        ds.key_by(lambda row: row["card_id"])
        .process(DetectMovingAverageAnomalies(), output_type=output_type_info)
    )

    anomalies_location = (
        ds.key_by(lambda row: row["card_id"])
        .process(DetectLocationChangeAnomalies(), output_type=output_type_info)
    )

    serialization_schema = (
        JsonRowSerializationSchema.builder()
        .with_type_info(type_info=output_type_info)
        .build()
    )

    kafka_sink = FlinkKafkaProducer(
        topic="Alarm",
        serialization_schema=serialization_schema,
        producer_config={"bootstrap.servers": "localhost:9092"},
    )

    anomalies_limit.add_sink(kafka_sink)
    anomalies_average.add_sink(kafka_sink)
    anomalies_location.add_sink(kafka_sink)

    env.execute("anomaly_detection")


if __name__ == "__main__":
    main()