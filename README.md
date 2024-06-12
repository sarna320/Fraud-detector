## To start 
Kafdrop and pyflink will be visible on [localhost:9000](http://localhost:9000/) [localhost:8081](http://localhost:8081/)
Requirments:
- installed wsl 2 
- installed docker-desktop
- Pull image
```sh
docker pull sarna320/kafka-pyflink:latest-only_services
```
- Clone repo
- After clone in repo
```sh
docker run --gpus all -d -p 9000:9000 -p 8081:8081 --name  kafka-pyflink-container -v ${PWD}/code/:/home/kafka/code/ sarna320/kafka-pyflink:latest-only_services
```
- After all services started
```sh
docker exec -it kafka-pyflink-container bash
```
## Data generator
Generation of users with cards. Need to run if there is no users_with_cards.json or you want diffrent users.
```sh
python3 gen_users.py
```
This is module used by producent.py. It generates transactions for provided users and cards in batches
```sh
gen_transactions.py
```
Generation of transaction on kafka topic. Main simulator of transactions. Generates defined sequences of transactions witch chance to transactions to be fraud.
```sh
python3 producer.py
```
Test consument in kafka to see transactions
```sh
python3 consumer.py
```

## PyFlink
This is prefered vesrion of running program, beacuse flink web app runnig locally will see this as a task
```
~/flink-1.18.1/bin/flink run -py ~/code/alarm.py 
```
This will work, but it will not be detected by flink web app
```
python3 ~/code/alarm.py 
```
