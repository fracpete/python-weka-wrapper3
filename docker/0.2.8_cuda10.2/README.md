# python-weka-wrapper3 Docker (CUDA 10.2)

## Docker

### Build local image

* Build the image from Docker file (from within `docker/0.2.8_cuda10.2`)

  ```bash
  docker build -t pww3_cuda10.2 .
  ```
  
* Run the container

  ```bash
  docker run --gpus=all -v /local/dir:/container/dir -it pww3_cuda10.2
  ```
  `/local/dir:/container/dir` maps a local disk directory into a directory inside the container

## Pre-built images

* Build

  ```bash
  docker build -t pww3:0.2.8_cuda10.2 .
  ```
  
* Tag

  ```bash
  docker tag \
    pww3:0.2.8_cuda10.2 \
    fracpete/pww3:0.2.8_cuda10.2
  ```
  
* Push

  ```bash
  docker push fracpete/pww3:0.2.8_cuda10.2
  ```

### Special directories

* `/workspace/wekafiles` - the directory that `WEKA_HOME` is pointing to (packages, props files, etc) 


## Usage

### Basic

For using the image interactively, you can run the following command: 

```bash
docker run --gpus=all -u $(id -u):$(id -g) \
    -it fracpete/pww3:0.2.8_cuda10.2
```

**NB:** Use `-v localdir:containerdir` to map directories from your host into the container.

### With local packages

Instead of having to reinstall your packages each time you start up the container, 
you can map your local Weka packages into the container as follows: 

```bash
docker run --gpus=all -u $(id -u):$(id -g) \
    -v $HOME/wekafiles/:/workspace/wekafiles \
    -it fracpete/pww3:0.2.8_cuda10.2
```

**NB:** That way, you can separate various package installations on your host system
in different directories.
