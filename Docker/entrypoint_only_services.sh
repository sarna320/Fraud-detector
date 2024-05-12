#!/bin/bash

# Function to stop services and clean up
cleanup() {
    echo "Stopping services and cleaning up..."

    # Stop Flink cluster
    ./flink-1.18.1/bin/stop-cluster.sh -q
    echo "Stop Flink cluster"

    # Stop Zookeeper and Kafka
    /home/kafka/kafka_2.12-3.1.0/bin/zookeeper-server-stop.sh -q
    /home/kafka/kafka_2.12-3.1.0/bin/kafka-server-stop.sh -q
    echo "Stop Zookeeper and Kafka"

    # Remove Kafka logs and Zookeeper data
    sudo rm -rf /tmp/*
    sudo rm -rf /home/kafka/logs/
    sudo rm -rf __pycache__
    sudo rm -rf kafka_2.12-3.1.0/log/*
    sudo rm -rf flink-1.18.1/log/*
    echo "Removes files"

    # Stop Kafdrop if running
    pkill -f "java.*kafdrop" || true -q
    echo "Stop Kafdrop if running"

    echo "Services stopped and cleaned up."
}

# Function to start services
start_services() {
    # Start Zookeeper and Kafka
    /home/kafka/kafka_2.12-3.1.0/bin/zookeeper-server-start.sh /home/kafka/kafka_2.12-3.1.0/config/zookeeper.properties &
    /home/kafka/kafka_2.12-3.1.0/bin/kafka-server-start.sh /home/kafka/kafka_2.12-3.1.0/config/server.properties &
    
    # Wait for Kafka to start
    sleep 10
    
    # Check if Kafka has started successfully
    if ! /home/kafka/kafka_2.12-3.1.0/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 &>/dev/null; then
        echo "Kafka failed to start properly. Clearing Kafka metadata..."
        cleanup
        echo "Attempting to start services again..."
        start_services
    fi
    
    # Create Kafka topics
    /home/kafka/kafka_2.12-3.1.0/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic Transactions
    /home/kafka/kafka_2.12-3.1.0/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic Alarm
    
    # Produce messages to Kafka topics
    # echo "Hello, World" | /home/kafka/kafka_2.12-3.1.0/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic Transactions > /dev/null
    # echo "Hello, World" | /home/kafka/kafka_2.12-3.1.0/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic Alarm > /dev/null
    
    # Start Flink cluster
    ./flink-1.18.1/bin/start-cluster.sh
    
    # Give permissions to Flink logs
    sudo chmod 777 /usr/local/lib/python3.10/site-packages/pyflink/log/
    
    # Start producer script
    #python3 producent.py &
    
    # Run Flink job
    #./flink-1.18.1/bin/flink run -py alarm.py &
    
    # Start Kafdrop
    java --add-opens=java.base/sun.nio.ch=ALL-UNNAMED -jar /home/kafka/kafdrop-4.0.1.jar --kafka.brokerConnect=localhost:9092 

    #export CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))
    #export LD_LIBRARY_PATH="$CUDNN_PATH/lib":"/usr/local/cuda/lib64"
}

# Register cleanup function to be called on container stop
trap cleanup EXIT

# Start services
start_services

# Keep the script running in foreground to prevent the container from exiting
# This allows the trap to catch the EXIT signal when the container stops
while true; do sleep 1; done
