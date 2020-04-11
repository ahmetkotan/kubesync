# Kubesync Example

### First Terminal
```shell script
cd nginx-app/
docker build -t kubesync-nginx:latest .
./watcher.sh
```

### Second Terminal
```shell script
kubesync create --selector=app=kubesync-example -c nginx -s $(pwd)/html\
  -d /usr/share/nginx/html/ --name example
kubectl apply -f app.yaml
echo "Kubesync post-sync" > html/index.html
```

### First Terminal Output
```textmate
Kubesync pre-sync
[+] Start watching.
[+] PID saved.
Kubesync pre-sync
Kubesync pre-sync
[+] app=kubesync-example::nginx container found.
[+] Handling kubesync/examples/nginx-app/html directory.
Kubesync pre-sync
Kubesync pre-sync
[+] Reloading app=kubesync-example::nginx/usr/share/nginx/html/
[+] Reloaded app=kubesync-example::nginx/usr/share/nginx/html/
Kubesync post-sync
Kubesync post-sync
Kubesync post-sync
```

``Ctrl+C`` for exit from watcher.


## Demo

![kubesync-watcher](casts/kubesync-watcher.gif)
![kubesync-tool](casts/kubesync-tool.gif)
