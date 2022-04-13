# python-weka-wrapper3 Docker (CPU)

## Build

```bash
docker build -t pww3 .
```

## Use

```bash
docker run -u $(id -u):$(id -g) -it -v $HOME/wekafiles/:/workspace/wekafiles pww3
```
