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
                    break;
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

        self.fig = plt.figure(figsize=(15, 10))
        gs = GridSpec(2, 3, height_ratios=[1, 1], width_ratios=[1, 1, 1])

        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax2 = self.fig.add_subplot(gs[0, 1])
        self.ax3 = self.fig.add_subplot(gs[0, 2])
        self.ax4 = self.fig.add_subplot(gs[1, 0])
        self.ax5 = self.fig.add_subplot(gs[1, 1])
        self.ax6 = self.fig.add_subplot(gs[1, 2])

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

    def update_table(self):
        last_five_transactions = list(self.last_two_transactions)[-5:]
        table_data = [
            [
                txn["card_id"],
                txn["user_id"],
                f"{txn['transaction_value']:.2f}",
                f"{txn['card_limit']:.2f}",
                txn["timestamp"],
                txn.get("anomaly", "N/A"),
            ]
            for txn in last_five_transactions
        ]

        self.ax6.clear()
        self.ax6.axis("off")

        table = self.ax6.table(
            cellText=table_data,
            colLabels=["Card ID", "User ID", "Value", "Limit", "Timestamp", "Anomaly"],
            loc="center",
            cellLoc="center",
        )

        for i, row in enumerate(table_data):
            anomaly = row[5]
            cell_color = "red" if anomaly != "N/A" else "green"
            for j in range(len(row)):
                table[(i + 1, j)].set_facecolor(cell_color)

    def update_plots(self, _):
        self.process_messages()

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.ax5.clear()
        self.ax6.clear()

        self.plot_counts(self.ax1, self.transaction_count, self.anomaly_count)
        self.plot_frauds(self.ax2)
        self.plot_transaction_values(self.ax3)
        self.plot_card_limits(self.ax4)
        self.plot_fraud_percentage(self.ax5)

        self.update_table()

    def plot_counts(self, ax, transaction_count, anomaly_count):
        counts = [transaction_count, anomaly_count]
        labels = ["Valid Transactions", "Anomalies"]

        ax.bar(labels, counts, color=["blue", "red"])
        ax.set_title("Transaction and Anomaly Counts")
        ax.set_ylabel("Count")

        for i, count in enumerate(counts):
            ax.text(i, count + 0.5, str(count), ha="center")

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

    def plot_transaction_values(self, ax):
        transaction_values = [txn["transaction_value"] for txn in self.last_two_transactions]

        ax.hist(transaction_values, bins=10, color="blue", edgecolor="black")
        ax.set_title("Transaction Values")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")

    def plot_card_limits(self, ax):
        card_limits = [txn["card_limit"] for txn in self.last_two_transactions]

        ax.hist(card_limits, bins=10, color="green", edgecolor="black")
        ax.set_title("Card Limits")
        ax.set_xlabel("Limit")
        ax.set_ylabel("Frequency")

    def plot_fraud_percentage(self, ax):
        if self.transaction_count == 0:
            fraud_percentage = 0
        else:
            fraud_percentage = (self.anomaly_count / self.transaction_count) * 100

        ax.bar(["Fraud Percentage"], [fraud_percentage], color=["red"])
        ax.set_ylim(0, 100)
        ax.set_title("Fraud Percentage")
        ax.set_ylabel("Percentage")

        ax.text(0, fraud_percentage + 2, f"{fraud_percentage:.2f}%", ha="center")

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
