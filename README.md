# Kubesync
Kubesync synchronization tool between kubernetes pods or pods and your host.

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
If you want to ignoring some directory or files, create ``.kubesyncignore`` file like ``.gitignore`` in source path.


## Demo

![kubesync-watcher](examples/casts/kubesync-watcher.gif)
![kubesync-tool](examples/casts/kubesync-tool.gif)

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

### Clone
Use clone If you want to reverse synchronization. It's mean, this container path synchronizations to your host path.
``kubesync clone --help``
* **-l, --selector** Pod label selector parameter
* **-c, --container** Pod container name
* **-s, --src** Source path from your host
* **-d, --dest** Destination path from pod container
```shell script
kubesync clone --selector=app=kubesync-example -c nginx -s $(pwd)/examples/nginx-app/html\
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
