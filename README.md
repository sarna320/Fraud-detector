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
