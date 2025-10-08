#!/bin/bash
# Start gunicorn with proper timeout settings to prevent random closures
gunicorn \
  --bind 0.0.0.0:5000 \
  --reuse-port \
  --reload \
  --timeout 120 \
  --graceful-timeout 60 \
  --workers 1 \
  --threads 4 \
  --worker-class sync \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --log-level info \
  --capture-output \
  --enable-stdio-inheritance \
  main:app
