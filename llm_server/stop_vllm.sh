#!/bin/bash
if [ -f vllm.pid ]; then
  kill -9 $(cat vllm.pid)
  rm vllm.pid
  echo "vLLM server stopped."
else
  echo "No PID file found. Server may not be running."
fi
