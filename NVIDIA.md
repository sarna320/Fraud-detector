## Setup
- install wsl (my version: 5.15.146.1-microsoft-standard-WSL2 Python 3.10.12)
- windows version
```sh
Caption                   Version    OSArchitecture BuildNumber
-------                   -------    -------------- -----------
Microsoft Windows 10 Home 10.0.19045 64-bitowy      19045
```
- instal your nvidia drivers on windows (my version: NVIDIA-SMI 545.37.02  12.3)
- check you nvida drivers in wsl
```sh
nvidia-smi
```
- setup nvidia on wsl https://docs.nvidia.com/cuda/wsl-user-guide/index.html (only this and correct version cuda)
- setup for docker wsl https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
- uinstall if needed https://askubuntu.com/questions/530043/removing-nvidia-cuda-toolkit-and-installing-new-one
```sh
sudo apt-get remove nvidia-cuda-toolkit
sudo apt-get remove --auto-remove nvidia-cuda-toolkit
```
```sh
sudo apt-get purge nvidia-cuda-toolkit  
```
or
```sh
sudo apt-get purge --auto-remove nvidia-cuda-toolkit 
```
Additionally, delete the /opt/cuda and ~/NVIDIA_GPU_Computing_SDK folders if they are present. and remove the export PATH=$PATH:/opt/cuda/bin and export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/cuda/lib:/opt/cuda/lib64 lines of the ~/.bash_profile file
- if you getting errors with sybmolic link follow https://github.com/microsoft/WSL/issues/5663#issuecomment-1068499676
- compability, it might work on new vesrsions but try to match it https://www.tensorflow.org/install/source#gpu

## Install pip and venv
``` sh
sudo apt update
sudo apt install python3-venv python3-pip
pip install --upgrade pip
```
## ENV creation
In folder with your project or your desired path
``` sh
python3 -m venv .env
```
## ENV activation
``` sh
source .env/bin/activate
```
## Instal tensorflow
my version: 2.16.1
```sh
pip install tensorflow[and-cuda]
```
## Path load
``` sh
export CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)")) &&\
export LD_LIBRARY_PATH="$CUDNN_PATH/lib":"/usr/local/cuda/lib64"
```
## Check Path
```sh
    echo $CUDNN_PATH &&\
    ls $CUDNN_PATH &&\
    echo $LD_LIBRARY_PATH
```
Path must be from your env example:
```sh
(.env) pawel@DESKTOP-KRPDJUA:~/projects/xxxxxx$ echo $CUDNN_PATH &&\
ls $CUDNN_PATH &&\
echo $LD_LIBRARY_PATH
/home/pawel/projects/xxxxxx/.env/lib/python3.10/site-packages/nvidia/cudnn
__init__.py  __pycache__  include  lib
/home/pawel/projects/xxxxxx/.env/lib/python3.10/site-packages/nvidia/cudnn/lib:/usr/local/cuda/lib64
```

## Check device
```sh
python3 -c "import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')))"
```
## Check in task manger if there is spike ine memory
```sh
python3 -c "import tensorflow as tf;
a = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[2, 3])
b = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[3, 2])
c = tf.matmul(a, b)
print(c)"
```