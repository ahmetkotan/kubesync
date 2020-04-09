#!/usr/bin/env bash

control_c() {
  kill -9 "$(cat kubesync.pid)"
  rm kubesync.pid
  kubesync clean
  exit;
}

kubesync clean
echo "Kubesync pre-sync" > html/index.html
POD_CHECK=$(kubectl get pods | grep kubesync-example-pod | awk '{print $2}')

while [[ ${POD_CHECK} != "1/1" ]]; do
    sleep 1
    POD_CHECK=$(kubectl get pods | grep kubesync-example-pod | awk '{print $2}')
done

kubesync watch --pid-file=kubesync.pid &
trap control_c SIGINT
while true; do
    curl localhost:8011
    sleep 2
done
