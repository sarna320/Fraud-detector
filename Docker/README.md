## Docker
On wsl need install https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html if wamma use tensorflow
Starting container will run all services and scripts

### Pulling
Not pushed yet with tensorflow
```sh
docker pull sarna320/kafka-pyflink-tensorflow:latest-only_services
```

With starting only service
```sh
docker pull sarna320/kafka-pyflink:latest-only_services
```

With starting service and scripts, not pushed yet
```sh
docker pull sarna320/kafka-pyflink:latest
```

### Building
With tensorflow
```sh
docker build -t sarna320/kafka-pyflink-tensorflow:latest -f Docker/Dockerfile_tensorflow_only_services Docker
```

With out tensorflow with only services starting 
```sh
docker build -t sarna320/kafka-pyflink:latest-only_services -f Docker/Dockerfile_no_tensorflow_only_services Docker
```

With starting service and scripts
```sh
docker build -t sarna320/kafka-pyflink-image:latest -f Docker/Dockerfile_no_tensorflow Docker
```

### Containers
```sh
docker run --gpus all -d -p 9000:9000 -p 8081:8081 --name  kafka-pyflink-tf-container -v ${PWD}/code/:/home/kafka/code/ sarna320/kafka-pyflink-tensorflow:latest
```

```sh
docker run --gpus all -d -p 9000:9000 -p 8081:8081 --name  kafka-pyflink-container -v ${PWD}/code/:/home/kafka/code/ sarna320/kafka-pyflink:latest-only_services
```

### Bash 
```sh
docker exec -it kafka-pyflink-container bash
```
