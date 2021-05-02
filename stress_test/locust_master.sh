#!/bin/sh
sudo prlimit -p "$$" --nofile=65535:65535
ulimit -n
locust --master --web-port 8080 --web-host 127.0.0.1
