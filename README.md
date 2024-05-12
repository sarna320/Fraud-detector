## Docker
On wsl need install https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
Starting container will run all services and scripts

### Pulling
```sh
docker pull kafka-pyflink-tensorflow:latest
```

### Building
```sh
docker build -t sarna320/kafka-pyflink-tensorflow:latest .
```

### Container with path to mount
```sh
docker run --gpus all -d -p 9000:9000 -p 8081:8081 --name  kafka-pyflink-tf-container -v ${PWD}/code/:/home/kafka/code/ sarna320/kafka-pyflink-tensorflow:latest
```

### Container
```sh
docker run --gpus all -d -p 9000:9000 -p 8081:8081 --name  kafka-pyflink-tf-container sarna320/kafka-pyflink-tensorflow:latest
```

### Bash 
```sh
docker exec -it kafka-pyflink-tf-container bash
```

## Data generator
Generation of users with cards. Need to run if there is no users_with_cards.json or you want diffrent users.
```
python3 gen_users.py
```
This is module used by producent.py. It generates transactions for provided users and cards in batches
```sh
gen_user.py
```
Generation of transaction on kafka topic. Main simulator of transactions. Generates defined sequences of transactions witch chance to transactions to be fraud.
```sh
python3 producer.py
```

## PyFlink
This is prefered vesrion of running program, beacuse flink web app runnig locally will see this as a task
```
./flink-1.18.1/bin/flink run -py alarm.py
```
This will work, but it will not be detected by flink web app
```
python3 alarm.py
```
