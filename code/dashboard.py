import threading
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import Counter, deque
from kafka import KafkaConsumer
import queue
import numpy as np
from matplotlib.gridspec import GridSpec


class KafkaConsumerThread(threading.Thread):
    def __init__(self, topic, message_queue):
        super().__init__()
        self.topic = topic
        self.message_queue = message_queue
        self.running = True
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers="localhost:9092",
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )

    def run(self):
        while self.running:
            for message in self.consumer:
                if not self.running:
                    break
                self.message_queue.put((self.topic, message.value))
        self.consumer.close()

    def stop(self):
        self.running = False


class TransactionMonitor:
    def __init__(self):
        self.transaction_count = 0
        self.anomaly_count = 0
        self.fraud_counts = Counter()
        self.message_queue = queue.Queue()
        self.last_two_transactions = deque(maxlen=5)

        self.kafka_thread_transactions = KafkaConsumerThread(
            "Transactions", self.message_queue
        )
        self.kafka_thread_frauds = KafkaConsumerThread("Alarm", self.message_queue)

        self.kafka_thread_transactions.start()
        self.kafka_thread_frauds.start()

        self.fig = plt.figure(figsize=(12, 10))
        gs = GridSpec(3, 1, height_ratios=[2, 2, 1])

        self.ax2 = self.fig.add_subplot(gs[1])


        self.colors = plt.cm.tab20(np.linspace(0, 1, 40))

        self.ani = animation.FuncAnimation(self.fig, self.update_plots, interval=1000)
        plt.tight_layout(pad=2.0)
        plt.show()

    def process_messages(self):
        while not self.message_queue.empty():
            topic, message = self.message_queue.get()
            print(f"Processing message from topic {topic}: {message}")
            if topic == "Transactions":
                self.transaction_count += 1
                self.last_two_transactions.append(message)
            elif topic == "Alarm":
                self.anomaly_count += 1
                self.fraud_counts[message["anomaly"]] += 1
                self.last_two_transactions.append(message)


    def update_plots(self, _):
        self.process_messages()

        self.ax2.clear()

        self.plot_frauds(self.ax2)


    def plot_frauds(self, ax):
        fraud_types = list(self.fraud_counts.keys())
        fraud_counts = list(self.fraud_counts.values())

        bar_colors = [self.colors[hash(t) % len(self.colors)] for t in fraud_types]

        ax.bar(fraud_types, fraud_counts, color=bar_colors)
        ax.set_title("Detected Fraud Types")
        ax.set_xlabel("Fraud Type")
        ax.set_ylabel("Count")

        for i, count in enumerate(fraud_counts):
            ax.text(i, count + 0.5, str(count), ha="center")

    def stop(self):
        self.kafka_thread_transactions.stop()
        self.kafka_thread_frauds.stop()


if __name__ == "__main__":
    monitor = TransactionMonitor()
    try:
        plt.show()
    except KeyboardInterrupt:
        monitor.stop()
        print("Stopped monitoring.")
