# Kubesync
Kubesync synchronization tool between kubernetes pods and your host.

## Install
### From Pypi

The script is [available on PyPI](https://pypi.org/project/kubesync/). To install with pip:
```shell script
pip install kubesync
```

### From Source Code

```shell script
git clone https://github.com/ahmetkotan/kubesync
cd kubesync
python setup.py build
python setup.py install
```

## Usage
First, you must start watcher with ``kubesync watch`` command and then create selectors with ``kubesync create`` command.  

[![asciicast](https://asciinema.org/a/318292.svg)](https://asciinema.org/a/318292)
[![asciicast](https://asciinema.org/a/318293.svg)](https://asciinema.org/a/318293)

### Watch
Start watching for real-time synchronizations.  
``kubesync watch --help``
* **--pid-file** Watcher PID save to where if you want keep pid, otherwise save to ``~/.kubesync/kubesync.pid`` file.
```shell script
kubesync watch --pid-file=kubesync.pid
```

### Create
Create real-time synchronization.  
``kubesync create --help``
* **-l, --selector** Pod label selector parameter
* **-c, --container** Pod container name
* **-s, --src** Source path from your host
* **-d, --dest** Destination path from pod container
* **-n, --name** Synchronization name. This is not required. This will be created automatically if you don't define it.

```shell script
kubesync create --selector=app=kubesync-example -c nginx -s $(pwd)/examples/nginx-app/html\
 -d /usr/share/nginx/html/ --name example
```

### Sync
Use sync if you want to once move your files to pod container. This doesn't work as real-time. It moves files and shuts.  
``kubesync sync --help``
* **-l, --selector** Pod label selector parameter
* **-c, --container** Pod container name
* **-s, --src** Source path from your host
* **-d, --dest** Destination path from pod container

```shell script
kubesync sync --selector=app=kubesync-example -c nginx -s $(pwd)/examples/nginx-app/html\
 -d /usr/share/nginx/html/
```

### Get
Get your all synchronization configurations.
```shell script
kubesync get
```

### Delete
Delete your synchronization configuration.  
``kubesync delete --help``
```shell script
kubesync delete example
```

### Clean
Delete all your synchronization configurations.
```shell script
kubesync clean
```
