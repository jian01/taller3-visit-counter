#!/bin/sh
sudo prlimit -p "$$" --nofile=65535:65535
locust --worker
