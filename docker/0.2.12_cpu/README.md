# python-weka-wrapper3 Docker (CPU)

## Docker

### Build local image

* Build the image from Docker file (from within `docker/0.2.12_cpu`)

  ```bash
  docker build -t pww3_cpu .
  ```
  
* Run the container

  ```bash
  docker run -v /local/dir:/container/dir -it pww3_cpu
  ```
  `/local/dir:/container/dir` maps a local disk directory into a directory inside the container

## Pre-built images

* Build

  ```bash
  docker build -t pww3:0.2.12_cpu .
  ```
  
* Tag

  ```bash
  docker tag \
    pww3:0.2.12_cpu \
    fracpete/pww3:0.2.12_cpu
  ```
  
* Push

  ```bash
  docker push fracpete/pww3:0.2.12_cpu
  ```

### Special directories

* `/workspace/wekafiles` - the directory that `WEKA_HOME` is pointing to (packages, props files, etc) 


## Usage

### Basic

For using the image interactively, you can run the following command: 

```bash
docker run -u $(id -u):$(id -g) \
    -it fracpete/pww3:0.2.12_cpu
```

**NB:** Use `-v localdir:containerdir` to map directories from your host into the container.

### With local packages

Instead of having to reinstall your packages each time you start up the container, 
you can map your local Weka packages into the container as follows: 

```bash
docker run -u $(id -u):$(id -g) \
    -v $HOME/wekafiles/:/workspace/wekafiles \
    -it fracpete/pww3:0.2.12_cpu
```

**NB:** That way, you can separate various package installations on your host system
in different directories.
